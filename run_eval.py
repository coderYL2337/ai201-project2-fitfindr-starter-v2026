#!/usr/bin/env python3
"""
Run your scenarios repeatedly and write the results down. ← UNIT 4

    python run_eval.py --label before      five tries, the default
    python run_eval.py --label after       after your improvement
    python run_eval.py --tries 10          more tries

This does the mechanical half of unit 4 for you. It runs every scenario in
`scenarios.py` five separate times, **with caching off** so you get five real
answers, captures the trace and the session for each, and writes it all into
`results/` in the table format the submission asks for.

Five, because your criteria are written out of five — "4 of 5 tries", "5 of 5
tries". One column per try means you count the passes and read the verdict
straight off the row, with no arithmetic in between.

⚠️ What it does NOT do is decide whether a try passed.

That judgment is yours, and it has to be, because it depends on criteria you
wrote. The Verdict column comes out blank and you fill it in from the output
underneath. Deciding what counts as a pass is the lesson — a scorer handed to
you would teach you nothing.

**Two of your three tools call a model, so tries will legitimately differ.**
That is expected here, unlike pair 1. If all five tries come back identical
on a criterion that involves the fit card, check that you're really in test
mode — caching is what usually explains it.
"""

import argparse
import datetime as dt
import sys
import traceback

import config
import scenarios as scenario_module


def run_once(scenario, use_trace=True):
    """One scenario, one try. Returns everything worth recording."""
    from agent import run_agent
    from utils.data_loader import get_example_wardrobe, get_empty_wardrobe
    import trace as trace_module

    direct_check = scenario.get("direct_check")
    if direct_check == "malformed_listing":
        return _check_malformed_listing(use_trace)
    if direct_check == "log_record":
        return _check_log_record(use_trace)

    wardrobe = (
        get_empty_wardrobe() if scenario["wardrobe"] == "empty" else get_example_wardrobe()
    )

    if use_trace:
        trace_module.start_trace()

    record = {"error": None, "session": None, "trace": "", "crashed": None, "note": None}
    try:
        record["session"] = run_agent(scenario["query"], wardrobe)
    except Exception as exc:  # noqa: BLE001 — a crash is a result worth logging
        record["crashed"] = f"{type(exc).__name__}: {exc}"
        record["traceback"] = traceback.format_exc()

    if use_trace:
        record["trace"] = trace_module.get_trace()

    return record


def _check_malformed_listing(use_trace):
    """Criterion 9 — a listing with no description shouldn't crash the branch.

    Real data always has a description, so this injects one malformed listing
    by mocking the MCP call site in agent.py — the same technique used to
    force ModelUnavailable in unit 4."""
    import unittest.mock as mock
    import agent as agent_module
    from utils.data_loader import get_example_wardrobe
    import trace as trace_module

    malformed = {
        "id": "test_malformed", "title": "Test Item With No Description",
        "description": None, "category": "tops", "style_tags": [], "size": "M",
        "condition": "fair", "price": 10.0, "colors": [], "brand": None,
        "platform": "depop",
    }

    if use_trace:
        trace_module.start_trace()

    record = {"error": None, "session": None, "trace": "", "crashed": None, "note": None}
    try:
        with mock.patch.object(agent_module, "call_tool", return_value=[malformed]):
            session = agent_module.run_agent("anything — search_listings is mocked", get_example_wardrobe())
        record["session"] = session
        ok = session.get("condition_flags") == [] and session.get("outfit_suggestion") is not None
        record["note"] = (
            f"condition_flags={session.get('condition_flags')!r}, "
            f"outfit_suggestion ran={session.get('outfit_suggestion') is not None}: "
            + ("PASS" if ok else "FAIL")
        )
    except Exception as exc:  # noqa: BLE001 — a crash here is exactly what criterion 9 checks for
        record["crashed"] = f"{type(exc).__name__}: {exc}"
        record["traceback"] = traceback.format_exc()

    if use_trace:
        record["trace"] = trace_module.get_trace()

    return record


def _check_log_record(use_trace):
    """Criterion 10 — every run leaves exactly one log record, success or
    failure. Runs 3 successes and 2 failures (one natural empty-search, one
    forced ModelUnavailable), then checks logs/run_log.jsonl grew by exactly
    5 records with the right outcome field on each."""
    import unittest.mock as mock
    import agent as agent_module
    import instrumentation
    from generate import ModelUnavailable
    from utils.data_loader import get_example_wardrobe
    import trace as trace_module

    if use_trace:
        trace_module.start_trace()

    wardrobe = get_example_wardrobe()
    before = len(instrumentation.read_log())

    # 3 runs expected to complete normally, 2 expected to end in session["error"]
    # (one via the natural empty-search branch, one via a forced ModelUnavailable) —
    # matching criterion 10's "3 that complete normally and 2 that end in error".
    success_queries = [
        "vintage graphic tee under $30",
        "90s track jacket in size M",
        "silk slip dress in midi length under $40",
    ]
    expect_error = []
    for query in success_queries:
        s = agent_module.run_agent(query, wardrobe)
        expect_error.append(bool(s.get("error")))

    s = agent_module.run_agent("designer ballgown size XXS under $5", wardrobe)
    expect_error.append(bool(s.get("error")))

    with mock.patch.object(agent_module, "suggest_outfit", side_effect=ModelUnavailable("forced for criterion 10")):
        s = agent_module.run_agent("corduroy pants under $25", wardrobe)
    expect_error.append(bool(s.get("error")))

    after_records = instrumentation.read_log()
    new_records = after_records[before:]
    grew_correctly = len(new_records) == len(expect_error)
    correct = grew_correctly and [
        (rec["outcome"] == "error") == expected
        for rec, expected in zip(new_records, expect_error)
    ]
    score = sum(correct) if grew_correctly else 0
    ok = grew_correctly and score == len(expect_error)

    record = {
        "error": None,
        "session": None,
        "trace": trace_module.get_trace() if use_trace else "",
        "crashed": None,
        "note": (
            f"log grew by {len(new_records)} (expected {len(expect_error)}), "
            f"{score}/{len(expect_error)} records had the correct outcome field — "
            + ("PASS" if ok else "FAIL")
        ),
    }
    return record


def main():
    parser = argparse.ArgumentParser(description="Run the scenarios and log the results.")
    parser.add_argument("--tries", "--trials", type=int, default=5, dest="tries",
                        help="tries per scenario (default 5, matching your criteria)")
    parser.add_argument("--label", default="", help="a name for this run, e.g. 'before'")
    args = parser.parse_args()

    problems = scenario_module.validate()
    if problems:
        print("scenarios.py has problems:\n", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        sys.exit(1)

    if not scenario_module.SCENARIOS:
        print("scenarios.py is empty. Milestone 3 starts by filling it in.", file=sys.stderr)
        sys.exit(1)

    if args.tries < 5:
        print(f"⚠️  {args.tries} tries. Your criteria are written out of five.\n")

    # Caching off. Five tries have to be five real answers.
    config.CACHE_ENABLED = False
    print("Cache is OFF for this run — that's deliberate.\n")

    rows = []
    for scenario in scenario_module.SCENARIOS:
        if scenario.get("direct_check"):
            print(f"{scenario['name']}  (direct check: {scenario['direct_check']})")
        else:
            print(f"{scenario['name']}  ({scenario['wardrobe']} wardrobe)")
            print(f"  query: {scenario['query']}")

        tries = []
        for attempt in range(1, args.tries + 1):
            record = run_once(scenario)
            tries.append(record)

            if record["crashed"]:
                print(f"  try {attempt}: CRASHED — {record['crashed']}")
            elif record.get("note"):
                print(f"  try {attempt}: {record['note']}")
            else:
                session = record["session"] or {}
                if session.get("error"):
                    print(f"  try {attempt}: stopped early — {str(session['error'])[:60]}")
                else:
                    card = (session.get("fit_card") or "")
                    print(f"  try {attempt}: completed — fit card {len(card)} chars")

        rows.append({"scenario": scenario, "tries": tries})
        print()

    write_report(rows, args)


def write_report(rows, args):
    config.RESULTS_DIR.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    label = f"_{args.label}" if args.label else ""
    path = config.RESULTS_DIR / f"run_{stamp}{label}.md"

    n = args.tries
    headers = " | ".join(f"Try {i}" for i in range(1, n + 1))
    divider = "|".join(["---"] * n)

    lines = [
        f"# Run log{f' — {args.label}' if args.label else ''}",
        "",
        "- Produced by: `run_eval.py::main`",
        "- Loop: `agent.py::run_agent` · tools: `tools.py`",
        f"- Tries per scenario: {n}, caching off",
        f"- Temperature: {config.TEMPERATURE}",
        f"- When: {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "Paste the table below into your README. Fill in the Criterion and",
        "Target columns from `criteria.md`, then mark each try PASS or FAIL",
        "from the output underneath and count them for the Verdict.",
        "",
        f"| Criterion | Target | {headers} | Verdict |",
        f"|---|---|{divider}|---|",
    ]

    for row in rows:
        scenario = row["scenario"]
        number = scenario.get("criterion")
        # A scenario with "criterion": None is a diagnostic run, not one of
        # your five. It's marked so you don't paste an unnumbered row into a
        # table the README asks you to number 1-5.
        label_text = (
            f"{number}. {scenario['name']}"
            if number
            else f"{scenario['name']} _(diagnostic — not one of your five)_"
        )
        lines.append(f"| {label_text} |  | {' | '.join([' '] * n)} |  |")

    lines += [
        "",
        "> The Try and Verdict columns are blank on purpose. Whether a try",
        "> passed depends on the criterion you wrote, so it's yours to decide.",
        "> Count the passes, then read that count against your target: a row",
        "> targeting 4 of 5 with three PASS cells is MISSED (3/5).",
        "",
        "---",
        "",
        "## What actually happened",
        "",
        "Real output, as text. Paste the relevant parts into your README —",
        "the rubric asks for output, not a description of it.",
        "",
    ]

    for row in rows:
        scenario = row["scenario"]
        if scenario.get("direct_check"):
            lines += [f"### {scenario['name']}", "",
                      f"- Direct check: `{scenario['direct_check']}`", ""]
        else:
            lines += [f"### {scenario['name']}", "",
                      f"- Query: `{scenario['query']}`",
                      f"- Wardrobe: {scenario['wardrobe']}", ""]

        for i, record in enumerate(row["tries"], 1):
            lines.append(f"**Try {i}**")
            lines.append("")

            if record["crashed"]:
                lines += ["Crashed:", "", "```", record["crashed"], "```", ""]
                continue

            if record.get("note"):
                lines += ["Note:", "", "```", record["note"], "```", ""]

            session = record["session"] or {}
            item = session.get("selected_item") or {}
            lines += [
                f"- stopped early: {'yes — ' + str(session.get('error')) if session.get('error') else 'no'}",
                f"- selected_item: {item.get('title', '(none)')}"
                + (f" (${item.get('price')}, {item.get('platform')})" if item else ""),
                f"- search_results: {len(session.get('search_results') or [])}",
                "",
            ]
            if session.get("outfit_suggestion"):
                lines += ["Outfit suggestion:", "", "```",
                          str(session["outfit_suggestion"]), "```", ""]
            if session.get("fit_card"):
                lines += ["Fit card:", "", "```", str(session["fit_card"]), "```", ""]
            if record["trace"]:
                lines += ["Trace:", "", "```", record["trace"], "```", ""]

    path.write_text("\n".join(lines), encoding="utf-8")

    import generate

    print(f"Wrote {path.relative_to(config.ROOT)}")
    print(generate.usage())
    print("\nCommit this file. It's the evidence the test actually happened.")

    if not any(r["tries"][0]["trace"] for r in rows):
        print(
            "\nNote: no trace was captured. You haven't added trace.step() calls\n"
            "to run_agent() yet — that's Milestone 2, and the trace is required\n"
            "evidence worth a point."
        )


if __name__ == "__main__":
    main()
