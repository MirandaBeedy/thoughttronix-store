"""Coupon model tests — plans/coupons.md, Phase 1.

The coupon on its own: lookup, the discount math and rounding, and every
customer-facing rejection in its fixed order.
"""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import ProtectedError

from products.models import Product

from .models import CartItem, Coupon, CouponError


@pytest.fixture
def cheap_product(category):
    return Product.objects.create(
        name="Thought Sticker",
        slug="thought-sticker",
        price=Decimal("19.99"),
        category=category,
    )


@pytest.fixture
def look_alike(category):
    return Product.objects.create(
        name="Seraphine Mini",
        slug="seraphine-mini",
        price=Decimal("99.00"),
        category=category,
    )


# --- Basics -----------------------------------------------------------------


def test_str_is_the_code(coupon):
    assert str(coupon) == "THOUGHTS10"


def test_code_is_stored_uppercase_and_trimmed(db):
    coupon = Coupon.objects.create(code="  welcome5 ", percent_off=5)
    coupon.refresh_from_db()
    assert coupon.code == "WELCOME5"


def test_codes_are_unique_regardless_of_case(coupon):
    with pytest.raises(IntegrityError):
        Coupon.objects.create(code="thoughts10", percent_off=20)


@pytest.mark.parametrize("percent", [0, 101])
def test_percent_off_outside_1_to_100_is_invalid(db, percent):
    coupon = Coupon(code="BAD", percent_off=percent)
    with pytest.raises(ValidationError) as excinfo:
        coupon.full_clean()
    assert "percent_off" in excinfo.value.message_dict


@pytest.mark.parametrize("percent", [1, 100])
def test_percent_off_bounds_are_valid(db, percent):
    Coupon(code="EDGE", percent_off=percent).full_clean()


def test_a_targeted_product_cannot_be_deleted(product_coupon, product):
    with pytest.raises(ProtectedError):
        product.delete()


def test_coupon_is_registered_in_admin():
    assert admin.site.is_registered(Coupon)


# --- Lookup -----------------------------------------------------------------


@pytest.mark.parametrize("typed", ["THOUGHTS10", "thoughts10", "  Thoughts10  "])
def test_get_by_code_ignores_case_and_spaces(coupon, typed):
    assert Coupon.objects.get_by_code(typed) == coupon


def test_get_by_code_rejects_an_unknown_code(db):
    with pytest.raises(CouponError) as excinfo:
        Coupon.objects.get_by_code("nope")
    assert str(excinfo.value) == "We don't recognize the coupon code “NOPE”."


# --- Expiry -----------------------------------------------------------------


def test_blank_expiry_never_expires(coupon):
    far_future = datetime(2999, 1, 1, tzinfo=UTC)
    assert not coupon.is_expired(now=far_future)


def test_expiry_exactly_now_counts_as_expired(expired_coupon):
    assert expired_coupon.is_expired(now=expired_coupon.expires_at)


def test_one_second_before_expiry_is_not_expired(expired_coupon):
    just_before = expired_coupon.expires_at - timedelta(seconds=1)
    assert not expired_coupon.is_expired(now=just_before)


# --- The math ---------------------------------------------------------------


def test_order_wide_discount_takes_percent_of_the_cart_total(cart, cart_item, coupon):
    # 2 × $349.99 = $699.98; 10% = $69.998 → $70.00
    assert coupon.discount_for(cart) == Decimal("70.00")


def test_product_discount_takes_percent_of_that_line_only(
    cart, cart_item, cheap_product, product_coupon
):
    CartItem.objects.create(cart=cart, product=cheap_product, quantity=3)
    # 50% of the Seraphine line (2 × $349.99); the stickers are untouched.
    assert product_coupon.discount_for(cart) == Decimal("349.99")


def test_product_discount_covers_every_unit_of_the_product(
    cart, product, product_coupon
):
    CartItem.objects.create(cart=cart, product=product, quantity=3)
    # 50% of 3 × $349.99 = $524.985 → $524.99
    assert product_coupon.discount_for(cart) == Decimal("524.99")


def test_discount_rounds_to_the_cent(cart, cheap_product):
    CartItem.objects.create(cart=cart, product=cheap_product)
    coupon = Coupon.objects.create(code="FIFTEEN", percent_off=15)
    # 15% of $19.99 = $2.9985 → $3.00
    assert coupon.discount_for(cart) == Decimal("3.00")


def test_rounding_is_half_up_not_bankers(cart, category):
    nickel = Product.objects.create(
        name="Nickel Thought", slug="nickel", price=Decimal("0.05"), category=category
    )
    CartItem.objects.create(cart=cart, product=nickel)
    coupon = Coupon.objects.create(code="TENPCT", percent_off=10)
    # 10% of $0.05 = $0.005 → $0.01 (banker's rounding would give $0.00)
    assert coupon.discount_for(cart) == Decimal("0.01")


def test_hundred_percent_discounts_everything(cart, cart_item):
    coupon = Coupon.objects.create(code="FREE", percent_off=100)
    assert coupon.discount_for(cart) == Decimal("699.98")


# --- Rejections -------------------------------------------------------------


def test_retired_coupon_is_rejected(cart, cart_item, retired_coupon):
    with pytest.raises(CouponError) as excinfo:
        retired_coupon.discount_for(cart)
    assert str(excinfo.value) == "The coupon LEAKED20 is no longer available."


def test_expired_coupon_is_rejected_with_its_date(cart, cart_item, expired_coupon):
    with pytest.raises(CouponError) as excinfo:
        expired_coupon.discount_for(cart)
    assert str(excinfo.value) == "The coupon SUMMER25 expired on Oct 31, 2025."


def test_future_expiry_is_accepted(cart, cart_item, coupon):
    coupon.expires_at = datetime(2999, 1, 1, tzinfo=UTC)
    coupon.save()
    assert coupon.discount_for(cart) == Decimal("70.00")


def test_product_coupon_rejected_when_product_not_in_cart(
    cart, cheap_product, product_coupon
):
    CartItem.objects.create(cart=cart, product=cheap_product)
    with pytest.raises(CouponError) as excinfo:
        product_coupon.discount_for(cart)
    assert str(excinfo.value) == (
        "SERAPHINE50 applies only to Seraphine Home Hub, which isn't in your cart."
    )


def test_product_coupon_ignores_look_alike_products(cart, look_alike, product_coupon):
    CartItem.objects.create(cart=cart, product=look_alike)
    with pytest.raises(CouponError, match="isn't in your cart"):
        product_coupon.discount_for(cart)


# --- Rejection order: the first failing check wins --------------------------


def test_retired_beats_expired(cart, cart_item, expired_coupon):
    expired_coupon.is_active = False
    expired_coupon.save()
    with pytest.raises(CouponError, match="no longer available"):
        expired_coupon.discount_for(cart)


def test_expired_beats_product_not_in_cart(cart, cheap_product, product_coupon):
    CartItem.objects.create(cart=cart, product=cheap_product)
    product_coupon.expires_at = datetime(2025, 10, 31, 12, 0, tzinfo=UTC)
    product_coupon.save()
    with pytest.raises(CouponError, match="expired on"):
        product_coupon.discount_for(cart)
