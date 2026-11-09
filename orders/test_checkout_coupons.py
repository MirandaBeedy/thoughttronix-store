"""Coupons at checkout — plans/coupons.md, Phase 3.

The coupon form, the cart's checkout summary, the HTMX "Apply"
preview, and the checkout POST that places a discounted order.
"""

from decimal import Decimal
from http import HTTPStatus

import pytest
from django.urls import reverse

from products.models import Product

from . import views
from .forms import CheckoutForm, CouponForm
from .models import CartItem, CouponError, Order
from .test_checkout_form import VALID_DATA

# Each unusable code (with a cart holding only a sticker) and its message.
UNUSABLE = [
    ("NOPE", "We don&#x27;t recognize the coupon code “NOPE”."),
    ("SUMMER25", "The coupon SUMMER25 expired on Oct 31, 2025."),
    ("LEAKED20", "The coupon LEAKED20 is no longer available."),
    (
        "SERAPHINE50",
        "SERAPHINE50 applies only to Seraphine Home Hub, which isn&#x27;t in your cart.",
    ),
]


@pytest.fixture
def all_coupons(coupon, product_coupon, expired_coupon, retired_coupon):
    return [coupon, product_coupon, expired_coupon, retired_coupon]


@pytest.fixture
def sticker_cart(cart, category):
    """A cart without the Seraphine — so SERAPHINE50 has nothing to discount."""
    sticker = Product.objects.create(
        name="Thought Sticker",
        slug="thought-sticker",
        price=Decimal("19.99"),
        category=category,
    )
    CartItem.objects.create(cart=cart, product=sticker)
    return cart


# --- The form ---------------------------------------------------------------


def coupon_form(cart, code):
    return CouponForm(data={"coupon_code": code}, cart=cart)


def test_checkout_form_stays_coupon_free():
    """The PRD's declarative showcase is untouched: coupons live elsewhere."""
    assert "coupon_code" not in CheckoutForm().fields


@pytest.mark.parametrize("blank", ["", "   "])
def test_coupon_code_is_optional(cart, blank):
    form = coupon_form(cart, blank)
    assert form.is_valid()
    assert form.cleaned_data["coupon_code"] == ""


def test_coupon_form_requires_a_cart():
    with pytest.raises(TypeError):
        CouponForm(data={"coupon_code": "THOUGHTS10"})


def test_coupon_input_joins_the_checkout_form_by_attribute(cart):
    assert 'form="checkout-form"' in str(CouponForm(cart=cart)["coupon_code"])


def test_a_valid_code_passes_and_is_normalized(cart, cart_item, coupon):
    form = coupon_form(cart, " thoughts10 ")
    assert form.is_valid()
    assert form.cleaned_data["coupon_code"] == "THOUGHTS10"


@pytest.mark.parametrize(
    ("code", "message"),
    [
        ("NOPE", "We don't recognize the coupon code “NOPE”."),
        ("SUMMER25", "The coupon SUMMER25 expired on Oct 31, 2025."),
        ("LEAKED20", "The coupon LEAKED20 is no longer available."),
        (
            "SERAPHINE50",
            "SERAPHINE50 applies only to Seraphine Home Hub, which isn't in your cart.",
        ),
    ],
)
def test_an_unusable_code_is_a_coupon_field_error(
    sticker_cart, all_coupons, code, message
):
    form = coupon_form(sticker_cart, code)
    assert not form.is_valid()
    assert form.errors["coupon_code"] == [message]


# --- Cart.checkout_summary --------------------------------------------------


def test_summary_without_a_code_is_full_price(cart, cart_item):
    summary = cart.checkout_summary()
    assert summary.subtotal == Decimal("699.98")
    assert summary.discount == Decimal("0.00")
    assert summary.total == Decimal("699.98")
    assert summary.coupon is None
    assert summary.error == ""


def test_summary_with_a_valid_code(cart, cart_item, coupon):
    summary = cart.checkout_summary("thoughts10")
    assert summary.discount == Decimal("70.00")
    assert summary.total == Decimal("629.98")
    assert summary.coupon == coupon
    assert summary.error == ""


def test_summary_with_an_unusable_code_carries_the_error(
    cart, cart_item, retired_coupon
):
    summary = cart.checkout_summary("LEAKED20")
    assert summary.total == Decimal("699.98")
    assert summary.coupon is None
    assert summary.error == "The coupon LEAKED20 is no longer available."


# --- The HTMX "Apply" preview -----------------------------------------------


def apply(client, code):
    return client.post(reverse("orders:apply_coupon"), {"coupon_code": code})


def test_apply_requires_login(client, db):
    response = apply(client, "THOUGHTS10")
    assert response.status_code == HTTPStatus.FOUND
    assert reverse("accounts:login") in response.url


def test_apply_is_post_only(client, customer):
    client.force_login(customer)
    response = client.get(reverse("orders:apply_coupon"))
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_apply_previews_an_order_wide_discount(client, customer, cart_item, coupon):
    client.force_login(customer)

    response = apply(client, "thoughts10")

    assert response.status_code == HTTPStatus.OK
    page = response.content.decode()
    assert "<html" not in page  # a partial, never base.html
    assert 'id="order-summary"' in page
    assert "Coupon THOUGHTS10" in page
    assert "(10% off)" in page
    assert "−$70.00" in page
    assert "$629.98" in page
    # The "Place order" button's amount is refreshed out-of-band.
    assert 'id="place-order-total" hx-swap-oob="true">629.98<' in page


def test_apply_previews_a_product_discount(client, customer, cart_item, product_coupon):
    client.force_login(customer)

    page = apply(client, "SERAPHINE50").content.decode()

    assert "(50% off Seraphine Home Hub)" in page
    assert "−$349.99" in page


@pytest.mark.parametrize(("code", "message"), UNUSABLE)
def test_apply_shows_why_a_code_is_unusable(
    client, customer, sticker_cart, all_coupons, code, message
):
    client.force_login(customer)

    page = apply(client, code).content.decode()

    assert message in page
    assert 'id="place-order-total" hx-swap-oob="true">19.99<' in page


def test_apply_with_a_blank_code_shows_the_plain_summary(client, customer, cart_item):
    client.force_login(customer)

    page = apply(client, "").content.decode()

    assert "Coupon " not in page
    assert 'role="alert"' not in page
    assert "$699.98" in page


def test_apply_places_nothing(client, customer, cart_item, coupon):
    client.force_login(customer)
    apply(client, "THOUGHTS10")
    assert not Order.objects.exists()
    assert CartItem.objects.exists()


# --- The checkout page and POST ---------------------------------------------


def checkout(client, code):
    return client.post(reverse("orders:checkout"), {**VALID_DATA, "coupon_code": code})


def test_checkout_page_offers_the_coupon_box(client, customer, cart_item):
    client.force_login(customer)

    page = client.get(reverse("orders:checkout")).content.decode()

    assert 'id="checkout-form"' in page
    assert 'name="coupon_code"' in page
    assert reverse("orders:apply_coupon") in page
    assert 'id="order-summary"' in page
    assert 'id="place-order-total">699.98<' in page


def test_checkout_with_a_valid_code_places_a_discounted_order(
    client, customer, cart_item, coupon
):
    client.force_login(customer)

    response = checkout(client, "thoughts10")

    order = Order.objects.get()
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse("orders:confirmation", kwargs={"pk": order.pk})
    assert order.total == Decimal("629.98")
    assert order.coupon_code == "THOUGHTS10"
    assert not CartItem.objects.exists()


def test_checkout_with_a_blank_code_places_a_full_price_order(
    client, customer, cart_item
):
    client.force_login(customer)

    checkout(client, "")

    order = Order.objects.get()
    assert order.total == Decimal("699.98")
    assert order.coupon_code == ""


@pytest.mark.parametrize(("code", "message"), UNUSABLE)
def test_checkout_with_an_unusable_code_places_nothing(
    client, customer, sticker_cart, all_coupons, code, message
):
    client.force_login(customer)

    response = checkout(client, code)

    assert response.status_code == HTTPStatus.OK
    page = response.content.decode()
    assert page.count(message) == 1  # shown once, in the summary
    assert f'value="{code}"' in page  # the typed code is preserved
    assert "12 Cortex Lane" in page  # so is everything else
    assert not Order.objects.exists()
    assert CartItem.objects.exists()


def test_a_valid_coupon_survives_an_unrelated_form_error(
    client, customer, cart_item, coupon
):
    client.force_login(customer)

    response = client.post(
        reverse("orders:checkout"),
        {**VALID_DATA, "coupon_code": "THOUGHTS10", "card_number": "4242"},
    )

    page = response.content.decode()
    assert response.status_code == HTTPStatus.OK
    assert "−$70.00" in page
    assert 'id="place-order-total">629.98<' in page
    assert not Order.objects.exists()


def test_backstop_coupon_rejection_is_shown_on_the_coupon_field(
    client, customer, cart_item, coupon, monkeypatch
):
    """The coupon passed the form, then place_order refused it (e.g. it
    was retired in between): the page re-renders with the reason."""

    def refuse(*args, **kwargs):
        raise CouponError("The coupon THOUGHTS10 is no longer available.")

    monkeypatch.setattr(views, "place_order", refuse)
    client.force_login(customer)

    response = checkout(client, "THOUGHTS10")

    assert response.status_code == HTTPStatus.OK
    assert "The coupon THOUGHTS10 is no longer available." in response.content.decode()
    assert CartItem.objects.exists()


def test_card_and_coupon_errors_show_together(
    client, customer, sticker_cart, retired_coupon
):
    client.force_login(customer)

    response = client.post(
        reverse("orders:checkout"),
        {**VALID_DATA, "coupon_code": "LEAKED20", "card_number": "4242"},
    )

    page = response.content.decode()
    assert "The coupon LEAKED20 is no longer available." in page
    assert "Enter a valid card number." in page
    assert not Order.objects.exists()


def test_backstop_other_rejections_are_shown_as_a_form_alert(
    client, customer, cart_item, monkeypatch
):
    def refuse(*args, **kwargs):
        raise ValueError("No longer available: Seraphine Home Hub.")

    monkeypatch.setattr(views, "place_order", refuse)
    client.force_login(customer)

    response = checkout(client, "")

    page = response.content.decode()
    assert response.status_code == HTTPStatus.OK
    assert 'class="alert alert-error"' in page
    assert "No longer available: Seraphine Home Hub." in page
