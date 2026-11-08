"""Saved addresses: model rules, the address form, and "My addresses" pages.

Checkout's use of saved addresses is tested in ``orders/test_saved_addresses.py``.
"""

from http import HTTPStatus

import pytest
from django.urls import reverse

from orders.models import Order

from .forms import AddressForm
from .models import Address

CHECKOUT_DATA = {
    "shipping_name": "Casey Monroe",
    "shipping_street": "214 Synapse Street",
    "shipping_line2": "Suite 3",
    "shipping_city": "Canyon",
    "shipping_state": "TX",
    "shipping_zip": "79015",
    "billing_name": "Casey Monroe",
    "billing_street": "77 Cortex Lane",
    "billing_line2": "",
    "billing_city": "Amarillo",
    "billing_state": "TX",
    "billing_zip": "79101",
}

ADDRESS_POST = {
    "name": "Casey Monroe",
    "street": "9 Axon Avenue",
    "line2": "",
    "city": "Norman",
    "state": "OK",
    "zip": "73019",
}


# --- The model --------------------------------------------------------------


def test_str_is_a_one_line_summary(address):
    assert str(address) == "Casey Monroe — 214 Synapse Street, Canyon, TX"


def test_as_checkout_initial_prefixes_every_field(address):
    assert address.as_checkout_initial("billing") == {
        "billing_name": "Casey Monroe",
        "billing_street": "214 Synapse Street",
        "billing_line2": "Suite 3",
        "billing_city": "Canyon",
        "billing_state": "TX",
        "billing_zip": "79015",
    }


def test_one_address_can_be_both_defaults(customer, address):
    customer.set_default_address("shipping", address)
    customer.set_default_address("billing", address)
    customer.refresh_from_db()

    assert customer.default_shipping_address == address
    assert customer.default_billing_address == address


def test_deleting_a_default_address_empties_the_slot_but_keeps_the_user(
    customer, address
):
    customer.set_default_address("shipping", address)

    address.delete()

    customer.refresh_from_db()
    assert customer.default_shipping_address is None


def test_deleting_a_user_deletes_their_addresses(customer, address):
    customer.set_default_address("shipping", address)

    customer.delete()

    assert not Address.objects.exists()


# --- save_from_checkout -------------------------------------------------------


def test_save_from_checkout_creates_from_the_shipping_section(customer):
    address = Address.objects.save_from_checkout(
        customer, CHECKOUT_DATA, prefix="shipping"
    )

    assert address.user == customer
    assert address.street == "214 Synapse Street"
    assert address.line2 == "Suite 3"


def test_save_from_checkout_creates_from_the_billing_section(customer):
    address = Address.objects.save_from_checkout(
        customer, CHECKOUT_DATA, prefix="billing"
    )

    assert address.street == "77 Cortex Lane"
    assert address.city == "Amarillo"


def test_save_from_checkout_returns_an_identical_existing_address(customer, address):
    saved = Address.objects.save_from_checkout(
        customer, CHECKOUT_DATA, prefix="shipping"
    )

    assert saved == address
    assert customer.addresses.count() == 1


def test_save_from_checkout_does_not_match_another_customers_address(
    other_customer, address
):
    saved = Address.objects.save_from_checkout(
        other_customer, CHECKOUT_DATA, prefix="shipping"
    )

    assert saved != address
    assert saved.user == other_customer


def test_any_field_difference_is_a_new_address(customer, address):
    Address.objects.save_from_checkout(
        customer, {**CHECKOUT_DATA, "shipping_line2": "Suite 4"}, prefix="shipping"
    )

    assert customer.addresses.count() == 2


def test_save_from_checkout_fills_only_the_matching_empty_default(customer):
    address = Address.objects.save_from_checkout(
        customer, CHECKOUT_DATA, prefix="shipping"
    )

    customer.refresh_from_db()
    assert customer.default_shipping_address == address
    assert customer.default_billing_address is None


def test_save_from_checkout_never_replaces_an_existing_default(customer, address):
    customer.set_default_address("billing", address)

    Address.objects.save_from_checkout(customer, CHECKOUT_DATA, prefix="billing")

    customer.refresh_from_db()
    assert customer.default_billing_address == address


def test_a_deleted_default_is_refilled_by_the_next_save(customer, address):
    customer.set_default_address("shipping", address)
    address.delete()
    customer.refresh_from_db()

    replacement = Address.objects.save_from_checkout(
        customer, CHECKOUT_DATA, prefix="shipping"
    )

    customer.refresh_from_db()
    assert customer.default_shipping_address == replacement


# --- AddressForm --------------------------------------------------------------


def test_address_form_accepts_a_valid_address():
    assert AddressForm(data=ADDRESS_POST).is_valid()


@pytest.mark.parametrize(
    ("field", "value"),
    [("state", "XX"), ("zip", "790"), ("zip", "79015-12"), ("name", "")],
)
def test_address_form_rejects_bad_input(field, value):
    form = AddressForm(data={**ADDRESS_POST, field: value})

    assert not form.is_valid()
    assert field in form.errors


def test_address_form_line2_is_optional():
    assert AddressForm(data={**ADDRESS_POST, "line2": ""}).is_valid()


# --- "My addresses" pages -----------------------------------------------------


@pytest.mark.parametrize(
    ("name", "args"),
    [
        ("accounts:addresses", []),
        ("accounts:address_create", []),
        ("accounts:address_update", [1]),
        ("accounts:address_delete", [1]),
    ],
)
def test_address_pages_require_login(client, db, name, args):
    url = reverse(name, args=args)

    response = client.get(url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f"{reverse('accounts:login')}?next={url}"


def test_empty_address_book_shows_the_empty_state(client, customer):
    client.force_login(customer)

    response = client.get(reverse("accounts:addresses"))

    assert response.status_code == HTTPStatus.OK
    assert "No saved addresses yet" in response.content.decode()


def test_address_list_shows_only_my_addresses_with_default_badges(
    client, customer, other_customer, address
):
    Address.objects.create(
        user=other_customer,
        name="Someone Else",
        street="1 Elsewhere Rd",
        city="Denver",
        state="CO",
        zip="80202",
    )
    customer.set_default_address("shipping", address)
    client.force_login(customer)

    page = client.get(reverse("accounts:addresses")).content.decode()

    assert "214 Synapse Street" in page
    assert "1 Elsewhere Rd" not in page
    assert "Default shipping" in page
    assert "Default billing" not in page


def test_create_saves_an_address_and_fills_both_empty_defaults(client, customer):
    client.force_login(customer)

    response = client.post(reverse("accounts:address_create"), ADDRESS_POST)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse("accounts:addresses")
    address = customer.addresses.get()
    assert address.street == "9 Axon Avenue"
    customer.refresh_from_db()
    assert customer.default_shipping_address == address
    assert customer.default_billing_address == address


def test_create_fills_an_empty_default_but_keeps_an_existing_one(
    client, customer, address
):
    customer.set_default_address("shipping", address)
    client.force_login(customer)

    client.post(reverse("accounts:address_create"), ADDRESS_POST)

    customer.refresh_from_db()
    new = customer.addresses.get(street="9 Axon Avenue")
    assert customer.default_shipping_address == address
    assert customer.default_billing_address == new


def test_create_with_bad_input_shows_errors_and_saves_nothing(client, customer):
    client.force_login(customer)

    response = client.post(
        reverse("accounts:address_create"), {**ADDRESS_POST, "zip": "nope"}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.context["form"].errors["zip"]
    assert not customer.addresses.exists()


def test_update_edits_my_address(client, customer, address):
    client.force_login(customer)

    response = client.post(
        reverse("accounts:address_update", args=[address.pk]),
        {**ADDRESS_POST, "street": "28 Ganglion Court"},
    )

    assert response.status_code == HTTPStatus.FOUND
    address.refresh_from_db()
    assert address.street == "28 Ganglion Court"


def test_delete_removes_my_address(client, customer, address):
    client.force_login(customer)

    page = client.get(reverse("accounts:address_delete", args=[address.pk]))
    response = client.post(reverse("accounts:address_delete", args=[address.pk]))

    assert page.status_code == HTTPStatus.OK
    assert response.status_code == HTTPStatus.FOUND
    assert not Address.objects.exists()


def test_set_default_makes_an_address_the_default(client, customer, address):
    client.force_login(customer)

    response = client.post(
        reverse("accounts:address_set_default", args=[address.pk, "billing"])
    )

    assert response.status_code == HTTPStatus.FOUND
    customer.refresh_from_db()
    assert customer.default_billing_address == address
    assert customer.default_shipping_address is None


def test_set_default_rejects_an_unknown_kind(client, customer, address):
    client.force_login(customer)

    response = client.post(
        reverse("accounts:address_set_default", args=[address.pk, "gift"])
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_set_default_is_post_only(client, customer, address):
    client.force_login(customer)

    response = client.get(
        reverse("accounts:address_set_default", args=[address.pk, "shipping"])
    )

    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.parametrize(
    ("method", "name", "extra"),
    [
        ("get", "accounts:address_update", []),
        ("post", "accounts:address_update", []),
        ("get", "accounts:address_delete", []),
        ("post", "accounts:address_delete", []),
        ("post", "accounts:address_set_default", ["shipping"]),
    ],
)
def test_another_customers_address_is_a_404(
    client, other_customer, address, method, name, extra
):
    client.force_login(other_customer)

    response = getattr(client, method)(
        reverse(name, args=[address.pk, *extra]), ADDRESS_POST
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    address.refresh_from_db()
    assert address.street == "214 Synapse Street"
    other_customer.refresh_from_db()
    assert other_customer.default_shipping_address is None


def test_editing_or_deleting_a_saved_address_leaves_orders_untouched(
    client, customer, address
):
    order = Order.objects.create(
        user=customer,
        total="10.00",
        email="casey@example.com",
        card_last4="4242",
        **address.as_checkout_initial("shipping"),
        **address.as_checkout_initial("billing"),
    )
    client.force_login(customer)

    client.post(
        reverse("accounts:address_update", args=[address.pk]),
        {**ADDRESS_POST, "street": "28 Ganglion Court"},
    )
    client.post(reverse("accounts:address_delete", args=[address.pk]))

    order.refresh_from_db()
    assert order.shipping_street == "214 Synapse Street"
    assert order.billing_street == "214 Synapse Street"


def test_navbar_links_signed_in_customers_to_their_addresses(client, customer):
    client.force_login(customer)

    page = client.get(reverse("products:catalog")).content.decode()

    assert reverse("accounts:addresses") in page
