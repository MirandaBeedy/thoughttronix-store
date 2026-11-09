from dataclasses import dataclass
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.formats import date_format

from products.models import Product

CENT = Decimal("0.01")


class Cart(models.Model):
    """A customer's cart — one per user, created lazily on first touch."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
    )

    def __str__(self):
        return f"Cart for {self.user.username}"

    @classmethod
    def for_user(cls, user):
        """Return the user's cart, creating it on first touch."""
        cart, _ = cls.objects.get_or_create(user=user)
        return cart

    def add(self, product):
        """Add a product to the cart; a duplicate add increments its line."""
        item, created = self.items.get_or_create(product=product)
        if not created:
            item.quantity += 1
            item.save()
        return item

    def lines(self):
        """Line items with their products loaded, ready for display."""
        return self.items.select_related("product")

    def total(self):
        return sum((item.line_total for item in self.lines()), Decimal("0.00"))

    def item_count(self):
        """Total units across all lines — the navbar badge number."""
        return self.items.aggregate(count=models.Sum("quantity"))["count"] or 0

    def checkout_summary(self, coupon_code: str = "") -> "CheckoutSummary":
        """Price the cart with an optional coupon, for display at checkout.

        Never raises: a coupon that can't be applied comes back as the
        summary's ``error``, with the cart at full price.
        """
        subtotal = self.total()
        if not normalize_code(coupon_code):
            return CheckoutSummary(subtotal=subtotal)
        try:
            coupon = Coupon.objects.select_related("product").get_by_code(coupon_code)
            discount = coupon.discount_for(self)
        except CouponError as error:
            return CheckoutSummary(subtotal=subtotal, error=str(error))
        return CheckoutSummary(subtotal=subtotal, discount=discount, coupon=coupon)


class CartItem(models.Model):
    """One product line in a cart; the cart–product pair is unique."""

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"], name="unique_cart_product"
            )
        ]

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"

    @property
    def line_total(self):
        return self.product.price * self.quantity

    def increment(self):
        self.quantity += 1
        self.save()

    def decrement(self):
        """Step the quantity down, stopping at one — removal is explicit."""
        if self.quantity > 1:
            self.quantity -= 1
            self.save()


class CouponError(ValueError):
    """A coupon can't be applied; ``str(error)`` is the customer-facing reason.

    A ``ValueError`` so it travels the same path as ``place_order``'s other
    checkout rejections (empty cart, unavailable product).
    """


def normalize_code(code: str) -> str:
    """Coupon codes are case-insensitive: compare and store them uppercased."""
    return code.strip().upper()


class CouponQuerySet(models.QuerySet):
    def get_by_code(self, code: str) -> "Coupon":
        """Return the coupon for ``code``, ignoring case and surrounding spaces.

        Raises ``CouponError`` if no coupon has that code.
        """
        normalized = normalize_code(code)
        try:
            return self.get(code=normalized)
        except self.model.DoesNotExist:
            raise CouponError(
                f"We don't recognize the coupon code “{normalized}”."
            ) from None


class Coupon(models.Model):
    """A percentage discount, order-wide or scoped to one product.

    A blank ``product`` means the coupon discounts the whole order; a set
    ``product`` means it discounts only that product's cart line. Retiring
    (``is_active`` off) and expiring (``expires_at`` passed) are separate
    facts with separate messages. Orders snapshot what they used, so
    editing or retiring a coupon never rewrites an order.
    """

    code = models.CharField(max_length=30, unique=True)
    percent_off = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="coupons",
        help_text="Leave blank to discount the whole order.",
    )
    expires_at = models.DateTimeField(
        null=True, blank=True, help_text="Leave blank to never expire."
    )
    is_active = models.BooleanField(
        default=True, help_text="Uncheck to retire the coupon."
    )
    created_at = models.DateTimeField(default=timezone.now)

    objects = CouponQuerySet.as_manager()

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        self.code = normalize_code(self.code)
        super().save(*args, **kwargs)

    def is_expired(self, now: datetime | None = None) -> bool:
        """True once ``expires_at`` is reached; a blank expiry never expires."""
        if self.expires_at is None:
            return False
        return self.expires_at <= (now or timezone.now())

    @property
    def status(self) -> str:
        """The back-office label: Retired, Expired or Active (retired wins)."""
        if not self.is_active:
            return "Retired"
        if self.is_expired():
            return "Expired"
        return "Active"

    def discount_for(self, cart: Cart) -> Decimal:
        """Return this coupon's discount on ``cart``, rounded to the cent.

        Checks run in a fixed order and the first failure wins: retired,
        expired, then (for a product coupon) whether that product is in
        the cart. An order-wide coupon takes ``percent_off`` of the cart
        total; a product coupon takes it of that product's line only.

        Raises ``CouponError`` with a customer-facing message if the
        coupon can't be applied.
        """
        if not self.is_active:
            raise CouponError(f"The coupon {self.code} is no longer available.")
        if self.is_expired():
            expired_on = date_format(timezone.localtime(self.expires_at), "M j, Y")
            raise CouponError(f"The coupon {self.code} expired on {expired_on}.")

        if self.product_id is None:
            base = cart.total()
        else:
            line = cart.lines().filter(product_id=self.product_id).first()
            if line is None:
                raise CouponError(
                    f"{self.code} applies only to {self.product.name}, "
                    "which isn't in your cart."
                )
            base = line.line_total

        discount = base * self.percent_off / Decimal(100)
        return discount.quantize(CENT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class CheckoutSummary:
    """A cart's price with an optional coupon — what checkout displays.

    ``coupon`` is set only when it applied; ``error`` is the reason it
    didn't. Not stored: the order snapshot is the record.
    """

    subtotal: Decimal
    discount: Decimal = Decimal("0.00")
    coupon: Coupon | None = None
    error: str = ""

    @property
    def total(self) -> Decimal:
        return self.subtotal - self.discount


class Order(models.Model):
    """A placed order — a snapshot, never a live view of the catalog.

    Addresses are flat denormalized fields: the order must not change if
    the customer later edits anything. Of the card, only the last four
    digits survive checkout.

    The coupon is snapshotted the same way: ``coupon_code``,
    ``coupon_percent_off`` and ``coupon_product_name`` are copied at
    purchase time, and receipts read only those. The ``coupon`` FK is a
    convenience link that goes null if the coupon is deleted. Invariant:
    ``total == subtotal - discount_amount``.
    """

    class Status(models.TextChoices):
        PLACED = "PLACED", "Placed"
        SHIPPED = "SHIPPED", "Shipped"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PLACED
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    total = models.DecimalField(max_digits=10, decimal_places=2)
    email = models.EmailField()

    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    coupon_code = models.CharField(max_length=30, blank=True)
    coupon_percent_off = models.PositiveSmallIntegerField(null=True, blank=True)
    # Blank for an order-wide coupon (or no coupon).
    coupon_product_name = models.CharField(max_length=200, blank=True)

    shipping_name = models.CharField(max_length=100)
    shipping_street = models.CharField(max_length=200)
    shipping_line2 = models.CharField(max_length=200, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=2)
    shipping_zip = models.CharField(max_length=10)

    billing_name = models.CharField(max_length=100)
    billing_street = models.CharField(max_length=200)
    billing_line2 = models.CharField(max_length=200, blank=True)
    billing_city = models.CharField(max_length=100)
    billing_state = models.CharField(max_length=2)
    billing_zip = models.CharField(max_length=10)

    card_last4 = models.CharField(max_length=4)

    # default (not auto_now_add) so the seed can backdate orders.
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.number

    def save(self, *args, **kwargs):
        """Fill in a missing subtotal from the invariant.

        Orders created without a coupon (the seed, test fixtures) needn't
        state a subtotal: it is ``total + discount_amount``.
        """
        if self.subtotal is None:
            self.subtotal = Decimal(self.total) + Decimal(self.discount_amount)
        super().save(*args, **kwargs)

    @property
    def number(self):
        """The customer-facing order number, e.g. ``TT-2026-00042``."""
        return f"TT-{self.created_at.year}-{self.pk:05d}"

    @property
    def has_discount(self) -> bool:
        """True when a coupon took something off — receipts show the breakdown."""
        return self.discount_amount > 0


class OrderItem(models.Model):
    """One line of an order, priced as of purchase time.

    Name and unit price are denormalized: order history must not change
    when the catalog does. The product FK survives for linking while the
    product exists.
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return f"{self.quantity} × {self.product_name}"

    @property
    def line_total(self):
        return self.unit_price * self.quantity
