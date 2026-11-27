#!/usr/bin/env python3
"""The weekly token budget, and what the next ledger run takes. Standard library only.

    python3 -I ledger/tools/next-run.py status                 balance, RUN, WAIT or HOLD, next area and methods; writes nothing
    python3 -I ledger/tools/next-run.py wake <YYYY-MM-DD>      log this week's wake, add the cap, print RUN or WAIT
    python3 -I ledger/tools/next-run.py run <YYYY-MM-DD-HHMM> <run tokens> <checking tokens>   log a run that has ended
    python3 -I ledger/tools/next-run.py selftest               check the arithmetic and the rotations on made-up logs

LEDGER.md is the rule and this is its arithmetic (Parameters: WEEKLY TOKEN CAP, RUN ESTIMATE, CADENCE; "Where
candidates come from", rule 5). The numbers are read from LEDGER.md, so a change there needs no change here.

  balance   starts at 0. The first wake of each budget week adds the cap, up to a ceiling of two caps; a later wake
            in the same week adds nothing. A budget week starts on the weekday CADENCE names (Thursday), so a wake
            that comes a day or two late still belongs to its own week and the next one is not short-changed.
            Each run subtracts what it used, checking included, and may leave a debt.
  RUN       when the balance after the wake is at least RUN ESTIMATE; otherwise WAIT, and no batch starts.
  one run   a wake that says RUN opens a run, and the run's own row closes it. While one is open no further wake is
            logged, so a run that died is accounted for before another starts. Log what it used with `run`, 0 and 0
            if it never started, under the date and time of the wake that opened it.
  area      the one after the last row of the log in ledger/rotation.md, in the five-turn cycle.
  methods   the next four in LEDGER.md's order after the last one used ("Drafting methods used" in rotation.md).

This script is the only writer of the table in ledger/usage.md. It checks every "Balance after" cell against its own
replay and stops if one differs, so a hand edit is found at the next wake. It reads the Note cell of a wake row to
tell a RUN from a WAIT, so that cell is part of the account too.
"""
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
CYCLE = ["mathematics", "physics", "computer science", "biology", "medicine"]
PER_RUN = 4
HEADER = "| Date (UTC) | Event | Tokens | Balance after | Note |"
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def read(*parts):
    with open(os.path.join(REPO, *parts), encoding="utf-8") as f:
        return f.read()


def number(text):
    return int(re.sub(r"[,+\s]", "", text))


def fmt(n):
    return f"{n:,}"


def parameters(ledger):
    cap = re.search(r"\*\*WEEKLY TOKEN CAP[^*]*?: ([\d,]+) tokens\.?\*\*", ledger)
    est = re.search(r"\*\*RUN ESTIMATE: ([\d,]+) tokens\*\*", ledger)
    if not cap or not est:
        sys.exit("LEDGER.md: could not read WEEKLY TOKEN CAP or RUN ESTIMATE from Parameters")
    return check_parameters(number(cap.group(1)), number(est.group(1)))


def check_parameters(cap, estimate):
    """The balance stops at two caps, so an estimate above that could never be met and every wake would say WAIT."""
    if cap <= 0 or estimate <= 0:
        sys.exit("LEDGER.md: WEEKLY TOKEN CAP and RUN ESTIMATE must both be above zero")
    if estimate > 2 * cap:
        sys.exit(f"LEDGER.md: RUN ESTIMATE ({fmt(estimate)}) is more than twice WEEKLY TOKEN CAP ({fmt(cap)}). The balance "
                 "stops at two caps, so no run could ever start. Change one of them in LEDGER.md.")
    return cap, estimate


def wake_day(ledger):
    """The weekday a budget week starts on, Monday 0: the first weekday named in LEDGER.md's CADENCE line."""
    m = re.search(r"^- \*\*CADENCE[^\n]*", ledger, re.M)
    day = re.search("|".join(DAYS), m.group(0)) if m else None
    if not day:
        sys.exit("LEDGER.md: could not read the wake day from the CADENCE line in Parameters")
    return DAYS.index(day.group(0))


def parse_date(text):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        sys.exit(f"'{text}' is not a date written YYYY-MM-DD")
    try:
        return datetime.date.fromisoformat(text)
    except ValueError:
        sys.exit(f"'{text}' is not a date in the calendar")


def week_start(date, first_day):
    return date - datetime.timedelta(days=(date.weekday() - first_day) % 7)


def method_list(ledger):
    m = re.search(r"^## Where candidates come from.*?(?=^## )", ledger, re.S | re.M)
    if not m:
        sys.exit("LEDGER.md has no 'Where candidates come from' section")
    names = [x.lower() for x in re.findall(r"^- \*\*([^.(*]+?)(?: \([^)]*\))?\.\*\*", m.group(0), re.M)]
    if len(names) < PER_RUN:
        sys.exit(f"LEDGER.md lists only {len(names)} generation methods")
    return names


def table_rows(text, header_start):
    """The body rows of the first Markdown table whose header line starts with header_start."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line.startswith(header_start):
            rows = []
            for row in lines[i + 2:]:
                if not row.startswith("|"):
                    break
                rows.append([c.strip() for c in row.strip().strip("|").split("|")])
            return rows
    return None


def replay(usage):
    """Return (balance, date of the last wake that added the cap, rows). Stops on a cell that does not add up."""
    rows = table_rows(usage, "| Date (UTC) | Event |")
    if rows is None:
        sys.exit("ledger/usage.md: the log table was not found")
    balance, last_wake = 0, None
    for r in rows:
        if len(r) != 5:
            sys.exit(f"ledger/usage.md: a row does not have five cells: {r}")
        date, event, tokens, after = r[0], r[1], number(r[2]), number(r[3])
        if event == "wake":
            if tokens:
                balance = max(balance, min(balance + tokens, 2 * tokens))
                last_wake = parse_date(date)
        elif event.startswith("run "):
            balance += tokens          # a run row carries a negative number
        else:
            sys.exit(f"ledger/usage.md: unknown event '{event}'")
        if balance != after:
            sys.exit(f"ledger/usage.md: the row for {date} ({event}) says the balance is {fmt(after)}, "
                     f"but the rows above it add up to {fmt(balance)}. The table was edited by hand; correct it first.")
    return balance, last_wake, rows


def open_run(rows):
    """The date of a wake that said RUN and has no run row after it, or None."""
    opened = None
    for r in rows:
        if r[1] == "wake" and r[4].startswith("RUN"):
            opened = r[0]
        elif r[1].startswith("run "):
            opened = None
    return opened


def has_run(rows, batch):
    return any(r[1] == f"run {batch}" for r in rows)


def next_area(rotation):
    rows = table_rows(rotation, "| Batch (UTC) | Area |")
    if not rows:
        sys.exit("ledger/rotation.md: the area log was not found")
    last = rows[-1][1].lower()
    for i, a in enumerate(CYCLE):
        if last.startswith(a):
            return CYCLE[(i + 1) % len(CYCLE)]
    return CYCLE[0]        # the open turn, or a label from an older cycle: the pass starts again at mathematics


def next_methods(rotation, methods):
    rows = table_rows(rotation, "| Batch (UTC) | Drafting methods |")
    start = 0
    if rows:
        last = [m.strip().lower() for m in rows[-1][1].split(",")][-1]
        if last not in methods:
            sys.exit(f"ledger/rotation.md: the last method logged, '{last}', is not in LEDGER.md's list")
        start = methods.index(last) + 1
    return [methods[(start + k) % len(methods)] for k in range(PER_RUN)]


def add_row(usage, row):
    lines = usage.rstrip("\n").split("\n")
    i = next(k for k, line in enumerate(lines) if line.startswith("| Date (UTC) | Event |"))
    j = i + 2
    while j < len(lines) and lines[j].startswith("|"):
        j += 1
    lines.insert(j, "| " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n"


def decide(balance, estimate):
    return "RUN" if balance >= estimate else "WAIT"


def plan_wake(usage, cap, date, first_day=3):
    """What a wake on `date` does: (tokens added, balance after, note for a refusal or None)."""
    balance, last_wake, _ = replay(usage)
    if last_wake is not None and week_start(date, first_day) <= week_start(last_wake, first_day):
        return 0, balance, f"this budget week's cap was already added on {last_wake.isoformat()}"
    return cap, max(balance, min(balance + cap, 2 * cap)), None


def report(balance, estimate, area, methods):
    verdict = decide(balance, estimate)
    print(f"balance: {fmt(balance)} tokens; a run is estimated at {fmt(estimate)}")
    print(verdict)
    if verdict == "WAIT":
        print(f"short by {fmt(estimate - balance)} tokens; no batch starts at this wake")
    print(f"{'area' if verdict == 'RUN' else 'next area'}: {area}")
    print(f"{'methods' if verdict == 'RUN' else 'next methods'}: {', '.join(methods)}")
    if verdict == "RUN":
        print("runner args: " + json.dumps({"area": area, "methods": methods}))
    return verdict


def selftest():
    fails = []

    def check(name, got, want):
        ok = got == want
        print(f"{'ok  ' if ok else 'FAIL'} {name}" + ("" if ok else f": got {got!r}, expected {want!r}"))
        if not ok:
            fails.append(name)

    head = f"# x\n\n{HEADER}\n|---|---|---|---|---|\n"
    cap = 3_200_000
    check("empty log: balance 0", replay(head)[0], 0)
    check("first wake adds the cap", plan_wake(head, cap, datetime.date(2026, 12, 3))[:2], (cap, cap))
    u = add_row(head, ["2026-12-03", "wake", "+3,200,000", "3,200,000", "RUN"])
    u = add_row(u, ["2026-12-03", "run 2026-12-03-1233", "-3,500,000", "-300,000", "run 2,400,000 + checking 1,100,000"])
    check("an overrun leaves a debt", replay(u)[0], -300_000)
    check("a second wake in the same budget week adds nothing", plan_wake(u, cap, datetime.date(2026, 12, 5))[:2], (0, -300_000))
    check("the day before the next wake day is still the same week", plan_wake(u, cap, datetime.date(2026, 12, 9))[0], 0)
    late = add_row(head, ["2026-12-11", "wake", "+3,200,000", "3,200,000", "WAIT"])
    check("a wake one day late does not cost the next week its cap", plan_wake(late, cap, datetime.date(2026, 12, 17))[0], cap)
    check("a budget week can start on another day", plan_wake(late, cap, datetime.date(2026, 12, 14), 0)[0], cap)
    opened = add_row(head, ["2026-12-03", "wake", "+3,200,000", "3,200,000", "RUN: mathematics"])
    check("a RUN wake with no run row after it is an open run", open_run(replay(opened)[2]), "2026-12-03")
    closed = add_row(opened, ["2026-12-03", "run 2026-12-03-1233", "-0", "3,200,000", "run 0 + checking 0"])
    check("its run row closes it, even at 0 tokens", open_run(replay(closed)[2]), None)
    check("a WAIT wake opens nothing", open_run(replay(late)[2]), None)
    check("a batch already logged is found", (has_run(replay(closed)[2], "2026-12-03-1233"), has_run(replay(closed)[2], "2026-12-10-1233")), (True, False))

    def refused(name, f):
        try:
            f()
            check(name, "accepted", "refused")
        except SystemExit:
            check(name, "refused", "refused")

    refused("an estimate above two caps is refused", lambda: check_parameters(cap, 2 * cap + 1))
    check("an estimate of exactly two caps is allowed", check_parameters(cap, 2 * cap), (cap, 2 * cap))
    refused("a date without hyphens is refused", lambda: parse_date("20261203"))
    refused("a date that is not in the calendar is refused", lambda: parse_date("2026-02-30"))
    added, bal, _ = plan_wake(u, cap, datetime.date(2026, 12, 10))
    check("the next wake pays the debt first", (added, bal, decide(bal, cap)), (cap, 2_900_000, "WAIT"))
    u = add_row(u, ["2026-12-10", "wake", "+3,200,000", "2,900,000", "WAIT"])
    added, bal, _ = plan_wake(u, cap, datetime.date(2026, 12, 17))
    check("the wake after that runs", (bal, decide(bal, cap)), (6_100_000, "RUN"))
    u = add_row(u, ["2026-12-17", "wake", "+3,200,000", "6,100,000", "RUN"])
    added, bal, _ = plan_wake(u, cap, datetime.date(2026, 12, 24))
    check("the balance stops at two caps", bal, 6_400_000)
    bad = add_row(head, ["2026-12-03", "wake", "+3,200,000", "3,000,000", "edited"])
    try:
        replay(bad)
        check("a hand-edited balance is refused", "accepted", "refused")
    except SystemExit:
        check("a hand-edited balance is refused", "refused", "refused")
    rot = ("| Batch (UTC) | Area | Entries |\n|---|---|---|\n| 2026-10-30 13:04 | medicine | a |\n| 2026-11-26 00:35 | open | b |\n\n"
           "## Drafting methods used\n\n| Batch (UTC) | Drafting methods |\n|---|---|\n")
    ms = ["m%d" % k for k in range(1, 15)]
    check("after the open turn comes mathematics", next_area(rot), "mathematics")
    check("after mathematics comes physics", next_area(rot.replace("| open |", "| mathematics |")), "physics")
    check("after medicine comes mathematics", next_area(rot.replace("| open |", "| medicine |")), "mathematics")
    check("the first run takes the first four methods", next_methods(rot, ms), ["m1", "m2", "m3", "m4"])
    check("the rotation wraps at the end of the list", next_methods(rot + "| x | m9, m10, m11, m12 |\n", ms), ["m13", "m14", "m1", "m2"])
    ledger = read("LEDGER.md")
    check("LEDGER.md's cap and estimate are readable", all(isinstance(x, int) and x > 0 for x in parameters(ledger)), True)
    check("LEDGER.md lists fourteen methods", len(method_list(ledger)), 14)
    check("LEDGER.md's CADENCE names the wake day", DAYS[wake_day(ledger)], "Thursday")
    replay(read("ledger", "usage.md"))
    check("ledger/usage.md adds up", True, True)
    check("ledger/rotation.md gives an area and four methods",
          (next_area(read("ledger", "rotation.md")) in CYCLE, len(next_methods(read("ledger", "rotation.md"), method_list(ledger)))), (True, 4))
    print("SELFTEST PASSED" if not fails else f"SELFTEST FAILED: {len(fails)}")
    sys.exit(1 if fails else 0)


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        sys.exit(__doc__)
    if argv[0] == "selftest":
        selftest()
    ledger, usage, rotation = read("LEDGER.md"), read("ledger", "usage.md"), read("ledger", "rotation.md")
    cap, estimate = parameters(ledger)
    area, methods = next_area(rotation), next_methods(rotation, method_list(ledger))
    path = os.path.join(REPO, "ledger", "usage.md")
    first_day = wake_day(ledger)
    balance, last_wake, rows = replay(usage)
    opened = open_run(rows)
    unlogged = (f"The wake of {opened} said RUN and ledger/usage.md has no run row after it. Finish that run, or log what "
                "it used before it stopped: next-run.py run <YYYY-MM-DD-HHMM> <run tokens> <checking tokens>, with 0 and 0 "
                "if it never started.")
    if argv[0] == "status" and len(argv) == 1:
        print(f"last wake that added the cap: {last_wake.isoformat() if last_wake else 'none yet'}; weekly cap {fmt(cap)}; "
              f"a budget week starts on {DAYS[first_day]}")
        if opened:
            print(f"balance: {fmt(balance)} tokens; a run is estimated at {fmt(estimate)}")
            print("HOLD")
            print(unlogged + " No wake is logged and no batch starts until then.")
            print(f"next area: {area}")
            print(f"next methods: {', '.join(methods)}")
        else:
            report(balance, estimate, area, methods)
    elif argv[0] == "wake" and len(argv) == 2:
        date = parse_date(argv[1])
        if any(r[0] == argv[1] and r[1] == "wake" for r in rows):
            sys.exit(f"ledger/usage.md already has a wake row for {argv[1]}; use status")
        if rows and date < parse_date(rows[-1][0]):
            sys.exit(f"{argv[1]} is before the last row of ledger/usage.md ({rows[-1][0]}); rows are added in date order")
        if opened:
            sys.exit("HOLD: no wake logged and no batch starts. " + unlogged)
        added, balance, refusal = plan_wake(usage, cap, date, first_day)
        verdict = decide(balance, estimate)
        note = f"{verdict}: {area}" if verdict == "RUN" else verdict
        if refusal:
            note += f"; nothing added, {refusal}"
            print(f"nothing added: {refusal}")
        with open(path, "w", encoding="utf-8") as f:
            f.write(add_row(usage, [argv[1], "wake", f"+{fmt(added)}", fmt(balance), note]))
        report(balance, estimate, area, methods)
    elif argv[0] == "run" and len(argv) == 4:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}-\d{4}", argv[1]):
            sys.exit(f"'{argv[1]}' is not a batch name written YYYY-MM-DD-HHMM")
        if has_run(rows, argv[1]):
            sys.exit(f"ledger/usage.md already has a row for run {argv[1]}; a run is logged once")
        if not all(re.fullmatch(r"[\d,]+", x) for x in argv[2:4]):
            sys.exit("token counts are whole numbers, zero or more")
        run_tokens, check_tokens = number(argv[2]), number(argv[3])
        balance = balance - run_tokens - check_tokens
        date = argv[1][:10]
        parse_date(date)
        with open(path, "w", encoding="utf-8") as f:
            f.write(add_row(usage, [date, f"run {argv[1]}", f"-{fmt(run_tokens + check_tokens)}", fmt(balance),
                                    f"run {fmt(run_tokens)} + checking {fmt(check_tokens)}"]))
        print(f"logged {argv[1]}: {fmt(run_tokens + check_tokens)} tokens; balance now {fmt(balance)}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
