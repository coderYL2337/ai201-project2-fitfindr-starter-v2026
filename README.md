# FitFindr

Repository: https://github.com/coderYL2337/ai201-project2-fitfindr-starter-v2026.git

```bash
git clone https://github.com/coderYL2337/ai201-project2-fitfindr-starter-v2026.git
cd ai201-project2-fitfindr-starter-v2026
```

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

A user asks for a thrifted item in plain language, e.g. "vintage graphic tee
under $30", optionally with a size and a price ceiling. FitFindr searches the
mock listings for the best match, suggests one or two outfits built from that
item and whatever's in the user's wardrobe (or general styling advice if their
wardrobe is empty), and writes a short social-post-style caption for the find.
If nothing in the listings matches, the agent says so and stops instead of
inventing an item.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Filters the mock listings by size and price, then scores
  the rest by keyword overlap with the description and returns the best matches,
  best match first. Doesn't call the model.
- **Inputs:** `description` (str) — keywords describing the item, e.g. "vintage
  graphic tee"; `size` (str or None) — matched case-insensitively against
  whole size tokens, not a raw substring, so `"M"` matches `"S/M"` but not
  `"US 9"`; `max_price` (float or None) — inclusive price ceiling.
- **Returns:** A list of listing dicts, each with `id`, `title`, `description`,
  `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`
  (may be `None`), and `platform`. Sorted by keyword-match score, capped at
  `config.SEARCH_RESULT_LIMIT`.
- **When it has nothing:** Returns `[]` — an empty list, never `None` and
  never an exception. `agent.py::run_agent` branches on this.

### `suggest_outfit`

- **What it does:** Calls the model to suggest one or two outfits that pair the
  found item with pieces from the user's wardrobe, naming specific items the
  user already owns.
- **Inputs:** `new_item` (dict) — the selected listing dict from
  `search_listings`; `wardrobe` (dict) — a wardrobe dict with an `items` key
  holding a list of wardrobe-item dicts (`id`, `name`, `category`, `colors`,
  `style_tags`, `notes`); `items` may be an empty list.
- **Returns:** A non-empty string with the outfit suggestion(s).
- **When it has nothing:** If `wardrobe['items']` is empty, returns general
  styling advice for the item instead of naming owned pieces — never raises
  and never returns `""`.

### `create_fit_card`

- **What it does:** Calls the model to write a short, social-post-style
  caption for the find, mentioning the item, its price, and its platform once
  each, and specific about the vibe — not a product description.
- **Inputs:** `outfit` (str) — the outfit-suggestion string from
  `suggest_outfit`; `new_item` (dict) — the listing dict for the item.
- **Returns:** A two-to-four sentence caption string, worded differently on
  each call (see `TEMPERATURE`/`CACHE_ENABLED` in `config.py` if it isn't).
- **When it has nothing:** If `outfit` is empty or whitespace-only, returns a
  descriptive fallback message instead of raising.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a message in
`session["error"]` naming what the user could change (loosen the price or size)
and return the session without calling `suggest_outfit` or `create_fit_card`.
Otherwise, take the first result as `session["selected_item"]` and continue on
to `suggest_outfit` and then `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex — pulling a price ceiling out of patterns
like "under $30" and a size token like "size M", with whatever's left of the
query used as the free-text description.

**What moves through the session:** `query` → `parsed` (description, size,
max_price) → `search_results` → `selected_item` → `outfit_suggestion` →
`fit_card`, with `error` set (and everything after it left `None`) if the loop
stops early.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask '...'

```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, ...4 more]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
You should definitely grab these—they're a great addition since your other jeans are dark and baggy! Pair them with your white ribbed tank top, brown leather belt, and chunky white sneakers for an effortless, classic 90s-inspired look. When it cools down, just throw your vintage black denim jacket over top and switch to your black combat boots for an edgy streetwear vibe.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Found my holy grail denim today and I'm honestly not shutting up about it. These Vintage Levi's 501 Jeans in the dreamiest medium wash just landed in my Depop shop, and they fit like an absolute glove. Grabbed them for $38.0 and I'm already picturing them worn in with crisp white sneakers for that effortlessly cool 90s off-duty look. Snag them before I change my mind and keep them forever!
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* I asked Copilot to implement `search_listings`'s size
  filter, following the warning already in the `tools.py` docstring that a
  plain substring test is wrong — `"s" in "us 9"` is `True`, and so is
  `"l" in "xl"`.
- *What came back:* A token-based matcher — `_size_tokens()` splits a size
  string on non-alphanumeric characters (`"S/M"` → `{"s", "m"}`) and checks
  for set overlap instead of substring containment.
- *What I changed:* Nothing in the logic, but I didn't trust it until I ran
  it — `search_listings('graphic tee', max_price=30)` came back only with
  tops sized `S/M` or `L`, no shoe listings sized `US 9` slipping in on a
  stray `"s"`. I kept it once the terminal test confirmed it.

**Moment 2**

- *What I asked for:* I asked for the empty-search branch in `run_agent` —
  stop before `suggest_outfit` when `search_listings` returns nothing.
- *What came back:* A first draft that set `session["error"] = "No results."`
- *What I changed:* The `run_agent` docstring itself says `"No results"` is
  not an acceptable message, so I rewrote it to name what the user could
  actually do: *"No listings matched. Try a higher price ceiling, a different
  size, or fewer keywords in the description."* I confirmed the fix by running
  the ballgown query and reading the message back.

**Moment 3**

- *What I asked for:* After the Before run showed crashes on criteria 1 and 5,
  I asked Copilot to diagnose why — it read `agent.py` and pointed out that
  `run_agent` never catches `ModelUnavailable`, so a real 503 from the model
  propagates straight out instead of becoming a `session["error"]` message.
- *What came back:* A second branch wrapping `suggest_outfit`/`create_fit_card`
  in `try/except ModelUnavailable`.
- *What I changed:* Nothing in the fix itself, but I didn't accept the After
  run's 5/5 table as proof it worked — that run happened to hit zero real
  503s. I asked for a way to verify the catch directly, and we mocked
  `agent.suggest_outfit` to raise `ModelUnavailable` on purpose and confirmed
  `session["error"]` came back readable with `fit_card` still `None`, instead
  of a stack trace.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | FAIL (crashed) | PASS | PASS | PASS | MET (4/5) |
| 2. Impossible query stops before second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. `selected_item` id matches item passed to `suggest_outfit`/`create_fit_card` (5 different queries: track jacket, slip dress, sneakers, denim jacket, graphic tee) | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card mentions price + platform, 2–4 sentences (5 different items: track jacket, slip dress, sneakers, denim jacket, graphic tee) | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Empty wardrobe returns non-empty advice, no crash, no invented item | 5 of 5 | FAIL (crashed) | PASS | FAIL (crashed) | FAIL (crashed) | PASS | MISSED (2/5) |

> Source: `results/run_2026-10-05_0210_before.md`, produced by `run_eval.py::main`
> (5 tries per scenario, caching off). For criteria 3 and 4, each "Try" column
> is a different scenario/query, not 5 repeats of one query, since those
> criteria require 5 different items.

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```
agent.py::run_agent → tools.py::suggest_outfit / tools.py::create_fit_card
scenario: "matching query completes", query "vintage graphic tee under $30", try 1

Outfit suggestion:
You should definitely grab it! Pair the baby tee with your baggy straight-leg jeans and chunky white sneakers for a classic, nostalgic Y2K streetwear look. Toss your black cropped zip hoodie over the top on cooler days to nail that effortless early-2000s vibe.

Fit card:
Found this literal dream of a butterfly print Y2K baby tee while digging through the racks, and I'm obsessed. It's giving major early-2000s mall rat energy, and I honestly can't wait to style it with some baggy denim and chunky sneakers. Snagged it on Depop for just $18.0 and I'm never taking it off.

Try 2 crash (generate.py raising ModelUnavailable):
ModelUnavailable: Couldn't reach the model: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Matching query completes all three tools | 4 of 5 | MET (4/5) | Counted PASS where the session reached `create_fit_card` with no crash; 1 try raised `ModelUnavailable` (503), leaving 4 completed. |
| 2 | Impossible query stops before second tool | 5 of 5 | MET (5/5) | All 5 tries stopped at the branch with `session["error"]` set and `fit_card` still `None`, confirmed in the trace. |
| 3 | `selected_item` id matches item passed downstream (5 different queries) | 5 of 5 | MET (5/5) | For each of the 5 different-item scenarios, compared the title/price/platform in `session["selected_item"]` against what appears in the generated outfit/fit card text — identical every time. |
| 4 | Fit card mentions price + platform, 2–4 sentences (5 different items) | 5 of 5 | MET (5/5) | Checked one completed try per item: every fit card named the dollar amount and the platform, and sentence counts landed at 3 each. |
| 5 | Empty wardrobe returns non-empty advice, no crash, no invented item | 5 of 5 | MISSED (2/5) | 3 of 5 tries raised `ModelUnavailable` before `suggest_outfit` could return anything — counted as failures since the criterion explicitly rules out exceptions. |

**Diagnoses**

Criterion 5 missed because of one mechanism, not five unrelated bad tries: `agent.py::run_agent` never catches `ModelUnavailable`. When `tools.py::suggest_outfit` or `tools.py::create_fit_card` calls the model in `generate.py` and the service returns a 503, the exception propagates straight out of `run_agent` uncaught. `run_eval.py::run_once` happens to catch it generically and logs "crashed", but in the real CLI path (`app.py::_ask_one`) nothing would turn that into the readable message the brief asks for — it would surface as a raw stack trace instead. The same mechanism also caused criterion 1's single miss (try 2's crash) and would affect criterion 3/4 equally if their underlying scenario's one verified try had hit the same error. This is a loop problem, not a tool problem: `suggest_outfit`/`create_fit_card` are working as designed, and `ModelUnavailable` is already defined for exactly this case — `run_agent` just never handles it.



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
python app.py ask 'vintage graphic tee under $30, size M' --trace

[1] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 8 items: Y2K Baby Tee — Butterfly Print, Mesh Long-Sleeve Top — Black, 90s Silk Slip Dress — Floral, Midi Length … +5 more
[2] suggest_outfit
      in:  dict with keys: selected_item, wardrobe
      out: Definitely buy it! Pair the Y2K baby tee with your baggy straight-leg jeans and chunky white sneakers for an e…
[3] create_fit_card
      in:  dict with keys: outfit, item
      out: Absolute peak 2000s energy right here. Just snagged this Y2K baby tee on Depop for $18.0 and I'm totally obses…
```

**Empty search**

```
python app.py ask 'designer ballgown size XXS under $5' --trace

[1] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
[2] branch
      →    empty search results, stopping before suggest_outfit
```

**On the MCP move:** In `run_agent()`, the direct call `search_listings(description, size=..., max_price=...)` was replaced with `call_tool("search_listings", {"description": ..., "size": ..., "max_price": ...})` (old line kept commented out above the new one for comparison). The call site changed shape — positional/keyword args became one dict, and the call now goes through a subprocess over stdio instead of an in-process function call — but the return value didn't: `search_listings` still comes back as a list of dicts with the same keys (`title`, `price`, `platform`, etc.), confirmed by the trace output above and by `_show()`/`_ask_one()` printing identical fields before and after the swap. No behavioral difference showed up, which suggests the tool was already returning plain JSON-safe data (no custom objects, no non-string keys) even before MCP was in the picture.



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:** Added a second branch in `agent.py::run_agent` — wrapped the `suggest_outfit` / `create_fit_card` calls in a `try/except ModelUnavailable`, setting `session["error"]` to a readable message (`"The model couldn't be reached: {exc}"`) and returning early instead of letting the exception propagate. One change only; `tools.py` and the MCP wiring are untouched.

**Which failure it was meant to fix:** The "model unavailable" failure mode. The Before diagnosis found that `run_agent` never caught `ModelUnavailable`, so real 503s from the model service came out of `run_agent` as raw, uncaught exceptions — the same mechanism caused the single miss on criterion 1 and all 3 misses on criterion 5 (empty wardrobe) in the Before run.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. `selected_item` id matches item passed downstream (5 different queries) | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card mentions price + platform, 2–4 sentences (5 different items) | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Empty wardrobe returns non-empty advice, no crash, no invented item | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

> Source: `results/run_2026-10-05_0234_after.md`. Zero crashes across all 65 tries
> in this run — the model simply didn't 503 this time, which is a problem for
> proving the fix (see below).

**Did it help, and how do I know:**

The raw numbers look like a clean win (criterion 5 went from 2/5 to 5/5, criterion
1 from 4/5 to 5/5), but I'm not willing to credit the fix based on that alone —
this After run happened not to hit a single 503, so the new `except
ModelUnavailable` branch was never actually exercised by `run_eval.py` this
time. An improvement measured only against an external service's uptime that
day isn't a measurement of the code change.

So I verified the mechanism directly instead of relying on luck: I patched
`agent.suggest_outfit` to raise `ModelUnavailable` on purpose and called
`run_agent` directly.

```
$ python -c "
import unittest.mock as mock
from generate import ModelUnavailable
import agent
from utils.data_loader import get_example_wardrobe
with mock.patch.object(agent, 'suggest_outfit', side_effect=ModelUnavailable('simulated 503 for verification')):
    session = agent.run_agent('vintage graphic tee under \$30', get_example_wardrobe())
    print('error:', session['error'])
    print('fit_card:', session['fit_card'])
"
[2] branch
      →    model unavailable, stopping before the rest of the loop
error: The model couldn't be reached: simulated 503 for verification
fit_card: None
```

Before this change, the same forced failure would have propagated out of
`run_agent` as an uncaught `ModelUnavailable`, exactly like the 4 crashes
recorded in the Before run log. Now it's caught, `session["error"]` carries a
readable message, and `fit_card`/`outfit_suggestion` stay `None` — the same
shape as the existing empty-search branch. So: **yes, it helped**, but the
evidence that matters is this forced test, not the 5/5 After table, which
mostly reflects a lucky day for the model API rather than the fix itself.

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->

All five criteria show MET in the After table, but I don't consider criteria 1
and 5 fully proven, and there's one real gap the fix doesn't cover:

- **Criteria 1 and 5 (model unavailable) — validated synthetically, not
  organically.** The After run happened to hit zero real 503s, so
  `run_eval.py` never exercised the new `except ModelUnavailable` branch on
  its own; my evidence is the forced mock test, not the 5/5 row. I'd want to
  re-run `python run_eval.py --label after` on a day the API is visibly
  rate-limited (or add a way to deliberately inject the error during eval) to
  see a real crash caught in the wild before I'd fully trust those two rows.
  I stopped here because reproducing a real 503 on demand isn't in my
  control, and the synthetic test exercises the exact same code path.

- **Partial session state when `create_fit_card` fails after `suggest_outfit`
  succeeds.** My `try` wraps both calls, so if the first succeeds and the
  second raises, `session["outfit_suggestion"]` stays populated while
  `session["error"]` is also set and `fit_card` is `None` — a mixed state the
  empty-search branch doesn't have (there, everything downstream is cleanly
  `None`). `_show()`/`_ask_one()` print `session["error"]` first either way,
  so nothing currently misbehaves, but a caller that reads `outfit_suggestion`
  before checking `error` would get a half-finished answer. I didn't fix this
  because my diagnosis named one mechanism (the missing catch), and widening
  the fix to also reset `outfit_suggestion` on this specific sub-case felt
  like a second, undiagnosed change — flagging it instead of fixing it blind.

- **Criteria 3 and 4 were checked by reading the printed output, not by an
  assertion in code.** I compared `selected_item`'s title/price/platform
  against the generated text by eye for one try per scenario. That's fine for
  five scenarios by hand, but it doesn't scale and it's not something
  `run_eval.py` checks for me — a real fix would be a small checker function
  that asserts the id match and the price/platform mention programmatically
  per try, not per scenario. I stopped short of writing it because this unit
  asked for one diagnosed improvement, not a new test harness.

**On the MCP move:** only `search_listings` runs over MCP; `suggest_outfit`
and `create_fit_card` are still direct in-process calls, exactly as
`mcp_server.py` scoped it ("you're moving one tool, not three"). Nothing
behaved differently after the move — the trace output, the branch logic, and
every fit card in this unit's runs are identical in shape to the direct-call
version, which is the whole point: the call shape changed, the return value
didn't.



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

<!-- ═══════════════════════ UNIT 5 ═══════════════════════

     Project 9 The Capstone.
     ═══════════════════════════════════════════════════════════════════ -->

---

## What This Extends

<!-- Which of your four systems, and what's new. -->
This extends project2 'FitFindr'. What's new is a fourth tool,
`flag_condition_issues(listing)` — it scans a listing's `description` for
condition-reducing language ("rip", "stain", "pilling", "fading", "pull") and
returns a list of flags plus a severity, independent of whatever the
`condition` field itself claims. It's a sanity check on the data, not a
retrieval or generation step, so it slots in right after `search_listings`
picks a candidate.

---

## The Shape

<!-- A, B or C, and what you decided is out of scope. -->
C — Extend one capability. Add a fourth tool,
`flag_condition_issues(listing)`, alongside the existing three.

**Out of scope:** I'm not adding a second retrieval strategy to
`search_listings` — the keyword-overlap scoring stays as-is. I'm not touching
`suggest_outfit`'s wardrobe-matching logic — the new tool only reads a
listing's `description`, it doesn't talk to the wardrobe. And I'm not moving
the new tool onto MCP — it stays a direct, in-process call like
`suggest_outfit` and `create_fit_card`, so the one capability I'm adding stays
isolated from the unit 4 MCP migration.

---

## Running It

<!-- Which path, and a pointer to RUNNING.md. -->
Path B — local with logs. 
Read [RUNNING.md](RUNNING.md) 

---

## Instrumentation

<!-- What each log record holds, and at least ten entries pasted as text. -->

Every call to `agent.run_agent()` appends one JSON record to `logs/run_log.jsonl`
via `instrumentation.py`. A `try/except/finally` wraps the whole run, so a
record is written whether the run finishes, stops at a branch, or raises —
the `finally` runs either way. Each record holds:

| Field | What it is |
|---|---|
| `timestamp` | UTC, ISO 8601 |
| `query` | what the user asked for |
| `outcome` | `"ok"` or `"error"` |
| `error` | `session["error"]`, or `None` |
| `duration_seconds` | wall-clock time for the whole `run_agent()` call |
| `search_result_count` | `len(session["search_results"])` |
| `selected_item_id` | the id of `session["selected_item"]`, or `None` |
| `condition_flags` | what `flag_condition_issues` returned for that item |
| `model_calls` | calls to `generate()` made during this run |
| `cache_hits` | of those, how many were served from cache |
| `tokens_total` | prompt + output tokens actually billed this run |

**Ten real entries, pasted as text** (two matching queries served from a
fresh model call, five served from cache, two that stop on the empty-search
branch, and one from a forced `ModelUnavailable`):

```
{"timestamp": "2026-11-09T06:29:48+00:00", "query": "vintage graphic tee under $30", "outcome": "ok", "error": null, "duration_seconds": 2.557, "search_result_count": 10, "selected_item_id": "lst_002", "condition_flags": [], "model_calls": 2, "cache_hits": 0, "tokens_total": 648}
{"timestamp": "2026-11-09T06:29:51+00:00", "query": "vintage graphic tee under $30", "outcome": "ok", "error": null, "duration_seconds": 3.01, "search_result_count": 10, "selected_item_id": "lst_002", "condition_flags": [], "model_calls": 2, "cache_hits": 0, "tokens_total": 679}
{"timestamp": "2026-11-09T06:30:19+00:00", "query": "90s track jacket in size M", "outcome": "ok", "error": null, "duration_seconds": 1.533, "search_result_count": 4, "selected_item_id": "lst_004", "condition_flags": [], "model_calls": 0, "cache_hits": 2, "tokens_total": 0}
{"timestamp": "2026-11-09T06:30:19+00:00", "query": "silk slip dress in midi length under $40", "outcome": "ok", "error": null, "duration_seconds": 0.911, "search_result_count": 5, "selected_item_id": "lst_013", "condition_flags": [{"flag": "worn", "severity": "minor"}], "model_calls": 0, "cache_hits": 2, "tokens_total": 0}
{"timestamp": "2026-11-09T06:30:20+00:00", "query": "designer ballgown size XXS under $5", "outcome": "error", "error": "No listings matched. Try a higher price ceiling, a different size, or fewer keywords in the description.", "duration_seconds": 0.885, "search_result_count": 0, "selected_item_id": null, "condition_flags": [], "model_calls": 0, "cache_hits": 0, "tokens_total": 0}
{"timestamp": "2026-11-09T06:30:21+00:00", "query": "denim jacket under $50", "outcome": "ok", "error": null, "duration_seconds": 0.886, "search_result_count": 7, "selected_item_id": "lst_007", "condition_flags": [], "model_calls": 0, "cache_hits": 2, "tokens_total": 0}
{"timestamp": "2026-11-09T06:30:22+00:00", "query": "corduroy pants under $25", "outcome": "error", "error": "No listings matched. Try a higher price ceiling, a different size, or fewer keywords in the description.", "duration_seconds": 0.844, "search_result_count": 0, "selected_item_id": null, "condition_flags": [], "model_calls": 0, "cache_hits": 0, "tokens_total": 0}
{"timestamp": "2026-11-09T06:30:23+00:00", "query": "leather bomber jacket", "outcome": "ok", "error": null, "duration_seconds": 0.853, "search_result_count": 7, "selected_item_id": "lst_022", "condition_flags": [], "model_calls": 0, "cache_hits": 2, "tokens_total": 0}
{"timestamp": "2026-11-09T06:30:24+00:00", "query": "platform sneakers size 8", "outcome": "ok", "error": null, "duration_seconds": 0.846, "search_result_count": 1, "selected_item_id": "lst_019", "condition_flags": [], "model_calls": 0, "cache_hits": 2, "tokens_total": 0}
{"timestamp": "2026-11-09T06:30:26+00:00", "query": "platform sneakers size 8", "outcome": "error", "error": "The model couldn't be reached: simulated 503 for the log demo", "duration_seconds": 1.437, "search_result_count": 1, "selected_item_id": "lst_019", "condition_flags": [], "model_calls": 0, "cache_hits": 0, "tokens_total": 0}
```

The full eighteen-entry file this unit's runs produced is committed at
`logs/run_log.jsonl`. The `ModelUnavailable` entry above was produced by
mocking `agent.suggest_outfit` to raise it on purpose, the same technique
used in unit 4 — it confirms the `finally` block in `run_agent` logs a
failure even when the exception propagates out of `_run_loop`.

---

## What It Costs

<!-- Your measured per-run cost, how you measured it, and the hundred-a-day
     arithmetic. -->

**How I measured it:** `generate.py` already counts real tokens billed per
call (`token_counts()`), not an estimate off a pricing page. With the cache
forced off (`AI201_CACHE=0`, since a cache hit costs nothing and would make
the average meaningless), I called `run_agent()` directly ten times on the
same matching query — `'vintage graphic tee under $30'` — and read
`duration_seconds` and `tokens_total` back out of the structured log for
those ten runs.

```
tokens_total per run: 654, 674, 659, 615, 650, 644, 631, 648, 648, 679
duration_seconds:     4.18, 2.87, 2.48, 2.44, 2.76, 2.25, 2.46, 44.03, 2.56, 3.01
```

**Measured per-run cost:** ~650 tokens (prompt + output combined) and 2
model calls, every run — `suggest_outfit` and `create_fit_card` each call the
model once; `search_listings` doesn't. Average duration was 6.90s including
all ten runs, but one run (44.03s) crossed the 15-requests-per-minute pacing
window in `generate.py` and waited on it — that's the limiter doing its job,
not the cost of the work itself. Excluding that one outlier, the other nine
runs averaged **2.78 seconds** of real wall-clock time per run.

**The hundred-a-day arithmetic:** at 100 runs/day, this system does:

- **~65,000 tokens/day** (100 × ~650)
- **200 model calls/day** (100 × 2) — at the free tier's 15-requests/minute
  pacing limit, 200 calls run back-to-back with no gaps between users would
  take roughly 13-14 minutes of pure pacing, not 200 minutes — a non-issue
  spread across a day, but the number that starts to matter if "a hundred a
  day" became "a hundred an hour"
- **~278 seconds (~4.6 minutes) of compute/day** (100 × 2.78s), which matters
  specifically because `serve.py` answers one request at a time — that's
  4.6 minutes the single worker would be busy out of 1,440 minutes in a day

---

## Run Log and Verdicts

<!-- Five criteria across three trials, MET or MISSED, and for each miss the
     stage and the mechanism. -->

Three trials, nothing changed in between, caching off. Produced by a one-off
harness built on `run_eval.py::run_once` (criteria 6–8 reuse the real
`agent.py::run_agent` loop against the `scenarios.py` entries tagged 6/7/8;
criteria 9 and 10 dispatch to `run_eval.py::_check_malformed_listing` and
`run_eval.py::_check_log_record`, two new `"direct_check"` scenario handlers).

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 6. Flags fire on known condition language | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 7. No false flags on clean listings | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 8. Flags computed on the item actually selected | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 9. Malformed listing doesn't crash the branch | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 10. Every run leaves exactly one log record | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |

No misses across any criterion or trial, so there's no stage/mechanism to
diagnose this round — all five targets held on every try.

**Real output, one per criterion, from Run 1:**

```
criterion 6 — tools.py::flag_condition_issues, via agent.py::run_agent
scenario: "condition flags: fading jeans (lst_001)"

[1] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Vintage Levi's 501 Jeans — Medium Wash, High-Waisted Denim Shorts — Cutoff, Baggy Carpenter Jeans — Dark Wash … +7 more
[2] flag_condition_issues
      in:  dict with keys: listing
      out: 3 items: {'flag': 'rips', 'severity': 'major'}…
[3] suggest_outfit
      in:  dict with keys: selected_item, wardrobe
      out: Yes, definitely buy them! Pair your new vintage Levi's with the white ribbed tank top, layered under the vinta…
[4] create_fit_card
      in:  dict with keys: outfit, item
      out: Found these vintage Levi's 501 jeans on depop for just $38 and I am never taking them off. They have that 90s …

condition_flags on lst_001: [{'flag': 'rips', 'severity': 'major'}, {'flag': 'stains', 'severity': 'major'}, {'flag': 'fading', 'severity': 'minor'}]
```

```
criterion 7 — tools.py::flag_condition_issues, via agent.py::run_agent
scenario: "condition flags: clean track jacket (lst_004)"

[1] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: 90s Track Jacket — Navy/White Stripe, Platform Sneakers — White Chunky Sole, 90s Leather Bomber — Black … +7 more
[2] flag_condition_issues
      in:  dict with keys: listing
      out: [] (empty)
[3] suggest_outfit
      in:  dict with keys: selected_item, wardrobe
      out: Definitely grab it—this will fit right into your wardrobe! Pair it with your **baggy straight-leg jeans** and …
[4] create_fit_card
      in:  dict with keys: outfit, item
      out: Scored this vintage 90s track jacket on Poshmark for just $45.00 and I am officially obsessed. Throwing it on …

condition_flags on lst_004: []
```

```
criterion 8 — agent.py::run_agent, spying on tools.py::flag_condition_issues
scenario: "state check (flags): track jacket"

id flag_condition_issues was actually called with: lst_004
id of session["selected_item"]:                    lst_004
(same id both ways — confirmed by wrapping the real flag_condition_issues in
 a spy function and comparing its captured argument against the session)
```

```
criterion 9 — run_eval.py::_check_malformed_listing
scenario: "malformed listing: missing description"

[1] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 1 items: Test Item With No Description
[2] flag_condition_issues
      in:  dict with keys: listing
      out: [] (empty)
[3] suggest_outfit
      in:  dict with keys: selected_item, wardrobe
      out: Since the thrifted top is a mystery, let's assume it's a versatile piece like a printed graphic tee or a brigh…
[4] create_fit_card
      in:  dict with keys: outfit, item
      out: Found this absolute mystery top while rummaging through the racks and I'm honestly obsessed with the vibe. Sco…

result: condition_flags=[], outfit_suggestion ran=True: PASS
```

```
criterion 10 — run_eval.py::_check_log_record, reading logs/run_log.jsonl
scenario: "log record: success + both failure branches"

result: log grew by 5 (expected 5), 5/5 records had the correct outcome field — PASS
```

---

## The Improvement

<!-- What you changed, why, and the second run log in the same format. -->

**None of the five formal criteria (6–10) missed** — all MET, 5/5, across all
three trials in Milestone 5. So this isn't a diagnosis of one of those five;
it's a real bug I found by hand-testing the system beyond the five criteria,
in the exact spot criterion 1's own reasoning warns about ("a phrasing that
shares no words... can miss an item") — except in reverse: a phrasing shared
the *wrong* word with the *wrong* item.

**What happened:** `python app.py ask 'clean shoes under $30'` returned a
navy crewneck sweatshirt instead of either pair of sneakers in the data.

**Diagnosis — stage and mechanism:** The stage is `tools.py::_score`, called
from `search_listings`. The mechanism: `_score` counted a query-word match
the same whether it hit the listing's `title`/`category` or just its
free-text `description`. For `"clean shoes"`, the sweatshirt's description
happens to end in the word *"clean"* (`"No graphics, clean."`) — one point.
The sneakers score a point too, but only because their `category` field is
literally `"shoes"` — also one point. Tied at 1, and `_score`'s caller sorts
with Python's stable sort, which keeps listings in their original
`listings.json` order on a tie. The sweatshirt happens to appear earlier in
the file, so it wins — not because it's more relevant, but because it's
first and the scorer can't tell the difference between an incidental
adjective and a word that names what the item *is*.

**What I changed:** One function, `tools.py::_score`. A query word matching
`title`, `category`, or `style_tags` now scores 2 points; a word matching
only in `description` scores 1. Nothing else — `search_listings`'s filtering,
`flag_condition_issues`, `suggest_outfit`, and `create_fit_card` are
untouched.

**Did it help?**

```
Before:
$ python -c "from tools import search_listings; print([l['title'] for l in search_listings('clean shoes', max_price=30)])"
['Oversized Crewneck Sweatshirt — Vintage Navy', 'Low-Top Canvas Sneakers — Off-White']

After:
$ python -c "from tools import search_listings; print([l['title'] for l in search_listings('clean shoes', max_price=30)])"
['Low-Top Canvas Sneakers — Off-White', 'Oversized Crewneck Sweatshirt — Vintage Navy']
```

Yes — the sneakers now outrank the sweatshirt for "clean shoes," and
`python app.py ask 'clean shoes under $30'` now selects a pair of shoes.

**Run Log and Verdicts, after — same five criteria, three more trials:**

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 6. Flags fire on known condition language | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 7. No false flags on clean listings | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 8. Flags computed on the item actually selected | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 9. Malformed listing doesn't crash the branch | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 10. Every run leaves exactly one log record | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |

Identical to the before table — expected, since the fix only touches
`search_listings`'s tie-breaking, and none of criteria 6–10 test search
ranking. **The honest reading:** the fix didn't move the numbers this unit's
own criteria measure, because those criteria were never testing for this —
the real evidence that it helped is the "clean shoes" example above, not
this table. That's worth naming rather than papering over: a clean set of
MET rows can coexist with a real bug the criteria simply weren't written to
catch.

---

## What's Still Broken

<!-- What you'd do about each remaining miss, why you stopped, and the one
     thing you'd do first. -->

---

## How I Used AI

<!-- Two specific moments — what you asked, what you got, what you changed. -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
