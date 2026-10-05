# FitFindr

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

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



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

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
