"""Receipts show the discount — plans/coupons.md, Phase 4.

Every page that shows an order shows its coupon breakdown, read from the
order's snapshot. An order without a discount looks exactly as before.
"""

from decimal import Decimal
from http import HTTPStatus

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import Order
from .services import place_order
from .test_checkout_form import VALID_DATA

# Customer-facing and back-office order pages, by URL name.
CUSTOMER_PAGES = ["orders:confirmation", "orders:detail"]
ALL_PAGES = [*CUSTOMER_PAGES, "orders:manage_order_detail"]


@pytest.fixture
def discounted_order(cart, cart_item, coupon):
    """2 × Seraphine Home Hub ($699.98) with THOUGHTS10: −$70.00 → $629.98."""
    return place_order(cart, cart.user, dict(VALID_DATA), coupon_code="THOUGHTS10")


@pytest.fixture
def product_discounted_order(cart, cart_item, product_coupon):
    """2 × Seraphine Home Hub ($699.98) with SERAPHINE50: −$349.99 → $349.99."""
    return place_order(cart, cart.user, dict(VALID_DATA), coupon_code="SERAPHINE50")


@pytest.fixture
def plain_order(cart, cart_item):
    return place_order(cart, cart.user, dict(VALID_DATA))


def get_page(client, customer, staff_user, url_name, order):
    """Fetch an order page as the right viewer: staff for the back office."""
    viewer = staff_user if url_name.startswith("orders:manage") else customer
    client.force_login(viewer)
    response = client.get(reverse(url_name, kwargs={"pk": order.pk}))
    assert response.status_code == HTTPStatus.OK
    return response.content.decode()


# --- The model --------------------------------------------------------------


def test_has_discount(discounted_order, customer):
    assert discounted_order.has_discount
    plain = Order.objects.create(
        user=customer,
        total=Decimal("9.00"),
        card_last4="4242",
        **{k: v for k, v in VALID_DATA.items() if not k.startswith("card_")},
    )
    assert not plain.has_discount


# --- Every order page -------------------------------------------------------


@pytest.mark.parametrize("url_name", ALL_PAGES)
def test_an_order_wide_discount_is_shown(
    client, customer, staff_user, discounted_order, url_name
):
    page = get_page(client, customer, staff_user, url_name, discounted_order)

    assert "Subtotal" in page
    assert "$699.98" in page
    assert "Coupon THOUGHTS10" in page
    assert "(10% off)" in page
    assert "−$70.00" in page
    assert "$629.98" in page


@pytest.mark.parametrize("url_name", ALL_PAGES)
def test_a_product_discount_names_the_product(
    client, customer, staff_user, product_discounted_order, url_name
):
    page = get_page(client, customer, staff_user, url_name, product_discounted_order)

    assert "Coupon SERAPHINE50" in page
    assert "(50% off Seraphine Home Hub)" in page
    assert "−$349.99" in page


@pytest.mark.parametrize("url_name", ALL_PAGES)
def test_an_order_without_a_discount_has_no_breakdown(
    client, customer, staff_user, plain_order, url_name
):
    page = get_page(client, customer, staff_user, url_name, plain_order)

    # Not a bare "Coupon": the back-office shell has a "Coupons" tab.
    assert "Subtotal" not in page
    assert "Coupon " not in page
    assert "% off" not in page
    assert "−$" not in page
    assert "$699.98" in page


@pytest.mark.parametrize("url_name", ALL_PAGES)
def test_the_receipt_survives_the_coupon_being_deleted(
    client, customer, staff_user, product_discounted_order, product_coupon, url_name
):
    product_coupon.delete()

    page = get_page(client, customer, staff_user, url_name, product_discounted_order)

    assert "Coupon SERAPHINE50" in page
    assert "(50% off Seraphine Home Hub)" in page
    assert "−$349.99" in page


@pytest.mark.parametrize("url_name", ALL_PAGES)
def test_the_receipt_ignores_later_coupon_edits(
    client, customer, staff_user, discounted_order, coupon, url_name
):
    coupon.percent_off = 50
    coupon.is_active = False
    coupon.save()

    page = get_page(client, customer, staff_user, url_name, discounted_order)

    assert "(10% off)" in page
    assert "−$70.00" in page
    assert "50% off" not in page


# --- Lists and the admin ----------------------------------------------------


def test_history_lists_the_charged_total(client, customer, discounted_order):
    client.force_login(customer)

    page = client.get(reverse("orders:history")).content.decode()

    assert "$629.98" in page
    assert "$699.98" not in page


def test_order_admin_lists_the_coupon_code(client, discounted_order):
    admin_user = get_user_model().objects.create_superuser(
        username="admin", password="admin123"
    )
    client.force_login(admin_user)

    response = client.get(reverse("admin:orders_order_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert "THOUGHTS10" in response.content.decode()
