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

> **Revised in unit 9:** Given a query that matches at least one listing, the
> agent completes all four tool calls — `search_listings`,
> `flag_condition_issues`, `suggest_outfit`, `create_fit_card` — and returns a
> fit card, in at least 4 of 5 tries.
>
> **Why revised:** Not a miss — a change underneath the criterion.
> `flag_condition_issues` is now a fourth tool in the loop, so "all three
> tools" no longer names the real sequence. The target itself didn't move;
> `flag_condition_issues` is a deterministic text check with no model
> variance to add, so 4 of 5 still only has to absorb `search_listings`'s one
> phrasing mismatch.

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

> **Revised in unit 9:** Given a query that matches no listings, the agent
> stops before calling `flag_condition_issues`, `suggest_outfit`, or
> `create_fit_card`, and returns a message naming what to change — 5 of 5
> tries.
>
> **Why revised:** `flag_condition_issues` sits between `search_listings` and
> `suggest_outfit`, so "the second tool" is now ambiguous about which one it
> means. The branch itself didn't move — it still returns before
> `session["selected_item"]` is ever set — so the same 5 of 5 now covers all
> three downstream tools instead of two.

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

> **Revised in unit 9:** Across 5 different matching queries, the `id` of
> `session["selected_item"]` matches the `id` of the item dict actually
> received by `flag_condition_issues`, by `suggest_outfit`, and by
> `create_fit_card` — 5 of 5 tries.
>
> **Why revised:** `flag_condition_issues` is a third place `session["selected_item"]`
> now gets handed off to, and a third place the wiring could silently pass the
> wrong dict. Checking only two of three downstream tools would leave the
> newest wiring the one thing this criterion doesn't actually cover.

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

# Unit 9 — criteria for the extension

Five more criteria, written before any unit 9 results existed, for the new
tool: `flag_condition_issues(listing)`. At least three are about the
extension itself, not the three tools that already worked; at least one
names a bad-input path.

---

## 6. Flags fire on known condition language

Across 5 listings whose `description` contains a known issue word (`rip`,
`stain`, `fading`, `pull`, `worn`, etc.), `flag_condition_issues` returns at
least one flag naming that exact word — 5 of 5 tries.

**Why this target:**

This is plain word matching against text that's already in the data —
deterministic, with nothing for a model to vary. A miss here isn't bad luck,
it's a bug in the word list or the tokenizing, so there's no reason to accept
less than 5 of 5.

---

## 7. No false flags on clean listings

Across 5 listings whose `description` contains none of the issue words,
`flag_condition_issues` returns `[]` — 5 of 5 tries.

**Why this target:**

The cost of a false positive here isn't abstract: a tool that flags "pull" in
"pullover" or invents issues on a clean listing is a tool a user learns to
ignore entirely, which is worse than not having it. Same determinism argument
as criterion 6 — 5 of 5 is fair because nothing here is supposed to vary.

---

## 8. Flags are computed on the item the loop actually selected

Across 5 different matching queries, the listing passed into
`flag_condition_issues` (per the trace step) has the same `id` as
`session["selected_item"]` — 5 of 5 tries.

**Why this target:**

Same reasoning as the original state criterion (#3): this is `run_agent`'s
wiring, not the tool's logic or the model's wording. If the wrong item's
flags ever showed up next to a different item's fit card, the bug is in the
loop, and there's no reason to expect it to vary between tries.

---

## 9. A listing missing a description doesn't crash the branch

Given a listing dict where `description` is missing or `None` — a malformed
record, the same kind of gap `brand` already has for most listings —
`flag_condition_issues` returns `[]` without raising, and `run_agent`
continues on to `suggest_outfit` rather than stopping the run — 5 of 5
tries.

**Why this target:**

Real thrift listings are hand-entered and incomplete fields are already
normal in this data (`brand` is `None` for most of them), so a missing
`description` is a plausible record, not a contrived edge case. The cost of
getting this wrong is the whole loop crashing on one incomplete listing
instead of degrading gracefully the way the empty-wardrobe path already does.

---

## 10. Every run leaves exactly one log record, success or failure

Across 5 runs — 3 that complete normally and 2 that end in `session["error"]`
being set (one via the empty-search branch, one via a forced
`ModelUnavailable`) — `logs/run_log.jsonl` gains exactly 5 new records, and
each record's `outcome` field is `"error"` if and only if that run's
`session["error"]` was set — 5 of 5.

**Why this target:**

The `finally` block in `run_agent` is what makes a failure leave a record
instead of just an absence — if a record is ever missing after a run, the
bug is in the logging wrapper, not in whichever tool failed. Five runs with
both failure mechanisms represented is enough to exercise every path the
`finally` block has to cover; there's no fuzziness in whether a dict key is
`None` or not, so 5 of 5 is the fair bar, matching the format of criteria
6–9 rather than inventing a stricter one.



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
