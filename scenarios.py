"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    {
        # A query the data can match. Criterion 1.
        "name": "matching query completes",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # A query nothing can match. Criterion 2 — the branch.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # A user with nothing saved. One of unit 4's three failure modes.
        # Criterion 5 — same query, 5 tries, checking every generation stays
        # sane with no wardrobe to draw on.
        "name": "empty wardrobe",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": 5,
    },

    # Criterion 3 — state. Five different matching queries so each one picks
    # a different selected_item; the id has to carry through to suggest_outfit
    # and create_fit_card unchanged every time.
    {
        "name": "state check: track jacket",
        "query": "90s track jacket in size M",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        "name": "state check: slip dress",
        "query": "silk slip dress in midi length under $40",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        "name": "state check: sneakers",
        "query": "platform sneakers size 8",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        "name": "state check: denim jacket",
        "query": "denim jacket under $50",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        "name": "state check: graphic tee",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 3,
    },

    # Criterion 4 — fit card. Five different items so the price/platform/
    # length check isn't just one lucky generation for one listing.
    {
        "name": "fit card check: track jacket",
        "query": "90s track jacket in size M",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        "name": "fit card check: slip dress",
        "query": "silk slip dress in midi length under $40",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        "name": "fit card check: sneakers",
        "query": "platform sneakers size 8",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        "name": "fit card check: denim jacket",
        "query": "denim jacket under $50",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        "name": "fit card check: graphic tee",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 4,
    },

    # ── Unit 9 — the extension: flag_condition_issues ──────────────────────

    # Criterion 6 — flags fire on known condition language. Five real
    # listings whose description already contains an issue word, selected by
    # a query specific enough to put each one first.
    {
        "name": "condition flags: fading jeans (lst_001)",
        "query": "vintage levi's 501 jeans medium wash",
        "wardrobe": "example",
        "criterion": 6,
    },
    {
        "name": "condition flags: flannel with pulls (lst_003)",
        "query": "oversized flannel shirt plaid red black",
        "wardrobe": "example",
        "criterion": 6,
    },
    {
        "name": "condition flags: corduroy pilling (lst_005)",
        "query": "corduroy wide-leg pants rust",
        "wardrobe": "example",
        "criterion": 6,
    },
    {
        "name": "condition flags: bootleg tee faded/worn (lst_006)",
        "query": "graphic tee 2003 tour bootleg style",
        "wardrobe": "example",
        "criterion": 6,
    },
    {
        "name": "condition flags: slip dress worn (lst_013)",
        "query": "90s silk slip dress floral midi length",
        "wardrobe": "example",
        "criterion": 6,
    },

    # Criterion 7 — no false flags on clean listings. Five real listings
    # whose description has none of the issue words.
    {
        "name": "condition flags: clean track jacket (lst_004)",
        "query": "90s track jacket navy white stripe",
        "wardrobe": "example",
        "criterion": 7,
    },
    {
        "name": "condition flags: clean denim jacket (lst_007)",
        "query": "denim jacket light wash cropped",
        "wardrobe": "example",
        "criterion": 7,
    },
    {
        "name": "condition flags: clean cardigan (lst_008)",
        "query": "knit cardigan chunky brown",
        "wardrobe": "example",
        "criterion": 7,
    },
    {
        "name": "condition flags: clean windbreaker (lst_010)",
        "query": "vintage windbreaker color block purple teal",
        "wardrobe": "example",
        "criterion": 7,
    },
    {
        "name": "condition flags: clean linen blazer (lst_018)",
        "query": "vintage linen blazer cream",
        "wardrobe": "example",
        "criterion": 7,
    },

    # Criterion 8 — flags are computed on the item the loop actually
    # selected. Reuses the five state-check queries from criterion 3; the
    # trace's flag_condition_issues step has to name the same id as
    # session["selected_item"] every time.
    {
        "name": "state check (flags): track jacket",
        "query": "90s track jacket in size M",
        "wardrobe": "example",
        "criterion": 8,
    },
    {
        "name": "state check (flags): slip dress",
        "query": "silk slip dress in midi length under $40",
        "wardrobe": "example",
        "criterion": 8,
    },
    {
        "name": "state check (flags): sneakers",
        "query": "platform sneakers size 8",
        "wardrobe": "example",
        "criterion": 8,
    },
    {
        "name": "state check (flags): denim jacket",
        "query": "denim jacket under $50",
        "wardrobe": "example",
        "criterion": 8,
    },
    {
        "name": "state check (flags): graphic tee",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 8,
    },

    # Criterion 9 — a listing with no description shouldn't crash the
    # branch. Doesn't go through search_listings (real data always has a
    # description) — run_eval.py special-cases "direct_check" scenarios and
    # dispatches to a function that injects one malformed listing directly.
    {
        "name": "malformed listing: missing description",
        "direct_check": "malformed_listing",
        "criterion": 9,
    },

    # Criterion 10 — every run leaves exactly one log record, success or
    # failure. Also a direct_check: it runs a small batch of real run_agent()
    # calls itself (one success, one natural failure, one forced
    # ModelUnavailable) and checks logs/run_log.jsonl grew to match.
    {
        "name": "log record: success + both failure branches",
        "direct_check": "log_record",
        "criterion": 10,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if scenario.get("direct_check"):
            # These bypass search_listings entirely, so they carry no query
            # or wardrobe for this check to validate.
            continue
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
