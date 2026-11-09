# Implementation Plan: Discount Coupons

*Design settled in a grill-me session on 2026-11-07. This plan owns both the decisions and the sequence. Where a task names a decision below, the decision is authoritative — do not improvise alternatives. The suite must be green at every phase boundary.*

---

## Requirements

1. Customers enter a coupon code at checkout to receive a discount.
2. Expired coupons are rejected with a clear error message.
3. Retiring a coupon never changes the totals of orders already placed.
4. Both order-wide discounts and product-specific discounts (e.g. 50% off Seraphine) are supported.

## Design decisions

| # | Question | Decision | Why |
|---|----------|----------|-----|
| 1 | Shape of a coupon | One `Coupon` model with an optional FK to `Product`. Blank product = order-wide; set = that product's lines only. | Meets both scopes with one table, one admin, one rule. Upgrading the FK to an M2M later is a contained migration. |
| 2 | How the discount is expressed | Percentage only: `percent_off`, integer 1–100. | A percentage can never exceed what it applies to, so totals can't go negative. Fixed-amount coupons can arrive later behind a `kind` field defaulting to percent. |
| 3 | Usable vs. unusable | `is_active` (retire switch) + optional `expires_at` (blank = never expires). | "Expired" (a date passed) and "retired" (staff switched it off) are different facts with different messages; retiring leaves the dates untouched and is reversible. |
| 4 | What an order remembers | Snapshot on `Order`: `subtotal`, `discount_amount`, `coupon_code`, `coupon_percent_off`, `coupon_product_name`, plus a nullable `coupon` FK with `on_delete=SET_NULL`. Receipts read only the snapshot. | Same snapshot pattern as `OrderItem.unit_price` / `product_name`: editing, retiring, or deleting a coupon cannot rewrite history. |
| 5 | Product coupon, product not in cart | Reject, naming the product. | A coupon that discounts nothing is an invalid coupon. Invariant: *if an order records a coupon, that coupon discounted something.* |
| 6 | Where the code is entered | A separate `CouponForm` (one `coupon_code` field, validated by `clean_coupon_code` against the cart) submitted in the same POST as `CheckoutForm`, + an HTMX "Apply" button that previews the summary. Re-validated in `place_order`. *(Revised in Phase 3: originally a field on `CheckoutForm`, but the PRD forbids `clean_*` methods there.)* | The customer sees the final price before paying; nothing is stored between requests, so nothing goes stale. Mirrors `AddressFieldsView`. `CheckoutForm` stays the PRD's declarative showcase, and "both forms valid ⇒ order placed" keeps the PRD's promise. |
| 7 | Usage limits | None — unlimited until expired or retired. | Not required. Per-customer limits are a later one-check addition using the order snapshot; a global cap needs row locking and is deferred. |
| 8 | Staff management | Back-office "Coupons" tab (list, create, edit; retire via `is_active`; **no delete**) + `CouponAdmin` registration. | Matches the product CRUD pattern and the convention of registering every model in admin. No delete keeps the order link intact for reporting. |
| 9 | Demo data | Seed four coupons, one per rule. No seeded discounted orders. | Every rule is demonstrable a minute after seeding. |

### Smaller decisions (taken as defaults)

- **Validation lives on the model.** One method, `Coupon.discount_for(cart) -> Decimal`, returns the discount or raises `CouponError(message)` (a `ValueError`). `CouponForm.clean_coupon_code`, the HTMX preview (via `Cart.checkout_summary`), and `place_order` all call it — the rules exist in exactly one place.
- **Codes are case-insensitive.** Stored uppercase (normalized in `save()` / the form); looked up with the uppercased input. `code` is unique.
- **One coupon per order.** No stacking.
- **The math.** `Decimal` throughout. Order-wide: `subtotal × percent_off / 100`. Product-scoped: `(product price × quantity of that product's line) × percent_off / 100` — every unit of the product is discounted. Rounded to the cent with `ROUND_HALF_UP`. `total = subtotal − discount_amount`.
- **Product matching is by FK, not by name.** A Seraphine coupon does not apply to Seraphine Mini or Seraphine Doorbell.
- **Validation order and messages** (first failing check wins):
  1. Unknown code → "We don't recognize the coupon code “X”."
  2. Retired (`is_active` false) → "The coupon X is no longer available."
  3. Expired (`expires_at` ≤ now) → "The coupon X expired on Oct 31, 2026." (date rendered in the site timezone)
  4. Product not in cart → "X applies only to Seraphine, which isn't in your cart."
- **A blank coupon field is not an error** — the order is placed at full price, exactly as today.
- **Existing orders.** The data migration sets `subtotal = total` and `discount_amount = 0` on every existing order, so old receipts add up.
- **Dashboard.** Revenue keeps summing `Order.total`, which now means money actually charged. `dashboard/queries.py` is unchanged.
- **Editing a used coupon is allowed.** The snapshot protects past orders.
- **The cart page is unchanged.** Coupons are a checkout concern.

### Data model

```text
Coupon (orders app)
  code              CharField(max_length=30, unique)   # stored uppercase
  percent_off       PositiveSmallIntegerField           # validators: 1..100
  product           FK Product, null/blank, on_delete=PROTECT   # blank = order-wide
  expires_at        DateTimeField, null/blank           # blank = never expires
  is_active         BooleanField(default=True)
  created_at        DateTimeField(default=timezone.now)

Order (new fields)
  subtotal              DecimalField(10, 2)
  discount_amount       DecimalField(10, 2, default=0)
  coupon                FK Coupon, null/blank, on_delete=SET_NULL
  coupon_code           CharField(30, blank)
  coupon_percent_off    PositiveSmallIntegerField, null/blank
  coupon_product_name   CharField(200, blank)           # blank = order-wide
```

`Coupon.product` uses `PROTECT`: a product that a coupon targets can't be deleted out from under it (staff retire or edit the coupon first). Products are normally made unavailable rather than deleted, so this rarely bites.

---

## Phase 1 — The Coupon Model and Its Rules

**Goal:** A `Coupon` exists and knows, on its own, whether and how much it discounts a given cart.

**Tasks:**
1. `Coupon` model per the data model above, with `__str__`, uppercase normalization, `percent_off` validators, and `ordering = ["code"]`.
2. `CouponError(Exception)` carrying the customer-facing message.
3. A custom manager/queryset: `Coupon.objects.get_by_code(code)` (case-insensitive; raises `CouponError` for unknown codes).
4. Model methods: `is_expired(now=None)`, and `discount_for(cart) -> Decimal` implementing the validation order and the math above. Docstrings and type hints.
5. `CouponAdmin`: `list_display` (code, percent_off, product, expires_at, is_active), `list_filter` (is_active), `search_fields` (code).
6. `conftest.py` grows: `coupon` (order-wide), `product_coupon` (targets the fixture product), `expired_coupon`, `retired_coupon`.

**Verification.** *Automated:* order-wide and product-scoped math; rounding (e.g. 15% of $19.99); every error message, in the validation order; case-insensitive lookup; blank `expires_at` never expires; `expires_at` exactly now counts as expired; product-scoped coupon ignores look-alike products. *Manual:* create a coupon in `/admin/`.

**Out of bounds:** checkout, orders, templates.

---

## Phase 2 — Orders Remember Their Coupon

**Goal:** `place_order` honours `coupon_code`, and every order carries a frozen record of its discount.

**Tasks:**
1. Add the snapshot fields to `Order`; schema migration plus a data migration backfilling `subtotal = total`, `discount_amount = 0`.
2. `place_order`: replace the dormant seam. When `coupon_code` is given, look it up and call `discount_for(cart)` inside the transaction; on `CouponError`, raise `ValueError(message)` (matching the existing backstop style) so no order is created and the cart is untouched. Write `subtotal`, `discount_amount`, `total`, and the snapshot fields. Update the docstring.
3. Replace `test_the_coupon_seam_is_accepted_and_ignored` with real tests.

**Verification.** *Automated:* order-wide and product coupons produce the right `subtotal` / `discount_amount` / `total`; snapshot fields filled; no coupon → `discount_amount = 0` and `subtotal == total`; invalid coupon → `ValueError`, no order, cart intact; **retiring, editing, and deleting the coupon after placing the order leave the order's total and snapshot unchanged** (requirement 3).

**Out of bounds:** forms, views, templates.

---

## Phase 3 — Checkout: Enter, Preview, Pay

**Goal:** A customer types a code, sees the discounted total, and places the order.

**Tasks:**
1. `CouponForm` (optional `coupon_code`, requires `cart=`); `clean_coupon_code` calls `discount_for` and turns `CouponError` into a field error. `CheckoutForm` is unchanged.
2. `Cart.checkout_summary(code) -> CheckoutSummary` (subtotal, discount, total, coupon, error) — what the page and the preview display.
3. `CheckoutView.post` validates both forms (so all errors show at once); `form_valid` passes the code to `place_order`, mapping `CouponError` to the coupon field and other `ValueError`s to a form alert (the backstop for a coupon that changed between preview and submit).
4. `ApplyCouponView` (HTMX, login required, POST only): renders `templates/orders/partials/_order_summary.html` — subtotal, discount line, total, or the error — and swaps the "Place order" amount out-of-band. URL `orders:apply_coupon`.
5. Checkout template: coupon box in the order-summary sidebar (the input joins `#checkout-form` via the HTML `form` attribute) with an "Apply" button; the summary partial rendered on first load too.

**Verification.** *Automated:* preview shows the discount for a valid code and each error message for invalid ones; submitting with each kind of invalid code re-renders the form with the error and creates no order; a valid code places a discounted order; blank code still places a full-price order. *Manual:* as `customer`, apply each seeded code at checkout.

**Out of bounds:** order display pages, back office.

---

## Phase 4 — Receipts Show the Discount

**Goal:** Everywhere an order is shown, its discount is shown — from the snapshot.

**Tasks:**
1. A shared receipt-summary partial (`templates/orders/partials/_receipt_summary.html`): Subtotal / "Coupon THOUGHTS10 (20%)" or "Coupon SERAPHINE50 — 50% off Seraphine" / Total. Discount lines appear only when `discount_amount > 0`.
2. Use it on the confirmation page, customer order detail, and back-office order detail.
3. `OrderAdmin`: show `coupon_code` in `list_display`.

**Verification.** *Automated:* each page shows the discount line for a discounted order and omits it otherwise; a receipt still shows the coupon after the coupon is deleted. *Manual:* place a discounted order and view it from both sides.

---

## Phase 5 — The Coupons Tab and the Demo World

**Goal:** Staff manage coupons from the back office; the demo world exercises every rule.

**Tasks:**
1. `CouponForm` (ModelForm): code, percent_off, product (available products, blank = "Whole order"), expires_at, is_active.
2. `ManageCouponListView`, `ManageCouponCreateView`, `ManageCouponUpdateView` — `StaffRequiredMixin`, `SuccessMessageMixin`, `section = "coupons"`, pk URLs under `backoffice/coupons/`. List shows status badges (Active / Expired / Retired) and a designed empty state. No delete view.
3. Add the "Coupons" tab to `templates/backoffice/base.html`.
4. Seed: `THOUGHTS10` (10%, order-wide, never expires), `SERAPHINE50` (50%, Seraphine), `SUMMER25` (25%, order-wide, expired), `LEAKED20` (20%, order-wide, retired). No seeded discounted orders.
5. Update `CLAUDE.md` (the seam is no longer dormant) and append a `PROMPTS.md` entry.

**Verification.** *Automated:* staff-only access (customer → 403/redirect); create and edit round-trip; `percent_off` outside 1–100 rejected; duplicate code (any case) rejected; empty state renders. *Manual:* seed, sign in as `employee`, retire `THOUGHTS10`, confirm checkout now rejects it and a past order using it is unchanged.

---

## Explicitly deferred

Fixed-amount coupons · coupons targeting several products or a category · per-customer or global usage limits · scheduled start dates · stacking · coupon entry on the cart page · per-line discount on `OrderItem` · seeded discounted orders · discount analytics on the dashboard.
