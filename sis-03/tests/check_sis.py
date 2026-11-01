#!/usr/bin/env python3
"""
check_sis.py - the SIS #03 checker. DO NOT EDIT: the grader runs its own copy over your files.

    python tests/check_sis.py          # from inside sis-03/
    python tests/check_sis.py --json   # machine-readable, for the grading pipeline

What it checks (Path A - Python, 55 checks; Path B - any other language, 36 checks):

    R1-R3    report.md: sections present, no template markers left, the setup table
    B1       section 2: your baseline - scope, criteria, failure points, contract, assumptions
    F1-F10   Path A: your final can_book in code/booking.py, against AC1-AC5
    O1       the first Python version is kept in code/original/
    U1-U2    Path A: your suite code/test_booking.py: 10 tests or more, green on your code
    M1-M10   Path A: your suite against ten FAULTY versions of can_book, one broken AC each
    P1-P3    Path B only: your implementation, your tests, three faults you planted
    V1-V2    section 3 (v1 review) and section 8 (critique decisions)
    W1-W5    the Bolt exports: web/final/ and web/original/, clean, in scope, different
    G1       section 4: the generated files, named by paths that exist in web/original/
    E1-E3    screenshots in evidence/: v1, before/after, narrow width
    C1-C4    section 5: the twelve cases - and, on Path A, whether the Python results you
             reported are what your two files actually return
    TR1      section 6: the traceability table
    I1-I2    section 7: the issue log
    A1-A3    section 9: the coding-agent analysis
    X1-X5    section 11: the AI exchanges, the Bolt prompt, v1 inside its Generate response
    K1       section 12: real output of your suite
    Q1       section 10: reflection of 100-200 words

It checks BEHAVIOUR and SHAPE, never the quality of your review. A clean run is the floor,
not the grade. The faulty versions are stored packed on purpose.

Verdicts:
    PASS   the check found what it was looking for
    FAIL   it runs, but the result is wrong or the content is not there
    ERROR  it could not run: a file, a folder, a section or the function is missing

Exit codes: 0 = no FAIL and no ERROR - 1 = at least one FAIL or ERROR - 3 = wrong directory.
Standard library only.
"""

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from datetime import date

CODE = "code"
IMPL = os.path.join(CODE, "booking.py")
SUITE = os.path.join(CODE, "test_booking.py")
ORIGINAL_DIR = os.path.join(CODE, "original")
V1 = os.path.join(ORIGINAL_DIR, "booking_v1.py")
WEB_FINAL = os.path.join("web", "final")
WEB_V1 = os.path.join("web", "original")
EVIDENCE = "evidence"
REPORT = "report.md"

MIN_TESTS = 10
REFLECTION = (100, 200)
MAX_EXPORT_MB = 5
MIN_IMAGE_BYTES = 3000
RUN_TIMEOUT = 5

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


def case(label, start, end, expected, now=BASE_NOW, blocked=False, existing=None, twice=False):
    return {"label": label, "start": start, "end": end, "now": now, "blocked": blocked,
            "existing": [list(p) for p in (BASE_EXISTING if existing is None else existing)],
            "expected": expected, "twice": twice}


GROUPS = [
    ("F1", "the six cases from the brief", "value", [
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

# The twelve cases of report.md section 5. T12 is the page only.
TABLE = [
    ("T1", "Touching", "Available", case("T1", 660, 720, True)),
    ("T2", "Overlap", "Unavailable", case("T2", 630, 690, False)),
    ("T3", "Blocked", "Unavailable", case("T3", 660, 720, False, blocked=True)),
    ("T4", "Exactly 120 min", "Available", case("T4", 720, 840, True)),
    ("T5", "121 min", "Unavailable", case("T5", 720, 841, False)),
    ("T6", "Starts now", "Unavailable", case("T6", 540, 570, False)),
    ("T7", "Reversed", "Unavailable", case("T7", 720, 660, False)),
    ("T8", "Ends at midnight", "Available", case("T8", 1380, 1440, True)),
    ("T9", "Past midnight", "Unavailable", case("T9", 1380, 1441, False)),
    ("T10", "Second booking", "Unavailable", case("T10", 720, 780, False, existing=[(600, 660), (700, 760)])),
    ("T11", "Same check twice", "Available", case("T11", 660, 720, True, twice=True)),
    ("T12", "Narrow screen", "Available", None),
]
DAY_BOUND_CASES = ("T8", "T9")       # a time input stops at 23:59: Not testable is accepted on the page

FAULT_TITLE = "your tests catch a fault in %s"

SECTIONS = {
    1: "Setup and reuse", 2: "Baseline", 3: "Python v1 review", 4: "Prototype v1 in Bolt.new",
    5: "Test cases", 6: "Traceability", 7: "Issue log", 8: "Critique decisions",
    9: "Coding-agent analysis", 10: "Reflection", 11: "Appendix A", 12: "Appendix B", 13: "Remaining limitations",
}
SETUP_ITEMS = ("coding assistant (tool)", "coding assistant model", "bolt.new model", "bolt project link",
               "language", "path", "python v1 from", "web v1 from")
CONTRACT = ("start", "end", "now", "blocked", "existing", "returns")
LOOP_STEPS = ("user goal", "model / plan", "tool call", "observation", "next step", "human review")
STAGES = ("plan", "generate", "critique", "repair")
BARE_TOOL_NAMES = {
    "chatgpt", "gpt", "claude", "gemini", "copilot", "github copilot", "deepseek", "bolt", "bolt.new",
    "grok", "mistral", "llama", "qwen", "perplexity", "cursor", "openai", "anthropic",
}
MODEL_HIDDEN = "not displayed"
GENERIC_PROMPT = re.compile(r"\bmake (it|this|the \w+) (better|nicer|cleaner)\b|\bimprove (it|everything|the (code|app|page|design))\b"
                            r"|\bfix (all|everything|the bugs)\b|\bclean (it|everything) up\b", re.I)

SOURCE_EXT = (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte", ".html", ".css", ".json")
CODE_EXT = (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte", ".html")
IGNORED_FILES = ("package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb", ".gitkeep", ".DS_Store")
IGNORED_DIRS = (".git", ".bolt", ".vscode", ".idea", "__pycache__")
SCOPE = [
    ("network call", r"\bfetch\s*\(|\baxios\b|XMLHttpRequest|new\s+WebSocket|\bEventSource\b"),
    ("browser storage", r"\blocalStorage\b|\bsessionStorage\b|\bindexedDB\b"),
    ("backend or database", r"supabase|firebase|@prisma|\bmongodb\b|\bmongoose\b|\bexpress\s*\("),
    ("login or account", r"\bsignIn\w*\s*\(|\bsign[ -]?in\b|\blog[ -]?in\b|\bpassword\b|\bauth0\b"),
    ("analytics", r"\bgtag\s*\(|google-analytics|\bmixpanel\b|\bposthog\b|\bsegment\.io\b"),
]

TITLES = [
    ("R1", "report.md: sections 1-13 present, in order"),
    ("R2", "report.md: no template markers left"),
    ("R3", "section 1: setup and reuse table complete"),
    ("B1", "section 2: baseline - scope, criteria, failure points, contract, assumptions"),
    ("F1", "the six cases from the brief"), ("F2", "AC1 time order and day bounds"),
    ("F3", "AC1 the start is in the future"), ("F4", "AC2 at most 120 minutes"),
    ("F5", "AC3 a blocked room accepts nothing"), ("F6", "AC4 every kind of overlap is rejected"),
    ("F7", "AC4 touching endpoints are allowed"), ("F8", "AC4 every existing booking is checked"),
    ("F9", "AC5 the result is a real Boolean"), ("F10", "AC5 the inputs are left unchanged"),
    ("P1", "Path B: your implementation is in code/"),
    ("P2", "Path B: your test file is in code/"),
    ("O1", "the first Python version is kept in code/original/"),
    ("U1", "your suite has at least %d tests" % MIN_TESTS),
    ("U2", "your suite is green on your own code"),
] + [("M%d" % i, "your tests catch a fault") for i in range(1, 11)] + [
    ("P3", "Path B: section 12.2, three faults you planted"),
    ("V1", "section 3: v1 reviewed branch by branch, AC1-AC4"),
    ("V2", "section 8: three critique decisions, one reject or modify"),
    ("W1", "final prototype exported to web/final/"),
    ("W2", "exports are clean: no node_modules, no .env, under %d MB" % MAX_EXPORT_MB),
    ("W3", "final stays in scope: no network, storage, backend, login"),
    ("W4", "v1 export kept in web/original/"),
    ("W5", "final differs from v1"),
    ("G1", "section 4: generated files named by real paths"),
    ("E1", "v1 screenshot: evidence/web-v1.png"),
    ("E2", "before/after screenshots: evidence/before-1.png, after-1.png"),
    ("E3", "narrow-width screenshot: evidence/final-narrow.png, portrait"),
    ("C1", "section 5: T1-T12 present, expected unchanged, every result filled"),
    ("C2", "section 5: Python v1 results are what v1 returns"),
    ("C3", "section 5: Python final results are what your final returns"),
    ("C4", "section 5: page final matches the expected result"),
    ("TR1", "section 6: traceability for AC1-AC6"),
    ("I1", "section 7: two issues or more, each complete"),
    ("I2", "section 7: focused prompts, reproductions and the before/after line"),
    ("A1", "section 9.1: one pass through the agent loop"),
    ("A2", "section 9.2: context, tools, permissions - observed and assumed"),
    ("A3", "section 9.3: safety checkpoint and dependability"),
    ("X1", "section 11: four exchanges or more, metadata complete"),
    ("X2", "section 11: prompts and responses pasted in full"),
    ("X3", "section 11: stages Plan, Generate, Critique and Repair all present"),
    ("X4", "section 4: the Bolt prompt carries AC1-AC6 and forbids login, backend, database"),
    ("X5", "section 11: your Python v1 is inside a Generate response"),
    ("K1", "section 12.1: real output of your suite"),
    ("Q1", "section 10: reflection of %d-%d words" % REFLECTION),
]
TITLE = dict(TITLES)
ORDER = [cid for cid, _ in TITLES]

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
                if c.get("twice"):
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

listed = list(walk(suite))
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
        test = getattr(test, "test_case", test)
        out["tests"][test.id()] = kind
for test, _ in result.skipped:
    out["tests"][test.id()] = "skipped"
sys.stdout.write("\n@@RESULT@@" + json.dumps(out))
'''


# --------------------------------------------------------------------------- small helpers


class Results:
    def __init__(self):
        self.rows = []

    def add(self, cid, verdict, message):
        self.rows.append({"id": cid, "title": TITLE.get(cid, ""), "verdict": verdict, "message": message})

    def counts(self):
        return {v: sum(1 for r in self.rows if r["verdict"] == v) for v in ("PASS", "FAIL", "ERROR")}


def read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            return handle.read()
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
    return text is None or not text.strip() or (
        "raise NotImplementedError" in text and len(re.findall(r"^\s*(?:if|for|while|return)\b", text, re.M)) == 0)


PLACEHOLDER = re.compile(r"\(write here[^)]*\)|\(paste here\)", re.I)
COMMENT = re.compile(r"<!--.*?-->", re.S)
FENCE = re.compile(r"^(`{3,}|~{3,})")


def words(text):
    text = COMMENT.sub(" ", text or "")
    text = re.sub(r"[*_`#>|]", " ", text)
    return [t for t in text.split() if re.search(r"[0-9A-Za-zА-Яа-яЁёӘәҒғҚқҢңӨөҰұҮүҺһІі]", t)]


def useful(cell, minimum=1):
    cell = COMMENT.sub("", cell or "").strip()
    return bool(cell) and not PLACEHOLDER.search(cell) and len(words(cell)) >= minimum


def shingles(text, n=5):
    toks = re.findall(r"\w+", (text or "").lower())
    return {" ".join(toks[i:i + n]) for i in range(max(0, len(toks) - n + 1))}


def share(part, whole_text):
    if not part:
        return 0.0
    return len(part & shingles(whole_text)) / len(part)


def split_sections(text):
    """({'1': body, '2.3': body, ...}, [order of top-level numbers]) - fence-aware, comments removed.
    A sub-section's lines also belong to its parent."""
    text = COMMENT.sub("", text)
    out, order, top, sub, in_fence = {}, [], None, None, None
    for line in text.splitlines():
        s = line.strip()
        fence = FENCE.match(s)
        if fence:
            if in_fence is None:
                in_fence = fence.group(1)
            elif s[0] == in_fence[0] and set(s) == {s[0]} and len(s) >= len(in_fence):
                in_fence = None
        elif in_fence is None:
            m2 = re.match(r"^##\s+(\d+)\.\s", line)
            m3 = re.match(r"^###\s+(\d+\.\d+)\b", line)
            if m2:
                top, sub = m2.group(1), None
                out[top] = []
                order.append(int(top))
                continue
            if m3:
                sub = m3.group(1)
                out[sub] = []
                if top is not None:
                    out[top].append(line)
                continue
        if top is not None:
            out[top].append(line)
        if sub is not None:
            out[sub].append(line)
    return {k: "\n".join(v) for k, v in out.items()}, order


def table_rows(body):
    """Data rows of every markdown table in `body`, outside fences: header and --- rows dropped."""
    rows, lines, in_fence = [], [], None
    for line in (body or "").splitlines():
        s = line.strip()
        fence = FENCE.match(s)
        if fence:
            in_fence = None if in_fence and s[0] == in_fence[0] else (in_fence or fence.group(1))
            continue
        if in_fence is None:
            lines.append(s)
    for i, line in enumerate(lines):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(re.match(r"^:?-{2,}:?$", c) for c in cells if c) and any(cells):
            continue
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if nxt.startswith("|") and re.match(r"^\|[\s:|-]+\|?$", nxt):
            continue
        rows.append(cells)
    return rows


def label_value(body, label):
    m = re.search(r"\*\*%s:?\*\*:?\s*(.*)" % re.escape(label), body or "")
    return m.group(1).strip() if m else None


def fenced_after(body, label):
    """The first fenced block after a line containing **label:**."""
    lines = (body or "").splitlines()
    start = None
    for i, line in enumerate(lines):
        if "**%s:**" % label in line:
            start = i + 1
            break
    if start is None:
        return None
    for i in range(start, len(lines)):
        stripped = lines[i].strip()
        if not stripped:
            continue
        opening = FENCE.match(stripped)
        if not opening:
            return None
        mark = opening.group(1)
        out = []
        for j in range(i + 1, len(lines)):
            s = lines[j].strip()
            if s and s[0] == mark[0] and set(s) == {mark[0]} and len(s) >= len(mark):
                return "\n".join(out)
            out.append(lines[j])
        return "\n".join(out)
    return None


def split_sub(body, pattern):
    """{ID: text} for `### <ID>` sub-headings outside code blocks."""
    parts, current, buf, in_fence = {}, None, [], None
    for line in (body or "").splitlines():
        fence = FENCE.match(line.strip())
        if fence:
            mark = fence.group(1)
            if in_fence is None:
                in_fence = mark
            elif mark[0] == in_fence[0] and set(line.strip()) == {mark[0]}:
                in_fence = None
        m = re.match(r"^###\s+(%s)\b" % pattern, line) if in_fence is None else None
        if m:
            if current:
                parts[current] = "\n".join(buf)
            current, buf = m.group(1).upper(), []
            continue
        if current:
            buf.append(line)
    if current:
        parts[current] = "\n".join(buf)
    return parts


def meta(block, name):
    m = re.search(r"^\s*[-*]?\s*\*\*%s:\*\*\s*(.*)$" % name, block or "", re.M)
    return m.group(1).strip() if m else ""


def model_problem(value):
    v = (value or "").strip()
    if not useful(v):
        return "left empty"
    if v.lower() == MODEL_HIDDEN:
        return None
    if v.lower() in BARE_TOOL_NAMES or not re.search(r"\d", v):
        return "%r is a tool name, not a model - give the exact model with its version, or write: not displayed" % v
    return None


def missing_section(res, ids, n):
    for cid in ids:
        res.add(cid, "ERROR", "section %s is missing from report.md - restore the heading from the template" % n)


# --------------------------------------------------------------------------- Python: run your code


def run_cases(path, cases):
    """Call can_book from `path` on every case. Returns (problem, results)."""
    try:
        proc = subprocess.run([sys.executable, "-c", DRIVER, os.path.abspath(path)],
                              input=json.dumps(cases), capture_output=True, text=True,
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
    out, i = [], 0
    for gid, _, kind, cases in GROUPS:
        chunk = results[i:i + len(cases)]
        i += len(cases)
        problem = None
        for c, r in zip(cases, chunk):
            if "exception" in r:
                problem = "%s raised %s" % (call_text(c), r["exception"])
            elif kind == "value" and not r["equal"]:
                problem = "%s returned %s, expected %s" % (call_text(c), r["repr"], c["expected"])
            elif kind == "type" and r["type"] != "bool":
                problem = "%s returned %s (%s) - the contract says True or False" % (call_text(c), r["repr"], r["type"])
            elif kind == "unchanged" and not r["unchanged"]:
                problem = "%s changed existing to %s" % (call_text(c), r["after"])
            if problem:
                break
        out.append((gid, "FAIL" if problem else "PASS", problem or "%d of %d cases" % (len(cases), len(cases))))
    return out


def table_actuals(path):
    """{'T1': 'true' | 'false' | 'error' | <repr>} for T1-T11, or None if the file cannot run at all."""
    cases = [c for _, _, _, c in TABLE if c]
    try:
        proc = subprocess.run([sys.executable, "-c", DRIVER, os.path.abspath(path)],
                              input=json.dumps(cases), capture_output=True, text=True,
                              timeout=RUN_TIMEOUT * 2, env=clean_env())
    except subprocess.TimeoutExpired:
        return None
    if "@@RESULT@@" not in proc.stdout:
        return None
    data = json.loads(proc.stdout.split("@@RESULT@@", 1)[1])
    if data["import_error"] or not data["has_function"]:
        return {c["label"]: "error" for c in cases}
    out = {}
    for c, r in zip(cases, data["results"]):
        out[c["label"]] = "error" if "exception" in r else r["repr"].lower()
    return out


def check_function(res, measured):
    if not os.path.exists(IMPL):
        problem, results = "code/booking.py not found", None
    else:
        problem, results = run_cases(IMPL, [c for _, _, _, cs in GROUPS for c in cs])
    if problem:
        for gid, _, _, _ in GROUPS:
            res.add(gid, "ERROR", problem)
        return False
    for row in judge_groups(results):
        res.add(*row)
    return True


def check_original_python(res, measured):
    text = read(V1)
    if text is None:
        res.add("O1", "ERROR", "code/original/booking_v1.py not found - your Week 05 v1, or a fresh one, saved BEFORE any fix")
        return None
    if is_starter(text) or "def can_book" not in text:
        res.add("O1", "FAIL", "code/original/booking_v1.py does not contain an implementation of can_book")
        return None
    res.add("O1", "PASS", "v1 kept (%d lines)" % len(text.strip().splitlines()))
    return text


def copy_code(dest):
    shutil.copytree(CODE, dest, ignore=shutil.ignore_patterns("original", "__pycache__", ".*"))


def run_suite(folder):
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
    packed = json.loads(zlib.decompress(base64.b64decode("".join(FAULTY_VERSIONS))).decode("utf-8"))
    reference = next(f["source"] for f in packed if f["id"] == "REF")
    return [f for f in packed if f["id"] != "REF"], reference


def test_outcomes(folder):
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
    faulty, reference = load_faulty()
    measured.update({"tests": None, "suite_green": False, "caught": [], "survived": [], "outside_contract": []})

    def all_faults(verdict, message):
        for f in faulty:
            res.add(f["id"], verdict, message)

    if not os.path.exists(SUITE):
        res.add("U1", "ERROR", "code/test_booking.py not found")
        res.add("U2", "ERROR", "code/test_booking.py not found")
        all_faults("ERROR", "not judged - there is no suite to run")
        return
    scratch = tempfile.mkdtemp(prefix="sis03-")
    try:
        work = os.path.join(scratch, "code")
        copy_code(work)
        ran, green, summary = run_suite(work)
        measured["tests"], measured["suite_green"] = ran, green
        if ran is None:
            res.add("U1", "ERROR", summary)
            res.add("U2", "ERROR", summary)
            all_faults("ERROR", "not judged - the suite does not run")
            return
        res.add("U1", "PASS" if ran >= MIN_TESTS else "FAIL",
                "%d tests" % ran if ran >= MIN_TESTS else
                "%d test%s - the brief's six cases plus reversed times, day bounds, multiple bookings "
                "and unchanged inputs make %d at least (README §5)" % (ran, "" if ran == 1 else "s", MIN_TESTS))
        if not function_runs:
            res.add("U2", "ERROR", "code/booking.py does not run yet, so there is nothing for the suite to test")
            all_faults("ERROR", "not judged - your suite must be green on your own code first (U2)")
            return
        res.add("U2", "PASS" if green else "FAIL", "%d tests, %s" % (ran, summary))
        if not green:
            all_faults("ERROR", "not judged - your suite must be green on your own code first (U2)")
            return

        def outcomes_with(source):
            with open(os.path.join(work, "booking.py"), "w", encoding="utf-8") as handle:
                handle.write(source)
            return test_outcomes(work)

        on_reference = outcomes_with(reference)
        if on_reference is None:
            all_faults("ERROR", "not judged - your suite could not be run test by test")
            return
        counted = {t for t, o in on_reference.items() if o == "ok"}
        measured["outside_contract"] = sorted(short(t) for t, o in on_reference.items() if o != "ok")
        for f in faulty:
            outcomes = outcomes_with(f["source"])
            if outcomes is None:
                res.add(f["id"], "ERROR", "the suite stopped running on this version")
                continue
            catchers = sorted(short(t) for t in counted if outcomes.get(t, "error") != "ok")
            if catchers:
                measured["caught"].append(f["id"])
                res.add(f["id"], "PASS", "%s - caught by %s" % (f["criterion"], ", ".join(catchers[:3])
                        + (" and %d more" % (len(catchers) - 3) if len(catchers) > 3 else "")))
            else:
                measured["survived"].append(f["id"])
                res.add(f["id"], "FAIL", "NOT caught - a can_book that breaks %s passed all %d of your tests "
                        "that follow the contract" % (f["criterion"], len(counted)))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


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


def v1_text_any():
    """Path B: the first file in code/original/, whatever its language."""
    if not os.path.isdir(ORIGINAL_DIR):
        return None, None
    for n in sorted(os.listdir(ORIGINAL_DIR)):
        p = os.path.join(ORIGINAL_DIR, n)
        if not n.startswith(".") and os.path.isfile(p) and os.path.getsize(p) > 0:
            return n, read(p)
    return None, None


def check_path_b(res, measured):
    impl, tests = other_language_files()
    res.add("P1", "PASS" if impl else "ERROR", "found code/" + impl[0] if impl else "no code/booking.<ext> found")
    res.add("P2", "PASS" if tests else "ERROR",
            "found code/" + tests[0] if tests else "no file with 'test' in its name found in code/")
    name, text = v1_text_any()
    res.add("O1", "PASS" if text else "ERROR",
            "found code/original/" + name if text else "code/original/ is empty - save v1 there BEFORE any fix")
    measured["implementation"] = impl[0] if impl else None
    return text


# --------------------------------------------------------------------------- the web prototype


def walk_files(root):
    for here, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in IGNORED_DIRS and d != "node_modules")
        for name in sorted(files):
            if name not in IGNORED_FILES:
                yield os.path.join(here, name)


def project_root(folder):
    if not os.path.isdir(folder):
        return None
    candidates = [folder] + sorted(os.path.join(folder, d) for d in os.listdir(folder)
                                   if os.path.isdir(os.path.join(folder, d)) and d not in IGNORED_DIRS)
    for c in candidates:
        if os.path.isfile(os.path.join(c, "package.json")) or os.path.isfile(os.path.join(c, "index.html")):
            return c
    return None


def code_files(root):
    return [p for p in walk_files(root) if p.lower().endswith(CODE_EXT)]


def fingerprint(root):
    out = {}
    for p in walk_files(root):
        if p.lower().endswith(SOURCE_EXT):
            rel = os.path.relpath(p, root).replace(os.sep, "/")
            data = open(p, "rb").read().replace(b"\r\n", b"\n").strip()
            out[rel] = hashlib.sha1(data).hexdigest()
    return out


def scope_hits(root):
    hits = []
    for p in walk_files(root):
        low = p.lower()
        if not (low.endswith(CODE_EXT) or os.path.basename(low) == "package.json"):
            continue
        for number, line in enumerate((read(p) or "").splitlines(), 1):
            for label, pattern in SCOPE:
                if re.search(pattern, line, re.I):
                    hits.append({"what": label, "where": "%s:%d" % (os.path.relpath(p, ".").replace(os.sep, "/"), number)})
    return hits


def check_exports(res, measured):
    final, v1 = project_root(WEB_FINAL), project_root(WEB_V1)
    files = code_files(final) if final else []
    if final and files:
        res.add("W1", "PASS", "%s: %d source files" % (final.replace(os.sep, "/"), len(files)))
    else:
        res.add("W1", "ERROR", "no package.json or index.html in web/final/ - download the final project from Bolt "
                "and unzip it there" if not final else "web/final/ has no source files")
    problems = []
    for folder in (WEB_FINAL, WEB_V1):
        if not os.path.isdir(folder):
            continue
        size = 0
        for here, dirs, names in os.walk(folder):
            if "node_modules" in dirs:
                problems.append("%s contains node_modules/ - delete it" % here.replace(os.sep, "/"))
                dirs.remove("node_modules")
            for n in names:
                if n == ".env" or n.startswith(".env."):
                    problems.append("%s/%s must not be committed" % (here.replace(os.sep, "/"), n))
                try:
                    size += os.path.getsize(os.path.join(here, n))
                except OSError:
                    pass
        if size > MAX_EXPORT_MB * 1024 * 1024:
            problems.append("%s/ is %.1f MB - an export is source files only" % (folder.replace(os.sep, "/"), size / 1048576.0))
    if not final:
        res.add("W2", "ERROR", "nothing to check until web/final/ holds the export")
    else:
        res.add("W2", "FAIL" if problems else "PASS", "; ".join(problems) if problems else "clean")
    if not final:
        res.add("W3", "ERROR", "no final prototype")
    else:
        hits = scope_hits(final)
        measured["scope_final"] = hits
        if hits:
            res.add("W3", "FAIL", "%s - e.g. %s" % (", ".join(sorted(set(h["what"] for h in hits))),
                                                     ", ".join(h["where"] for h in hits[:4])))
        else:
            res.add("W3", "PASS", "nothing out of scope found in the source")
    if v1:
        measured["scope_v1"] = scope_hits(v1)
    if v1 and code_files(v1):
        res.add("W4", "PASS", v1.replace(os.sep, "/"))
    else:
        res.add("W4", "ERROR", "web/original/ holds no project - your Week 06 v1 export, or a fresh v1, "
                "downloaded BEFORE the first cleanup prompt")
    if not (final and v1):
        res.add("W5", "ERROR", "needs both web/final/ and web/original/")
    else:
        a, b = fingerprint(v1), fingerprint(final)
        changed = sorted(p for p in set(a) | set(b) if a.get(p) != b.get(p))
        measured["changed_files"] = changed
        res.add("W5", "PASS" if changed else "FAIL",
                "%d file(s) changed, e.g. %s" % (len(changed), ", ".join(changed[:3])) if changed
                else "web/final/ is identical to web/original/ - the brief says v1 is not the final submission")
    return v1


def image_info(path):
    try:
        data = open(path, "rb").read()
    except OSError:
        return None
    if data[:8] == b"\x89PNG\r\n\x1a\n" and len(data) > 24:
        return struct.unpack(">II", data[16:24])
    if data[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            length = struct.unpack(">H", data[i + 2:i + 4])[0]
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return (w, h)
            i += 2 + length
    return None


def find_image(stem):
    if not os.path.isdir(EVIDENCE):
        return None
    for name in os.listdir(EVIDENCE):
        base, ext = os.path.splitext(name)
        if base.lower() == stem.lower() and ext.lower() in (".png", ".jpg", ".jpeg"):
            return os.path.join(EVIDENCE, name)
    return None


def image_problem(path, stem):
    if path is None:
        return "evidence/%s.png (or .jpg) not found" % stem
    if os.path.getsize(path) < MIN_IMAGE_BYTES:
        return "%s is too small to be a screenshot" % path.replace(os.sep, "/")
    if image_info(path) is None:
        return "%s is not a real PNG or JPEG" % path.replace(os.sep, "/")
    return None


def file_hash(path):
    return hashlib.sha1(open(path, "rb").read()).hexdigest()


def check_evidence(res):
    p = find_image("web-v1")
    why = image_problem(p, "web-v1")
    res.add("E1", ("FAIL" if p else "ERROR") if why else "PASS", why or p.replace(os.sep, "/"))

    before, after = find_image("before-1"), find_image("after-1")
    probs = [w for w in (image_problem(before, "before-1"), image_problem(after, "after-1")) if w]
    if not probs and file_hash(before) == file_hash(after):
        probs.append("before-1 and after-1 are the same file - the after shot is taken after the fix")
    res.add("E2", ("FAIL" if (before or after) else "ERROR") if probs else "PASS",
            "; ".join(probs) if probs else "before-1 and after-1, different")

    p = find_image("final-narrow")
    why = image_problem(p, "final-narrow")
    if why:
        res.add("E3", "FAIL" if p else "ERROR", why)
    else:
        w, h = image_info(p)
        res.add("E3", "PASS" if h > w else "FAIL", "%dx%d" % (w, h) + ("" if h > w else
                " - not portrait; take it at phone width (about 375 px) with the device toolbar"))


# --------------------------------------------------------------------------- report.md


PY_WORD = {"true": "true", "false": "false", "error": "error", "raised": "error", "exception": "error", "n/a": "n/a"}
PAGE_WORD = {"available": "Available", "unavailable": "Unavailable", "not testable": "Not testable",
             "not-testable": "Not testable", "n/t": "Not testable"}


def py_value(cell):
    c = COMMENT.sub("", cell or "").strip().strip("*`").strip().lower()
    return PY_WORD.get(c, c if c else None)


def page_value(cell):
    c = COMMENT.sub("", cell or "").strip().strip("*`").strip().lower()
    return PAGE_WORD.get(c)


def check_structure(res, text, sec, order):
    missing = [n for n in SECTIONS if str(n) not in sec]
    if missing:
        res.add("R1", "ERROR", "missing heading(s): " + ", ".join("## %d." % n for n in missing)
                + " - restore them from the template")
    elif [n for n in order if n in SECTIONS] != sorted(SECTIONS):
        res.add("R1", "FAIL", "sections out of order: %s" % order)
    else:
        res.add("R1", "PASS", "sections 1-13 present, in order")
    left = PLACEHOLDER.findall(COMMENT.sub("", text))
    res.add("R2", "FAIL" if left else "PASS",
            "%d template marker(s) like '(write here)' still in report.md" % len(left) if left
            else "no template markers left")


def check_setup(res, measured, sec, path):
    if "1" not in sec:
        return missing_section(res, ["R3"], 1)
    rows = {r[0].strip().lower(): (r[1] if len(r) > 1 else "") for r in table_rows(sec["1"])}
    probs = []
    for item in SETUP_ITEMS:
        if not useful(rows.get(item, "")):
            probs.append("%s empty" % item)
    mp = model_problem(rows.get("coding assistant model", ""))
    if mp and "empty" not in mp:
        probs.append("coding assistant model: " + mp)
    bp = model_problem(rows.get("bolt.new model", ""))
    if bp and "empty" not in bp:
        probs.append("Bolt.new model: " + bp)
    declared_path = COMMENT.sub("", rows.get("path", "")).strip().upper()[:1]
    if declared_path in ("A", "B") and declared_path != path:
        probs.append("Path says %s, but code/ looks like Path %s" % (declared_path, path))
    elif useful(rows.get("path", "")) and declared_path not in ("A", "B"):
        probs.append("Path must be A or B")
    reuse = {}
    for item, week in (("python v1 from", "week-05"), ("web v1 from", "week-06")):
        v = COMMENT.sub("", rows.get(item, "")).strip().lower()
        if useful(v):
            if v not in (week, "fresh"):
                probs.append("%s must be %s or fresh" % (item, week))
            reuse[item.split()[0]] = v
    measured["model"] = COMMENT.sub("", rows.get("coding assistant model", "")).strip() or None
    measured["reuse"] = reuse
    res.add("R3", "FAIL" if probs else "PASS",
            "; ".join(probs) if probs else "tool, models, project link, language, path and reuse recorded")


def check_baseline(res, sec):
    if "2" not in sec:
        return missing_section(res, ["B1"], 2)
    probs = []
    scope = label_value(sec.get("2.1", ""), "Scope") or ""
    if not useful(scope, 15):
        probs.append("2.1 **Scope:** empty or under 15 words")
    acs = {r[0].upper().replace(" ", ""): r[1] for r in table_rows(sec.get("2.2", "")) if len(r) > 1}
    thin = ["AC%d" % n for n in range(1, 7) if not useful(acs.get("AC%d" % n, ""), 4)]
    if thin:
        probs.append("2.2 needs AC1-AC6 each in your own words, 4 words or more (missing: %s)" % ", ".join(thin))
    fps = [r for r in table_rows(sec.get("2.3", "")) if sum(1 for c in r[1:] if useful(c)) >= 3]
    if len(fps) < 2:
        probs.append("2.3 needs 2 failure points, each with its AC and how you will check it (found %d)" % len(fps))
    contract = {r[0].strip("` ").lower(): r for r in table_rows(sec.get("2.4", "")) if r}
    lost = [p for p in CONTRACT if p not in contract or sum(1 for c in contract[p][1:] if useful(c)) < 2]
    if lost:
        probs.append("2.4 contract rows incomplete: " + ", ".join(lost))
    s25 = sec.get("2.5", "")
    assumptions = [i for i in re.findall(r"^\s*\d+[.)]\s+(.*)$", s25, re.M) if useful(i, 3)]
    manual = [i for i in re.findall(r"^\s*[-*]\s+(.*)$", s25, re.M) if useful(i, 3)]
    if len(assumptions) < 2:
        probs.append("2.5 needs 2 numbered assumptions (found %d)" % len(assumptions))
    if not manual:
        probs.append("2.5 needs at least one item under **Checked manually:**")
    res.add("B1", "FAIL" if probs else "PASS", "; ".join(probs) if probs else
            "scope, AC1-AC6 in your words, %d failure points, contract, %d assumptions" % (len(fps), len(assumptions)))


def check_v1_review(res, sec):
    if "3" not in sec:
        return missing_section(res, ["V1"], 3)
    rows = [r for r in table_rows(sec["3"]) if len(r) >= 4 and useful(r[0]) and sum(1 for c in r[1:] if useful(c)) >= 3]
    seen = set(re.findall(r"\bAC\s?-?\s?([1-5])\b", " ".join(" ".join(r) for r in rows)))
    lost = [n for n in "1234" if n not in seen]
    ok = len(rows) >= 4 and not lost
    res.add("V1", "PASS" if ok else "FAIL", "%d branches reviewed, AC1-AC4 all named" % len(rows) if ok else
            "section 3 needs one row per branch of v1 - 4 or more (found %d) - and AC1-AC4 all named (missing: %s)"
            % (len(rows), ", ".join("AC" + n for n in lost) or "-"))


def check_critique(res, measured, sec):
    if "8" not in sec:
        return missing_section(res, ["V2"], 8)
    rows = [r for r in table_rows(sec["8"]) if len(r) >= 5 and sum(1 for c in r[1:5] if useful(c)) >= 4]
    decided = [r for r in rows if re.search(r"\b(accept|reject|modif)", r[3], re.I)]
    pushed = [r for r in decided if re.search(r"\b(reject|modif)", r[3], re.I)]
    measured["critique_decisions"] = len(decided)
    probs = []
    if len(decided) < 3:
        probs.append("3 rows, each with a claim, how you verified it, accept / reject / modify and a reason (found %d)" % len(decided))
    if not pushed:
        probs.append("at least one recommendation rejected or modified")
    res.add("V2", "FAIL" if probs else "PASS", "section 8 needs " + "; ".join(probs) if probs
            else "%d decisions, %d rejected or modified" % (len(decided), len(pushed)))


def check_generated(res, sec, v1_root):
    if "4" not in sec:
        return missing_section(res, ["G1"], 4)
    rows = [r for r in table_rows(sec["4"]) if len(r) >= 3 and useful(r[0]) and useful(r[2])]
    found, absent = [], []
    for r in rows:
        path = r[1].strip().strip("`").lstrip("./")
        if not path or not useful(path):
            continue
        if v1_root and os.path.isfile(os.path.join(v1_root, path)):
            found.append(path)
        else:
            absent.append(path)
    if len(found) >= 2:
        res.add("G1", "PASS", "%d files named, found in web/original/: %s" % (len(found), ", ".join(found[:3]))
                + ("; not found: %s" % ", ".join(absent[:3]) if absent else ""))
    else:
        res.add("G1", "FAIL" if v1_root else "ERROR",
                "section 4 needs 2 generated files with paths that exist in web/original/ (found %d%s)"
                % (len(found), "; not found: " + ", ".join(absent[:3]) if absent else ""))


def check_bolt_prompt(res, sec):
    if "4" not in sec:
        return missing_section(res, ["X4"], 4)
    prompt = fenced_after(sec["4"], "Prompt as sent")
    if not prompt or not useful(prompt, 20):
        res.add("X4", "FAIL" if prompt is not None else "ERROR",
                "section 4 needs the Bolt prompt exactly as you sent it, under **Prompt as sent:**")
        return
    acs = set(re.findall(r"\bAC\s?-?\s?([1-6])\b", prompt, re.I))
    lost = ["AC%s" % n for n in "123456" if n not in acs]
    # His Week 06 prompt forbade "authentication, backend services": a reused prompt keeps it.
    week06 = "do not add authentication, backend services" in re.sub(r"\s+", " ", prompt.lower())
    patterns = {"login": r"log[ -]?in|sign[ -]?in|authenticat", "backend": r"back[ -]?end",
                "database": r"data ?base|\bdb\b|persist|storage"}
    forbid = [] if week06 else [w for w, p in patterns.items() if not re.search(p, prompt, re.I)]
    probs = []
    if lost:
        probs.append("it does not carry " + ", ".join(lost))
    if forbid:
        probs.append("it does not forbid " + ", ".join(forbid))
    res.add("X4", "FAIL" if probs else "PASS", "the Bolt prompt: " + "; ".join(probs) if probs
            else "AC1-AC6 included; login, backend and database excluded")


def case_table(sec):
    out = {}
    for cells in table_rows(sec.get("5", "")):
        cid = cells[0].strip().upper() if cells else ""
        if re.match(r"^T(1[0-2]|[1-9])$", cid) and cid not in out and len(cells) >= 8:
            out[cid] = cells
    return out


def check_cases(res, measured, sec, path):
    if "5" not in sec:
        return missing_section(res, ["C1", "C2", "C3", "C4"], 5)
    rows = case_table(sec)
    probs = []
    for cid, name, expected, _ in TABLE:
        r = rows.get(cid)
        if r is None:
            probs.append("row %s missing" % cid)
            continue
        if page_value(r[3]) != expected:
            probs.append("%s: Expected says %r - it is %s, from the ACs" % (cid, r[3], expected))
        if cid != "T12":
            for col, label in ((4, "Python v1"), (5, "Python final")):
                if py_value(r[col]) not in ("true", "false", "error"):
                    probs.append("%s %s: write True, False or Error" % (cid, label))
        for col, label in ((6, "page v1"), (7, "page final")):
            if page_value(r[col]) is None:
                probs.append("%s %s: write Available, Unavailable or Not testable" % (cid, label))
    res.add("C1", "FAIL" if probs and rows else ("ERROR" if not rows else "PASS"),
            "; ".join(probs[:5]) + (" (+%d more)" % (len(probs) - 5) if len(probs) > 5 else "") if probs
            else "twelve rows, every result filled")

    expected_py = {cid: ("true" if exp == "Available" else "false") for cid, _, exp, c in TABLE if c}
    measured["python_final_matches"] = sum(1 for cid in expected_py if cid in rows and py_value(rows[cid][5]) == expected_py[cid])
    measured["page_final_matches"] = sum(1 for cid, _, exp, _ in TABLE if cid in rows and page_value(rows[cid][7]) == exp)

    for cid_check, col, path_file, label in (("C2", 4, V1, "v1"), ("C3", 5, IMPL, "final")):
        if path == "B":
            filled = [cid for cid in expected_py if cid in rows and py_value(rows[cid][col]) in ("true", "false", "error")]
            res.add(cid_check, "PASS" if len(filled) == len(expected_py) else "FAIL",
                    "Path B: %d of 11 results reported - your grader compares them with section 12" % len(filled))
            continue
        if not os.path.exists(path_file):
            res.add(cid_check, "ERROR", "%s not found, nothing to run" % path_file.replace(os.sep, "/"))
            continue
        actual = table_actuals(path_file)
        if actual is None:
            res.add(cid_check, "ERROR", "%s did not finish running" % path_file.replace(os.sep, "/"))
            continue
        wrong = []
        for cid in expected_py:
            if cid not in rows:
                continue
            said = py_value(rows[cid][col])
            if said != actual[cid]:
                wrong.append("%s: you wrote %s, it returns %s" % (cid, rows[cid][col] or "nothing", actual[cid].capitalize()))
        measured["python_%s_actual" % label] = actual
        res.add(cid_check, "FAIL" if wrong else "PASS",
                "; ".join(wrong[:4]) + (" (+%d more)" % (len(wrong) - 4) if len(wrong) > 4 else "") if wrong
                else "all 11 match a run of %s" % path_file.replace(os.sep, "/"))

    off = []
    for cid, _, exp, _ in TABLE:
        if cid not in rows:
            continue
        got = page_value(rows[cid][7])
        if got == exp or (got == "Not testable" and cid in DAY_BOUND_CASES):
            continue
        off.append("%s: %s" % (cid, got or "empty"))
    res.add("C4", "FAIL" if off else ("PASS" if rows else "ERROR"),
            "page final differs from expected - " + ", ".join(off) if off else
            "every case gives the expected result on the final page (Not testable accepted on T8/T9)")


def check_traceability(res, sec):
    if "6" not in sec:
        return missing_section(res, ["TR1"], 6)
    rows = {r[0].upper().replace(" ", ""): r for r in table_rows(sec["6"]) if r}
    thin = [ac for ac in ("AC%d" % n for n in range(1, 7))
            if ac not in rows or len(rows[ac]) < 6 or sum(1 for c in rows[ac][1:6] if useful(c)) < 5]
    res.add("TR1", "FAIL" if thin else "PASS", "rows incomplete: " + ", ".join(thin) if thin
            else "AC1-AC6 each traced to a file, inputs, expected, v1 and final")


def check_issues(res, measured, sec):
    if "7" not in sec:
        return missing_section(res, ["I1", "I2"], 7)
    rows = [r for r in table_rows(sec["7"]) if len(r) >= 6 and sum(1 for c in r[1:6] if useful(c)) >= 5]
    good = [r for r in rows if re.search(r"\b(high|medium|low)\b", r[3], re.I)]
    measured["issues"] = len(rows)
    res.add("I1", "PASS" if len(good) >= 2 else "FAIL",
            "%d issues, each with reproduction, priority, change and retest" % len(good) if len(good) >= 2 else
            "section 7 needs 2 issues with every column filled and a priority of High, Medium or Low (found %d)" % len(good))
    probs = []
    for r in rows:
        if not re.search(r"\bT(1[0-2]|[1-9])\b|\bAC\s?-?[1-6]\b", r[2], re.I):
            probs.append("issue %s: the reproduction names no case (T1-T12) or AC" % r[0])
        if GENERIC_PROMPT.search(r[4]):
            probs.append("issue %s: a generic prompt - name the behaviour to change" % r[0])
    ba = label_value(sec["7"], "Before / after") or ""
    if not useful(ba, 6) or not re.search(r"\b(\d+)\b", re.sub(r"before-1|after-1", "", ba)):
        probs.append("the **Before / after:** line must say which issue the screenshots show")
    res.add("I2", "FAIL" if probs or not rows else "PASS",
            "; ".join(probs) if probs else ("no issues to check" if not rows else "reproductions named, prompts focused, before/after described"))


def check_agent(res, sec):
    if "9" not in sec:
        return missing_section(res, ["A1", "A2", "A3"], 9)
    steps = {r[0].strip().lower(): r[1] for r in table_rows(sec.get("9.1", "")) if len(r) > 1}
    thin = [s for s in LOOP_STEPS if not useful(steps.get(s, ""), 3)]
    res.add("A1", "FAIL" if thin else "PASS", "steps empty or under 3 words: " + ", ".join(thin) if thin
            else "all six steps described")
    rows = [r for r in table_rows(sec.get("9.2", "")) if len(r) >= 4 and sum(1 for c in r[:4] if useful(c)) >= 4]
    obs = [r for r in rows if re.search(r"\bobserved\b", r[3], re.I)]
    ass = [r for r in rows if re.search(r"\bassumed\b", r[3], re.I)]
    probs = []
    if len(rows) < 3:
        probs.append("3 complete rows (found %d)" % len(rows))
    if not obs or not ass:
        probs.append("Observed and Assumed each used at least once in the last column")
    res.add("A2", "FAIL" if probs else "PASS", "section 9.2 needs " + "; ".join(probs) if probs
            else "%d rows - %d observed, %d assumed" % (len(rows), len(obs), len(ass)))
    s93 = sec.get("9.3", "")
    cp = len(words(label_value(s93, "Safety checkpoint") or "")) if useful(label_value(s93, "Safety checkpoint") or "") else 0
    dep = label_value(s93, "Reliability, security, responsibility") or ""
    dw = len(words(dep)) if useful(dep) else 0
    probs = []
    if cp < 25:
        probs.append("**Safety checkpoint:** %d words, 25 or more" % cp)
    if dw < 40:
        probs.append("**Reliability, security, responsibility:** %d words, 40 or more" % dw)
    res.add("A3", "FAIL" if probs else "PASS", "; ".join(probs) if probs else "checkpoint %d words, dependability %d words" % (cp, dw))


def check_exchanges(res, measured, sec, v1_text):
    ids = ("X1", "X2", "X3", "X5")
    if "11" not in sec:
        return missing_section(res, ids, 11)
    ex = split_sub(sec["11"], r"B\d+")
    measured["exchanges"] = len(ex)
    if not ex:
        for cid in ids:
            res.add(cid, "ERROR", "no ### B1 ... exchanges in section 11")
        return
    probs, stages = [], {}
    for e, block in sorted(ex.items()):
        for name in ("Tool", "Model", "Date", "Stage", "Source"):
            if not useful(meta(block, name)):
                probs.append("%s %s empty" % (e, name))
        mp = model_problem(meta(block, "Model"))
        if mp and "empty" not in mp:
            probs.append("%s model: %s" % (e, mp))
        d = meta(block, "Date")
        if useful(d):
            try:
                if date.fromisoformat(d).year != 2026:
                    probs.append("%s date %s is not in 2026" % (e, d))
            except ValueError:
                probs.append("%s date %r is not YYYY-MM-DD" % (e, d))
        src = meta(block, "Source").lower()
        if useful(src) and not re.search(r"this sis|sis-?03|week-?0?5|week-?0?6", src):
            probs.append("%s source must be this SIS, week-05 or week-06" % e)
        stage = meta(block, "Stage").lower()
        for s in STAGES:
            if s in stage:
                stages.setdefault(s, []).append(e)
    if len(ex) < 4:
        probs.insert(0, "%d exchange(s), 4 or more required" % len(ex))
    res.add("X1", "FAIL" if probs else "PASS", "; ".join(probs[:6]) if probs else
            "%d exchanges, tool, model, date, stage and source on each" % len(ex))

    prompts = {e: fenced_after(b, "Prompt") for e, b in ex.items()}
    responses = {e: fenced_after(b, "Response") for e, b in ex.items()}
    probs = []
    for e in sorted(ex):
        if not useful(prompts[e] or "", 15):
            probs.append("%s prompt missing or under 15 words" % e)
        if not useful(responses[e] or "", 60):
            probs.append("%s response missing or under 60 words - paste it complete" % e)
    res.add("X2", "FAIL" if probs else "PASS", "; ".join(probs[:6]) if probs else "every prompt and response pasted in full")

    lost = [s.capitalize() for s in STAGES if s not in stages]
    res.add("X3", "FAIL" if lost else "PASS", "no exchange with Stage: " + ", ".join(lost) if lost
            else "Plan %s, Generate %s, Critique %s, Repair %s" % tuple(",".join(stages[s]) for s in STAGES))

    if not v1_text:
        res.add("X5", "ERROR", "no Python v1 in code/original/ to look for")
        return
    gen = [e for e in stages.get("generate", [])]
    best = max([share(shingles(v1_text), responses[e] or "") for e in gen] or [0.0])
    res.add("X5", "PASS" if best >= 0.6 else "FAIL",
            "%.0f%% of your v1 is in a Generate response" % (best * 100) if best >= 0.6 else
            ("no exchange has Stage: Generate" if not gen else
             "only %.0f%% of code/original/ is in a Generate response - v1 is the assistant's answer, unedited, "
             "and its exchange is pasted in section 11" % (best * 100)))


def check_output(res, sec, path):
    if "12" not in sec:
        return missing_section(res, ["K1"] + (["P3"] if path == "B" else []), 12)
    blocks = re.findall(r"^(~{3,}|`{3,})[^\n]*\n(.*?)^\1", sec.get("12.1", ""), re.S | re.M)
    real = [b for _, b in blocks if not PLACEHOLDER.search(b) and len([l for l in b.splitlines() if l.strip()]) >= 3]
    ok = bool(real) and (path == "B" or any(re.search(r"^Ran \d+ tests?", b, re.M) for b in real))
    res.add("K1", "PASS" if ok else "FAIL", "suite output pasted" if ok else
            "section 12.1 needs the complete terminal output of your suite"
            + ("" if path == "B" else " (the part ending in 'Ran N tests' and OK or FAILED)"))
    if path == "B":
        rows = [r for r in table_rows(sec.get("12.2", "")) if sum(1 for c in r[1:] if useful(c)) >= 3]
        res.add("P3", "PASS" if len(rows) >= 3 else "FAIL",
                "%d planted faults, each with the test that caught it" % len(rows) if len(rows) >= 3 else
                "section 12.2 needs 3 rows: the line you broke, the AC, the test that failed (found %d)" % len(rows))


def check_reflection(res, measured, sec):
    if "10" not in sec:
        return missing_section(res, ["Q1"], 10)
    n = len(words(sec["10"])) if useful(sec["10"]) else 0
    measured["reflection_words"] = n
    lo, hi = REFLECTION
    res.add("Q1", "PASS" if lo <= n <= hi else "FAIL", "%d words, range %d-%d" % (n, lo, hi))


# --------------------------------------------------------------------------- main


def run():
    res, measured = Results(), {}
    path = detect_path()
    measured["path"] = path

    if path == "B":
        v1_text = check_path_b(res, measured)
    else:
        runs = check_function(res, measured)
        v1_text = check_original_python(res, measured)
        check_suite(res, measured, runs)

    v1_root = check_exports(res, measured)
    check_evidence(res)

    text = read(REPORT)
    if text is None:
        report_ids = ["R1", "R2", "R3", "B1", "V1", "V2", "G1", "C1", "C2", "C3", "C4", "TR1", "I1", "I2",
                      "A1", "A2", "A3", "X1", "X2", "X3", "X4", "X5", "K1", "Q1"] + (["P3"] if path == "B" else [])
        for cid in report_ids:
            res.add(cid, "ERROR", "report.md not found")
    else:
        sec, order = split_sections(text)
        check_structure(res, text, sec, order)
        check_setup(res, measured, sec, path)
        check_baseline(res, sec)
        check_v1_review(res, sec)
        check_critique(res, measured, sec)
        check_generated(res, sec, v1_root)
        check_bolt_prompt(res, sec)
        check_cases(res, measured, sec, path)
        check_traceability(res, sec)
        check_issues(res, measured, sec)
        check_agent(res, sec)
        check_exchanges(res, measured, sec, v1_text)
        check_output(res, sec, path)
        check_reflection(res, measured, sec)
    res.rows.sort(key=lambda r: ORDER.index(r["id"]))
    return res, measured


def print_human(res, measured):
    counts = res.counts()
    print("SIS #03 - can_book, the Bolt prototype, the evidence   (Path %s)" % measured["path"])
    print("Checks behaviour and shape, never the quality of your review.\n")
    width = max(len(r["title"]) for r in res.rows)
    for r in res.rows:
        print(("%-6s %-4s %-*s  %s" % (r["verdict"], r["id"], width, r["title"], r["message"])).rstrip())
    print("-" * 78)
    if measured.get("python_v1_actual"):
        v1 = measured["python_v1_actual"]
        print("Your v1 returns:    " + "  ".join("%s %s" % (k, v[:5]) for k, v in v1.items()))
    if measured.get("python_final_actual"):
        f = measured["python_final_actual"]
        print("Your final returns: " + "  ".join("%s %s" % (k, v[:5]) for k, v in f.items()))
    if measured.get("scope_v1"):
        print("v1 (web/original/) has out-of-scope code: %s - a candidate for your issue log."
              % ", ".join(sorted(set(h["what"] for h in measured["scope_v1"]))))
    if measured.get("outside_contract"):
        print("Not counted for M - these fail on a can_book that follows the contract exactly: "
              + ", ".join(measured["outside_contract"]))
    print("SUMMARY pass=%d fail=%d error=%d   (%d checks)" % (counts["PASS"], counts["FAIL"], counts["ERROR"], len(res.rows)))
    if counts["FAIL"] or counts["ERROR"]:
        print("Every FAIL or ERROR you keep goes in report.md section 13 and in submission.yml known_fails.")
        print("One you report and explain costs you nothing. One you hide costs the whole criterion.")
    else:
        print("Behaviour and shape are clean. The grader still reads your review and opens your screenshots.")


def main():
    parser = argparse.ArgumentParser(description="SIS #03 checker - run from inside sis-03/")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()
    if not os.path.isdir("tests") and not os.path.exists(REPORT) and not os.path.isdir(CODE):
        message = "run this from inside your sis-03/ folder:  cd sis-03 && python tests/check_sis.py"
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
