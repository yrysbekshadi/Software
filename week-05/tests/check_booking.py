#!/usr/bin/env python3
"""
check_booking.py - the Week 05 checker. DO NOT EDIT: the grader runs its own copy over your files.

    python tests/check_booking.py          # from inside week-05/
    python tests/check_booking.py --json   # machine-readable, for the grading pipeline

What it checks (Path A - Python, 32 checks):

    F1-F10   your final can_book in code/booking.py, against AC1-AC5
    O1       the assistant's first version is kept in code/original/booking_v1.py
    S1-S2    your own suite code/test_booking.py: at least 11 tests, green on your own code
    M1-M10   your suite is run against ten FAULTY versions of can_book. Each one breaks
             exactly one acceptance criterion. PASS = at least one of your tests failed on
             it ("caught"). FAIL = the fault survived all your tests.
    L1-L9    lab-report.md has the sections filled in

Path B (any other language, 13 checks): P1-P3 and O1 replace F, S and M - see README section 6.

It checks BEHAVIOUR and SHAPE, never the quality of your review. A clean run is the floor,
not the grade. The faulty versions are stored packed on purpose: you are meant to derive
tests from AC1-AC5, not from reading the faults.

Verdicts:
    PASS   the check found what it was looking for
    FAIL   it runs, but the result is wrong or the content is not there
    ERROR  it could not run: a file or the function is missing, the signature is wrong,
           or nothing is implemented yet

Exit codes: 0 = no FAIL and no ERROR - 1 = at least one FAIL or ERROR - 3 = wrong directory.
Standard library only.
"""

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zlib

CODE = "code"
IMPL = os.path.join(CODE, "booking.py")
SUITE = os.path.join(CODE, "test_booking.py")
ORIGINAL_DIR = os.path.join(CODE, "original")
V1 = os.path.join(ORIGINAL_DIR, "booking_v1.py")
REPORT = "lab-report.md"

MIN_TESTS = 11
WORDS_MIN, WORDS_MAX = 120, 180
RUN_TIMEOUT = 5          # seconds, per run of your code or your suite

FAULTY_VERSIONS = (
    "eNrtll1rgzAUhv/KIVcKbqi1+5CmMMZ6t5uxu7aMqHGElqTEyAZj/31J0U6YzHaudl3NXQ7vezznPEYzfUMsQSGg"
    "ew85gGLJFJVMcBO6uV3HMpHLmJrAjCc0hZjwp0iIhZUpIpUDlCcOcPHiQLQU8YLqHX1lmWL82Q5nHPRiqRYosFwY"
    "YVjbYGR8ZusFgVvqzJJU5ZLDhCwzunGXHv2YJqlJe1YYxuD5bpOhqPpbWSokEN0gML5prmKoVBgB0QWYIsZAKpL6"
    "vEXkUeY6gN4d2ODwD4BjWwz4hDgMOuaAf3IuTglIUAPE/2Pfqd154OMFMqwBMjh6II08uh/0Rc2gg/8/6N9+8XEV"
    "CG5F5LInsiORaejN93tKrnomrU4JqfYWgdF/Nhm1AHNdA2bYg9nz76TMdU5WK+2xKkO17SZkntsz41vMNhNSWfaB"
    "7gUPd5MvlHpE3d7S5h92vRuO"
)

# --------------------------------------------------------------------------- the acceptance cases

BASE_NOW = 540
BASE_EXISTING = [(600, 660)]


def case(label, start, end, expected, now=BASE_NOW, blocked=False, existing=None):
    return {"label": label, "start": start, "end": end, "now": now, "blocked": blocked,
            "existing": [list(p) for p in (BASE_EXISTING if existing is None else existing)],
            "expected": expected}


GROUPS = [
    ("F1", "the six cases from the task table", "value", [
        case("touching", 660, 720, True),
        case("overlap", 630, 690, False),
        case("blocked", 660, 720, False, blocked=True),
        case("exactly 2 hours", 720, 840, True),
        case("over 2 hours", 720, 841, False),
        case("starts now", 540, 570, False),
    ]),
    ("F2", "AC1 time order and day bounds", "value", [
        case("zero length", 700, 700, False),
        case("reversed", 720, 700, False),
        case("ends exactly at 1440", 1380, 1440, True),
        case("ends after 1440", 1380, 1441, False),
        case("negative start", -30, 30, False),
    ]),
    ("F3", "AC1 the start is in the future", "value", [
        case("starts now", 540, 570, False),
        case("starts one minute after now", 541, 571, True),
        case("starts in the past", 500, 530, False),
        case("now is 0, start is 0", 0, 60, False, now=0),
        case("now is 0, start is 1", 1, 61, True, now=0),
    ]),
    ("F4", "AC2 at most 120 minutes", "value", [
        case("exactly 120", 720, 840, True),
        case("121", 720, 841, False),
        case("one minute", 720, 721, True),
    ]),
    ("F5", "AC3 a blocked room accepts nothing", "value", [
        case("blocked, otherwise valid", 660, 720, False, blocked=True),
        case("blocked, no bookings at all", 660, 720, False, blocked=True, existing=[]),
    ]),
    ("F6", "AC4 every kind of overlap is rejected", "value", [
        case("partial, over the end", 630, 690, False),
        case("partial, over the start", 570, 630, False),
        case("inside the existing booking", 615, 645, False),
        case("contains the existing booking", 570, 690, False),
        case("identical to the existing booking", 600, 660, False),
    ]),
    ("F7", "AC4 touching endpoints are allowed", "value", [
        case("starts at the existing end", 660, 720, True),
        case("ends at the existing start", 570, 600, True),
        case("fits exactly between two", 660, 720, True, existing=[(600, 660), (720, 780)]),
    ]),
    ("F8", "AC4 every existing booking is checked", "value", [
        case("overlaps the second booking", 720, 780, False, existing=[(600, 660), (700, 760)]),
        case("overlaps one in an unsorted list", 610, 650, False, existing=[(900, 960), (600, 660)]),
        case("no bookings at all", 600, 660, True, existing=[]),
        case("free slot among three", 760, 800, True, existing=[(600, 660), (700, 760), (800, 860)]),
    ]),
    ("F9", "AC5 the result is a real Boolean", "type", [
        case("accepted request", 660, 720, True),
        case("rejected request", 630, 690, False),
        case("blocked room", 660, 720, False, blocked=True),
    ]),
    ("F10", "AC5 the inputs are left unchanged", "unchanged", [
        case("accepted request, unsorted bookings", 780, 840, True,
             existing=[(900, 960), (600, 660), (700, 760)]),
        case("rejected request, unsorted bookings", 610, 650, False,
             existing=[(900, 960), (600, 660), (700, 760)]),
    ]),
]

FAULT_TITLE = "your tests catch a fault in %s"

LAB_TITLES = {
    "L1": "report 1: tool, model and language",
    "L2": "report 2: the plan, and what you corrected",
    "L3": "report 3: v1 mapped to AC1-AC4",
    "L4": "report 4: at least %d of your tests listed" % MIN_TESTS,
    "L5": "report 5: debugging evidence",
    "L6": "report 6: the critique, each point judged",
    "L7": "report 7: change log",
    "L8": "report 8.1: real output of your suite",
    "L9": "report 10: conclusion of %d-%d words" % (WORDS_MIN, WORDS_MAX),
}

# Runs inside a separate process, so a crash, a print or an endless loop in your code
# cannot take the checker down with it.
DRIVER = r'''
import contextlib, importlib.util, io, json, sys
path = sys.argv[1]
cases = json.load(sys.stdin)
out = {"import_error": None, "has_function": False, "results": []}
fn = None
try:
    spec = importlib.util.spec_from_file_location("booking_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(mod)
    fn = getattr(mod, "can_book", None)
except BaseException as exc:
    out["import_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
if callable(fn):
    out["has_function"] = True
    for c in cases:
        existing = [tuple(p) for p in c["existing"]]
        snapshot = list(existing)
        r = {}
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                got = fn(c["start"], c["end"], c["now"], c["blocked"], existing)
            r["type"] = type(got).__name__
            r["repr"] = repr(got)[:60]
            try:
                r["equal"] = bool(got == c["expected"])
            except Exception:
                r["equal"] = False
            r["unchanged"] = existing == snapshot
            r["after"] = repr(existing)[:120]
        except BaseException as exc:
            r["exception"] = (type(exc).__name__ + ": " + str(exc)[:120]).rstrip(": ")
        out["results"].append(r)
sys.stdout.write("\n@@RESULT@@" + json.dumps(out))
'''


# Runs your suite the way `python -m unittest` discovers it, and reports each test's outcome,
# so a fault is judged by which tests caught it rather than by the suite as a whole.
SUITE_DRIVER = r'''
import contextlib, io, json, sys, unittest
out = {"load_error": None, "tests": {}}
sink = io.StringIO()
with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
    suite = unittest.TestLoader().discover(".", pattern="test*.py")

def walk(node):
    for item in node:
        if isinstance(item, unittest.TestSuite):
            yield from walk(item)
        else:
            yield item

listed = list(walk(suite))                  # before run(): a suite empties itself as it goes
with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
    result = unittest.TestResult()
    suite.run(result)
for test in listed:
    if type(test).__name__ == "_FailedTest" or test.id().startswith("unittest.loader"):
        out["load_error"] = test.id()
    out["tests"][test.id()] = "ok"
for kind, rows in (("fail", result.failures), ("error", result.errors),
                   ("fail", [(t, "") for t in result.unexpectedSuccesses])):
    for test, _ in rows:
        test = getattr(test, "test_case", test)          # a failing subTest fails its test
        out["tests"][test.id()] = kind
for test, _ in result.skipped:
    out["tests"][test.id()] = "skipped"
sys.stdout.write("\n@@RESULT@@" + json.dumps(out))
'''


# --------------------------------------------------------------------------- small helpers


class Results:
    def __init__(self):
        self.rows = []

    def add(self, cid, title, verdict, message):
        self.rows.append({"id": cid, "title": title, "verdict": verdict, "message": message})

    def counts(self):
        return {v: sum(1 for r in self.rows if r["verdict"] == v) for v in ("PASS", "FAIL", "ERROR")}


def read(path):
    try:
        return open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return None


def clean_env():
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.pop("PYTHONPATH", None)
    return env


def call_text(c):
    return "can_book(%d, %d, now=%d, blocked=%s, existing=%s)" % (
        c["start"], c["end"], c["now"], c["blocked"], [tuple(p) for p in c["existing"]])


def is_starter(text):
    """The shipped starter, or anything else that does not implement the function yet."""
    return text is None or not text.strip() or (
        "raise NotImplementedError" in text and len(re.findall(r"^\s*(?:if|for|while|return)\b", text, re.M)) == 0)


# --------------------------------------------------------------------------- F: the function


def run_cases(path):
    """Call can_book from `path` on every acceptance case. Returns (problem, results-by-case)."""
    flat = [c for _, _, _, cases in GROUPS for c in cases]
    try:
        proc = subprocess.run([sys.executable, "-c", DRIVER, os.path.abspath(path)],
                              input=json.dumps(flat), capture_output=True, text=True,
                              timeout=RUN_TIMEOUT * 2, env=clean_env())
    except subprocess.TimeoutExpired:
        return "it did not finish within %d seconds (an endless loop?)" % (RUN_TIMEOUT * 2), None
    if "@@RESULT@@" not in proc.stdout:
        tail = (proc.stderr or proc.stdout).strip().splitlines()[-1:] or ["no output"]
        return "it could not be run: " + tail[0][:160], None
    data = json.loads(proc.stdout.split("@@RESULT@@", 1)[1])
    if data["import_error"]:
        return "it could not be imported - " + data["import_error"], None
    if not data["has_function"]:
        return "it defines no function called can_book", None
    results = data["results"]
    raised = [r for r in results if "exception" in r]
    if len(raised) == len(results):
        return "can_book raised %s on every call - not implemented, or the signature changed" \
               % raised[0]["exception"], None
    return None, results


def judge_groups(results):
    """Turn per-case results into one verdict per F group: [(id, title, verdict, message)]."""
    out, i = [], 0
    for gid, title, kind, cases in GROUPS:
        chunk = results[i:i + len(cases)]
        i += len(cases)
        problem = None
        for c, r in zip(cases, chunk):
            if "exception" in r:
                problem = "%s raised %s" % (call_text(c), r["exception"])
            elif kind == "value" and not r["equal"]:
                problem = "%s returned %s, expected %s" % (call_text(c), r["repr"], c["expected"])
            elif kind == "type" and r["type"] != "bool":
                problem = "%s returned %s (%s) - the contract says True or False" \
                          % (call_text(c), r["repr"], r["type"])
            elif kind == "unchanged" and not r["unchanged"]:
                problem = "%s changed existing to %s" % (call_text(c), r["after"])
            if problem:
                break
        out.append((gid, title, "FAIL" if problem else "PASS",
                    problem or "%d of %d cases" % (len(cases), len(cases))))
    return out


def check_function(res, measured):
    if not os.path.exists(IMPL):
        problem, results = "code/booking.py not found", None
    else:
        problem, results = run_cases(IMPL)
    if problem:
        for gid, title, _, _ in GROUPS:
            res.add(gid, title, "ERROR", problem)
        measured["final"] = {"passes": [], "fails": [g[0] for g in GROUPS]}
        return False
    judged = judge_groups(results)
    for row in judged:
        res.add(*row)
    measured["final"] = {"passes": [r[0] for r in judged if r[2] == "PASS"],
                         "fails": [r[0] for r in judged if r[2] != "PASS"]}
    return True


# --------------------------------------------------------------------------- O: the first version


def normalise(text):
    return "\n".join(line.rstrip() for line in (text or "").strip().splitlines() if line.strip())


def check_original(res, measured):
    title = "the assistant's first version is kept"
    text = read(V1)
    if text is None:
        res.add("O1", title, "ERROR", "code/original/booking_v1.py not found - save v1 there BEFORE you edit anything")
        measured["v1"] = None
        return
    if is_starter(text) or "def can_book" not in text:
        res.add("O1", title, "FAIL", "code/original/booking_v1.py does not contain an implementation of can_book")
        measured["v1"] = None
        return
    problem, results = run_cases(V1)
    info = {"identical_to_final": normalise(text) == normalise(read(IMPL))}
    if problem:
        info["passes"], info["fails"], info["note"] = [], [g[0] for g in GROUPS], problem
    else:
        judged = judge_groups(results)
        info["passes"] = [r[0] for r in judged if r[2] == "PASS"]
        info["fails"] = [r[0] for r in judged if r[2] != "PASS"]
    measured["v1"] = info
    res.add("O1", title, "PASS", "v1 kept (%d lines)" % len(text.strip().splitlines()))


# --------------------------------------------------------------------------- S and M: your suite


def copy_code(dest):
    """A scratch copy of code/ without original/, so your suite can be run against other booking.py files."""
    shutil.copytree(CODE, dest, ignore=shutil.ignore_patterns("original", "__pycache__", ".*"))


def run_suite(folder):
    """python -m unittest -v inside `folder`. Returns (ran, green, summary) - ran is None if it never started."""
    try:
        proc = subprocess.run([sys.executable, "-m", "unittest", "-v"], cwd=folder,
                              capture_output=True, text=True, timeout=RUN_TIMEOUT, env=clean_env())
    except subprocess.TimeoutExpired:
        return None, False, "the suite did not finish within %d seconds" % RUN_TIMEOUT
    text = proc.stderr + proc.stdout
    if re.search(r"Failed to import test module|unittest\.loader\._FailedTest", text):
        why = re.findall(r"^(\w*(?:Error|Exception)\b.*)$", text, re.M)
        return None, False, "your test file could not be loaded: " + (why[-1][:120] if why else "import failed")
    ran = re.search(r"^Ran (\d+) tests?", text, re.M)
    if not ran:
        tail = text.strip().splitlines()[-1:] or ["no output"]
        return None, False, "unittest did not report a run: " + tail[0][:140]
    n = int(ran.group(1))
    verdict = re.search(r"^(OK|FAILED)\b.*$", text, re.M)
    green = proc.returncode == 0 and n > 0 and bool(verdict) and verdict.group(1) == "OK"
    return n, green, verdict.group(0) if verdict else "no verdict line"


def load_faulty():
    """(faulty versions, the contract-exact version) from the packed blob."""
    packed = json.loads(zlib.decompress(base64.b64decode("".join(FAULTY_VERSIONS))).decode("utf-8"))
    reference = next(f["source"] for f in packed if f["id"] == "REF")
    return [f for f in packed if f["id"] != "REF"], reference


def test_outcomes(folder):
    """{test id: ok | fail | error | skipped} for every test, or None if the suite did not run."""
    try:
        proc = subprocess.run([sys.executable, "-c", SUITE_DRIVER], cwd=folder, capture_output=True,
                              text=True, timeout=RUN_TIMEOUT, env=clean_env())
    except subprocess.TimeoutExpired:
        return None
    if "@@RESULT@@" not in proc.stdout:
        return None
    data = json.loads(proc.stdout.split("@@RESULT@@", 1)[1])
    return None if data["load_error"] else data["tests"]


def short(test_id):
    return test_id.rsplit(".", 1)[-1]


def check_suite(res, measured, function_runs):
    t1 = "your suite has at least %d tests" % MIN_TESTS
    t2 = "your suite is green on your own code"
    faulty, reference = load_faulty()
    measured.update({"tests": None, "suite_green": False, "caught": [], "survived": [],
                     "outside_contract": []})

    def all_faults(verdict, message):
        for f in faulty:
            res.add(f["id"], FAULT_TITLE % f["criterion"], verdict, message)

    if not os.path.exists(SUITE):
        res.add("S1", t1, "ERROR", "code/test_booking.py not found")
        res.add("S2", t2, "ERROR", "code/test_booking.py not found")
        all_faults("ERROR", "not judged - there is no suite to run")
        return

    scratch = tempfile.mkdtemp(prefix="week05-")
    try:
        work = os.path.join(scratch, "code")
        copy_code(work)
        ran, green, summary = run_suite(work)
        measured["tests"], measured["suite_green"] = ran, green
        if ran is None:
            res.add("S1", t1, "ERROR", summary)
            res.add("S2", t2, "ERROR", summary)
            all_faults("ERROR", "not judged - the suite does not run")
            return
        res.add("S1", t1, "PASS" if ran >= MIN_TESTS else "FAIL",
                "%d tests" % ran if ran >= MIN_TESTS else
                "%d test%s - the task asks for the six table cases plus five more kinds (README Part 3)"
                % (ran, "" if ran == 1 else "s"))
        if not function_runs:
            res.add("S2", t2, "ERROR", "code/booking.py does not run yet, so there is nothing for the suite to test")
            all_faults("ERROR", "not judged - your suite must be green on your own code first (S2)")
            return
        res.add("S2", t2, "PASS" if green else "FAIL", "%d tests, %s" % (ran, summary))
        if not green:
            all_faults("ERROR", "not judged - your suite must be green on your own code first (S2)")
            return
        # Only tests that pass on a version that follows the contract exactly may catch a fault.
        # A test of what the contract leaves open (a non-integer time) or one whose expected
        # value contradicts an AC fails on every faulty version for the wrong reason.
        def outcomes_with(source):
            with open(os.path.join(work, "booking.py"), "w", encoding="utf-8") as handle:
                handle.write(source)
            return test_outcomes(work)

        on_reference = outcomes_with(reference)
        if on_reference is None:
            all_faults("ERROR", "not judged - your suite could not be run test by test")
            return
        counted = {t for t, outcome in on_reference.items() if outcome == "ok"}
        measured["outside_contract"] = sorted(short(t) for t, o in on_reference.items() if o != "ok")
        for f in faulty:
            title = FAULT_TITLE % f["criterion"]
            outcomes = outcomes_with(f["source"])
            if outcomes is None:
                res.add(f["id"], title, "ERROR", "the suite stopped running on this version")
                continue
            catchers = sorted(short(t) for t in counted if outcomes.get(t, "error") != "ok")
            if catchers:
                measured["caught"].append(f["id"])
                res.add(f["id"], title, "PASS", "caught by " + ", ".join(catchers[:3])
                        + (" and %d more" % (len(catchers) - 3) if len(catchers) > 3 else ""))
            else:
                measured["survived"].append(f["id"])
                res.add(f["id"], title, "FAIL",
                        "NOT caught - a can_book that breaks %s passed all %d of your tests that "
                        "follow the contract" % (f["criterion"], len(counted)))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


# --------------------------------------------------------------------------- L: lab-report.md

PLACEHOLDER = re.compile(r"\(paste here\)|^<.*>$|yes / no|accept / reject|allowed / not-allowed", re.I)


def sections(text):
    """{'1': body, '8.3': body, ...} - split on the numbered '## N.' and '### N.M' headings."""
    out, current = {}, None
    for line in text.splitlines():
        m = re.match(r"^#{2,3}\s+(\d+(?:\.\d+)?)[.\s]", line)
        if m:
            current = m.group(1)
            out[current] = []
            top = current.split(".")[0]
            if top != current:
                out.setdefault(top, [])
        elif current is not None:
            out[current].append(line)
            top = current.split(".")[0]
            if top != current:
                out[top].append(line)
    return {k: "\n".join(v) for k, v in out.items()}


def table_rows(body):
    """Data rows of every markdown table in `body`: the header row and the --- row are dropped."""
    rows, lines = [], [l.strip() for l in body.splitlines()]
    for i, line in enumerate(lines):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(re.match(r"^:?-{2,}:?$", c) for c in cells if c) and any(cells):
            continue
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if nxt.startswith("|") and re.match(r"^\|[\s:|-]+\|?$", nxt):
            continue                                   # this is a header row
        rows.append(cells)
    return rows


def useful(cell):
    cell = re.sub(r"<!--.*?-->", "", cell).strip()
    return bool(cell) and not PLACEHOLDER.search(cell)


def filled(cells, need):
    """A row counts when `need` cells after the first (the row number or label) hold real content."""
    return sum(1 for c in cells[1:] if useful(c)) >= need


def blocks(body):
    return re.findall(r"```[^\n]*\n(.*?)```", body, re.S)


def real_block(body, min_lines=3):
    for b in blocks(body):
        lines = [l for l in b.splitlines() if l.strip()]
        if len(lines) >= min_lines and not PLACEHOLDER.search(b):
            return b
    return None


def word_count(body):
    body = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
    body = "\n".join(l for l in body.splitlines() if not l.lstrip().startswith((">", "|", "#")))
    return len(re.findall(r"[^\W_]+(?:['\u2019-][^\W_]+)*", body))


def check_report(res, measured, path_b):
    text = read(REPORT)
    if text is None:
        for cid, title in LAB_TITLES.items():
            res.add(cid, title, "ERROR", "lab-report.md not found")
        if path_b:
            res.add("P3", "report 8.3: three faults you planted yourself", "ERROR", "lab-report.md not found")
        return
    sec = sections(text)

    def add(cid, ok, good, bad):
        res.add(cid, LAB_TITLES[cid], "PASS" if ok else "FAIL", good if ok else bad)

    setup = {r[0].lower(): r[1] for r in table_rows(sec.get("1", "")) if len(r) > 1}
    missing = [k for k in ("tool", "model", "language")
               if not any(k in label and useful(value) for label, value in setup.items())]
    add("L1", not missing, "tool, model and language recorded",
        "section 1 has no value for: " + ", ".join(missing))

    plan = real_block(sec.get("2", ""))
    rows2 = [r for r in table_rows(sec.get("2", "")) if filled(r, 2)]
    add("L2", bool(plan) and bool(rows2), "plan pasted, %d row(s) on what you corrected or verified" % len(rows2),
        "section 2 needs the assistant's plan pasted" if not plan
        else "section 2 needs at least one filled row: what the plan said, what the AC says, what you did")

    rows3 = [r for r in table_rows(sec.get("3", "")) if filled(r, 2)]
    seen = set(re.findall(r"\bAC\s?-?\s?([1-5])\b", " ".join(" ".join(r) for r in rows3)))
    lost = [n for n in "1234" if n not in seen]
    add("L3", len(rows3) >= 4 and not lost, "%d conditions mapped, AC1-AC4 all present" % len(rows3),
        "section 3 needs one row per condition in v1 (found %d) and AC1-AC4 all named (missing: %s)"
        % (len(rows3), ", ".join("AC" + n for n in lost) or "-"))

    rows4 = [r for r in table_rows(sec.get("4", "")) if filled(r, 4)]
    add("L4", len(rows4) >= MIN_TESTS, "%d tests listed" % len(rows4),
        "section 4 lists %d filled test rows, the task asks for %d" % (len(rows4), MIN_TESTS))

    rows5 = [r for r in table_rows(sec.get("5", "")) if filled(r, 3)]
    add("L5", bool(rows5), "%d row(s) of input / expected / actual" % len(rows5),
        "section 5 needs at least one row with the input, the expected and the actual result")

    rows6 = [r for r in table_rows(sec.get("6", ""))
             if filled(r, 2) and re.search(r"\b(accept|reject)(ed)?\b", " ".join(r), re.I)]
    critique = real_block(sec.get("6", ""))
    add("L6", bool(critique) and len(rows6) >= 2, "critique pasted, %d points judged" % len(rows6),
        "section 6 needs the critique pasted and at least 2 points marked accept or reject with a reason (found %d)"
        % len(rows6))

    rows7 = [r for r in table_rows(sec.get("7", "")) if filled(r, 2)]
    add("L7", bool(rows7), "%d change-log row(s)" % len(rows7),
        "section 7 needs at least one row - if nothing changed, the row says so and why")

    output = real_block(sec.get("8.1", ""))
    ok = bool(output) and (path_b or bool(re.search(r"^Ran \d+ test", output, re.M)))
    add("L8", ok, "suite output pasted",
        "section 8.1 needs the complete terminal output of your suite"
        + ("" if path_b else " (the part ending in 'Ran N tests ...')"))

    words = word_count(sec.get("10", ""))
    measured["conclusion_words"] = words
    add("L9", WORDS_MIN <= words <= WORDS_MAX, "%d words" % words,
        "section 10 has %d words, the task asks for %d-%d" % (words, WORDS_MIN, WORDS_MAX))

    if path_b:
        rows83 = [r for r in table_rows(sec.get("8.3", "")) if filled(r, 3)]
        res.add("P3", "report 8.3: three faults you planted yourself",
                "PASS" if len(rows83) >= 3 else "FAIL",
                "%d planted faults with the test that caught each" % len(rows83) if len(rows83) >= 3
                else "section 8.3 needs 3 rows: the line you broke, the AC, the test that failed (found %d)" % len(rows83))


# --------------------------------------------------------------------------- Path B


def other_language_files():
    if not os.path.isdir(CODE):
        return [], []
    names = [n for n in os.listdir(CODE) if os.path.isfile(os.path.join(CODE, n))]
    skip = (".py", ".md", ".txt", ".gitkeep")
    impl = [n for n in names if os.path.splitext(n)[0].lower() == "booking"
            and os.path.splitext(n)[1].lower() not in skip and os.path.getsize(os.path.join(CODE, n)) > 0]
    tests = [n for n in names if "test" in n.lower() and os.path.splitext(n)[1].lower() not in skip
             and os.path.getsize(os.path.join(CODE, n)) > 0]
    return impl, tests


def detect_path():
    impl, _ = other_language_files()
    return "B" if impl and is_starter(read(IMPL)) else "A"


def check_path_b(res, measured):
    impl, tests = other_language_files()
    res.add("P1", "your implementation is in code/", "PASS" if impl else "ERROR",
            "found code/" + impl[0] if impl else "no code/booking.<ext> found")
    res.add("P2", "your test file is in code/", "PASS" if tests else "ERROR",
            "found code/" + tests[0] if tests else "no file with 'test' in its name found in code/")
    kept = []
    if os.path.isdir(ORIGINAL_DIR):
        kept = [n for n in os.listdir(ORIGINAL_DIR)
                if not n.startswith(".") and os.path.getsize(os.path.join(ORIGINAL_DIR, n)) > 0]
    res.add("O1", "the assistant's first version is kept", "PASS" if kept else "ERROR",
            "found code/original/" + kept[0] if kept
            else "code/original/ is empty - save v1 there BEFORE you edit anything")
    measured["implementation"] = impl[0] if impl else None


# --------------------------------------------------------------------------- main


def run():
    res, measured = Results(), {}
    path = detect_path()
    measured["path"] = path
    if path == "B":
        check_path_b(res, measured)
        check_report(res, measured, path_b=True)
        order = ["P1", "P2", "O1", "P3"] + list(LAB_TITLES)
        res.rows.sort(key=lambda r: order.index(r["id"]))
    else:
        function_runs = check_function(res, measured)
        check_original(res, measured)
        check_suite(res, measured, function_runs)
        check_report(res, measured, path_b=False)
    return res, measured


def print_human(res, measured):
    counts = res.counts()
    print("Week 05 - can_book: the function, your tests, the evidence   (Path %s)\n" % measured["path"])
    width = max(len(r["title"]) for r in res.rows)
    for r in res.rows:
        print(("%-6s %-4s %-*s  %s" % (r["verdict"], r["id"], width, r["title"], r["message"])).rstrip())
    print("-" * 78)
    v1 = measured.get("v1")
    if v1:
        print("v1 (code/original/booking_v1.py): passes %s - fails %s - identical to your final: %s"
              % (" ".join(v1["passes"]) or "nothing", " ".join(v1["fails"]) or "nothing",
                 "yes" if v1["identical_to_final"] else "no"))
        if v1.get("note"):
            print("   v1 note: " + v1["note"])
    if measured.get("outside_contract"):
        print("Not counted for M - these fail on a can_book that follows the contract exactly, so they")
        print("test what the contract leaves open or contradict an AC: " + ", ".join(measured["outside_contract"]))
    if measured["path"] == "B":
        print("Path B: F, S and M cannot run on your language. P1-P3 and O1 replace them; your grader")
        print("reads lab-report.md sections 4 and 8 by hand, and your pasted output is the evidence.")
    print("SUMMARY pass=%d fail=%d error=%d   (%d checks)"
          % (counts["PASS"], counts["FAIL"], counts["ERROR"], len(res.rows)))
    if counts["FAIL"] or counts["ERROR"]:
        print("Every FAIL or ERROR you keep goes in lab-report.md section 9 and in submission.yml known_fails.")
        print("One you report and explain costs you nothing. One you hide costs the whole criterion.")
    else:
        print("Behaviour and shape are clean. This says nothing about the quality of your review.")


def main():
    parser = argparse.ArgumentParser(description="Week 05 checker - run from inside week-05/")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    if not os.path.isdir("tests") and not os.path.exists(REPORT) and not os.path.isdir(CODE):
        message = "run this from inside your week-05/ folder:  cd week-05 && python tests/check_booking.py"
        print(json.dumps({"ok": False, "error": message}) if args.json else "ERROR: " + message)
        return 3

    res, measured = run()
    counts = res.counts()
    ok = counts["FAIL"] == 0 and counts["ERROR"] == 0
    if args.json:
        print(json.dumps({"ok": ok, "counts": counts, "total": len(res.rows),
                          "rows": res.rows, "measured": measured}, ensure_ascii=False, indent=2))
    else:
        print_human(res, measured)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
