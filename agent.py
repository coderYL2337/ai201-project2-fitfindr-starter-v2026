"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re
import time

import config
import generate
import instrumentation
import trace
# from tools import search_listings, suggest_outfit, create_fit_card
from mcp_client import call_tool
from tools import suggest_outfit, create_fit_card, flag_condition_issues
from generate import ModelUnavailable


# ── query parsing ─────────────────────────────────────────────────────────────

_PRICE_RE = re.compile(r"under\s*\$?\s*(\d+(?:\.\d+)?)", re.I)
_SIZE_RE = re.compile(r"\bsize\s+([a-zA-Z0-9/]+)", re.I)


def _parse_query(query: str) -> dict:
    """Regex — pull a price ceiling and a size out of the query, whatever's
    left becomes the free-text description."""
    remainder = query
    max_price = None
    size = None

    price_match = _PRICE_RE.search(remainder)
    if price_match:
        max_price = float(price_match.group(1))
        remainder = remainder[: price_match.start()] + remainder[price_match.end():]

    size_match = _SIZE_RE.search(remainder)
    if size_match:
        size = size_match.group(1)
        remainder = remainder[: size_match.start()] + remainder[size_match.end():]

    description = re.sub(r"\s+", " ", remainder).strip(" ,.")
    return {"description": description, "size": size, "max_price": max_price}


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "condition_flags": [],       # what flag_condition_issues returned for the selected item
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    ─────────────────────────────────────────────────────────────────────────
    TODO — build this, following the branch rule you wrote in Milestone 2.

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings() with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - put a message in session["error"] saying what the user could
                change — "No results" is not that message
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      7. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      8. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.

    Every call also appends one structured record to config.LOG_FILE via
    `instrumentation` — success or failure, so a run that errors still leaves
    a trace of having happened. See instrumentation.py.
    """
    start = time.monotonic()
    calls_before = generate.call_count()
    cache_before = generate.cache_hit_count()
    tokens_before = generate.token_counts()["total"]

    session = new_session(query, wardrobe)
    try:
        _run_loop(query, wardrobe, session)
    except Exception as exc:
        session["error"] = session.get("error") or str(exc)
        raise
    finally:
        record = instrumentation.build_record(
            query,
            session,
            duration_seconds=time.monotonic() - start,
            model_calls=generate.call_count() - calls_before,
            cache_hits=generate.cache_hit_count() - cache_before,
            tokens_total=generate.token_counts()["total"] - tokens_before,
        )
        instrumentation.log_run(record)

    return session


def _run_loop(query: str, wardrobe: dict, session: dict) -> None:
    """The actual planning loop — mutates `session` in place. Split out of
    run_agent() so timing/logging wraps every exit, including an uncaught
    exception."""
    trace.check_iterations(1)

    session["parsed"] = _parse_query(query)

    # results = search_listings(
    #     session["parsed"]["description"],
    #     size=session["parsed"]["size"],
    #     max_price=session["parsed"]["max_price"],
    # )
    search_inputs = {
        "description": session["parsed"]["description"],
        "size": session["parsed"]["size"],
        "max_price": session["parsed"]["max_price"],
    }
    results = call_tool("search_listings", search_inputs)
    session["search_results"] = results
    trace.step("search_listings (via MCP)", inputs=search_inputs, returned=results)

    # THE BRANCH: nothing matched, stop before suggest_outfit / create_fit_card.
    if not results:
        session["error"] = (
            "No listings matched. Try a higher price ceiling, a different "
            "size, or fewer keywords in the description."
        )
        trace.step("branch", note="empty search results, stopping before suggest_outfit")
        return

    session["selected_item"] = results[0]

    session["condition_flags"] = flag_condition_issues(session["selected_item"])
    trace.step(
        "flag_condition_issues",
        inputs={"listing": session["selected_item"]},
        returned=session["condition_flags"],
    )

    # SECOND BRANCH: the model is unreachable, stop with a message instead of a stack trace.
    try:
        session["outfit_suggestion"] = suggest_outfit(session["selected_item"], wardrobe)
        trace.step(
            "suggest_outfit",
            inputs={"selected_item": session["selected_item"], "wardrobe": wardrobe},
            returned=session["outfit_suggestion"],
        )

        session["fit_card"] = create_fit_card(
            session["outfit_suggestion"], session["selected_item"]
        )
        trace.step(
            "create_fit_card",
            inputs={"outfit": session["outfit_suggestion"], "item": session["selected_item"]},
            returned=session["fit_card"],
        )
    except ModelUnavailable as exc:
        session["error"] = f"The model couldn't be reached: {exc}"
        trace.step("branch", note="model unavailable, stopping before the rest of the loop")


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  condition flags: {session['condition_flags']}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
