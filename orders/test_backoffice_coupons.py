"""Back-office coupon management — plans/coupons.md, Phase 5.

Access control, the list (statuses, empty state), create/edit round-trips,
retiring via the toggle, and the form's validation.
"""

from datetime import UTC, datetime
from decimal import Decimal
from http import HTTPStatus

import pytest
from django.urls import NoReverseMatch, reverse

from products.models import Product

from .forms import ManageCouponForm
from .models import Coupon, Order
from .services import place_order
from .test_checkout_form import VALID_DATA

pytestmark = pytest.mark.django_db


def manage_urls(coupon):
    """Every staff-only coupon URL, for the access-control sweeps."""
    return [
        reverse("orders:manage_coupons"),
        reverse("orders:manage_coupon_create"),
        reverse("orders:manage_coupon_update", kwargs={"pk": coupon.pk}),
    ]


def coupon_data(**overrides):
    data = {
        "code": "welcome5",
        "percent_off": "5",
        "product": "",
        "expires_at": "",
        "is_active": "on",
    }
    data.update(overrides)
    return data


# --- Access control ---------------------------------------------------------


def test_anonymous_users_are_sent_to_login(client, coupon):
    for url in manage_urls(coupon):
        response = client.get(url)
        assert response.status_code == HTTPStatus.FOUND, url
        assert reverse("accounts:login") in response.url


def test_customers_get_403(client, customer, coupon):
    client.force_login(customer)
    for url in manage_urls(coupon):
        assert client.get(url).status_code == HTTPStatus.FORBIDDEN, url


def test_staff_get_200(client, staff_user, coupon):
    client.force_login(staff_user)
    for url in manage_urls(coupon):
        assert client.get(url).status_code == HTTPStatus.OK, url


def test_customers_cannot_create_coupons(client, customer):
    client.force_login(customer)
    client.post(reverse("orders:manage_coupon_create"), coupon_data())
    assert not Coupon.objects.exists()


def test_there_is_no_delete(coupon):
    with pytest.raises(NoReverseMatch):
        reverse("orders:manage_coupon_delete", kwargs={"pk": coupon.pk})


# --- The tab and the list ---------------------------------------------------


def test_coupons_tab_is_in_the_staff_shell_and_active(client, staff_user):
    client.force_login(staff_user)

    page = client.get(reverse("orders:manage_coupons")).content.decode()

    assert f'tab-active"\n       href="{reverse("orders:manage_coupons")}"' in page


def test_coupons_tab_appears_on_other_back_office_pages(client, staff_user):
    client.force_login(staff_user)

    page = client.get(reverse("orders:manage_orders")).content.decode()

    assert reverse("orders:manage_coupons") in page


def test_list_has_a_designed_empty_state(client, staff_user):
    client.force_login(staff_user)

    page = client.get(reverse("orders:manage_coupons")).content.decode()

    assert "No coupons yet" in page
    assert "Create the first coupon" in page


def test_list_shows_each_coupon_and_its_status(
    client, staff_user, coupon, product_coupon, expired_coupon, retired_coupon
):
    client.force_login(staff_user)

    page = client.get(reverse("orders:manage_coupons")).content.decode()

    assert "4 coupons" in page
    for code in ["THOUGHTS10", "SERAPHINE50", "SUMMER25", "LEAKED20"]:
        assert code in page
    assert "Whole order" in page
    assert "Seraphine Home Hub" in page
    assert "Never" in page
    assert "Oct 31, 2025 12:00 UTC" in page
    assert page.count(">Active</span>") == 2
    assert page.count(">Expired</span>") == 1
    assert page.count(">Retired</span>") == 1


def test_status_property(coupon, expired_coupon, retired_coupon):
    assert coupon.status == "Active"
    assert expired_coupon.status == "Expired"
    assert retired_coupon.status == "Retired"
    expired_coupon.is_active = False
    assert expired_coupon.status == "Retired"  # retired wins, as at checkout


# --- Create and edit --------------------------------------------------------


def test_staff_can_create_an_order_wide_coupon(client, staff_user):
    client.force_login(staff_user)

    response = client.post(reverse("orders:manage_coupon_create"), coupon_data())

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse("orders:manage_coupons")
    coupon = Coupon.objects.get()
    assert coupon.code == "WELCOME5"  # uppercased
    assert coupon.percent_off == 5
    assert coupon.product is None
    assert coupon.expires_at is None
    assert coupon.is_active


def test_create_shows_a_success_message(client, staff_user):
    client.force_login(staff_user)

    response = client.post(
        reverse("orders:manage_coupon_create"), coupon_data(), follow=True
    )

    assert "Coupon WELCOME5 created." in response.content.decode()


def test_staff_can_create_a_product_coupon_with_an_expiry(client, staff_user, product):
    client.force_login(staff_user)

    client.post(
        reverse("orders:manage_coupon_create"),
        coupon_data(product=str(product.pk), expires_at="2027-01-31T23:59"),
    )

    coupon = Coupon.objects.get()
    assert coupon.product == product
    assert coupon.expires_at == datetime(2027, 1, 31, 23, 59, tzinfo=UTC)


def test_staff_can_edit_a_coupon(client, staff_user, coupon):
    client.force_login(staff_user)

    client.post(
        reverse("orders:manage_coupon_update", kwargs={"pk": coupon.pk}),
        coupon_data(code="THOUGHTS10", percent_off="15"),
    )

    coupon.refresh_from_db()
    assert coupon.percent_off == 15


def test_staff_can_retire_a_coupon(client, staff_user, coupon):
    client.force_login(staff_user)
    data = coupon_data(code="THOUGHTS10", percent_off="10")
    del data["is_active"]  # an unchecked toggle sends nothing

    client.post(reverse("orders:manage_coupon_update", kwargs={"pk": coupon.pk}), data)

    coupon.refresh_from_db()
    assert not coupon.is_active
    assert coupon.status == "Retired"


def test_retiring_in_the_back_office_leaves_placed_orders_alone(
    client, staff_user, cart, cart_item, coupon
):
    """Requirement 3, end to end through the staff screen."""
    order = place_order(cart, cart.user, dict(VALID_DATA), coupon_code="THOUGHTS10")
    client.force_login(staff_user)
    data = coupon_data(code="THOUGHTS10", percent_off="10")
    del data["is_active"]

    client.post(reverse("orders:manage_coupon_update", kwargs={"pk": coupon.pk}), data)

    order = Order.objects.get(pk=order.pk)
    assert order.total == Decimal("629.98")
    assert order.discount_amount == Decimal("70.00")
    assert order.coupon_code == "THOUGHTS10"


# --- Validation -------------------------------------------------------------


@pytest.mark.parametrize("percent", ["0", "101"])
def test_percent_off_must_be_1_to_100(client, staff_user, percent):
    client.force_login(staff_user)

    response = client.post(
        reverse("orders:manage_coupon_create"), coupon_data(percent_off=percent)
    )

    assert response.status_code == HTTPStatus.OK
    assert not Coupon.objects.exists()


def test_duplicate_code_in_any_case_is_a_form_error(client, staff_user, coupon):
    client.force_login(staff_user)

    response = client.post(
        reverse("orders:manage_coupon_create"), coupon_data(code="thoughts10")
    )

    assert response.status_code == HTTPStatus.OK
    assert "Coupon with this Code already exists." in response.content.decode()
    assert Coupon.objects.count() == 1


def test_code_is_required(client, staff_user):
    client.force_login(staff_user)

    response = client.post(reverse("orders:manage_coupon_create"), coupon_data(code=""))

    assert response.status_code == HTTPStatus.OK
    assert not Coupon.objects.exists()


def test_product_menu_offers_available_products_and_whole_order(
    product, unavailable_product
):
    form = ManageCouponForm()

    assert product in form.fields["product"].queryset
    assert unavailable_product not in form.fields["product"].queryset
    assert form.fields["product"].empty_label == "Whole order"


def test_product_menu_keeps_a_coupons_now_unavailable_product(product_coupon):
    product = product_coupon.product
    product.is_available = False
    product.save()

    form = ManageCouponForm(instance=product_coupon)

    assert product in form.fields["product"].queryset
    assert (
        not form.fields["product"]
        .queryset.exclude(pk=product.pk)
        .filter(is_available=False)
    )


def test_editing_keeps_the_coupons_unavailable_product_valid(
    client, staff_user, product_coupon
):
    product = product_coupon.product
    product.is_available = False
    product.save()
    client.force_login(staff_user)

    response = client.post(
        reverse("orders:manage_coupon_update", kwargs={"pk": product_coupon.pk}),
        coupon_data(code="SERAPHINE50", percent_off="40", product=str(product.pk)),
    )

    assert response.status_code == HTTPStatus.FOUND
    product_coupon.refresh_from_db()
    assert product_coupon.percent_off == 40
    assert Product.objects.filter(pk=product.pk).exists()
