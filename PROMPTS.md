# PROMPTS.md — AI Usage Log

This file is the record of AI use on this codebase. At the end of every
agent session, direct the agent to write the session log with this prompt:

> Append a session log to PROMPTS.md at the repo root, under today's date,
> newest entry at the top. Record every prompt I gave you this session, in
> order, including any corrections. End the entry with a short summary:
> the outcome, any places where I deviated from a recommended answer or
> asked follow-up questions, and anything that went sideways.

Two rules:

- Entries are added only by that prompt, never unprompted.
- New entries go at the top. Never rewrite or delete an old entry — the
  log is part of your work, and an honest log of a session that went
  sideways is worth more than a tidy one.

Each entry has this shape:

    ## YYYY-MM-DD — <one-line summary>

    ### Prompts
    1. ...

    ### Summary
    - **Outcome:** what was built and what was kept
    - **Deviations:** recommendations overridden, follow-up questions asked
    - **Sideways:** failures, wrong turns, and how they were caught

## 2026-11-08 — Homework 4: discount coupons (design, build, review, crash fix)

One Claude Code session, Nov 7, 2026 at 10:46 PM to Nov 8 at 8:55 PM
(Central time; transcript `aa1f21c1-851c-4977-a436-098f0da54c36`). Prompts
are quoted word for word, with paragraph breaks joined. Prompts 2–10 answer
the `/grill-me` interview; the question each one answered is noted in
brackets. The complete conversation follows the Summary.

### Prompts
1. "/grill-me I want to add discount coupons to the ThoughtTronix Store
   checkout. Customers should be able to enter a coupon code to receive a
   discount. Expired coupons must be rejected with a clear error message.
   Retiring a coupon must not change the totals of orders already placed.
   The system must support both order-wide discounts and product-specific
   discounts, such as 50% off Seraphine. Help me design this feature before
   implementing it. Ask me one question at a time and explain the options
   because I am a beginner."
2. [Q1, shape of a coupon] "A" (one `Coupon` model with an optional product
   link)
3. [Q2, how the discount is expressed] "A" (percentage only)
4. [Q3, expired vs. retired] "B. An optional expires_at is fine."
   (`is_active` + optional `expires_at`)
5. [Q4, what an order remembers] "B" (snapshot fields on the order plus a
   `SET_NULL` link)
6. [Q5, product coupon whose product isn't in the cart] "A" (reject, naming
   the product)
7. [Q6, where the code is entered] "B" (checkout field plus an HTMX "Apply"
   preview)
8. [Q7, usage limits] "A" (none)
9. [Q8, how staff manage coupons] "C" (back-office Coupons tab plus the
   Django admin)
10. [Q9, demo data] "A, without seeded past orders. Please write the design
    to plans/coupons.md before implementing anything."
11. "Start Phase 1 of plans/coupons.md. Follow the plan and CLAUDE.md
    instructions. Run the required tests and report the results before
    proceeding to Phase 2."
12. "Start Phase 2 of plans/coupons.md. Follow CLAUDE.md, run the required
    tests, and report the results before proceeding to Phase 3. Do not
    commit anything yet."
13. "Start Phase 3 of plans/coupons.md. Follow CLAUDE.md, run the required
    tests, and report the results before proceeding to Phase 4. Do not
    commit anything yet. Leave unrelated files unchanged."
14. [Answer to the agent's mid-phase question: CheckoutForm must have no
    `clean_*` methods (PRD rule) but the plan put `clean_coupon_code` on it,
    so how should Phase 3 resolve this?] Chose "Separate CouponForm
    (Recommended)".
15. "Start Phase 4 of plans/coupons.md. Follow CLAUDE.md, run all required
    tests, and report the results before proceeding to Phase 5. Do not
    commit anything yet. Leave unrelated files unchanged."
16. [The user rejected the agent's test-run tool call, which interrupted the
    request: "[Request interrupted by user for tool use]"]
17. "Resume Phase 4 of plans/coupons.md. The previous session was
    interrupted while writing orders/test_receipts.py. First inspect the
    existing changes so you don't duplicate work. Complete Phase 4, follow
    CLAUDE.md, and run the required tests. Report the results before
    proceeding to Phase 5. Do not commit anything yet, and leave unrelated
    files unchanged."
18. "Start Phase 5 of plans/coupons.md. Follow CLAUDE.md and implement the
    back-office Coupons tab and four sample coupons. Run all required tests
    and report the results. Do not commit anything yet. Do not reset
    existing database data or run the seed command without asking me
    first. Leave unrelated files unchanged."
19. "Yes. Test the seed command against a temporary copy of my database
    only. Verify that all four coupons are created correctly and that
    running the seed twice doesn't cause problems. Do not modify or reset
    my real database. Report the results and stop. Do not commit anything
    yet."
20. "Review the completed discount coupon implementation against
    plans/coupons.md and the Homework 4 requirements. Identify 2-3
    meaningful improvements we could make after the initial feature commit.
    Explain each in beginner-friendly language. Do not modify any files,
    run the seed command, or commit anything yet. Report your findings and
    stop."
21. "Before the first Homework 4 commit, review git status and git diff.
    Confirm which files belong to the completed coupon feature, identify
    any unrelated changes, and run the full test suite. Do not fix the
    improvements yet. Do not run the seed command. Do not modify files or
    commit anything. Report the results and stop."
22. "Stage only the 26 files identified in your review as belonging to the
    completed Homework 4 coupon feature. Do not stage accounts/views.py or
    any unrelated changes. Create the first commit with the message "Add
    discount coupon feature". After committing, show me the commit hash and
    git status. Do not push yet, do not implement any improvements, and do
    not modify any other files."
23. "Implement Improvement 1 from your Homework 4 coupon code review: the
    confirmed crash you identified. First explain the cause of the crash.
    Then make the smallest appropriate fix and add an automated regression
    test that would have caught the problem. Run the relevant tests and
    full test suite. Report the results and explain the fix in
    beginner-friendly language. Do not commit or push anything yet. Leave
    accounts/views.py and all unrelated files unchanged."
24. "Stage only the files changed for Improvement 1 (the duplicate coupon
    code admin crash fix and its regression tests). Create the second
    commit with the message "Fix duplicate coupon code admin crash". Do not
    include accounts/views.py or unrelated changes. After committing,
    report the commit hash and git status. Do not push yet or make any
    additional changes."
25. "Review PROMPTS.md and the available Claude Code session history for
    Homework 4. Append the Homework 4 interaction transcript to PROMPTS.md,
    preserving the existing entries from previous assignments. Include the
    /grill-me design interview, implementation phases, testing, code
    review, and duplicate coupon code crash fix. Do not invent or
    reconstruct missing conversation messages. Tell me if any session
    history is unavailable. Do not commit or push anything yet. Do not
    modify any files other than PROMPTS.md."

### Summary
- **Outcome:**
  - Design (`/grill-me`, prompts 1–10): nine one-at-a-time questions,
    each with options and a recommendation, written to `plans/coupons.md`.
    The design: a `Coupon` model with a percentage (1–100) and an optional
    product (blank = whole order); `is_active` (retire) plus an optional
    `expires_at`; orders snapshot `subtotal`, `discount_amount`,
    `coupon_code`, `coupon_percent_off` and `coupon_product_name`; one
    coupon per order; no usage limits.
  - Phase 1: `Coupon` model, `get_by_code` (ignores case and spaces),
    `discount_for(cart)` with four customer-facing errors (unknown,
    retired, expired, product not in cart), round-half-up to the cent,
    `CouponAdmin`, migration `0003`, fixtures in `conftest.py`. Tests 225 →
    254.
  - Phase 2: snapshot fields on `Order` (hand-written migration `0004`
    backfills `subtotal = total`); `place_order` applies the coupon and
    rejects a bad one with no order created and the cart intact. Tests
    prove retiring, editing or deleting a coupon (or renaming its product)
    leaves placed orders unchanged. The migration was checked on a scratch
    copy of the database (54 orders backfilled). Tests → 270.
  - Phase 3: separate `CouponForm`; `Cart.checkout_summary`; HTMX
    `ApplyCouponView` previews the discount and updates the "Place order"
    total; checkout validates both forms; `place_order` is the backstop.
    Tests → 304.
  - Phase 4: `_receipt_summary.html` shows the subtotal and coupon line
    (from the snapshot only) on the confirmation page, the customer's order
    detail and the back-office order detail; `OrderAdmin` lists
    `coupon_code`. Tests → 322.
  - Phase 5: back-office Coupons tab (list with Active/Expired/Retired
    badges and an empty state, create and edit, retire via toggle, no
    delete) with `ManageCouponForm`; seed creates THOUGHTS10, SERAPHINE50,
    SUMMER25 (expired) and LEAKED20 (retired); `CLAUDE.md` updated. Tests →
    345.
  - Seed testing (prompt 19): run twice against a scratch copy of the
    database; all checks passed both times. The real database's checksum
    was unchanged and the copy was deleted.
  - Review (prompt 20): all four requirements met. Three improvements
    proposed: (1) the Django admin crashes (500) on a duplicate code typed
    in lowercase, confirmed with a throwaway test, plus admin delete and
    editable order totals; (2) Enter in the coupon box submits the whole
    checkout; (3) expiry dates are in UTC for a Texas store. Also
    mentioned: a usage count.
  - Commits: `63ea2e8` "Add discount coupon feature" (26 files) and
    `244c92e` "Fix duplicate coupon code admin crash". The fix is
    `Coupon.clean()`, which uppercases the code before Django's uniqueness
    check, with 4 regression tests that failed before the fix. Tests →
    349. Nothing pushed.
- **Deviations:**
  - Every `/grill-me` recommendation was accepted. Q9's optional seeded
    discounted orders were declined, matching the recommendation.
  - The plan changed once, at the user's choice (prompt 14): the coupon
    field moved from `CheckoutForm` to a separate `CouponForm` to keep the
    PRD's "no `clean_*`" rule. `plans/coupons.md` was updated to match.
  - Agent choices not spelled out in the plan, all reported at the time:
    `CouponError` subclasses `ValueError`; `Order.save()` fills in a
    missing `subtotal`; receipts reuse the checkout wording "(50% off
    Seraphine Home Hub)"; the `PROMPTS.md` entry the plan listed for Phase 5
    was skipped because this file allows entries only on request.
  - Follow-ups the user added: testing the seed on a database copy (19), a
    review (20), a pre-commit audit (21), and fixing only the crash from
    Improvement 1 (23). Still not done: Improvement 1's admin-delete and
    editable-order-field issues, and Improvements 2 and 3.
- **Sideways:**
  - Phase 1: `ruff format .` also reformatted unrelated
    `accounts/views.py` (one missing blank line). The agent reported it,
    formatted only touched files from Phase 3 on, and left it out of both
    commits; it is still uncommitted.
  - Phase 3: an existing test caught that the plan broke the PRD's
    declarative-validation rule for `CheckoutForm`. The agent asked how to
    resolve it (prompt 14). A new test also used the wrong login URL name
    (`login` instead of `accounts:login`); fixed.
  - Phase 4: the user interrupted the test run (prompt 16). On resume the
    agent found all the files complete on disk and only re-ran the tests.
  - Phase 5: the new "Coupons" tab broke a too-broad Phase 4 test that
    checked the word "Coupon" was absent; the test was tightened. The
    agent also found, before running anything, that the seed would crash
    on a second run (a product coupon protects its product from deletion)
    and moved the coupon wipe ahead of products.
  - Review: the first throwaway probe failed to start (pytest-django
    picked the wrong project folder); rerun with an explicit Python path.
  - Pre-commit audit: the real database's checksum had changed. A
    read-only check traced it to the user's own manual testing outside
    this chat: migration `0004` applied, coupons created by hand, two
    discounted orders placed, THOUGHTS10 retired. The agent did not cause
    the change.
  - Crash fix: ruff's DJ012 rule required `save()` before `clean()`; the
    methods were reordered.

### Complete conversation

Exported from the saved session file, not retyped, in chronological order.
Included: every user message, every visible Claude reply, and the one
question dialog with its answer. Omitted: tool-call details (each spot is
marked *[Tools used: …]* with the tool's short description), tool output,
and Claude's internal reasoning, which was never shown in the conversation.
Times are Central. A new heading starts when the speaker changes or after a
pause of more than two minutes. It ends with the prompt that requested this
export; the reply to that prompt is this section.

**User** · Nov 7, 2026, 10:46 PM

> /grill-me I want to add discount coupons to the ThoughtTronix Store checkout. Customers should be able to enter a coupon code to receive a discount. Expired coupons must be rejected with a clear error message. Retiring a coupon must not change the totals of orders already placed. The system must support both order-wide discounts and product-specific discounts, such as 50% off Seraphine. Help me design this feature before implementing it. Ask me one question at a time and explain the options because I am a beginner.

**Claude** · Nov 7, 2026, 10:46 PM

> I'll start by reading the checkout code, since the project already has a "coupon seam" in `place_order`.
>
> *[Tools used: Bash — Read order services, models, and search for coupon references]*
>
> I read the checkout code. A few things already help us:
>
> - **`place_order` already has a `coupon_code` parameter.** It accepts it and ignores it for now (`orders/services.py:39`). The original plan left this as the place to plug coupons in, so we won't need to change the function's signature.
> - **Orders are already snapshots.** `Order.total` and each `OrderItem.unit_price` are saved as plain numbers when the order is placed. That's a good start on your rule that retiring a coupon must not change old orders. We still need to decide how the discount itself gets recorded on the order.
> - **Nothing coupon-related exists yet.** There's no model, no form field and no back-office screen.
>
> Let's start with the decision everything else builds on.
>
> ---
>
> ### Question 1: What *is* a coupon? (the shape of the `Coupon` model)
>
> **What this settles:** how one database table can hold both "10% off your whole order" and "50% off Seraphine." Your answer decides which fields the model has, and those fields shape the math, the validation and the admin screen.
>
> There are two things a coupon could vary on:
> - **Scope:** does it apply to the whole order or to one product?
> - **Kind:** is it a percentage (50% off) or a fixed amount ($10 off)?
>
> **Option A: one `Coupon` model with an optional product link**
> Fields would be roughly `code`, `percent_off`, `product` (blank means the whole order) and the expiry fields. If `product` is empty, the discount applies to the whole order. If it's set, the discount applies only to that product's lines.
> *Gives you:* one table, one admin screen and a simple rule for "which kind is it?"
> *Gives up:* each coupon can target only one product. "20% off all smart speakers" would need a different design later.
>
> **Option B: one `Coupon` model with a many-to-many link to products (or categories)**
> This is the same as A, except a coupon can target a *set* of products, or even a category.
> *Gives you:* flexibility, such as "25% off Seraphine and Aurelius."
> *Gives up:* more complexity. The form needs a multi-select, the math has to loop over several targets, and there are more edge cases to test.
>
> **Option C: two separate models, `OrderCoupon` and `ProductCoupon`**
> *Gives you:* each model only has the fields it needs.
> *Gives up:* checkout has to search two tables for one code, two codes could collide across the tables, and you end up with two admin screens. It's more code for no real gain.
>
> There's also a smaller question inside this one: **percentage only, or percentage *and* fixed-dollar amounts?** Fixed amounts bring in awkward cases, such as a $20-off coupon on a $15 order. I'll ask about that separately.
>
> **My recommendation: Option A.** It meets your stated requirement ("50% off Seraphine" or order-wide) with the fewest moving parts. For a beginner it's one model you can fully understand and test. If you later need multi-product coupons, changing the single product link into a many-to-many link is a manageable migration.
>
> **Which do you choose: A, B, or C?**

**User** · Nov 7, 2026, 10:50 PM

> A

**Claude** · Nov 7, 2026, 10:50 PM

> Locked in: **one `Coupon` model with an optional `product` link.** If the link is blank, the coupon applies to the whole order. If it's set, it applies only to that product.
>
> ---
>
> ### Question 2: How is the discount amount expressed?
>
> **What this settles:** the field (or fields) that store "how much off," and the math `place_order` does. Every later question about rounding and edge cases depends on this one.
>
> **Option A: percentage only (`percent_off`, a whole number from 1 to 100)**
> Every coupon reads as "X% off." Product-scoped coupons take X% off that product's lines, and order-wide coupons take X% off the subtotal.
> *Gives you:* the discount can never exceed what it applies to, so a total can never go negative. You need one field and one formula, and the model can enforce a 1–100 range.
> *Gives up:* no "$10 off" coupons.
>
> **Option B: percentage *or* fixed amount (a `kind` choice plus an `amount` field)**
> A coupon is either "X% off" or "$X off."
> *Gives you:* both kinds of promotion marketing usually wants.
> *Gives up:* you need extra rules. For example, a $20-off coupon on a $15 order has to be capped so the total doesn't go below $0. For product coupons you also have to decide whether "$10 off Seraphine" means $10 per unit or $10 once. That means more validation and more tests.
>
> **Option C: both fields on every coupon (`percent_off` *and* `amount_off`, either may be blank)**
> *Gives up:* a coupon could end up with both fields filled in or neither. You'd need an extra check to prevent that. B is the cleaner way to support both kinds.
>
> **My recommendation: Option A, percentage only.** Your requirements only mention percentages ("50% off Seraphine"). Percentages also remove the negative-total problem entirely. If you add fixed-dollar coupons later, the change is contained: add a `kind` field that defaults to "percent," so existing coupons keep working unchanged.
>
> **Do you choose A, B, or C?**

**User** · Nov 7, 2026, 10:55 PM

> A

**Claude** · Nov 7, 2026, 10:55 PM

> Locked in: **percentage only**, stored as `percent_off` (a whole number from 1 to 100).
>
> ---
>
> ### Question 3: What makes a coupon usable or unusable? ("expired" vs. "retired")
>
> **What this settles:** the fields that control *when* a coupon works, and the error messages customers see. Your requirements use two different words, **expired** and **retired**, so we need to decide whether they mean the same thing.
>
> - **Expired** suggests a date has passed. That happens automatically, with nobody clicking anything.
> - **Retired** suggests a staff member deliberately switched the coupon off, for example because a code leaked online, even if its date hasn't passed yet.
>
> **Option A: an expiry date only (`expires_at`)**
> The coupon works until `expires_at`, then it's rejected. To retire one early, staff set `expires_at` to now.
> *Gives you:* one field and one check.
> *Gives up:* "retiring" is really just editing a date, and the original expiry date gets overwritten, so you lose the record of what it was. The only error message available is "expired," even when staff pulled the coupon on purpose.
>
> **Option B: an expiry date plus an on/off switch (`expires_at` + `is_active`)**
> A coupon works only if `is_active` is on *and* `now < expires_at`. Retiring means unchecking `is_active`, and the dates stay untouched.
> *Gives you:* two clear, separate concepts. That leads to two clear error messages: "This coupon expired on Oct 31, 2026" and "This coupon is no longer available." A retired coupon can also be switched back on.
> *Gives up:* one extra field, and staff need to understand the difference between the two.
>
> **Option C: a full validity window (`starts_at` + `expires_at` + `is_active`)**
> This is the same as B, plus a start date, so marketing can create a Black Friday code in advance that only starts working on Friday.
> *Gives you:* scheduled promotions.
> *Gives up:* a third check and a third error message ("not valid yet"), plus more tests. Your requirements don't ask for it.
>
> A small sub-point I'll decide unless you object: **should `expires_at` be required?** I'd make it *optional*, so a blank value means the coupon never expires. Then a permanent code like a "welcome" coupon is possible.
>
> **My recommendation: Option B.** Your requirements name both ideas, and B keeps them as separate fields with separate, clear messages. The real need behind "retiring" is turning off a leaked or mistaken code right away without rewriting its history, and a switch handles that cleanly. C is easy to add later if marketing asks for scheduled launches.
>
> **Do you choose A, B, or C? And is an optional `expires_at` okay?**

**User** · Nov 7, 2026, 10:57 PM

> B. An optional expires_at is fine.

**Claude** · Nov 7, 2026, 10:57 PM

> Locked in: **`is_active` + optional `expires_at`.** A blank `expires_at` means the coupon never expires. Unchecking `is_active` retires the coupon without touching its dates.
>
> ---
>
> ### Question 4: What does an order remember about its coupon?
>
> **What this settles:** your "retiring must not change old orders" requirement, and what the order history and back-office order screens can show.
>
> Here's the risk. `Order.total` is already saved as a number, so *retiring* a coupon can't change it. But staff could also **edit** a coupon (change 20% to 30%) or **delete** it. If an order only *points to* the coupon and works out its discount by looking the coupon up again, then editing that coupon would quietly rewrite the receipt for every past order that used it. Even when the total is safe, the receipt could show "20% off" next to a discount that was actually calculated at 30%.
>
> The fix is the same approach the codebase already uses for prices: **snapshot** the facts onto the order at the moment of purchase.
>
> **Option A: only a foreign key (`Order.coupon → Coupon`)**
> *Gives you:* the least work.
> *Gives up:* the receipt reads live coupon data, so edits rewrite history. Deleting the coupon either blocks the delete or wipes the link. This breaks your requirement in spirit.
>
> **Option B: snapshot on the `Order` (`subtotal`, `discount_amount`, `coupon_code`, `coupon_percent_off`), plus an optional link to the coupon**
> The order stores the numbers and the code as plain values. A `coupon` foreign key with `on_delete=SET_NULL` can stay alongside them, so staff can still answer "how many orders used THOUGHTS10?" while the coupon exists. Receipts read only the snapshot fields.
> *Gives you:* old orders are frozen no matter what happens to the coupon, and receipts can show "Subtotal $200, THOUGHTS10 (20%) −$40, Total $160." The pattern matches how `OrderItem` already stores `product_name` and `unit_price`.
> *Gives up:* four or five new columns, and the snapshot copies some data that also lives on the coupon. Copying it is intentional here.
>
> **Option C: B, plus a per-line `discount_amount` on each `OrderItem`**
> With a product coupon, the receipt could show the discount *on the Seraphine line itself* instead of only in the order summary.
> *Gives you:* the most detailed receipts, and line-level numbers for later work like refunding one item.
> *Gives up:* more columns, and the line discounts have to add up exactly to the order discount, which is a rounding headache (that's the next question).
>
> **My recommendation: Option B.** It fully meets your requirement, and it follows the snapshot pattern already in `Order` and `OrderItem`. A product coupon's receipt can still name the product ("50% off Seraphine −$75") in the summary. Line-level discounts (C) matter mostly for partial refunds, which this store doesn't have.
>
> **Do you choose A, B, or C?**

**User** · Nov 7, 2026, 11:02 PM

> B

**Claude** · Nov 7, 2026, 11:02 PM

> Locked in: **snapshot on the Order** (`subtotal`, `discount_amount`, `coupon_code`, `coupon_percent_off`), plus a `coupon` foreign key with `SET_NULL`.
>
> I'll add one field so the receipt can name the product: **`coupon_product_name`**, blank for order-wide coupons. It copies the product's name the same way `OrderItem.product_name` does, so the receipt still reads correctly if the product is later renamed or deleted.
>
> I'll also decide the math myself unless you object. Use `Decimal` throughout. A product coupon's discount is `percent_off × (Seraphine price × quantity)`, so it covers every Seraphine unit in the cart. Round to the cent with round-half-up, which is how people round money by hand. Then `total = subtotal − discount_amount`.
>
> ---
>
> ### Question 5: What happens when a product coupon's product isn't in the cart?
>
> **What this settles:** one of the validation rules, and a customer-facing message. Say a customer types `SERAPHINE50`, but their cart only holds an Aurelius speaker. The code exists, it's active and it isn't expired. It just applies to nothing.
>
> **Option A: reject it with a clear error**
> "SERAPHINE50 applies only to Seraphine Home Hub, which isn't in your cart."
> *Gives you:* the customer understands immediately and isn't misled. It's consistent with your "clear error message" requirement for expired coupons.
> *Gives up:* one more rule and one more test.
>
> **Option B: accept it silently with a $0 discount**
> *Gives you:* no extra rule.
> *Gives up:* the customer sees "Coupon applied ✓" and saves nothing. That feels broken, and the order records a coupon that did nothing. This is the option that generates support emails.
>
> **Option C: accept it with a warning ("applied, but nothing in your cart qualifies")**
> *Gives up:* it's more confusing than A for no benefit, because an order can't use a coupon that does nothing anyway.
>
> **My recommendation: Option A.** A coupon that can't reduce the total should be treated like any other invalid coupon. Saying exactly why helps the customer, perhaps by prompting them to add Seraphine to the cart. It also gives a simple rule for later: **if an order records a coupon, that coupon actually discounted something.**
>
> **Do you choose A, B, or C?**

**User** · Nov 7, 2026, 11:03 PM

> A

**Claude** · Nov 7, 2026, 11:03 PM

> Locked in: **a product coupon is rejected if its product isn't in the cart**, and the error names the product.
>
> ---
>
> ### Question 6: Where does the customer enter the code, and when do they see the discount?
>
> **What this settles:** which page, form and view change, and whether the customer sees the new total *before* they click "Place order." Let me check the cart and checkout pages first.
>
> *[Tools used: Bash — Read order views, urls, partials and form outline]*
>
> Here's what I found. Checkout is **one page** with one `CheckoutForm` (addresses and card), and it already uses one small HTMX interaction to refill address fields. The cart page uses HTMX for quantity changes. So the project already has two patterns we can follow.
>
> **Option A: a plain `coupon_code` field on `CheckoutForm`, checked when the customer clicks "Place order"**
> The form's `clean_coupon_code` method looks up the code and raises the "expired," "retired" or "not in your cart" error under the field, like any other form error. If the code is valid, the order is placed with the discount.
> *Gives you:* the smallest change. One field, and form validation does all the work, which is the project's "forms own their validation" rule.
> *Gives up:* the customer **never sees the discounted total before paying.** The first time they see $160 instead of $200 is on the confirmation page. That's poor shopping experience, and it's risky: they commit without knowing the final price.
>
> **Option B: A, plus an HTMX "Apply" button on the checkout page that previews the discount**
> The checkout page gets a coupon box with an "Apply" button. The button hits a small HTMX endpoint, which renders a partial (`_order_summary.html`) showing the subtotal, the discount line and the new total, or the error message. The code stays in the form field, so "Place order" submits it and the server **checks it again** before placing the order.
> *Gives you:* the customer sees exactly what they'll pay before committing, and errors appear immediately. It follows the existing `AddressFieldsView` pattern. Nothing is stored between requests, so there's no stale state.
> *Gives up:* one extra view, URL, partial and set of tests.
>
> **Option C: apply the coupon on the cart page and remember it in the session (or on the `Cart`)**
> This is the Amazon-style flow: apply on the cart, and the discount follows you to checkout.
> *Gives you:* the most familiar shopping experience.
> *Gives up:* the coupon now has to be **remembered**, and remembered things go stale. The customer removes Seraphine, or the coupon expires while they browse, and every cart change must re-check it. It's the most code and the most edge cases.
>
> **Whichever you pick, `place_order` checks the coupon again inside its transaction.** The form check is for friendly messages. The service is the final safeguard, the same "backstop" approach the code already uses for unavailable products. `place_order` will raise a `ValueError` for a bad code, and the view will show it as a form error.
>
> **My recommendation: Option B.** Showing the price before payment matters, B gets there with one small HTMX endpoint that copies a pattern you already have, and it avoids C's stale-state problems completely.
>
> **Do you choose A, B, or C?**

**User** · Nov 7, 2026, 11:04 PM

> B

**Claude** · Nov 7, 2026, 11:05 PM

> Locked in: **a coupon field on `CheckoutForm` plus an HTMX "Apply" preview**, with the code checked again in `place_order`.
>
> Here are some decisions I'll make myself, following your project's conventions, unless you object:
> - **Where validation lives:** a `Coupon` model method, roughly `coupon.discount_for(cart)`, which returns the discount amount or raises a `CouponError` with the customer-facing message. The form, the HTMX preview and `place_order` all call that same method, so the rules exist in exactly one place.
> - **Codes are case-insensitive.** They're saved in uppercase, so `thoughts10` works.
> - **One coupon per order, no stacking.** This already follows from the single `coupon_code` field.
>
> ---
>
> ### Question 7: Is there a limit on how many times a coupon can be used?
>
> **What this settles:** whether the model needs usage-limit fields, and whether `place_order` has to count past orders. Your requirements don't mention this, but it's the first thing anyone abuses ("I used SERAPHINE50 forty times").
>
> **Option A: no limits (unlimited use until it expires or is retired)**
> *Gives you:* nothing extra to build. This is fine for public promo codes like a newsletter discount.
> *Gives up:* there's no protection against one customer reusing a code on every order. The only control is retiring the code.
>
> **Option B: one use per customer**
> Before applying a code, check whether this user already has an order with this coupon. If they do: "You've already used THOUGHTS10."
> *Gives you:* the most common real-world rule, at low cost. It reuses the `Order.coupon` link from Question 4, so it needs no new model fields.
> *Gives up:* one query and one more error message. One catch: if the coupon is deleted, `SET_NULL` erases the link. Comparing the snapshot `coupon_code` instead avoids that.
>
> **Option C: a configurable total cap (`max_uses`, e.g. "first 100 customers")**
> *Gives you:* limited-quantity promotions.
> *Gives up:* it's the hardest to get right. Two customers checking out at the same moment can both claim use #100, so you'd need database row locking (`select_for_update`). That's an advanced topic. It also needs another field and more tests.
>
> **Option D: B and C together, both configurable per coupon**
> *Gives up:* all of C's complexity, plus more settings for staff.
>
> **My recommendation: Option A for now**, unless your instructor or your own goals call for limits. It meets every requirement you stated and keeps the first version focused. Because the order snapshot (Question 4) records which code each order used, adding B later is a single extra check with no migration. If you'd like some protection from day one, **B is the cheap one**. I'd avoid C until you're comfortable with database locking.
>
> **Do you choose A, B, C, or D?**

**User** · Nov 7, 2026, 11:08 PM

> A

**Claude** · Nov 7, 2026, 11:08 PM

> Locked in: **no usage limits.** Coupons can be used without limit until they expire or are retired.
>
> ---
>
> ### Question 8: How do staff create and retire coupons?
>
> **What this settles:** whether we build new back-office screens or reuse something that already exists. Let me check what your back office has today.
>
> *[Tools used: Bash — Check back-office tabs, admin registrations, and product views]*
>
> Your project has **two** management surfaces. One is Django's built-in `/admin/`, where every model is registered. The other is your own **back office**: a staff shell with tabs (Products, Categories & tags, Orders, Dashboard) and full create/edit/delete views for products. Employees (`is_staff`) work in the back office.
>
> **Option A: Django admin only (`CouponAdmin` in `orders/admin.py`)**
> *Gives you:* about ten lines of code. Listing, searching, filtering by `is_active` and editing come free.
> *Gives up:* it doesn't match the rest of the store. Staff would leave your designed back office for Django's generic admin, which normally only the superuser uses. It's also inconsistent with how products and orders are managed.
>
> **Option B: a new "Coupons" tab in the back office (list, create and edit views; retire with an `is_active` toggle; no delete)**
> It follows the product CRUD pattern exactly: `StaffRequiredMixin`, `section = "coupons"`, a designed empty state ("No coupons yet"), and a ModelForm that validates `percent_off` is between 1 and 100. **No delete button on purpose.** Retiring is how a coupon ends, which keeps the link from past orders intact for reporting. Your Question 4 snapshot protects old orders even if one were deleted, so this is extra safety, not a requirement.
> *Gives you:* consistency with your app's conventions, and a natural place to show "times used" later.
> *Gives up:* the most code of the three. Three views, two templates, URLs and tests, though all of it copies patterns you already have.
>
> **Option C: both**
> Register it in admin (ten lines, useful to the superuser) *and* build the back-office tab.
> *Gives up:* almost nothing beyond B, since admin registration is nearly free. Every other model in your project is registered in both places.
>
> **My recommendation: Option C.** In practice that means building B, which is the real staff tool and matches your conventions, plus the tiny admin registration your project already does for every model. If you want to keep the first version small, **A alone is an acceptable starting point**: staff could manage coupons today, and the tab could come in a later phase.
>
> **Do you choose A, B, or C?**

**User** · Nov 7, 2026, 11:09 PM

> C

**Claude** · Nov 7, 2026, 11:09 PM

> Locked in: **a back-office "Coupons" tab** (list, create and edit; retire through `is_active`; no delete), **plus a `CouponAdmin` registration.**
>
> Here are a few more details I'll decide myself unless you object:
> - **Where the discount shows:** the checkout summary (HTMX partial), the confirmation page, the customer's order detail and the back-office order detail. Each shows a "Subtotal / Coupon THOUGHTS10 (20%) / Total" breakdown read from the snapshot fields. The cart page stays as it is, since coupons are applied at checkout.
> - **Existing orders:** the migration fills in `subtotal = total` and `discount_amount = 0` for every order already in the database, so old receipts still add up.
> - **The dashboard:** revenue keeps summing `Order.total`, which is now the amount after the discount, meaning money actually charged. Nothing in `dashboard/queries.py` changes.
> - **Editing a coupon after it's been used is allowed.** The snapshot keeps old orders correct.
>
> ---
>
> ### Question 9 (the last one): Should the demo world include sample coupons?
>
> **What this settles:** whether `uv run python manage.py seed` creates coupons, which decides how quickly you, a grader or a teammate can try the feature by hand.
>
> **Option A: seed a coupon for each case**
> For example:
> - `THOUGHTS10`: 10% off the whole order, never expires
> - `SERAPHINE50`: 50% off Seraphine Home Hub
> - `SUMMER25`: expired (`expires_at` in the past)
> - `LEAKED20`: retired (`is_active` off)
>
> Optionally, a couple of seeded past orders could use `THOUGHTS10`, so the order screens and the dashboard show discounts right away.
> *Gives you:* every rule can be demonstrated within a minute of seeding. You type each code and see the matching message.
> *Gives up:* a little more seed code. The seed is already destructive and idempotent, so the coupons fit that pattern. Tests still never call the seed (your CLAUDE.md rule) and use their own fixtures.
>
> **Option B: no seed coupons, so staff create them in the back office**
> *Gives you:* the seed stays unchanged.
> *Gives up:* every demo starts with "first, go create four coupons." The empty state shows up, but nobody sees the feature working.
>
> **My recommendation: Option A, without the seeded past orders.** Four coupons cover every rule we designed (order-wide, product-specific, expired, retired). Backdating discounted orders into the demo history adds complexity for little benefit, though it's easy to add if you want the dashboard to show discounts.
>
> **Do you choose A or B?** Once you answer, I'll summarize the whole design in one place. If you'd like, I can also write it up as `plans/coupons.md`, matching your existing `plans/core-platform.md`, before we implement anything.

**User** · Nov 7, 2026, 11:22 PM

> A, without seeded past orders. Please write the design to plans/coupons.md before implementing anything.

**Claude** · Nov 7, 2026, 11:22 PM

> Let me check the format of the existing plan so the new one matches.
>
> *[Tools used: Bash — Read existing plan format and confirm Seraphine product name; Write — `plans/coupons.md`]*
>
> I wrote the design to `plans/coupons.md`. Nothing is implemented and nothing is committed yet.
>
> The file has the 9 decisions in a table with the reason for each, the smaller defaults, the exact error messages, the data model, five build phases (each with tests and a manual check), and a list of what's deferred. It follows the same format as `plans/core-platform.md`.
>
> Three things in the plan you didn't explicitly pick:
>
> 1. **The product name in the seed is "Seraphine", not "Seraphine Home Hub".** That's what `products/management/commands/seed.py` uses, so the plan says "Seraphine". There are also "Seraphine Mini" and "Seraphine Doorbell" products. The plan says `SERAPHINE50` applies **only** to the exact product it's linked to, not to those two.
> 2. **`Coupon.product` uses `on_delete=PROTECT`.** You can't delete a product while a coupon still points at it; staff have to retire or edit the coupon first. Products in this store are normally marked unavailable rather than deleted, so this should rarely come up. The alternative is `SET_NULL`, but then a "50% off Seraphine" coupon would quietly become "50% off your whole order", which is much worse.
> 3. **A code that's exactly at its expiry time counts as expired.** If `expires_at` is 5:00:00 and someone applies the code at 5:00:00, it's rejected.
>
> Read through the file. When you're happy with it, tell me to start Phase 1 (the model and its rules). I'll keep the test suite passing at the end of each phase, as your CLAUDE.md requires.

**User** · Nov 7, 2026, 11:24 PM

> Start Phase 1 of plans/coupons.md. Follow the plan and CLAUDE.md instructions. Run the required tests and report the results before proceeding to Phase 2.

**Claude** · Nov 7, 2026, 11:24 PM

> *[Tools used: Bash — Read conftest, product model, and test conventions]*
>
> Before changing anything, I'll confirm the test suite passes on the current code and check the timezone settings, since the expiry message prints a date.
>
> *[Tools used: Bash — Check timezone settings and run baseline tests]*
>
> The suite passes on the current code: **225 tests**. The site uses UTC with timezone support on, so expiry dates will be displayed in UTC. Now I'll add the model.
>
> *[Tools used: Edit — `orders/models.py`; Edit — `orders/models.py`; Edit — `orders/admin.py`]*
>
> Next, the shared fixtures in `conftest.py`, the migration, and the tests.
>
> *[Tools used: Bash — Add coupon fixtures and generate the Coupon migration]*
>
> Now the tests. They cover every Phase 1 check listed in the plan.
>
> *[Tools used: Write — `orders/test_coupons.py`; Bash — Format, lint, check migrations, and run the full test suite]*
>
> Phase 1 is done and the full test suite passes: **254 tests** (the 225 that already passed, plus 29 new coupon tests). Ruff format and lint are clean, and Django confirms the models and migration match. Nothing is committed, and Phase 2 hasn't started.
>
> **What I built:**
> - **`orders/models.py`:** a new `Coupon` model with the fields from the plan. It has three main methods:
>   - `Coupon.objects.get_by_code(code)` finds a coupon, ignoring capital letters and extra spaces.
>   - `is_expired(now=None)` checks the date.
>   - `discount_for(cart)` either returns the discount, rounded to the cent, or rejects the coupon with a customer-facing message.
> - **Error messages:** the checks run in a fixed order and the first failure wins:
>   1. Unknown code: "We don't recognize the coupon code “NOPE”."
>   2. Retired: "The coupon LEAKED20 is no longer available."
>   3. Expired: "The coupon SUMMER25 expired on Oct 31, 2025."
>   4. Product not in cart: "SERAPHINE50 applies only to Seraphine Home Hub, which isn't in your cart."
> - **`orders/admin.py`:** `CouponAdmin`, so coupons can be listed, searched, filtered by active/retired and edited in `/admin/`.
> - **`orders/migrations/0003_coupon.py`:** creates the coupon table. It only adds a table, so existing data is untouched.
> - **`conftest.py`:** four shared sample coupons for tests: `coupon`, `product_coupon`, `expired_coupon`, `retired_coupon`.
>
> **What the 29 new tests in `orders/test_coupons.py` check:**
> - **Math:** the order-wide percentage, a product coupon discounting only its own line, every unit of that product getting the discount, and 100% off.
> - **Rounding:** 15% of $19.99 comes to $3.00. 10% of $0.05 rounds *up* to $0.01, which proves we round half-up the way people do by hand.
> - **Rules:** every rejection message, the order they're checked in, an expiry at exactly the current moment counting as expired, a blank expiry never expiring, and "Seraphine Mini" not counting as Seraphine.
> - **Data safety:** percentages outside 1–100 are rejected, `thoughts10` and `THOUGHTS10` can't both exist, and a product with a coupon pointing at it can't be deleted.
>
> **One thing to know:** the site's timezone is UTC, so expiry dates in messages are shown in UTC. A coupon set to expire late in the evening US time would show the next day's date. If that matters, change `TIME_ZONE` in the settings.
>
> **Your manual check from the plan:** I didn't apply the migration to your local database. To try it yourself, run `uv run python manage.py migrate`, start the server, sign in as `admin` and add a coupon at `/admin/orders/coupon/`. Try typing a lowercase code: it should save in uppercase.
>
> Phase 2 next adds the discount fields to `Order` and makes `place_order` apply the coupon.

**User** · Nov 7, 2026, 11:48 PM

> Start Phase 2 of plans/coupons.md. Follow CLAUDE.md, run the required tests, and report the results before proceeding to Phase 3. Do not commit anything yet.

**Claude** · Nov 7, 2026, 11:48 PM

> I'll start by finding everywhere an `Order` gets created. The new `subtotal` field will be required, so every one of those places needs to supply it.
>
> *[Tools used: Bash — Find all Order creation sites and the seam test; Bash — Check database settings and seed order creation; Read — `orders/models.py`; Edit — `orders/models.py`; Edit — `orders/models.py`; Edit — `orders/models.py`; Edit — `orders/models.py`]*
>
> Now the migration. I'm writing it by hand in three steps so existing orders get the right `subtotal`, rather than a placeholder default:
>
> *[Tools used: Write — `orders/migrations/0004_order_coupon_snapshot.py`]*
>
> Now `place_order`, replacing the dormant seam:
>
> *[Tools used: Edit — `orders/services.py`; Edit — `orders/services.py`; Edit — `orders/services.py`; Bash — Add Decimal import to services module]*
>
> Now I'll replace the old "seam is ignored" test with the real Phase 2 tests.
>
> *[Tools used: Bash — Show the end of the services test file; Bash — Replace seam test with Phase 2 coupon tests; Bash — Fix docstring wrap, then format, lint, check migrations, run tests; Bash — Apply migrations to a copy of the dev database and verify the backfill; Bash — Run seed on the database copy, verify, clean up, show git status]*
>
> The seed works too. But `git status` lists **`accounts/views.py` as modified, and I haven't touched that file.** Let me see what changed.
>
> *[Tools used: Bash — Show the unexpected change to accounts views]*
>
> Phase 2 is done and the full test suite passes: **270 tests** (254 before, minus the old "coupon is ignored" test, plus 17 new ones). Ruff format and lint are clean, and the migration matches the models. Nothing is committed.
>
> **What changed:**
> - **`orders/models.py`:**
>   - `Order` has six new fields. `subtotal` and `discount_amount` hold the numbers. `coupon_code`, `coupon_percent_off` and `coupon_product_name` are the frozen copy of the coupon, and `coupon` is the link to the coupon itself, which becomes empty if the coupon is deleted.
>   - `Order.save()` fills in a missing `subtotal` as `total + discount_amount`. That's why the seed and the existing test fixtures didn't need changes.
> - **`orders/migrations/0004_order_coupon_snapshot.py`:** I wrote this by hand so existing orders get their real `subtotal` instead of a placeholder.
> - **`orders/services.py`:** `place_order` now uses `coupon_code`. It looks the code up (ignoring capitals), applies the discount, saves the frozen copy, and sets `total = subtotal − discount`. A blank code means full price. A bad code places no order and leaves the cart as it was.
>
> **Two choices I made that weren't spelled out in the plan:**
> 1. **`CouponError` is now a kind of `ValueError`.** The plan said to convert one into the other. This gets the same result with less code: anything that catches `place_order`'s existing errors catches coupon errors too.
> 2. **The automatic `subtotal` in `Order.save()`.** The alternative was editing four test files and the seed command to supply it.
>
> **What the new tests check:** full price with no coupon or a blank one, order-wide and product discounts, the frozen copy on the order, each of the four rejection messages leaving no order and the cart intact, and the automatic `subtotal`. The most important group covers your third requirement. Retiring, editing or deleting the coupon after an order is placed, or renaming the discounted product, leaves that order's numbers and receipt details unchanged.
>
> **Checks outside the test suite:** I ran the migration on a *copy* of your local database. All 54 existing orders got `subtotal = total`, and none were given a discount. Re-seeding the copy also worked, producing 52 orders, all with correct subtotals. I deleted the copy afterwards, so your real database hasn't been migrated yet. Run `uv run python manage.py migrate` when you're ready.
>
> **One unexpected change in your working tree:** `git status` shows `accounts/views.py` as modified. In Phase 1, `ruff format .` added one missing blank line between two classes in that file. It was already in your last commit unformatted, and has nothing to do with coupons. You can keep it as a separate small commit, or undo it with `git checkout accounts/views.py`.
>
> Phase 3 adds the coupon box and the "Apply" preview to the checkout page.

**User** · Nov 8, 2026, 12:06 AM

> Start Phase 3 of plans/coupons.md. Follow CLAUDE.md, run the required tests, and report the results before proceeding to Phase 4. Do not commit anything yet. Leave unrelated files unchanged.

**Claude** · Nov 8, 2026, 12:06 AM

> I'll read the checkout form, the checkout template, the existing HTMX partial pattern and the checkout tests before changing anything.
>
> *[Tools used: Bash — Read checkout form, template, and partials; Bash — Survey existing checkout form and view tests]*
>
> Let me check how the site's existing HTMX POST requests send the CSRF token, and whether the cart page already has an `oob_badge`-style pattern I can reuse.
>
> *[Tools used: Bash — Check HTMX CSRF setup, OOB pattern, and checkout tests; Edit — `orders/models.py`; Edit — `orders/models.py`; Bash — Add dataclass import to orders models]*
>
> Now the form. Its docstring promises "no `clean_*` methods", so I'll update that to explain the one exception.
>
> *[Tools used: Edit — `orders/forms.py`; Edit — `orders/forms.py`; Edit — `orders/forms.py`; Edit — `orders/views.py`; Edit — `orders/views.py`; Edit — `orders/views.py`; Edit — `orders/views.py`; Edit — `orders/urls.py`; Write — `templates/orders/partials/_order_summary.html`]*
>
> Now the checkout page template:
>
> *[Tools used: Edit — `templates/orders/checkout.html`; Edit — `templates/orders/checkout.html`; Edit — `templates/orders/checkout.html`; Edit — `templates/orders/checkout.html`; Write — `orders/test_checkout_coupons.py`]*
>
> Now I'll format **only the files I touched** this phase, so unrelated files stay as they are, and then run the full suite.
>
> *[Tools used: Bash — Format touched files, lint, check migrations, run full test suite]*

**Claude** · Nov 8, 2026, 12:14 AM

> *[Tools used: Bash — Read the declarative-form test, PRD rule, and login URL name]*
>
> *[Question dialog]* **Your PRD says CheckoutForm must have no clean_* methods (an existing test enforces this), but the coupon plan put clean_coupon_code on CheckoutForm. Checking a coupon needs the database and the customer's cart, so a simple field rule can't do it. How should Phase 3 resolve this?**
>
> - **Separate CouponForm (Recommended)** — A small CouponForm with its own clean_coupon_code checks the coupon. CheckoutForm stays exactly as the PRD describes and its test passes unchanged. The checkout view checks both forms. Both PRD promises still hold: a valid CheckoutForm plus a valid CouponForm always places an order. Costs a little more view code.
> - **Let place_order check it** — Keep a plain coupon_code field on CheckoutForm with no clean method. place_order rejects a bad coupon, and the view shows that error under the coupon box. Smallest change, but it breaks the PRD's other promise ('a valid form always results in a successful order'), because a form with a bad coupon would still count as valid.
> - **Change the PRD rule** — Keep clean_coupon_code on CheckoutForm as the plan says. Edit the PRD and the test so the one exception is allowed and documented. The plan stays as written, but the form is no longer a pure example of declarative validation.

**User** · Nov 8, 2026, 12:19 AM

> *[Answer chosen in the question dialog:]* **Separate CouponForm (Recommended)**

**Claude** · Nov 8, 2026, 12:19 AM

> *[Tools used: Bash — Restore CheckoutForm file to its committed state; Bash — Add CouponForm below the untouched CheckoutForm]*
>
> Now the checkout view validates both forms:
>
> *[Tools used: Read — `orders/views.py`; Read — `orders/views.py`; Edit — `orders/views.py`; Edit — `orders/views.py`; Edit — `orders/views.py`; Bash — Point checkout template at the coupon form]*
>
> One quick fix in the view: `kwargs.get("coupon_form") or ...` depends on a form object always counting as "truthy". An explicit `None` check is clearer.
>
> *[Tools used: Edit — `orders/views.py`; Read — `orders/test_checkout_coupons.py`; Bash — Rewrite form tests for CouponForm and fix the login URL name; Bash — Format touched files, lint, and rerun the full suite]*
>
> All **304 tests** pass. Let me confirm that only files belonging to this phase were touched.
>
> *[Tools used: Bash — Show working tree changes; Edit — `plans/coupons.md`; Edit — `plans/coupons.md`; Edit — `plans/coupons.md`]*
>
> Phase 3 is done and the full test suite passes: **304 tests** (270 before, plus 34 new). Ruff lint is clean, I formatted only the files I touched, and there are no new migrations. Nothing is committed, and I haven't started Phase 4.
>
> **Partway through, two tests failed:**
> 1. One of my new tests used the wrong login URL name. The site calls it `accounts:login`, and I've fixed the test.
> 2. An existing test enforces your PRD rule that `CheckoutForm` has no `clean_*` methods. My plan had broken it. You chose a separate `CouponForm`, so I restored `CheckoutForm` exactly as committed and built the coupon check as its own form. That existing test now passes unchanged. I also updated decision 6 and the Phase 3 tasks in `plans/coupons.md` so the plan matches the code.
>
> **What the customer gets:**
> - The checkout sidebar has a **Coupon code** box with an **Apply** button, just above the totals.
> - **Apply** previews the result without placing an order. The sidebar shows the subtotal, then either a discount line ("Coupon THOUGHTS10 (10% off) −$70.00") or the error message, then the new total. The amount on the **"Place order"** button updates to match.
> - **Place order** always sends whatever code is typed, even if the customer never clicked Apply, and the server checks it again. If the code is bad, no order is placed, everything they typed stays filled in, and the error is shown once. If the card is also wrong, both errors appear together.
> - If a coupon is retired between Apply and Place order, `place_order` catches it and the page explains why.
>
> **What changed:**
> - **`orders/forms.py`:** a new `CouponForm`. `CheckoutForm` is unchanged.
> - **`orders/models.py`:** `Cart.checkout_summary(code)` works out the subtotal, discount, total and any error message, for the page and the preview to display.
> - **`orders/views.py`:** `CheckoutView` checks both forms on every submit. The new `ApplyCouponView` handles the HTMX preview, accepts only POST and requires login.
> - **`orders/urls.py`:** a new URL, `orders:apply_coupon`.
> - **Templates:** `templates/orders/checkout.html` has the coupon box, and the new `templates/orders/partials/_order_summary.html` holds the summary.
>
> **What the 34 new tests in `orders/test_checkout_coupons.py` check:**
> - **`CouponForm`:** a blank code is allowed, codes ignore capitals, each of the four error messages appears, and `CheckoutForm` stays free of coupons.
> - **The summary:** totals with no code, a valid code and a bad code.
> - **The Apply preview:** login required, POST only, it returns the summary snippet rather than a whole page, it updates the button total, and it never places an order.
> - **Checkout:** a valid code places a discounted order, a blank code places a full-price order, and each bad code places none and keeps what was typed. Card and coupon errors appear together, and both backstop paths show their error.
>
> **Not checked yet:** the tests confirm the server returns the right HTML, but I haven't clicked through the page in a real browser. In particular, I haven't watched the Apply button pick up the typed code. The plan's manual check uses the seeded coupons, which arrive in Phase 5. To try it sooner:
> 1. Run `uv run python manage.py migrate`.
> 2. Create `THOUGHTS10` in `/admin/`.
> 3. As `customer`, apply it at checkout.
>
> I can also drive the browser and check it myself if you'd like.
>
> Phase 4 shows the discount on the confirmation page, the order history pages and the back-office order screens.

**User** · Nov 8, 2026, 12:23 AM

> Start Phase 4 of plans/coupons.md. Follow CLAUDE.md, run all required tests, and report the results before proceeding to Phase 5. Do not commit anything yet. Leave unrelated files unchanged.

**Claude** · Nov 8, 2026, 12:23 AM

> I'll read the three order pages that need the receipt summary.
>
> *[Tools used: Bash — Read order display templates; Bash — Locate the Order.number property; Bash — Add has_discount property and the receipt summary partial]*
>
> Now I'll add the partial to the three pages, just above each page's total:
>
> *[Tools used: Edit — `templates/orders/confirmation.html`; Edit — `templates/orders/order_detail.html`; Edit — `templates/orders/manage_order_detail.html`; Edit — `orders/admin.py`]*
>
> Now the tests:
>
> *[Tools used: Write — `orders/test_receipts.py`; Bash — Format touched files, lint, check migrations, run full suite]*

**User** · Nov 8, 2026, 12:24 AM

> *[Rejected the tool call above; it did not run.]*
>
> [Request interrupted by user for tool use]

**User** · Nov 8, 2026, 7:47 PM

> Resume Phase 4 of plans/coupons.md. The previous session was interrupted while writing orders/test_receipts.py. First inspect the existing changes so you don't duplicate work. Complete Phase 4, follow CLAUDE.md, and run the required tests. Report the results before proceeding to Phase 5. Do not commit anything yet, and leave unrelated files unchanged.

**Claude** · Nov 8, 2026, 7:47 PM

> I'll check what's already on disk before doing anything else.
>
> *[Tools used: Bash — Inspect Phase 4 changes already on disk; Bash — Show the end of the receipts test file]*
>
> The file is complete, so nothing needs rewriting. Now the step that was interrupted: format only this phase's Python files, lint, check migrations, and run the full suite.
>
> *[Tools used: Bash — Format Phase 4 files, lint, check migrations, run full suite]*

**Claude** · Nov 8, 2026, 7:52 PM

> Phase 4 is done and the full test suite passes: **322 tests** (304 before, plus 18 new). Ruff lint is clean, formatting changed nothing, and there are no new migrations. Nothing is committed, and Phase 5 hasn't started.
>
> **Resuming:** all of the interrupted session's code and its test file were already complete on disk. The only thing cut off was the test run, so I ran it without rewriting anything.
>
> **What changed:**
> - **The order model:** `Order.has_discount` is a new property that's true when a coupon took money off.
> - **A new receipt partial**, `templates/orders/partials/_receipt_summary.html`, shows "Subtotal" and a coupon line such as "Coupon THOUGHTS10 (10% off) −$70.00" or "Coupon SERAPHINE50 (50% off Seraphine Home Hub) −$349.99". It reads only the copy saved on the order, never the live coupon.
> - **Three pages show it** just above the total: the **confirmation** page, the **customer's order detail**, and the **back-office order detail**.
> - **Orders without a coupon look exactly as before.** The breakdown only appears when there's a discount.
> - **`OrderAdmin`** now lists each order's `coupon_code`.
> - **The order list pages are unchanged.** Their "Total" column already shows the amount actually charged.
>
> **What the 18 new tests in `orders/test_receipts.py` check**, mostly run against all three order pages:
> - order-wide and product discounts are shown
> - orders with no discount show no breakdown
> - a receipt still shows correctly after its coupon is deleted, which backs your rule that retiring a coupon never changes past orders
> - a receipt ignores later edits to the coupon (changing it to 50% and retiring it still shows "10% off −$70.00")
> - the order history shows the charged total
> - the admin list shows the code
>
> **One small difference from the plan's wording:** the plan described the product coupon line as "Coupon SERAPHINE50 — 50% off Seraphine". The receipts use the same format as the checkout summary from Phase 3, "Coupon SERAPHINE50 (50% off Seraphine Home Hub)", so customers see identical wording before and after paying.
>
> **Unrelated files:** none were touched this phase. `accounts/views.py` still has only the one-line formatting change from Phase 1.
>
> **Not checked yet:** as with Phase 3, the tests check the HTML the server returns, but I haven't looked at the pages in a browser.
>
> Phase 5 is next: the back-office Coupons tab, the four seed coupons, and the `CLAUDE.md` and `PROMPTS.md` updates.

**User** · Nov 8, 2026, 7:54 PM

> Start Phase 5 of plans/coupons.md. Follow CLAUDE.md and implement the back-office Coupons tab and four sample coupons. Run all required tests and report the results. Do not commit anything yet. Do not reset existing database data or run the seed command without asking me first. Leave unrelated files unchanged.

**Claude** · Nov 8, 2026, 7:55 PM

> I'll start by reading the existing product back-office code, since the Coupons tab should copy its patterns.
>
> *[Tools used: Bash — Read product back-office views, forms, URLs, and staff mixin; Bash — Read back-office shell and product management templates; Bash — Survey seed command structure, PROMPTS.md tail, and back-office tests]*
>
> Let me look at the seed command's main flow and the start of `PROMPTS.md`, which records entries newest-first.
>
> *[Tools used: Bash — Read seed flow, PROMPTS.md format, and back-office test setup; Bash — Check product URL patterns, field partial, and available manager; Edit — `orders/models.py`; Bash — Add the ManageCouponForm back-office form; Edit — `orders/models.py`; Edit — `orders/views.py`; Bash — Check view imports and file tail; Bash — Add coupon management views and URLs]*
>
> Now the templates and the new tab:
>
> *[Tools used: Write — `templates/orders/manage_coupons.html`; Write — `templates/orders/manage_coupon_form.html`; Edit — `templates/backoffice/base.html`; Bash — Add coupons to the seed command code without running it; Bash — Find the stale lines in CLAUDE.md; Bash — Show the deep-modules paragraph in CLAUDE.md; Bash — Update the two stale CLAUDE.md lines about coupons]*
>
> Line 40 runs past the file's wrapping width, so I'll rewrap that paragraph:
>
> *[Tools used: Edit — `CLAUDE.md`; Write — `orders/test_backoffice_coupons.py`]*
>
> Now I'll format only this phase's Python files, lint, check migrations, and run the full suite:
>
> *[Tools used: Bash — Format Phase 5 files, lint, check migrations, run full suite; Read — `orders/test_receipts.py`; Edit — `orders/test_receipts.py`; Bash — Rerun lint and the full suite after the test fix]*

**Claude** · Nov 8, 2026, 8:01 PM

> All **345 tests** pass. One final check of the working tree:
>
> *[Tools used: Bash — Show working tree and Phase 5 non-orders changes]*
>
> Phase 5 is implemented and the full test suite passes: **345 tests** (322 before, plus 23 new). Ruff lint is clean and there are no new migrations. Nothing is committed. **I haven't run the seed command or touched your database**, so the four sample coupons exist only in the seed code so far.
>
> **The Coupons tab** sits between Orders and Dashboard in the back office:
> - **List:** each coupon shows its code, discount, "Applies to" (a product or "Whole order"), its expiry (or "Never"), and an **Active / Expired / Retired** badge. An empty store shows a "No coupons yet" screen.
> - **Add and Edit:** the code is saved in uppercase. A duplicate in any capitalization ("thoughts10") shows a form error. The percentage must be 1–100. The product menu lists available products plus "Whole order".
> - **Retiring:** edit the coupon and switch off "Active". There's deliberately no delete.
> - **What changed:** the form is `ManageCouponForm` in `orders/forms.py`, the screens are three views in `orders/views.py` with matching URLs, and there are two new templates plus the tab in `templates/backoffice/base.html`. The model also has a new `Coupon.status` property for the badges.
>
> **Sample coupons in the seed:** `THOUGHTS10` (10% off the whole order), `SERAPHINE50` (50% off Seraphine), `SUMMER25` (expired 60 days before the seed runs) and `LEAKED20` (retired). No seeded orders use them. I also fixed a crash the seed would otherwise have hit: it now deletes coupons *before* products. Without that, `SERAPHINE50` would block Seraphine from being deleted on the second seed run.
>
> **One test failure along the way:** my Phase 4 receipt test checked that the word "Coupon" never appears on a page for an order without a discount. The new "Coupons" tab broke that assumption. I changed the test to look for the actual breakdown text ("Coupon ", "% off", "−$"). The app itself was fine.
>
> **What the 23 new tests in `orders/test_backoffice_coupons.py` check:**
> - **Access:** anonymous visitors are sent to login, customers get 403, and staff get the page. There's no delete URL.
> - **The tab and list:** the tab appears and highlights correctly, the empty state shows, and each status badge is right.
> - **Create and edit:** creating, editing and retiring all work. Retiring a coupon from the staff screen leaves an already-placed order's $629.98 total unchanged.
> - **The form's rules:** the percentage bounds, duplicate codes, the required code, and the product menu all behave as described.
>
> **Other files:**
> - **`CLAUDE.md`:** I updated the two lines that still called the coupon seam "dormant", since that would mislead future sessions.
> - **`PROMPTS.md`:** not touched. It says entries are added only when you ask with the logging prompt, even though the plan listed it.
> - **Unrelated files:** none changed. `accounts/views.py` still has only the Phase 1 formatting change.
>
> **Still to do:**
> 1. **Try the seed safely:** I can run it against a throwaway copy of your database in the scratchpad and confirm the four coupons are created and that seeding twice works. That's the one seed path no test covers, since tests never run the seed. Your real database wouldn't be touched. Should I go ahead?
> 2. **The plan's manual check:** this needs the coupons in your real database, which means either running the seed yourself or creating them in the Coupons tab. Then sign in as `employee`, retire `THOUGHTS10`, check that checkout rejects it, and check that a past order that used it is unchanged.

**User** · Nov 8, 2026, 8:05 PM

> Yes. Test the seed command against a temporary copy of my database only. Verify that all four coupons are created correctly and that running the seed twice doesn't cause problems. Do not modify or reset my real database. Report the results and stop. Do not commit anything yet.

**Claude** · Nov 8, 2026, 8:05 PM

> I'll use the same approach as in Phase 2: copy the database into the scratchpad and point Django at the copy through a temporary settings file. First I'll record a checksum of your real database, so I can prove afterwards that it wasn't touched.
>
> *[Tools used: Bash — Checksum the real database, make a scratch copy, confirm the copy is in use; Bash — Write verification script and migrate the scratch copy; Bash — Run the seed twice on the copy and verify after each run]*
>
> Both runs passed every check. Last step: confirm your real database is byte-for-byte unchanged, then delete the scratch copy.
>
> *[Tools used: Bash — Verify real database checksum is unchanged and delete the scratch copy]*
>
> The seed works on a copy of your database: all four coupons are created correctly, and running it twice causes no problems. Your real database is untouched and nothing is committed.
>
> **Your real database:**
> - Its SHA-256 checksum is the same before and after (`37918a1c…c562`), and its size and timestamp haven't changed.
> - It still has migration `0004` unapplied, exactly as before.
> - All the work happened on a copy in the scratchpad, which I've deleted.
>
> **Seed runs on the copy:** first I applied migration `0004` to the copy, since it was missing there too. Both seed runs then completed and printed the same summary: "Seeded 6 categories, 12 tags, 34 products, 12 users, 52 orders, **4 coupons**, and a live cart for 'customer'."
>
> **Coupon checks**, all passing after both runs:
>
> | Code | Discount | Applies to | Expiry | Status |
> |---|---|---|---|---|
> | `THOUGHTS10` | 10% | Whole order | Never | Active |
> | `SERAPHINE50` | 50% | Seraphine | Never | Active |
> | `SUMMER25` | 25% | Whole order | Sep 10, 2026 (60 days before the seed ran) | Expired |
> | `LEAKED20` | 20% | Whole order | Never | Retired |
>
> None of the 52 seeded orders uses a coupon, as the plan intended.
>
> **Checkout behavior:** I used a temporary cart that was rolled back afterwards, so nothing was saved even in the copy.
> - `THOUGHTS10` on a $99.00 Calm Collar takes off **$9.90**.
> - `SERAPHINE50` without Seraphine in the cart says "SERAPHINE50 applies only to Seraphine, which isn't in your cart."
> - `SERAPHINE50` with Seraphine ($249.00) in the cart takes off **$124.50**.
> - `SUMMER25` says "The coupon SUMMER25 expired on Sep 10, 2026."
> - `LEAKED20` says "The coupon LEAKED20 is no longer available."
>
> **Running it twice:** the second run is the one that would have crashed before I fixed the wipe order, because `SERAPHINE50` already existed and protects Seraphine from deletion. It finished normally and produced the same four coupons with new IDs (5–8 instead of 1–4), so the old rows were replaced rather than duplicated.
>
> **Things to know before using it on your real database:**
> - You'll need to run `uv run python manage.py migrate` first, then `uv run python manage.py seed`.
> - The seed is destructive: it wipes the demo data, and now that includes any coupons you've created yourself.
> - The `SUMMER25` expiry date depends on when the seed runs, so its message will show a different date each time.
>
> I've stopped here.

**User** · Nov 8, 2026, 8:37 PM

> Review the completed discount coupon implementation against plans/coupons.md and the Homework 4 requirements. Identify 2-3 meaningful improvements we could make after the initial feature commit. Explain each in beginner-friendly language.
>
> Do not modify any files, run the seed command, or commit anything yet. Report your findings and stop.

**Claude** · Nov 8, 2026, 8:37 PM

> I'll start by looking for a written Homework 4 spec in the repo, and re-read the plan's requirements section.
>
> *[Tools used: Bash — Search for a Homework 4 spec and show the plan's requirements; Bash — Probe admin duplicate-code handling in a throwaway test, then clean up]*
>
> The probe didn't run: pytest-django looked for the project in the wrong folder. Your database is still unchanged (checksum OK). I'll retry with the Python path set explicitly.
>
> *[Tools used: Bash — Rerun the admin probe with explicit Python path, then clean up]*
>
> I reviewed the code against the plan and your four requirements. **All four requirements are met and tested.** Below are three improvements worth making after the first commit. The first is a real bug I confirmed with a throwaway test. Nothing in your project or database changed: the test ran in pytest's temporary database, your real database's checksum is unchanged, and the probe file is deleted.
>
> ## Requirements check
>
> | Requirement | Met? | Proven by |
> |---|---|---|
> | 1. Customers enter a code at checkout and get a discount | Yes | `orders/test_checkout_coupons.py` (preview, discounted checkout) |
> | 2. Expired coupons are rejected with a clear message | Yes | "The coupon SUMMER25 expired on Oct 31, 2025." is tested in the model, the form, the preview and the checkout page |
> | 3. Retiring a coupon never changes past orders | Yes | Tests cover retiring, editing and deleting the coupon, and retiring it from the staff screen; the order's numbers and receipt stay the same |
> | 4. Order-wide and product-specific discounts | Yes | THOUGHTS10 and SERAPHINE50 are tested through the math, checkout, receipts and seed |
>
> ## Improvement 1: The Django admin crashes on a duplicate code typed in lowercase (confirmed bug)
>
> **What happens:** if `THOUGHTS10` exists and someone adds `thoughts10` in Django's built-in `/admin/`, the page crashes with a **500 Server Error** instead of saying "this code already exists." My probe test confirmed the 500, and no duplicate was saved.
>
> **Why:** the duplicate check runs *before* the code is uppercased. It looks for "thoughts10", finds nothing, and passes. Then `Coupon.save()` uppercases it to "THOUGHTS10", and the database rejects the duplicate with an error the form isn't set up to catch. The back-office Coupons tab doesn't have this bug, because `ManageCouponForm.clean_code` uppercases first. The admin uses Django's default form, which skips that step.
>
> **There are two related gaps in the admin**, which skips the rules the back office enforces:
> - The admin lets someone **delete** a coupon, even though the design says coupons are retired, never deleted.
> - `OrderAdmin` has no read-only fields, so an admin could hand-edit an order's `total` or `discount_amount` and break the rule `total = subtotal − discount`. That works against requirement 3: a placed order is supposed to be frozen.
>
> **The fix (small):**
> - Have `CouponAdmin` use `ManageCouponForm`.
> - Turn off deleting in the admin.
> - Make the order's money and coupon fields read-only in `OrderAdmin`.
> - Add a test for each.
>
> ## Improvement 2: Pressing Enter in the coupon box places the order
>
> **What happens:** a customer types `THOUGHTS10` and presses **Enter**, expecting it to work like "Apply". The coupon box belongs to the checkout form (through `form="checkout-form"`), and in a browser, Enter in a form's text box submits that form. If the address and card are already filled in, **the order is placed immediately**.
>
> **Why it matters:** the whole point of decision 6 was that customers see the final price before paying. They'd never pay *more* than the button showed, because a bad code blocks the order. But a customer who just wanted to check a code would be surprised to find they'd placed an order.
>
> **Caveat:** this comes from how browsers handle forms, not from a test. Server-side tests can't press keys, and I haven't tried it in a real browser.
>
> **The fix (medium):**
> - Give the coupon box its own small HTMX form, so Enter means "Apply".
> - When a code applies, the summary snippet includes a hidden copy of it that belongs to the checkout form, so "Place order" still sends it.
>
> The trade-off is that a code typed but never applied wouldn't be sent. The summary would need a hint like "Press Apply to use this code."
>
> ## Improvement 3: Expiry dates are in UTC, but the store is in Texas
>
> **What happens:** `TIME_ZONE = "UTC"` in `config/settings.py`. Say staff want a coupon to end at 11:59 PM on Oct 31, Texas time. That moment is **5:59 AM on Nov 1 in UTC**. So staff have to convert times themselves (the form says "Expires at (UTC)"), and the expired message tells customers "expired on **Nov 1**" when the store means Oct 31.
>
> **Why it matters:** requirement 2 asks for a *clear* error message, and a date that's off by one day isn't clear.
>
> **The fix (small change, but worth testing):** set `TIME_ZONE = "America/Chicago"`. Django still *stores* every time in UTC; the setting only changes how times are shown and how typed-in times are read.
>
> The catch is that it applies to the whole site, so order dates and the dashboard's grouping by day would also move to Texas time. That's probably what you want, but tests that use fixed dates would need checking.
>
> ## Also worth mentioning
>
> The Coupons tab doesn't show **how many orders used each coupon**. That's a useful number for staff, and an easy addition later: count orders by their saved `coupon_code`.
>
> ## My recommendation
>
> Do **Improvement 1** first, right after the feature commit. It's a confirmed crash with a small, well-understood fix. Improvement 2 is the biggest experience issue for customers, and Improvement 3 is a one-line setting that needs a careful test run. I haven't changed anything; tell me which ones to do.

**User** · Nov 8, 2026, 8:39 PM

> Before the first Homework 4 commit, review git status and git diff. Confirm which files belong to the completed coupon feature, identify any unrelated changes, and run the full test suite.
>
> Do not fix the improvements yet. Do not run the seed command. Do not modify files or commit anything. Report the results and stop.

**Claude** · Nov 8, 2026, 8:39 PM

> *[Tools used: Bash — Show git status, diff summary, untracked files, and suspect diffs; Bash — Scan the full diff for unrelated hunks, debug code, and removed lines; Bash — Run lint, format check, migration check, system check, and full test suite; Bash — Confirm the real database checksum and that git status is unchanged; Bash — Inspect the real database read-only to explain the checksum change]*
>
> I've found the cause, and it's nothing to worry about. **The database changed because you used the app, not because of anything I ran.** The evidence, read in read-only mode:
> - Migration `0004` is now applied. I only ever applied it to scratch copies.
> - There are 4 coupons, but they aren't the seed's set: `SPRING20` exists, `LEAKED20` doesn't, and all 56 orders are still there. So the seed wasn't run; these were created by hand.
> - `employee` signed in at 8:14 PM your time. Two new orders were placed at 8:24 PM and 8:30 PM: **$89.10** (a $99.00 item with THOUGHTS10's 10% off) and **$124.50** (Seraphine at $249.00 with SERAPHINE50's 50% off). `THOUGHTS10` is now **retired**. The file was last modified at 8:37 PM.
>
> That's the plan's manual check: create coupons, place discounted orders, retire `THOUGHTS10`. All my commands in this review only read the database (`check`, `makemigrations --check`, `showmigrations`), and pytest uses its own separate test database.
>
> ## Results
>
> All checks pass, and no files were modified or committed:
>
> | Check | Result |
> |---|---|
> | `uv run pytest` | **345 passed** |
> | `ruff check .` | All checks passed |
> | `ruff format --check .` | 58 files already formatted |
> | `makemigrations --check` | No changes detected (models and migrations match) |
> | `manage.py check` | No issues |
> | `git diff --check` | No whitespace errors or conflict markers |
> | Diff scan | No debug prints, TODOs or secrets; every removed line is a coupon-related replacement |
>
> ## Files in the coupon feature (26)
>
> **Changed (15):**
> - `orders/`: `models.py`, `services.py`, `forms.py`, `views.py`, `urls.py`, `admin.py`, `test_services.py`
> - `conftest.py` (the coupon fixtures)
> - `products/management/commands/seed.py` (the sample coupons and the wipe-order fix)
> - Templates: `templates/backoffice/base.html` (Coupons tab), `templates/orders/checkout.html`, `confirmation.html`, `order_detail.html`, `manage_order_detail.html`
> - `CLAUDE.md` (the two stale "dormant seam" lines)
>
> **New (11):**
> - Migrations: `orders/migrations/0003_coupon.py`, `0004_order_coupon_snapshot.py`
> - Tests: `orders/test_coupons.py`, `test_checkout_coupons.py`, `test_receipts.py`, `test_backoffice_coupons.py`
> - Templates: `templates/orders/manage_coupons.html`, `manage_coupon_form.html`, `partials/_order_summary.html`, `partials/_receipt_summary.html`
> - `plans/coupons.md`
>
> ## Unrelated changes (1)
>
> - **`accounts/views.py`:** one added blank line between two classes. `ruff format .` added it back in Phase 1. It's a valid formatting fix (your committed file was missing it), but it has nothing to do with coupons. You can leave it out of the coupon commit and commit it separately as something like "Format accounts views", or undo it with `git checkout accounts/views.py`.
>
> ## Two minor notes
>
> - **Line-ending warnings** ("LF will be replaced by CRLF") on three files are Git on Windows converting line endings. They're harmless and don't affect the diff.
> - **Nothing is staged yet.** For the coupon commit, stage the 26 files above by name rather than using `git add .`, so `accounts/views.py` stays out.
>
> I've stopped here.

**User** · Nov 8, 2026, 8:43 PM

> Stage only the 26 files identified in your review as belonging to the completed Homework 4 coupon feature. Do not stage accounts/views.py or any unrelated changes.
>
> Create the first commit with the message "Add discount coupon feature".
>
> After committing, show me the commit hash and git status. Do not push yet, do not implement any improvements, and do not modify any other files.

**Claude** · Nov 8, 2026, 8:43 PM

> I'll stage exactly the 26 files by name, then check what's staged before committing.
>
> *[Tools used: Bash — Stage the 26 coupon feature files and verify the staged set]*
>
> Exactly 26 files are staged, and `accounts/views.py` is the only file left unstaged. Committing now:
>
> *[Tools used: Bash — Create the coupon commit and show its hash and git status]*
>
> The coupon feature is committed locally and hasn't been pushed.
>
> **Commit:** `63ea2e85d158d2fa700c9d2ba53b85c658283bc1` (short form `63ea2e8`)
> - **Message:** "Add discount coupon feature". I added a `Co-Authored-By: Claude` line below it, which is the standard attribution for commits I create.
> - **Contents:** exactly the 26 coupon files: 26 files changed, 2,151 insertions, 35 deletions.
>
> **`git status`:**
> ```
> On branch main
> Your branch is ahead of 'origin/main' by 1 commit.
>   (use "git push" to publish your local commits)
>
> Changes not staged for commit:
> 	modified:   accounts/views.py
> ```
>
> `accounts/views.py` was left out as you asked, and it still has its one-line formatting change, uncommitted. No other files were changed and none of the improvements were started.

**User** · Nov 8, 2026, 8:44 PM

> Implement Improvement 1 from your Homework 4 coupon code review: the confirmed crash you identified.
>
> First explain the cause of the crash. Then make the smallest appropriate fix and add an automated regression test that would have caught the problem.
>
> Run the relevant tests and full test suite. Report the results and explain the fix in beginner-friendly language.
>
> Do not commit or push anything yet. Leave accounts/views.py and all unrelated files unchanged.

**Claude** · Nov 8, 2026, 8:44 PM

> ## What causes the crash
>
> Coupon codes are case-insensitive. The app enforces that by uppercasing every code inside `Coupon.save()` (`orders/models.py`). The problem is **when** that happens. When someone submits a form in Django's admin, these steps run in order:
>
> 1. **Validate the form**, including the uniqueness check: "Is there already a coupon with this code?"
> 2. **Save** the coupon, which is where `save()` uppercases the code.
>
> Typing `thoughts10` while `THOUGHTS10` exists goes like this:
> - **Step 1** searches for `thoughts10`. SQLite compares text with case sensitivity, so it finds nothing, and validation passes.
> - **Step 2** uppercases the code to `THOUGHTS10`, and the database's `unique` rule rejects the insert. That raises an `IntegrityError`, which the form isn't designed to handle, so the page crashes with a **500 error**.
>
> The back-office Coupons tab doesn't crash, because `ManageCouponForm.clean_code` uppercases the code during step 1. The admin uses Django's default form, which doesn't have that method.
>
> **The smallest correct fix** is to move the uppercasing *into validation* at the model level. Django calls a model's `clean()` method during step 1, right before the uniqueness check. Adding the uppercasing there fixes the admin, and any other form built on the `Coupon` model gets the fix automatically.
>
> First I'll write the regression tests and **watch them fail** against the current code, which shows they really catch this bug. Then I'll apply the fix.
>
> *[Tools used: Bash — Check test imports and Coupon.save location; Bash — Add regression tests and run them against the unfixed code; Edit — `orders/models.py`; Bash — Run the regression tests and all coupon-related tests]*
>
> All four regression tests pass now, along with all 133 coupon-related tests. Next, lint, a format check on the two touched files, the migration check, and the full suite:
>
> *[Tools used: Bash — Format check, lint, migration check, full suite, and git status; Edit — `orders/models.py`; Bash — Recheck lint, rerun regression tests and full suite, show git status]*

**Claude** · Nov 8, 2026, 8:48 PM

> I fixed the admin crash: typing a lowercase version of an existing coupon code now shows an error message on the form instead of crashing the page. The full test suite passes (**349 tests**: the 345 from before plus 4 new ones). Nothing is committed or pushed.
>
> ## Why it crashed
>
> Coupon codes ignore capital letters, so the app stores them all in uppercase. That uppercasing only happened at the moment of **saving**. Django's admin works in two steps:
>
> 1. **Check the form.** One check is "does a coupon with this code already exist?"
> 2. **Save it.**
>
> If `THOUGHTS10` already exists and you type `thoughts10`, step 1 looks for `thoughts10`, finds nothing, and lets it through. Step 2 then uppercases it to `THOUGHTS10`, and the database refuses to store a second coupon with that code. The form had no way to handle that refusal, so the page crashed with a "500 Server Error."
>
> ## The fix
>
> I added a `clean()` method to the `Coupon` model in `orders/models.py`, which uppercases the code. Django runs `clean()` during step 1, right before the duplicate check. Now the check compares `THOUGHTS10` to `THOUGHTS10`, catches the duplicate, and shows Django's normal message: **"Coupon with this Code already exists."**
>
> Because the fix is in the model rather than in one form, every form built on `Coupon` gets it, including the Django admin. `save()` still uppercases too, as a safety net for code that creates coupons directly, such as the seed and tests.
>
> The fix is 11 lines in `orders/models.py`, and only one line inside `clean()` does the work. I also moved `clean()` below `save()` because ruff requires Django's standard method order.
>
> ## The regression tests
>
> I added four tests to `orders/test_coupons.py`. I ran them **before** fixing anything, and the admin test hit the same crash I had found in my review. That shows the tests really catch this bug.
>
> | Test | Before the fix | After |
> |---|---|---|
> | Admin rejects `thoughts10` when `THOUGHTS10` exists, with no crash | Crashed (500) | Passes |
> | The model's validation uppercases the code | Failed | Passes |
> | The model's validation rejects a duplicate typed in another case | Failed | Passes |
> | Admin still adds a new code (`spring20` is saved as `SPRING20`) | Passed | Passes |
>
> The last row was already passing; it's there to make sure the fix doesn't break normal adding.
>
> ## Checks
>
> | Check | Result |
> |---|---|
> | The 4 new tests | 4 passed |
> | All coupon-related test files | 133 passed |
> | Full suite | **349 passed** |
> | `ruff check .` | All checks passed |
> | `ruff format --check` on both changed files | Already formatted |
> | Migrations | No changes needed (a `clean()` method doesn't change the database) |
>
> ## Files
>
> `git status` shows two changed files from this fix, `orders/models.py` and `orders/test_coupons.py`. `accounts/views.py` still has its old formatting change; I didn't touch it.
>
> ## Not fixed yet
>
> Two smaller admin issues from the same part of the review are still open: the admin can delete coupons, and admins can edit an order's money fields. You asked only for the crash, so I left both alone.

**User** · Nov 8, 2026, 8:52 PM

> Stage only the files changed for Improvement 1 (the duplicate coupon code admin crash fix and its regression tests).
>
> Create the second commit with the message "Fix duplicate coupon code admin crash".
>
> Do not include accounts/views.py or unrelated changes.
>
> After committing, report the commit hash and git status. Do not push yet or make any additional changes.

**Claude** · Nov 8, 2026, 8:52 PM

> *[Tools used: Bash — Stage the two Improvement 1 files and verify the staged set]*
>
> Only the two fix files are staged, and `accounts/views.py` stays unstaged. Committing:
>
> *[Tools used: Bash — Create the fix commit and show hash, history, and git status]*
>
> The crash fix is committed as the second commit, and nothing has been pushed.
>
> **Commit:** `244c92e1afb74f0e282ce2386a598a482dd6aa20` (short form `244c92e`)
> - **Message:** "Fix duplicate coupon code admin crash", with the same `Co-Authored-By: Claude` line as the first commit.
> - **Contents:** only the two files from the fix: `orders/models.py` (+11 lines) and `orders/test_coupons.py` (+54 lines).
>
> **Recent history:**
> ```
> 244c92e Fix duplicate coupon code admin crash
> 63ea2e8 Add discount coupon feature
> cc887d9 Improve saved addresses page heading
> ```
>
> **`git status`:**
> ```
> On branch main
> Your branch is ahead of 'origin/main' by 2 commits.
>   (use "git push" to publish your local commits)
>
> Changes not staged for commit:
> 	modified:   accounts/views.py
> ```
>
> `accounts/views.py` was left out and still has its one-line formatting change, uncommitted.

**User** · Nov 8, 2026, 8:55 PM

> Review PROMPTS.md and the available Claude Code session history for Homework 4.
>
> Append the Homework 4 interaction transcript to PROMPTS.md, preserving the existing entries from previous assignments.
>
> Include the /grill-me design interview, implementation phases, testing, code review, and duplicate coupon code crash fix.
>
> Do not invent or reconstruct missing conversation messages. Tell me if any session history is unavailable.
>
> Do not commit or push anything yet. Do not modify any files other than PROMPTS.md.

**Claude** · Nov 8, 2026, 8:55 PM

> I'll start by re-reading `PROMPTS.md` in full to see its format rules and existing entries, and by checking what Claude Code session files exist on disk for this project.
>
> *[Tools used: Bash — Outline PROMPTS.md and list Claude Code session files for this project; Bash — Check whether the other recent session contains coupon work; Bash — Extract this session's user prompts and check for compaction; Read — `PROMPTS.md`; Edit — `PROMPTS.md`]*
>
> One sentence came out garbled ("Improvements 1's…"). I'll fix it, then confirm the old entry is byte-for-byte unchanged and that `PROMPTS.md` is the only file touched.
>
> *[Tools used: Edit — `PROMPTS.md`; Bash — Verify the old PROMPTS.md content is untouched and only PROMPTS.md changed]*
>
> I added the Homework 4 log to `PROMPTS.md`, and nothing else changed. Nothing is committed or pushed.
>
> **Where it went:** at the **top** of the log, above the Featured Products entry, because the file's rules say "New entries go at the top." The existing header and the Featured Products entry are byte-for-byte unchanged (I compared them against the committed version), and the diff is 193 lines added, 0 removed.
>
> **What the entry contains:** it follows the file's required shape (date heading, then Prompts, then Summary) and covers everything you listed:
> - **All 25 prompts, quoted exactly:**
>   - the `/grill-me` request and your 9 interview answers, each labeled with the question it answered so "A" or "B" makes sense on its own
>   - the five phase prompts, plus the Phase 4 resume
>   - your answer to my Phase 3 `CouponForm` question
>   - the Phase 4 interruption
>   - the seed test, the review, the pre-commit audit, both commit requests, the crash fix, and this request
> - **Outcome:** each phase's work with the test count after it (225 → 254 → 270 → 304 → 322 → 345 → 349), the seed test on a database copy, the review's findings, and both commits (`63ea2e8` and `244c92e`).
> - **Deviations:** you accepted every design recommendation and made one plan change (`CouponForm`). It also lists the choices I made on my own, and the improvements still open.
> - **Sideways:** the stray formatting change to `accounts/views.py`, the conflict with the PRD rule, the wrong login URL in a test, the interruption, the test that broke when the Coupons tab was added, the seed crash I caught before running it, the probe that failed to start, the database checksum change, and the method-order lint fix.
>
> **Session history:** **nothing for Homework 4 is missing.** All of it happened in this one Claude Code session, and its saved transcript on disk is complete: no parts were summarized away, and all 24 of your typed messages are there. The other two session files for this project cover earlier work (the address book and Featured Products), not coupons. Two limits:
> - **My replies aren't copied word for word.** The file's format records your prompts exactly and summarizes what I did. A full copy of my replies would be thousands of lines. If your assignment needs the complete back-and-forth, tell me and I'll think about how to include it.
> - **Your own testing outside this chat isn't in any session history.** You applied the migration, created coupons, placed two orders and retired THOUGHTS10. The entry mentions that only because I found it in the database during the pre-commit audit, and it says so; I didn't reconstruct any conversation for it.
>
> **Files:** `git status` shows `PROMPTS.md` (this entry) and `accounts/views.py` (its old one-line formatting change, untouched).

**User** · Nov 8, 2026, 8:57 PM

> Review the Homework 4 instructions and compare the PROMPTS.md entry you just added against the exact transcript requirement.
>
> Does the current entry fully satisfy the assignment, or does it require the complete back-and-forth conversation?
>
> Do not modify any files yet. Explain your findings and stop.

**Claude** · Nov 8, 2026, 8:57 PM

> I need the actual Homework 4 instructions to answer this, and my earlier search found no instruction file inside the project. I'll search the project's text files again for anything about transcripts, and look one level up in your course folder.
>
> *[Tools used: Bash — Search the repo and course folder for homework instructions; Bash — Measure the size of the full conversation text in this session]*
>
> I can't confirm the entry satisfies Homework 4, because I can't read the Homework 4 instructions: they aren't in the project or in your course folder. So the comparison has to go against the wording in your own prompts and in `PROMPTS.md`. On that evidence, **the entry probably falls short if the assignment asks for a transcript.**
>
> ## What the entry satisfies
>
> It follows the format `PROMPTS.md` itself defines: every prompt you gave, in order (including the interruption and your answer to my Phase 3 question), followed by a summary of the outcome, the deviations, and what went wrong.
>
> ## Why it probably isn't a "transcript"
>
> Your request asked me to "append the Homework 4 interaction transcript" and to include "the /grill-me design interview." A transcript normally means **both sides** of the conversation, and the entry only has your side.
>
> The `/grill-me` interview is where this matters most. The entry records your answers ("A", "B", "C") with a short bracketed label, but leaves out what an interview transcript would show:
> - my nine questions
> - the options for each and what each one gives up
> - my recommendation and the reason for it
>
> That's where the design reasoning lives, and it's probably what an instructor wants to see.
>
> It also leaves out every reply I gave during the phases, the review and the fix: what I found, what I asked, and what I reported.
>
> One smaller accuracy point: the entry says prompts are "quoted exactly." The words are exact, but I joined some multi-paragraph prompts into single paragraphs. A strict transcript would keep the original line breaks.
>
> ## Size of a complete transcript
>
> - **Your messages:** 25, about 800 words.
> - **My replies:** 66, about 10,400 words.
> - **Tool calls:** 138 (commands, file edits and test runs). Copying all of those, with their output, would add thousands of lines that are mostly noise.
>
> All of it is saved on disk, so **nothing would need to be reconstructed**. Your messages and my replies, about 11,000 words, can be exported directly.
>
> ## Options
>
> 1. **Keep the current entry.** This is enough if the assignment only asks for the prompts you gave, which is what the `PROMPTS.md` header describes.
> 2. **Add the full `/grill-me` exchange.** Each of my questions, its options and recommendation, and your answer. This fixes the biggest gap, at roughly 2,500 more words.
> 3. **Add the complete conversation:** every message from you and every reply from me, in order, exported from the saved session. Tool calls would be left out, but noted wherever they happened.
>
> **My recommendation:** check the exact wording in the Homework 4 instructions. If they say "transcript" or "complete conversation," choose **option 3**. If they only ask for "prompts," the current entry is fine, though **option 2** is still worth adding because the interview is the core of this assignment.
>
> I haven't changed anything. If you paste the assignment's transcript requirement here, I can tell you which option it calls for.

**User** · Nov 8, 2026, 8:59 PM

> Choose Option 3. Append the complete Homework 4 Claude Code conversation to PROMPTS.md, including my messages and your responses in chronological order.
>
> Use the actual saved session history. Do not invent missing messages. You may omit tool-call details, but indicate where tools were used.
>
> Preserve all previous assignment entries in PROMPTS.md.
>
> Do not modify any other files, commit, or push. Report what was added and whether any conversation history was unavailable.

## 2026-10-31 — Featured products: `is_featured` field and "Featured" badges

### Prompts
1. "Add an is_featured BooleanField to the Product model in products/models.py,
   with default=False. Do not add any badges or modify the templates yet. Only
   make the model change."
2. "Add a "Featured" badge to both the product catalog listing and the
   individual product detail page. The badge should only appear when a
   product's is_featured field is True. Use the existing Tailwind/DaisyUI
   styling and keep the changes limited to the necessary templates. Do not
   change the Product model or create any migrations."
3. "Create or update PROMPTS.md in the project root. Under today's date,
   document the prompts I gave you during this Featured Products homework
   session, including any corrections, what you changed, and the results.
   Include the model change, migration, Featured badges, and successful
   tests. Keep the newest session first if the file already exists. Do not
   modify any other files."
4. "Update only the Featured Products session entry in PROMPTS.md. Correct
   the summary to reflect that I marked Seraphine, SoulSear Mark II, and
   SoulSear Mark I as featured through Django Admin. I also discovered that
   Seraphine Doorbell was accidentally featured, unchecked it, and verified
   the correction. I confirmed the badges appeared in the catalog and on
   Seraphine's individual product page. Keep the original prompts and
   existing log entries intact. Do not modify any other files."

### Summary
- **Outcome:**
  - Model: added `is_featured = models.BooleanField(default=False)` to
    `Product` in `products/models.py`, directly after `is_available`.
  - Migration: the agent did not create one, as instructed. It suggested
    `makemigrations products` and `migrate`. Before the badge work, the
    agent confirmed that `products/migrations/0003_product_is_featured.py`
    already existed, created outside the agent's edits.
  - Badges: added `<span class="badge badge-secondary">Featured</span>`,
    shown only when `product.is_featured` is True, to
    `templates/products/catalog.html` (first in each card's badge row) and
    `templates/products/detail.html` (next to the stock badge, with
    `flex flex-wrap gap-2` added to the wrapper `div` for spacing).
  - Tests: `uv run pytest` passed, 164 tests.
  - Featured data (user, through Django Admin): marked Seraphine,
    SoulSear Mark II, and SoulSear Mark I as featured.
  - Manual verification (user): confirmed the "Featured" badge appears in
    the catalog and on Seraphine's product detail page.
  - Log: this entry added to `PROMPTS.md`.
- **Deviations:** none. No recommendations were overridden. The agent's
  offer to generate the migration in turn 1 was not taken up through the
  agent.
- **Sideways:** no agent-side failures. While setting featured products
  in Django Admin, the user found that Seraphine Doorbell had been featured
  by mistake, unchecked it, and verified the correction. The seed data
  doesn't set `is_featured`, so re-running `seed` will clear these choices.
  The first version of this summary said no products were featured. It was
  corrected in prompt 4.
