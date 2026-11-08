"""Saved addresses at checkout: default pre-fill, the HTMX fill endpoint,
and the "save this address" checkboxes.

``place_order`` itself is unchanged; its tests in ``test_services.py``
cover it untouched.
"""

from http import HTTPStatus

import pytest
from django.urls import reverse

from accounts.models import Address

from .models import Order
from .test_checkout_form import VALID_DATA, form_with

# --- The form -----------------------------------------------------------------


def test_save_checkboxes_are_optional_and_default_to_false():
    form = form_with()

    assert form.is_valid()
    assert form.cleaned_data["save_shipping"] is False
    assert form.cleaned_data["save_billing"] is False


def test_save_checkboxes_are_not_part_of_the_address_field_groups():
    form = form_with()

    shipping = [field.name for field in form.shipping_fields()]
    section = form.shipping_section()
    assert "save_shipping" not in shipping
    assert [field.name for field in section["fields"]] == shipping
    assert section["save_field"].name == "save_shipping"


# --- Default pre-fill -------------------------------------------------------------


def test_checkout_prefills_both_sections_from_defaults(
    client, customer, cart_item, address
):
    work = Address.objects.create(
        user=customer,
        name="Casey Monroe",
        street="77 Cortex Lane",
        city="Amarillo",
        state="TX",
        zip="79101",
    )
    customer.set_default_address("shipping", address)
    customer.set_default_address("billing", work)
    client.force_login(customer)

    form = client.get(reverse("orders:checkout")).context["form"]

    assert form["shipping_street"].value() == "214 Synapse Street"
    assert form["shipping_line2"].value() == "Suite 3"
    assert form["billing_street"].value() == "77 Cortex Lane"
    assert form["billing_zip"].value() == "79101"


def test_checkout_without_defaults_starts_blank(client, customer, cart_item, address):
    client.force_login(customer)

    response = client.get(reverse("orders:checkout"))

    form = response.context["form"]
    assert form["shipping_street"].value() is None
    assert form["billing_street"].value() is None
    # The saved address is still offered in the dropdowns.
    assert "214 Synapse Street" in response.content.decode()


def test_checkout_with_no_saved_addresses_shows_no_picker(client, customer, cart_item):
    client.force_login(customer)

    page = client.get(reverse("orders:checkout")).content.decode()

    assert "Use a saved address" not in page
    assert "Save this address to my account" in page


def test_checkout_picker_preselects_the_default(client, customer, cart_item, address):
    customer.set_default_address("shipping", address)
    client.force_login(customer)

    page = client.get(reverse("orders:checkout")).content.decode()

    assert f'<option value="{address.pk}" selected>' in page
    assert reverse("orders:address_fields", args=["shipping"]) in page


# --- The HTMX fill endpoint -------------------------------------------------------


def test_fill_endpoint_requires_login(client, db):
    url = reverse("orders:address_fields", args=["shipping"])

    response = client.get(url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url.startswith(reverse("accounts:login"))


@pytest.mark.parametrize("prefix", ["shipping", "billing"])
def test_fill_endpoint_returns_the_section_partial_filled(
    client, customer, address, prefix
):
    client.force_login(customer)

    response = client.get(
        reverse("orders:address_fields", args=[prefix]), {"address": address.pk}
    )

    assert response.status_code == HTTPStatus.OK
    page = response.content.decode()
    assert "<html" not in page  # a partial, never base.html
    assert f'id="{prefix}-address-fields"' in page
    assert f'name="{prefix}_street"' in page
    assert 'value="214 Synapse Street"' in page
    assert 'value="Suite 3"' in page
    assert '<option value="TX" selected>' in page


def test_fill_endpoint_renders_the_save_checkbox_unchecked(client, customer, address):
    client.force_login(customer)

    response = client.get(
        reverse("orders:address_fields", args=["shipping"]), {"address": address.pk}
    )

    page = response.content.decode()
    assert 'name="save_shipping"' in page
    assert "checked" not in page


def test_fill_endpoint_with_blank_choice_renders_empty_fields(client, customer):
    client.force_login(customer)

    response = client.get(
        reverse("orders:address_fields", args=["billing"]), {"address": ""}
    )

    assert response.status_code == HTTPStatus.OK
    assert 'name="billing_street"' in response.content.decode()
    assert "Synapse" not in response.content.decode()


def test_fill_endpoint_404s_for_another_customers_address(
    client, other_customer, address
):
    client.force_login(other_customer)

    response = client.get(
        reverse("orders:address_fields", args=["shipping"]), {"address": address.pk}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    ("prefix", "pk"), [("payment", "1"), ("shipping", "abc"), ("shipping", "999")]
)
def test_fill_endpoint_404s_on_bad_input(client, customer, prefix, pk):
    client.force_login(customer)

    response = client.get(
        reverse("orders:address_fields", args=[prefix]), {"address": pk}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


# --- Saving at checkout -----------------------------------------------------------


def test_unticked_boxes_save_nothing(client, customer, cart_item):
    client.force_login(customer)

    response = client.post(reverse("orders:checkout"), VALID_DATA)

    assert response.status_code == HTTPStatus.FOUND
    assert Order.objects.count() == 1
    assert not Address.objects.exists()


def test_ticked_boxes_save_both_addresses_and_fill_defaults(
    client, customer, cart_item
):
    client.force_login(customer)
    data = {
        **VALID_DATA,
        "billing_street": "77 Cortex Lane",
        "save_shipping": "on",
        "save_billing": "on",
    }

    client.post(reverse("orders:checkout"), data)

    assert Order.objects.count() == 1
    shipping = customer.addresses.get(street="12 Cortex Lane")
    billing = customer.addresses.get(street="77 Cortex Lane")
    assert shipping.line2 == "Unit 7"
    customer.refresh_from_db()
    assert customer.default_shipping_address == shipping
    assert customer.default_billing_address == billing


def test_same_address_ticked_twice_is_saved_once_for_both_defaults(
    client, customer, cart_item
):
    client.force_login(customer)
    data = {
        **VALID_DATA,
        "billing_line2": VALID_DATA["shipping_line2"],
        "billing_zip": VALID_DATA["shipping_zip"],
        "save_shipping": "on",
        "save_billing": "on",
    }

    client.post(reverse("orders:checkout"), data)

    address = customer.addresses.get()
    customer.refresh_from_db()
    assert customer.default_shipping_address == address
    assert customer.default_billing_address == address


def test_resaving_an_existing_address_creates_no_duplicate(client, customer, cart_item):
    client.force_login(customer)
    Address.objects.save_from_checkout(customer, VALID_DATA, prefix="shipping")

    client.post(reverse("orders:checkout"), {**VALID_DATA, "save_shipping": "on"})

    assert customer.addresses.count() == 1


def test_an_invalid_checkout_saves_no_address(client, customer, cart_item):
    client.force_login(customer)

    response = client.post(
        reverse("orders:checkout"),
        {**VALID_DATA, "card_cvv": "1", "save_shipping": "on"},
    )

    assert response.status_code == HTTPStatus.OK
    assert not Order.objects.exists()
    assert not Address.objects.exists()


def test_order_keeps_its_own_copy_of_a_saved_address(client, customer, cart_item):
    client.force_login(customer)
    client.post(reverse("orders:checkout"), {**VALID_DATA, "save_shipping": "on"})
    address = customer.addresses.get()

    address.street = "1 Changed Street"
    address.save()

    assert Order.objects.get().shipping_street == "12 Cortex Lane"
