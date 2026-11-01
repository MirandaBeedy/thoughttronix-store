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
