# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**

`search_listings` scores by plain keyword overlap against listing text, not a
semantic match, so a phrasing that shares no words with the listing's title or
description can miss an item that's actually in the data. 4 of 5 leaves room
for that one phrasing mismatch without excusing a search that misses often.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**

This path doesn't depend on keyword phrasing lining up with real data — it only
requires that nothing scores above zero, which a query for an item that isn't
in the listings at all (e.g. "designer ballgown size XXS under $5") guarantees
every time. There's no fuzziness here the way there is in criterion 1, so it
should hold on every try.

---

## 3. Something about state

<!-- YOU WRITE THIS ONE.

     How would you know that the item your search found is the same item the
     next tool received? Name something countable or observable.

     This is the criterion people find hardest, because state failure doesn't
     look like state failure — it looks like a tool problem. Something that
     compares session["selected_item"] against what actually reached
     suggest_outfit is the shape you're after. -->

Across 5 different matching queries, the `id` of `session["selected_item"]`
matches the `id` of the item dict actually received by `suggest_outfit` and by
`create_fit_card` — 5 of 5 tries.

**Why this target:**

This is a plumbing check, not a model check — passing the same dict reference
along the session is deterministic code, not something the model's wording can
affect. If this ever fails, the bug is in `run_agent`'s wiring rather than in
any one tool, so there's no reason to expect it to vary between tries.

---

## 4. Something about the fit card

<!-- YOU WRITE THIS ONE.

     The fit card calls a model, so the same input can produce different words
     each time. That's not a bug — it's the nature of the tool. So what would
     make it acceptable?

     Think about what you'd actually be unhappy to see. A caption that never
     mentions the price? Two different items producing the same opening
     sentence? A card longer than a caption anyone would post? Any of those can
     be turned into a number. -->

For 5 different items, every fit card mentions the item's price and platform
at least once each and is 2 to 4 sentences long — 5 of 5 tries.

**Why this target:**

The model can vary its wording freely, and that's expected — but a caption
that drops the price or platform, or sprawls into a paragraph, has stopped
doing what a fit card is for. Those are things I can count regardless of which
words the model happens to pick, so 5 of 5 is fair even though the exact
sentences aren't.

## 5. Your choice

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. Speed, the empty
     wardrobe path, what happens when the model can't be reached, whether the
     search respects a price ceiling — anything, as long as it names a number
     or an observable outcome. -->

Run with `--empty-wardrobe`, `suggest_outfit` returns non-empty general
styling advice for the item — never an empty string, never an exception, and
never a sentence naming a specific wardrobe item that doesn't exist — 5 of 5
tries.

**Why this target:**

The empty wardrobe is one of unit 4's three named failure modes, and it's the
kind most likely to fail silently — the model inventing a piece the user
doesn't own — rather than loudly, with an error. That's worth locking down
now, while it's cheap to check, rather than discovering it as a bad diagnosis
later.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
