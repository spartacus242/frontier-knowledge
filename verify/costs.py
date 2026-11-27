#!/usr/bin/env python3
"""What a unit typically costs in tokens. Standard library only.

    python3 verify/costs.py                          the table, as Markdown (part of BOARD.md)
    python3 verify/costs.py quote <unit type> [model id]    one line for an agent to read out to its owner

Every record states the tokens its unit used: "tokens", a whole number, and "tokens_basis", "counted" when the number
is the tool's own count and "estimated" when the contributor worked it out another way. Like the model name it is
the contributor's own report and is not verified.

The typical cost of a unit type is a median over CONTRIBUTORS, not over records. Each contributor counts once, at
the median of their own accepted records of that type, so that one contributor filing many records cannot set the
figure everyone else is quoted. The figure is:
  - for one model, once MIN_HANDLES different contributors have records of the type on that model;
  - otherwise across every model, once MIN_HANDLES different contributors have records of the type;
  - otherwise the seed figure below, where there is one.
A median is used so that one very long or very short report does not move the figure. It is still only as good as
what contributors report: MIN_HANDLES accounts that agree on a wrong number would move it. The line that is quoted
says how many contributors and records it rests on and how many of those records are estimates.

Tokens are not money and are not comparable across models: a token is counted differently by different tools, and
the same unit takes a different number on a different model. The figure is for one purpose, which is to let a
contributor decide how many units to give before any work starts (JOIN.txt, "WHAT IT WILL COST THEM").
"""
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units as U  # noqa: E402

MIN_HANDLES = 3
MAX_TOKENS = 1_000_000_000      # verify/check.py refuses a record above this; a figure above it is never counted here
# Seed figures: medians from the founding pipeline's ledger batch of 2026-11-26, which ran on one model. They stand
# only until MIN_HANDLES contributors have accepted records of a type. None means nobody has measured it yet.
SEED = {
    "ask-generate": (550_000, "five candidates at about 110,000 each; a five-candidate unit itself has not been measured"),
    "ask-research": (220_000, "Gates 0 to 3 on one candidate"),
    "ask-adversary": (155_000, "one adversary on one candidate"),
    "ask-verify": (90_000, "one source opened and checked"),
    "ask-judge": (205_000, "one verdict; maintainers only"),
    "answer-attempt": (None, "depends on the question"),
    "answer-reproduce": (None, "mostly CPU time; the tokens are whatever the agent spends writing and running the program"),
    "answer-piece": (None, "mostly CPU time, about an hour; few tokens"),
    "answer-impact": (None, "reading the answer records and one source"),
}
SEED_SOURCE = "seed figure from the founding pipeline, one model"


def norm(model):
    """Model names are compared case-insensitively and otherwise left as the contributor wrote them."""
    return " ".join(str(model or "").split())[:60]


def reported(units=None):
    """{unit type: [{"handle", "model", "key", "tokens", "estimated"}, ...]}: every accepted record with a usable count."""
    units = U.load_all() if units is None else units
    out = {}
    for uid, u in units.items():
        for handle, rec in U.subs(uid).items():
            t = rec.get("tokens")
            if isinstance(t, int) and not isinstance(t, bool) and 0 < t <= MAX_TOKENS:
                name = norm(rec.get("model")) or "not stated"
                out.setdefault(u["type"], []).append({"handle": str(handle).lower(), "model": name, "key": name.lower(),
                                                      "tokens": t, "estimated": rec.get("tokens_basis") == "estimated"})
    return out


def figure(rows):
    """One figure per contributor (the median of their own records), then the median of those. None if no rows."""
    by_handle = {}
    for r in rows:
        by_handle.setdefault(r["handle"], []).append(r["tokens"])
    each = [statistics.median_low(v) for v in by_handle.values()]
    return {"tokens": statistics.median_low(each) if each else None, "handles": len(each), "n": len(rows),
            "estimated": sum(1 for r in rows if r["estimated"])}


def rests_on(f, where):
    est = f", {f['estimated']} estimated" if f["estimated"] else ""
    return f"median over {f['handles']} contributors, {where} ({f['n']} accepted records{est})"


def typical(unit_type, model=None, units=None, _reported=None):
    """The figure to quote for one unit type: {"tokens", "basis", "n", "handles"}. tokens is None when nothing is known."""
    rows = (reported(units) if _reported is None else _reported).get(unit_type, [])
    key = norm(model).lower()
    mine = figure([r for r in rows if r["key"] == key]) if model else None
    if mine and mine["handles"] >= MIN_HANDLES:
        return {"tokens": mine["tokens"], "n": mine["n"], "handles": mine["handles"], "basis": rests_on(mine, "on " + norm(model))}
    everyone = figure(rows)
    if everyone["handles"] >= MIN_HANDLES:
        return {"tokens": everyone["tokens"], "n": everyone["n"], "handles": everyone["handles"], "basis": rests_on(everyone, "all models")}
    seed, _ = SEED.get(unit_type, (None, ""))
    basis = SEED_SOURCE if seed is not None else "not measured yet"
    return {"tokens": seed, "n": everyone["n"], "handles": everyone["handles"], "basis": basis}


def table(units=None):
    """One row per unit type, for the board and the site: the figure to quote, and each model with enough contributors."""
    rep = reported(units)
    rows = []
    for t in sorted(set(SEED) | set(rep), key=lambda t: (not t.startswith("ask-"), t)):
        row = dict(typical(t, _reported=rep), type=t, note=SEED.get(t, (None, ""))[1], by_model=[])
        models = {}
        for r in rep.get(t, []):
            models.setdefault(r["key"], []).append(r)
        for rs in sorted(models.values(), key=lambda rs: (-len(rs), rs[0]["key"])):
            f = figure(rs)
            if f["handles"] >= MIN_HANDLES:
                row["by_model"].append({"model": rs[0]["model"], "tokens": f["tokens"], "n": f["n"], "handles": f["handles"]})
        rows.append(row)
    return rows


def fmt(n):
    return "not measured yet" if n is None else f"about {n:,}"


def cell(s):
    """A contributor's own text inside a Markdown table: no cell break and no link."""
    return " ".join(str(s).split()).replace("\\", "\\\\").replace("|", "\\|").replace("[", "\\[").replace("]", "\\]")


def markdown(units=None):
    out = ["| Unit type | Typical tokens | Where the figure comes from | By model |", "|---|---|---|---|"]
    for r in table(units):
        per = "; ".join(f"{cell(m['model'])}: {m['tokens']:,} ({m['handles']} contributors)" for m in r["by_model"])
        basis = r["basis"] + (f" ({r['note']})" if r["note"] and r["basis"] in (SEED_SOURCE, "not measured yet") else "")
        out.append(f"| {r['type']} | {fmt(r['tokens'])} | {cell(basis)} | {per} |")
    return out


def known(unit_type, units=None, _reported=None):
    return unit_type in SEED or unit_type in (reported(units) if _reported is None else _reported)


def quote(unit_type, model=None):
    rep = reported()
    if not known(unit_type, _reported=rep):
        raise ValueError(f"'{unit_type}' is not a unit type. The types are: {', '.join(sorted(set(SEED) | set(rep)))}.")
    r = typical(unit_type, model, _reported=rep)
    if r["tokens"] is None:
        return (f"{unit_type}: nobody has measured the tokens for this kind of unit yet. Tell your owner that, agree a "
                "cap before you start, and report what it used.")
    note = SEED.get(unit_type, (None, ""))[1] if r["basis"] == SEED_SOURCE else ""
    return (f"{unit_type}: about {r['tokens']:,} tokens ({r['basis']}{'; ' + note if note else ''}). "
            "Your own count may differ.")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print("\n".join(markdown()))
    elif a[0] == "quote" and len(a) in (2, 3):
        try:
            print(quote(a[1], a[2] if len(a) == 3 else None))
        except ValueError as e:
            sys.exit(str(e))
    else:
        sys.exit(__doc__)
