"""The checkout form — the codebase's showcase of declarative validation.

Every rule is visible at its field declaration, in the style of data
annotations: field types validate (``EmailField``), field arguments
validate (``required``, ``max_length``, ``ChoiceField``), and the
``validators=[...]`` list carries the rest. No ``clean_*`` methods
and no ``clean()`` — none of its current rules need imperative validation.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db.models import Q

from products.forms import StyledModelForm
from products.models import Product

from .models import Coupon, CouponError, Order, normalize_code
from .validators import validate_card_number, validate_expiry

US_STATES = [
    ("AL", "Alabama"),
    ("AK", "Alaska"),
    ("AZ", "Arizona"),
    ("AR", "Arkansas"),
    ("CA", "California"),
    ("CO", "Colorado"),
    ("CT", "Connecticut"),
    ("DE", "Delaware"),
    ("DC", "District of Columbia"),
    ("FL", "Florida"),
    ("GA", "Georgia"),
    ("HI", "Hawaii"),
    ("ID", "Idaho"),
    ("IL", "Illinois"),
    ("IN", "Indiana"),
    ("IA", "Iowa"),
    ("KS", "Kansas"),
    ("KY", "Kentucky"),
    ("LA", "Louisiana"),
    ("ME", "Maine"),
    ("MD", "Maryland"),
    ("MA", "Massachusetts"),
    ("MI", "Michigan"),
    ("MN", "Minnesota"),
    ("MS", "Mississippi"),
    ("MO", "Missouri"),
    ("MT", "Montana"),
    ("NE", "Nebraska"),
    ("NV", "Nevada"),
    ("NH", "New Hampshire"),
    ("NJ", "New Jersey"),
    ("NM", "New Mexico"),
    ("NY", "New York"),
    ("NC", "North Carolina"),
    ("ND", "North Dakota"),
    ("OH", "Ohio"),
    ("OK", "Oklahoma"),
    ("OR", "Oregon"),
    ("PA", "Pennsylvania"),
    ("RI", "Rhode Island"),
    ("SC", "South Carolina"),
    ("SD", "South Dakota"),
    ("TN", "Tennessee"),
    ("TX", "Texas"),
    ("UT", "Utah"),
    ("VT", "Vermont"),
    ("VA", "Virginia"),
    ("WA", "Washington"),
    ("WV", "West Virginia"),
    ("WI", "Wisconsin"),
    ("WY", "Wyoming"),
]

zip_validator = RegexValidator(
    r"^\d{5}(-\d{4})?$", "Enter a ZIP code like 79016 or 79016-1234."
)
cvv_validator = RegexValidator(r"^\d{3,4}$", "Enter the 3- or 4-digit CVV.")


class CheckoutForm(forms.Form):
    """One page, one POST: contact, shipping, billing, payment.

    The two ``save_*`` checkboxes are optional booleans that ``place_order``
    ignores; the checkout view acts on them after the order is placed.
    """

    email = forms.EmailField(label="Email")

    shipping_name = forms.CharField(label="Full name", max_length=100)
    shipping_street = forms.CharField(label="Street address", max_length=200)
    shipping_line2 = forms.CharField(
        label="Apt, suite, etc. (optional)", max_length=200, required=False
    )
    shipping_city = forms.CharField(label="City", max_length=100)
    shipping_state = forms.ChoiceField(label="State", choices=US_STATES)
    shipping_zip = forms.CharField(
        label="ZIP code", max_length=10, validators=[zip_validator]
    )
    save_shipping = forms.BooleanField(
        label="Save this address to my account", required=False
    )

    billing_name = forms.CharField(label="Full name", max_length=100)
    billing_street = forms.CharField(label="Street address", max_length=200)
    billing_line2 = forms.CharField(
        label="Apt, suite, etc. (optional)", max_length=200, required=False
    )
    billing_city = forms.CharField(label="City", max_length=100)
    billing_state = forms.ChoiceField(label="State", choices=US_STATES)
    billing_zip = forms.CharField(
        label="ZIP code", max_length=10, validators=[zip_validator]
    )
    save_billing = forms.BooleanField(
        label="Save this address to my account", required=False
    )

    card_number = forms.CharField(
        label="Card number", max_length=23, validators=[validate_card_number]
    )
    card_expiry = forms.CharField(
        label="Expiry (MM/YY)", max_length=5, validators=[validate_expiry]
    )
    card_cvv = forms.CharField(label="CVV", max_length=4, validators=[cvv_validator])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.Select):
                widget.attrs["class"] = "select w-full"
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = "checkbox checkbox-sm"
            else:
                widget.attrs["class"] = "input w-full"

    # Field groups for the template — the form owns its own structure.

    def shipping_fields(self):
        return [self[name] for name in self.fields if name.startswith("shipping_")]

    def billing_fields(self):
        return [self[name] for name in self.fields if name.startswith("billing_")]

    def address_section(self, prefix):
        """One address section — its fields and its "save" checkbox — as
        the context ``_address_fields.html`` renders. Shared by the
        checkout page and the HTMX fill endpoint."""
        return {
            "prefix": prefix,
            "fields": [
                self[name] for name in self.fields if name.startswith(f"{prefix}_")
            ],
            "save_field": self[f"save_{prefix}"],
        }

    def shipping_section(self):
        return self.address_section("shipping")

    def billing_section(self):
        return self.address_section("billing")

    def card_fields(self):
        return [self[name] for name in self.fields if name.startswith("card_")]


class CouponForm(forms.Form):
    """The checkout coupon box — deliberately apart from ``CheckoutForm``.

    ``CheckoutForm`` stays the declarative-validation showcase (no
    ``clean_*``, per the PRD). A coupon is only valid against the database
    and this customer's cart, which no field validator can see, so it gets
    its own small form that owns that check. Together the two keep the
    PRD's promise: when both are valid, ``place_order`` succeeds.

    The input joins ``#checkout-form`` by the HTML ``form`` attribute, so
    it can sit in the order-summary sidebar and still be submitted with
    "Place order".
    """

    coupon_code = forms.CharField(
        label="Coupon code",
        max_length=30,
        required=False,
        widget=forms.TextInput(
            attrs={
                "form": "checkout-form",
                "autocomplete": "off",
                "class": "input join-item w-full",
            }
        ),
    )

    def __init__(self, *args, cart, **kwargs):
        super().__init__(*args, **kwargs)
        self.cart = cart

    def clean_coupon_code(self):
        """Normalize the code; reject one that can't apply to this cart."""
        code = normalize_code(self.cleaned_data["coupon_code"])
        if code:
            try:
                Coupon.objects.get_by_code(code).discount_for(self.cart)
            except CouponError as error:
                raise ValidationError(str(error)) from error
        return code


class ManageCouponForm(StyledModelForm):
    """The back-office coupon form — create and edit; retiring is the toggle.

    ``clean_code`` uppercases the code *before* the uniqueness check, so
    "thoughts10" is caught as a duplicate of "THOUGHTS10" with a form
    error rather than a database error. The product menu offers available
    products (blank = the whole order), plus the coupon's current product
    even if it has since become unavailable.
    """

    class Meta:
        model = Coupon
        fields = ["code", "percent_off", "product", "expires_at", "is_active"]
        labels = {
            "percent_off": "Percent off",
            "expires_at": "Expires at (UTC)",
            "is_active": "Active",
        }
        help_texts = {
            "code": "Customers type this at checkout; case doesn't matter.",
            "percent_off": "A whole number from 1 to 100.",
        }
        widgets = {
            "expires_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        products = Q(is_available=True)
        if self.instance.product_id is not None:
            products |= Q(pk=self.instance.product_id)
        product_field = self.fields["product"]
        product_field.queryset = Product.objects.filter(products)
        product_field.empty_label = "Whole order"

    def clean_code(self):
        return normalize_code(self.cleaned_data["code"])


class OrderStatusForm(forms.ModelForm):
    """The back-office status dropdown — any of the four states, anytime.

    Guarding the workflow (no un-cancelling, no re-shipping a delivered
    order) is deliberately left as a student exercise.
    """

    class Meta:
        model = Order
        fields = ["status"]
        widgets = {"status": forms.Select(attrs={"class": "select"})}
