from collections.abc import Iterable, Mapping
from typing import Any

from django.contrib.auth.models import AbstractUser
from django.db import models

# The two roles a saved address can play — at checkout, and as a default.
ADDRESS_KINDS = ("shipping", "billing")


class User(AbstractUser):
    """The store's user model.

    Roles use Django's own vocabulary and nothing else: customers are
    plain users, employees are ``is_staff``, the admin is ``is_superuser``.

    Default addresses are foreign keys rather than flags on ``Address``:
    a single FK can hold only one value, so "two default shipping
    addresses" is impossible by construction. Deleting an address that is
    a default simply empties the slot (``SET_NULL``).
    """

    # Nullable per the PRD: an absent job title is unknown, not empty.
    job_title = models.CharField(max_length=150, null=True, blank=True)  # noqa: DJ001
    default_shipping_address = models.ForeignKey(
        "Address",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    default_billing_address = models.ForeignKey(
        "Address",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    def default_address(self, kind: str) -> "Address | None":
        """The default address for ``kind`` (``"shipping"`` or ``"billing"``)."""
        return getattr(self, f"default_{kind}_address")

    def set_default_address(self, kind: str, address: "Address") -> None:
        """Make ``address`` the default for ``kind``, replacing any other."""
        field = f"default_{kind}_address"
        setattr(self, field, address)
        self.save(update_fields=[field])

    def fill_empty_defaults(
        self, address: "Address", kinds: Iterable[str] = ADDRESS_KINDS
    ) -> None:
        """Make ``address`` the default for each of ``kinds`` whose slot is
        empty. An existing default is never overwritten."""
        filled = []
        for kind in kinds:
            field = f"default_{kind}_address"
            if getattr(self, f"{field}_id") is None:
                setattr(self, field, address)
                filled.append(field)
        if filled:
            self.save(update_fields=filled)


class AddressManager(models.Manager):
    def save_from_checkout(
        self, user: User, data: Mapping[str, Any], *, prefix: str
    ) -> "Address":
        """Save one checkout address section to ``user``'s address book.

        ``data`` is a valid ``CheckoutForm``'s ``cleaned_data``; ``prefix``
        (``"shipping"`` or ``"billing"``) picks the section. Returns the
        existing address if an identical one is already saved — no
        duplicates. If the user has no default for this section yet, the
        address becomes it; an existing default is never replaced.
        """
        values = {part: data[f"{prefix}_{part}"] for part in Address.PARTS}
        address = self.filter(user=user, **values).first()
        if address is None:
            address = self.create(user=user, **values)
        user.fill_empty_defaults(address, kinds=[prefix])
        return address


class Address(models.Model):
    """A customer's saved address — usable for shipping, billing, or both.

    The fields mirror ``Order``'s ``shipping_*`` / ``billing_*`` fields.
    Orders copy an address at checkout, so editing or deleting a saved
    address never changes order history.
    """

    PARTS = ("name", "street", "line2", "city", "state", "zip")

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    name = models.CharField(max_length=100)
    street = models.CharField(max_length=200)
    line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=10)

    objects = AddressManager()

    class Meta:
        ordering = ["pk"]
        verbose_name_plural = "addresses"

    def __str__(self):
        return f"{self.name} — {self.street}, {self.city}, {self.state}"

    def as_checkout_initial(self, prefix: str) -> dict[str, str]:
        """This address as ``CheckoutForm`` initial data for one section."""
        return {f"{prefix}_{part}": getattr(self, part) for part in self.PARTS}
