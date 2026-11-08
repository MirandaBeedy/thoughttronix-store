from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from orders.forms import US_STATES, zip_validator

from .models import Address, User


class SignupForm(UserCreationForm):
    """Django's stock signup fields — username plus password and confirmation.

    No email: signing up asks for the minimum. The widgets carry DaisyUI
    classes because plain Django forms own their own styling here.
    """

    class Meta(UserCreationForm.Meta):
        model = User

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input w-full"


class SignInForm(AuthenticationForm):
    """The stock authentication form, dressed in DaisyUI."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input w-full"


class AddressForm(forms.ModelForm):
    """A saved address, validated by the same declarative rules as checkout:
    a US state from the list and a ZIP like 79016 or 79016-1234."""

    state = forms.ChoiceField(label="State", choices=US_STATES)
    zip = forms.CharField(label="ZIP code", max_length=10, validators=[zip_validator])

    class Meta:
        model = Address
        fields = ["name", "street", "line2", "city", "state", "zip"]
        labels = {
            "name": "Full name",
            "street": "Street address",
            "line2": "Apt, suite, etc. (optional)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "select w-full"
            else:
                field.widget.attrs["class"] = "input w-full"
