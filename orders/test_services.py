"""place_order tests — coverage priority 3 in the PRD.

Denormalization, cart emptying, atomicity, unavailable rejection, coupons,
and the card_last4-only rule.
"""

from decimal import Decimal

import pytest

from products.models import Product

from .models import CartItem, CouponError, Order, OrderItem
from .services import ADDRESS_FIELDS, place_order
from .test_checkout_form import VALID_DATA


@pytest.fixture
def checkout_data():
    return dict(VALID_DATA)


def test_creates_an_order_with_denormalized_snapshot(cart, cart_item, checkout_data):
    order = place_order(cart, cart.user, checkout_data)

    assert order.user == cart.user
    assert order.total == Decimal("699.98")
    assert order.status == Order.Status.PLACED
    item = order.items.get()
    assert item.product_name == "Seraphine Home Hub"
    assert item.unit_price == Decimal("349.99")
    assert item.quantity == 2
    assert item.line_total == Decimal("699.98")


def test_order_history_survives_catalog_changes(cart, cart_item, checkout_data):
    order = place_order(cart, cart.user, checkout_data)

    product = cart_item.product
    product.name = "Seraphine Home Hub II"
    product.price = Decimal("999.00")
    product.save()

    item = order.items.get()
    assert item.product_name == "Seraphine Home Hub"
    assert item.unit_price == Decimal("349.99")


def test_addresses_and_email_are_copied_onto_the_order(cart, cart_item, checkout_data):
    order = place_order(cart, cart.user, checkout_data)

    assert order.email == "casey@example.com"
    assert order.shipping_street == "12 Cortex Lane"
    assert order.shipping_line2 == "Unit 7"
    assert order.shipping_state == "TX"
    assert order.billing_zip == "79015-1234"


def test_only_the_last_four_card_digits_are_stored(cart, cart_item, checkout_data):
    order = place_order(cart, cart.user, checkout_data)

    assert order.card_last4 == "4242"
    stored = [field.name for field in Order._meta.get_fields()]
    assert "card_number" not in stored
    assert "card_cvv" not in stored
    assert "card_expiry" not in stored


def test_the_cart_is_emptied(cart, cart_item, checkout_data):
    place_order(cart, cart.user, checkout_data)

    assert not cart.items.exists()
    assert cart.total() == Decimal("0.00")


def test_an_empty_cart_is_rejected(cart, checkout_data):
    with pytest.raises(ValueError):
        place_order(cart, cart.user, checkout_data)

    assert not Order.objects.exists()


def test_an_unavailable_product_is_rejected(
    cart, cart_item, unavailable_product, checkout_data
):
    cart.items.create(product=unavailable_product)

    with pytest.raises(ValueError, match="EchoPatch"):
        place_order(cart, cart.user, checkout_data)

    assert not Order.objects.exists()
    assert cart.items.count() == 2  # the cart is untouched


def test_a_failure_midway_leaves_no_partial_order(
    cart, cart_item, category, checkout_data, monkeypatch
):
    """All-or-nothing: if any line fails, no order and no emptied cart."""
    cart.add(
        Product.objects.create(
            name="Charging Pillow",
            slug="charging-pillow",
            price=Decimal("69.00"),
            category=category,
        )
    )

    original = OrderItem.objects.create
    calls = {"count": 0}

    def create_then_explode(**kwargs):
        calls["count"] += 1
        if calls["count"] == 2:
            raise RuntimeError("boom")
        return original(**kwargs)

    monkeypatch.setattr(OrderItem.objects, "create", create_then_explode)

    with pytest.raises(RuntimeError):
        place_order(cart, cart.user, checkout_data)

    assert not Order.objects.exists()
    assert not OrderItem.objects.exists()
    assert CartItem.objects.count() == 2


# --- Coupons (plans/coupons.md, Phase 2) --------------------------------------


def test_without_a_coupon_the_order_is_full_price(cart, cart_item, checkout_data):
    order = place_order(cart, cart.user, checkout_data)

    assert order.subtotal == Decimal("699.98")
    assert order.discount_amount == Decimal("0.00")
    assert order.total == Decimal("699.98")
    assert order.coupon is None
    assert order.coupon_code == ""
    assert order.coupon_percent_off is None
    assert order.coupon_product_name == ""


@pytest.mark.parametrize("blank", ["", "   "])
def test_a_blank_coupon_code_is_no_coupon(cart, cart_item, checkout_data, blank):
    order = place_order(cart, cart.user, checkout_data, coupon_code=blank)

    assert order.total == Decimal("699.98")
    assert order.coupon is None


def test_order_wide_coupon_discounts_and_snapshots(
    cart, cart_item, checkout_data, coupon
):
    order = place_order(cart, cart.user, checkout_data, coupon_code="THOUGHTS10")

    assert order.subtotal == Decimal("699.98")
    assert order.discount_amount == Decimal("70.00")
    assert order.total == Decimal("629.98")
    assert order.coupon == coupon
    assert order.coupon_code == "THOUGHTS10"
    assert order.coupon_percent_off == 10
    assert order.coupon_product_name == ""


def test_product_coupon_discounts_and_snapshots(
    cart, cart_item, checkout_data, product_coupon, category
):
    sticker = Product.objects.create(
        name="Thought Sticker",
        slug="thought-sticker",
        price=Decimal("19.99"),
        category=category,
    )
    CartItem.objects.create(cart=cart, product=sticker)

    order = place_order(cart, cart.user, checkout_data, coupon_code="SERAPHINE50")

    # 2 × $349.99 + $19.99 = $719.97; half off the Seraphine line = $349.99
    assert order.subtotal == Decimal("719.97")
    assert order.discount_amount == Decimal("349.99")
    assert order.total == Decimal("369.98")
    assert order.coupon_code == "SERAPHINE50"
    assert order.coupon_percent_off == 50
    assert order.coupon_product_name == "Seraphine Home Hub"


def test_line_prices_are_not_rewritten_by_a_coupon(
    cart, cart_item, checkout_data, product_coupon
):
    order = place_order(cart, cart.user, checkout_data, coupon_code="SERAPHINE50")

    assert order.items.get().unit_price == Decimal("349.99")


def test_the_coupon_code_ignores_case(cart, cart_item, checkout_data, coupon):
    order = place_order(cart, cart.user, checkout_data, coupon_code=" thoughts10 ")

    assert order.coupon_code == "THOUGHTS10"
    assert order.total == Decimal("629.98")


@pytest.mark.parametrize(
    ("code", "message"),
    [
        ("NOPE", "We don't recognize"),
        ("SUMMER25", "expired on Oct 31, 2025"),
        ("LEAKED20", "no longer available"),
        ("SERAPHINE50", "isn't in your cart"),
    ],
)
def test_an_unusable_coupon_places_no_order_and_keeps_the_cart(
    cart,
    checkout_data,
    expired_coupon,
    retired_coupon,
    product_coupon,
    category,
    code,
    message,
):
    sticker = Product.objects.create(
        name="Thought Sticker",
        slug="thought-sticker",
        price=Decimal("19.99"),
        category=category,
    )
    CartItem.objects.create(cart=cart, product=sticker)

    with pytest.raises(CouponError, match=message):
        place_order(cart, cart.user, checkout_data, coupon_code=code)

    assert not Order.objects.exists()
    assert not OrderItem.objects.exists()
    assert cart.items.count() == 1


def test_coupon_error_is_a_value_error():
    # Callers that already catch place_order's ValueError catch coupons too.
    assert issubclass(CouponError, ValueError)


# --- Requirement 3: a placed order is frozen --------------------------------


def _place_with_coupon(cart, checkout_data):
    order = place_order(cart, cart.user, checkout_data, coupon_code="SERAPHINE50")
    return order.pk


def _assert_frozen(pk):
    order = Order.objects.get(pk=pk)
    assert order.subtotal == Decimal("699.98")
    assert order.discount_amount == Decimal("349.99")
    assert order.total == Decimal("349.99")
    assert order.coupon_code == "SERAPHINE50"
    assert order.coupon_percent_off == 50
    assert order.coupon_product_name == "Seraphine Home Hub"
    return order


def test_retiring_the_coupon_leaves_placed_orders_unchanged(
    cart, cart_item, checkout_data, product_coupon
):
    pk = _place_with_coupon(cart, checkout_data)

    product_coupon.is_active = False
    product_coupon.save()

    assert _assert_frozen(pk).coupon == product_coupon


def test_editing_the_coupon_leaves_placed_orders_unchanged(
    cart, cart_item, checkout_data, product_coupon, category
):
    pk = _place_with_coupon(cart, checkout_data)

    product_coupon.code = "SERAPHINE75"
    product_coupon.percent_off = 75
    product_coupon.product = Product.objects.create(
        name="Seraphine Mini",
        slug="seraphine-mini",
        price=Decimal("99.00"),
        category=category,
    )
    product_coupon.save()

    _assert_frozen(pk)


def test_deleting_the_coupon_leaves_placed_orders_unchanged(
    cart, cart_item, checkout_data, product_coupon
):
    pk = _place_with_coupon(cart, checkout_data)

    product_coupon.delete()

    assert _assert_frozen(pk).coupon is None


def test_renaming_the_targeted_product_leaves_placed_orders_unchanged(
    cart, cart_item, checkout_data, product_coupon, product
):
    pk = _place_with_coupon(cart, checkout_data)

    product.name = "Seraphine Home Hub (2027 Edition)"
    product.save()

    _assert_frozen(pk)


# --- The Order model's subtotal default -------------------------------------


def test_an_order_without_a_subtotal_gets_one_from_the_invariant(
    customer, checkout_data
):
    addresses = {name: checkout_data[name] for name in ADDRESS_FIELDS}
    plain = Order.objects.create(
        user=customer, total=Decimal("9.00"), card_last4="4242", **addresses
    )
    discounted = Order.objects.create(
        user=customer,
        total=Decimal("9.00"),
        discount_amount=Decimal("1.00"),
        card_last4="4242",
        **addresses,
    )

    assert plain.subtotal == Decimal("9.00")
    assert discounted.subtotal == Decimal("10.00")
