# PRD: The ThoughtTronix Store — Saved Addresses

*Commissioned by ThoughtTronix Product Management. "Your Thoughts, Our Business."*

---

## Problem Statement

Every checkout asks the customer to type a shipping address and a billing address from scratch — twelve fields, every time, even for a customer whose last eleven orders all went to the same house. Our loyal customers are, in effect, penalized for their loyalty. Analytics reports that the average returning customer spends longer typing their own street name than considering a MindSync upgrade.

## Solution

Customers can keep an address book on their account and reuse it at checkout.

**At checkout.** Each address section (shipping, billing) gets a dropdown of the customer's saved addresses. Choosing one fills that section's fields in place via HTMX — nothing else on the page is disturbed. The page opens already filled with the customer's default shipping and billing addresses. Under each section, a "Save this address to my account" checkbox lets a customer add a newly typed address to their book as a side effect of ordering.

**On a "My addresses" page.** Customers list, add, edit, and delete saved addresses, and choose their default shipping and default billing address.

Orders are unaffected: an order still stores its own flat copy of both addresses, so editing or deleting a saved address never alters order history.

## User Stories

**Customer (signed in)**

1. As a customer, I can view my saved addresses on a "My addresses" page — and when I have none, I see a designed empty state, not a blank page.
2. As a customer, I can add, edit, and delete a saved address, with the same validation checkout uses (US state, ZIP format, required fields).
3. As a customer, I can mark any saved address as my default shipping address and, independently, as my default billing address. The same address may be both.
4. As a customer, when I open checkout, the shipping and billing sections are already filled with my default addresses.
5. As a customer, I can pick a different saved address for shipping or for billing at checkout, and that section refills without a page reload and without losing anything else I've typed.
6. As a customer, a saved address only fills the form — I can still adjust any field before placing the order.
7. As a customer, I can tick "Save this address to my account" under either address section at checkout, and that address is added to my book when my order is placed.
8. As a customer, saving an address identical to one I already have does not create a duplicate.
9. As a customer, my first saved shipping address becomes my default shipping address automatically (and likewise for billing), but an address I've already chosen as a default is never replaced without my action.
10. As a customer, editing or deleting a saved address never changes my past orders.
11. As a customer, I cannot see, use, edit, or delete another customer's addresses.

**Admin**

12. As an admin, I can view and correct any customer's saved addresses in the Django admin, inline on the user's page.

**Any developer**

13. As a developer, after running `seed`, the `customer` demo login has saved addresses and defaults, so the feature is visible on the first demo checkout.

## Implementation Decisions

**Data model: one generic `Address`.** A new `accounts.Address` model: FK `user` (`on_delete=CASCADE`, `related_name="addresses"`) plus the same six fields an order uses — `name`, `street`, `line2` (blank allowed), `city`, `state` (2 chars), `zip` — with the same lengths as `Order`'s address fields. An address carries **no type**: any saved address may be used for shipping, billing, or both. No `label`/nickname field; `__str__` returns a one-line summary such as `"Jordan Lee — 123 Main St, Canyon, TX"`, used in dropdowns and lists.

`Address` lives in `accounts` because `User` points at it (below); placing it in `orders` would create a circular app dependency.

**Defaults: two foreign keys on `User`.** `accounts.User` gains `default_shipping_address` and `default_billing_address`, each a nullable FK to `Address` with `on_delete=SET_NULL` and `related_name="+"`. A single FK can hold only one value, so "two defaults of one kind" is impossible by construction. Deleting an address that is a default simply empties that slot.

**Saving from checkout: a manager method, called after the order.** `CheckoutForm` gains two declarative fields, `save_shipping` and `save_billing` (`BooleanField(required=False)`). The form keeps its showcase status — still no `clean()` and no `clean_*` methods. `place_order` is **unchanged**: it reads only `ADDRESS_FIELDS` and ignores the new keys.

A manager method on `Address` — `Address.objects.save_from_checkout(user, data, *, prefix)` where `prefix` is `"shipping"` or `"billing"` — owns the saving rules and returns the `Address`. `CheckoutView.form_valid` calls `place_order` first, then `save_from_checkout` once per ticked box. The two steps are deliberately not one transaction: the order matters more than the address book, and a failed address save must never cost a customer their order.

**Rule: exact-match de-duplication.** `save_from_checkout` returns the user's existing address if one with identical field values already exists (`get_or_create` on the six fields). Django's `CharField` already strips surrounding whitespace, so trivial spacing differences match. Case and abbreviation differences (`"St"` vs `"Street"`) are deliberately not normalized.

**Rule: fill empty defaults.** When `save_from_checkout` saves an address from the shipping section and the user has no `default_shipping_address`, it becomes the default; billing likewise. An address added on the "My addresses" page fills *any* empty default slot. An existing default is never overwritten automatically.

**Checkout fill-in: HTMX partial + initial defaults.**

- On page load, `CheckoutView.get_initial` fills the shipping and billing fields from the user's default addresses.
- Each address section has a dropdown of saved addresses. Changing it issues an `hx-get` to a new endpoint (e.g. `orders:address_fields`) with the address pk and section prefix, which renders `templates/orders/partials/_address_fields.html` — that section's six fields pre-filled, swapped in place.
- The partial renders that section's "Save this address" checkbox **unchecked** when filled from a saved address, preventing most duplicates before the de-dup rule is needed.
- The endpoint fetches the address through `request.user.addresses`, returning 404 for any pk the user doesn't own — never by bare primary key.
- This is the only new HTMX interaction. The submitted form is the same flat fields as today, validated the same way; a saved address is a convenience for filling the form, never trusted input.

**"My addresses" page.** Class-based list / create / update / delete views in `accounts`, under the `accounts` namespace (e.g. `accounts:addresses`, `accounts:address_create`, `accounts:address_update`, `accounts:address_delete`), plus a POST action to set an address as the default shipping or default billing address. All querysets filtered to `request.user`; URLs use pks. An `AddressForm` (`ModelForm`) reuses `US_STATES` and `zip_validator` imported from `orders/forms.py`. A navbar link for signed-in customers points to the page. The list has a designed empty state.

**Staff visibility: Django admin only.** Register `Address` in `accounts/admin.py` and add it as an inline on the `User` admin. No back-office tab — staff work from orders, which carry their own address copies.

**Seed data.** `seed` gives the `customer` demo login two saved addresses drawn from `SEED_ADDRESSES` (one set as both default shipping and default billing, one alternative), so the dropdown has a real choice. Background customers get none. Addresses are removed with their users during the wipe (cascade).

## Out of Scope

- Guest checkout (checkout already requires sign-in).
- A "billing same as shipping" checkbox — choosing the same saved address in both dropdowns covers it.
- Address nicknames/labels — `__str__` summary instead; addable later in one migration.
- Fuzzy de-duplication (case-folding, abbreviation matching).
- A cap on how many addresses a customer may save.
- Non-US addresses.
- A staff back-office view of customers' address books.

## Testing Decisions

Same approach as the core platform: pytest + pytest-django, plain fixtures in `conftest.py` (add an `address` fixture for the existing customer user), no factory-boy, never invoking `seed`.

Coverage priorities, in order:

1. **`Address.objects.save_from_checkout`** — creates an address from shipping-prefixed and billing-prefixed data; returns the existing address on an exact match (no duplicate); fills an empty default slot for the matching section; never overwrites an existing default.
2. **Default FKs** — deleting a default address sets the slot to `NULL` and does not delete the user; the same address can be both defaults.
3. **Checkout integration** — ticking a save box creates an address after a successful order; unticked boxes create nothing; `place_order` behavior is unchanged (its existing tests stay green untouched); `get_initial` pre-fills from defaults, and from nothing when there are none.
4. **Access control** — the HTMX fill endpoint and every "My addresses" view return 404 for another user's address and redirect anonymous users to sign in.
5. **HTMX endpoint** — returns the partial (not a full page) with the address's values filled and the save checkbox unchecked.
6. **`AddressForm`** — rejects a bad ZIP and an invalid state; accepts a valid address.
7. **View smoke tests** — list (including the empty state), create, update, delete, and set-default each work for the owning customer.
8. **Order immutability** — editing or deleting a saved address leaves an existing order's address fields unchanged.
