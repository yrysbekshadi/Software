#!/usr/bin/env python3
"""
check_debugging.py - the Week 08 checker. DO NOT EDIT: the grader runs its own copy over your files.

    python tests/check_debugging.py          # from inside week-08/
    python tests/check_debugging.py --json   # machine-readable, for the grading pipeline

What it checks (31 checks):

    B1-B6    your project in app/: the provided canBook pasted in and repaired with a minimal
             change - BUG-A (touching endpoints) and BUG-B (the check changes the bookings) fixed,
             the rest of the function untouched, the page still using it, the export clean
    S1-S5    your suite: the Week 07 suite kept, plus one regression test named BUG-A and one
             named BUG-B
    K1-K7    the skill you wrote by hand: skills/bug-detector/SKILL.md and the ZIP you uploaded
    E1       evidence/install.png - the installation (or the prompt-only simulation)
    R1-R3    the runs you pasted: green before, failing on the buggy code, green after
    L1-L9    lab-report.md has its sections filled in

It never runs your tests, never runs your code and never talks to an assistant. It reads files.
The terminal output you paste is YOUR evidence; R3 checks that it is consistent with the suite you
committed. A clean run is the floor, not the grade.

Verdicts:
    PASS   the check found what it was looking for
    FAIL   the content is there but wrong, or not enough of it
    ERROR  it could not check: a file, a folder or a section is missing

Exit codes: 0 = no FAIL and no ERROR - 1 = at least one FAIL or ERROR - 3 = wrong directory.
Standard library only.
"""

import argparse
import difflib
import hashlib
import json
import os
import re
import struct
import sys
import zipfile

APP = "app"
SKILL_DIR = os.path.join("skills", "bug-detector")
SKILL = os.path.join(SKILL_DIR, "SKILL.md")
SKILL_ZIP = os.path.join("skills", "bug-detector.zip")
EVIDENCE = "evidence"
REPORT = "lab-report.md"

MAX_EXPORT_MB = 5
MIN_IMAGE_BYTES = 3000
MIN_TESTS = 19
WORDS_MIN, WORDS_MAX = 80, 150
MAX_CHANGED = 4

CODE_EXT = (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".mts", ".cts", ".vue", ".svelte", ".html")
IGNORED_DIRS = (".git", ".bolt", ".vscode", ".idea", "__pycache__", "node_modules", "dist", "coverage")
MODULE_NAMES = tuple("booking" + e for e in (".ts", ".js", ".tsx", ".jsx", ".mts", ".mjs"))
T_IDS = ["T%02d" % n for n in range(1, 15)]

# The provided function, as in buggy/booking.ts and buggy/booking.js. Only canBook is compared:
# everything else in your booking module is yours.
BUGGY_TS = """export function canBook({ start, end, now, blocked, bookings }: {
  start: number;
  end: number;
  now: number;
  blocked: boolean;
  bookings: { start: number; end: number }[];
}): boolean {
  if (!(0 <= start && start < end && end <= 1440)) return false;
  if (!(start > now)) return false;
  if (end - start > 120) return false;
  if (blocked) return false;
  for (const b of bookings) {
    if (start <= b.end && end >= b.start) return false;
  }
  // keep the room's list current with the slot that was just found free
  bookings.push({ start, end });
  return true;
}"""
BUGGY_JS = """export function canBook({ start, end, now, blocked, bookings }) {
  if (!(0 <= start && start < end && end <= 1440)) return false;
  if (!(start > now)) return false;
  if (end - start > 120) return false;
  if (blocked) return false;
  for (const b of bookings) {
    if (start <= b.end && end >= b.start) return false;
  }
  // keep the room's list current with the slot that was just found free
  bookings.push({ start, end });
  return true;
}"""

# The skill, from the practice deck (slides 13-14). These phrases must be in your SKILL.md.
SKILL_STEPS = ("Read acceptance criteria, code, and observed failure.",
               "Reproduce with the smallest deterministic input.",
               "Identify the likely root cause and relevant lines.",
               "Separate confirmed defects from hypotheses.",
               "Suggest a minimal fix, but do not edit code yet.",
               "Propose a regression test and expected result.",
               "Output: defect | evidence | root cause | fix | test.")
SECRET = re.compile(r"\bsk-[A-Za-z0-9_-]{16,}|\bghp_[A-Za-z0-9]{20,}|\bgithub_pat_\w{20,}|\bAKIA[0-9A-Z]{16}\b|"
                    r"\b(?:api[_-]?key|password|passwd|secret|token)\s*[:=]\s*\S{6,}|-----BEGIN [A-Z ]*PRIVATE KEY", re.I)

# The deck's two questions (Tasks #04 and #05), compared after normalising whitespace and quotes.
BASELINE_QUESTION = ("Find the root cause of the failed room-booking test.",
                     "Propose minimal patch and regression test.", "Do not edit code.")
SKILL_QUESTION = ("Use the bug-detector skill to diagnose the failed room-booking test.",)
COMPARE = ["Correct root cause", "Reproducible test", "Minimal proposed patch", "Unsupported claims",
           "Clarity of explanation"]

TITLES = {
    "B1": "project in app/ with a booking module",
    "B2": "the page imports and calls canBook",
    "B3": "canBook is the provided one, changed in %d lines or fewer" % MAX_CHANGED,
    "B4": "BUG-A fixed: touching endpoints are not an overlap",
    "B5": "BUG-B fixed: canBook does not change the bookings",
    "B6": "export is clean: no node_modules, no .env, under %d MB" % MAX_EXPORT_MB,
    "S1": "suite beside the module imports vitest and the real canBook",
    "S2": "nothing mocked, skipped, focused or table-driven",
    "S3": "the Week 07 suite kept: T01-T14, %d tests or more" % MIN_TESTS,
    "S4": "regression test BUG-A: a touching request, exactly true",
    "S5": "regression test BUG-B: an Available call, bookings compared",
    "K1": "skills/bug-detector/SKILL.md exists, named exactly",
    "K2": "YAML frontmatter between two --- lines",
    "K3": "name: bug-detector",
    "K4": "description says what and WHEN",
    "K5": "the seven-step procedure from the deck",
    "K6": "no secrets or keys in the skill",
    "K7": "skills/bug-detector.zip holds bug-detector/SKILL.md, the same file",
    "E1": "installation screenshot: evidence/install.png",
    "R1": "report 2.1: the Week 07 suite green on your own code",
    "R2": "report 2.2-2.3: failures on the buggy code, BUG-A and BUG-B among them",
    "R3": "report 8.2: the final run, all passing, same suite",
    "L1": "report 1: assistant, model, where installed, where run, Vitest",
    "L2": "report 3: defect log for BUG-A and BUG-B",
    "L3": "report 4: checks answered, ZIP listing, installation",
    "L4": "report 5: the question without the skill, and the answer",
    "L5": "report 6: the skill question, the same input, and the answer",
    "L6": "report 7: both columns of the comparison",
    "L7": "report 8: one diff per bug",
    "L8": "report 9.2: one limitation, 20 words or more",
    "L9": "report 10: conclusion of %d-%d words" % (WORDS_MIN, WORDS_MAX),
}
ORDER = list(TITLES)


# --------------------------------------------------------------------------- small helpers


class Results:
    def __init__(self):
        self.rows = []

    def add(self, cid, verdict, message):
        self.rows.append({"id": cid, "title": TITLES[cid], "verdict": verdict, "message": message})

    def counts(self):
        return {v: sum(1 for r in self.rows if r["verdict"] == v) for v in ("PASS", "FAIL", "ERROR")}


def read(path):
    try:
        return open(path, encoding="utf-8", errors="replace").read()
    except (OSError, TypeError):
        return None


def rel(path):
    return path.replace(os.sep, "/") if path else path


def walk_files(root):
    for here, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in IGNORED_DIRS)
        for name in sorted(files):
            yield os.path.join(here, name)


def project_root(folder):
    """The project: the folder itself, or the one sub-folder a downloaded zip unpacks into."""
    if not os.path.isdir(folder):
        return None
    candidates = [folder] + sorted(os.path.join(folder, d) for d in os.listdir(folder)
                                   if os.path.isdir(os.path.join(folder, d)) and d not in IGNORED_DIRS)
    for c in candidates:
        if os.path.isfile(os.path.join(c, "package.json")) or os.path.isfile(os.path.join(c, "index.html")):
            return c
    return None


def is_test_file(path):
    return bool(re.search(r"\.(test|spec)\.[cm]?[jt]sx?$", os.path.basename(path)))


def norm(text):
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r"[‐-―]", "-", text)
    return re.sub(r"\s+", " ", text).strip()


def strip_js_comments(src):
    src = re.sub(r"/\*.*?\*/", " ", src, flags=re.S)
    return re.sub(r"(?m)(^|[^:'\"`\\])//.*$", r"\1", src)


def image_info(path):
    """(width, height) for a real PNG or JPEG, else None."""
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
    for name in sorted(os.listdir(EVIDENCE)):
        base, ext = os.path.splitext(name)
        if base.lower() == stem.lower() and ext.lower() in (".png", ".jpg", ".jpeg"):
            return os.path.join(EVIDENCE, name)
    return None


def image_problem(path):
    if path is None:
        return "missing"
    if os.path.getsize(path) < MIN_IMAGE_BYTES:
        return "%s is too small to be a screenshot" % rel(path)
    if image_info(path) is None:
        return "%s is not a real PNG or JPEG" % rel(path)
    return None


# --------------------------------------------------------------------------- reading a test file

TEST_CALL = re.compile(r"\b(?:test|it)((?:\.\w+)*)\s*\(\s*(['\"`])((?:\\.|(?!\2).)*?)\2", re.S)


def tests_in(src):
    """[(title, modifiers, block)] - one per test(...) / it(...) call, in order."""
    src = strip_js_comments(src or "")
    found = list(TEST_CALL.finditer(src))
    out = []
    for i, m in enumerate(found):
        end = found[i + 1].start() if i + 1 < len(found) else len(src)
        out.append((m.group(3), m.group(1) or "", src[m.start():end]))
    return out


def booleans_asserted(block):
    """The exact boolean values a test block asserts with toBe/toEqual/toStrictEqual."""
    vals = set()
    for m in re.finditer(r"(\.not)?\.(?:toBe|toEqual|toStrictEqual)\(\s*(true|false)\s*\)", block):
        if not m.group(1):
            vals.add(m.group(2) == "true")
    return vals


def without_assertions(block):
    return re.sub(r"\.(?:not\.)?to\w*\([^()]*\)", " ", block)


def ids_in(title):
    return set(re.findall(r"\b(T0[1-9]|T1[0-4]|X[12]|AC5)\b", title))


def vitest_summaries(text):
    """Every 'Tests  1 failed | 16 passed (17)' line in text, as dicts."""
    out = []
    for line in (text or "").splitlines():
        m = re.match(r"^\s*Tests\s+(.*\(\s*(\d+)\s*\))\s*$", line)
        if not m:
            continue
        body = m.group(1)
        get = lambda word: int((re.search(r"(\d+)\s+%s" % word, body) or [0, 0])[1])
        out.append({"failed": get("failed"), "passed": get("passed"), "skipped": get("skipped"),
                    "todo": get("todo"), "total": int(m.group(2))})
    return out


def vitest_version(text):
    m = re.search(r"\bRUN\s+v(\d+\.\d+\.\d+)", text or "")
    return m.group(1) if m else None


# --------------------------------------------------------------------------- lab-report.md parsing

PLACEHOLDER = re.compile(r"\(paste here\)|\(write here[^)]*\)|^<.*>$|yes / no|"
                         r"accept / revise / reject|Detected / Survived|Pass / Fail / Not testable", re.I)


def sections(text):
    """{'1': body, '6.1': body, ...} - split on the numbered '## N.' and '### N.M' headings."""
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
    rows, lines = [], [l.strip() for l in (body or "").splitlines()]
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


def useful(cell):
    cell = re.sub(r"<!--.*?-->", "", cell or "").strip()
    return bool(cell) and not PLACEHOLDER.search(cell)


def blocks(body):
    return re.findall(r"```[^\n]*\n(.*?)```", body or "", re.S)


def real_blocks(body, min_lines=2):
    return [b for b in blocks(body)
            if len([l for l in b.splitlines() if l.strip()]) >= min_lines and not PLACEHOLDER.search(b)]


def strip_comments(body):
    return re.sub(r"<!--.*?-->", " ", body or "", flags=re.S)


def word_count(body):
    body = strip_comments(body)
    body = re.sub(r"```.*?```", " ", body, flags=re.S)
    body = "\n".join(l for l in body.splitlines() if not l.lstrip().startswith((">", "|", "#")))
    return len(re.findall(r"[^\W_]+(?:['’-][^\W_]+)*", body))


def after_marker(body, marker="Write below this line"):
    return body.split(marker, 1)[1] if marker in (body or "") else (body or "")


def row_by_id(rows, rid):
    for cells in rows:
        if cells and cells[0].strip().upper() == rid.upper():
            return cells
    return None


def cell_word(cell, words):
    cell = re.sub(r"<!--.*?-->", "", cell or "").strip().strip("*").strip().lower()
    for w in words:
        if cell == w.lower():
            return w
    return None


PLACEHOLDER = re.compile(r"\(paste here\)|\(write here[^)]*\)|^<.*>$|yes / no(?: / not shown)?", re.I)


def ids_in(title):
    return set(re.findall(r"\b(T0[1-9]|T1[0-4]|X[12]|AC5|BUG-[AB])\b", title))


# --------------------------------------------------------------------------- B: the project


def find_module(root):
    hits = [p for p in walk_files(root) if os.path.basename(p) in MODULE_NAMES]
    hits.sort(key=lambda p: (0 if "/src/" in rel(p) + "/" else 1, len(p)))
    return hits[0] if hits else None


def find_suite(module):
    if not module:
        return None
    folder = os.path.dirname(module)
    for name in sorted(os.listdir(folder)):
        if re.match(r"^booking\.(test|spec)\.[cm]?[jt]sx?$", name):
            return os.path.join(folder, name)
    return None


def function_text(src, name="canBook"):
    """The source of `function canBook ... { ... }` (braces matched), or None."""
    m = re.search(r"(?:export\s+)?(?:async\s+)?function\s+%s\b" % name, src or "")
    if not m:
        return None
    # skip the parameter list (and a TypeScript type literal inside it): the body brace is the
    # first "{" after the ")" that closes the parameters
    depth_paren, j = 0, m.end()
    while j < len(src):
        ch = src[j]
        if ch == "(":
            depth_paren += 1
        elif ch == ")":
            depth_paren -= 1
            if depth_paren == 0:
                break
        j += 1
    i = src.find("{", j)
    if i < 0:
        return None
    depth = 0
    for k in range(i, len(src)):
        if src[k] == "{":
            depth += 1
        elif src[k] == "}":
            depth -= 1
            if depth == 0:
                return src[m.start():k + 1]
    return None


def code_lines(text):
    """Lines of code, comments and blank lines removed, whitespace collapsed."""
    out = []
    for line in strip_js_comments(text or "").splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        if line:
            out.append(line)
    return out


def changed_lines(a, b):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    n = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            n += max(i2 - i1, j2 - j1)
    return n, sm.ratio()


def body_of(fn):
    """The function body only - the part between the body's braces."""
    return fn[fn.index("{", fn.index(")") if ")" in fn else 0):] if fn else ""


def check_project(res, measured):
    root = project_root(APP)
    measured["app_root"] = rel(root)
    sources = [p for p in walk_files(root) if p.lower().endswith(CODE_EXT)] if root else []
    module = None
    if root:
        hits = [p for p in walk_files(root) if os.path.basename(p) in MODULE_NAMES]
        hits.sort(key=lambda p: (0 if "/src/" in rel(p) + "/" else 1, len(p)))
        module = hits[0] if hits else None
    measured["module"] = rel(module)
    fn = function_text(read(module) or "") if module else None

    # B1
    if not root:
        res.add("B1", "ERROR", "no package.json or index.html in app/ - bring your Week 07 app/ over (README Part 0)")
    elif not module:
        res.add("B1", "ERROR", "no booking.ts / booking.js in the project")
    elif not fn:
        res.add("B1", "FAIL", "%s has no `function canBook` - paste the whole function from buggy/" % rel(module))
    else:
        res.add("B1", "PASS", "%s, function canBook" % rel(module))

    # B2
    users = []
    if module:
        imp = re.compile(r"import\s*\{[^}]*\bcanBook\b[^}]*\}\s*from\s*['\"][^'\"]*\bbooking(?:\.[cm]?[jt]sx?)?['\"]")
        for p in sources:
            if p == module or is_test_file(p):
                continue
            src = strip_js_comments(read(p) or "")
            if imp.search(src) and re.search(r"\bcanBook\s*\(", src):
                users.append(rel(p))
    if not module:
        res.add("B2", "ERROR", "no booking module to look for")
    else:
        res.add("B2", "PASS" if users else "FAIL",
                "called from " + ", ".join(users[:3]) if users
                else "no page file imports canBook from the booking module and calls it")

    # B3
    if not fn:
        res.add("B3", "ERROR", "no canBook to compare with the provided one")
        measured["lines_changed"] = None
    else:
        mine = code_lines(fn)
        best = min((changed_lines(code_lines(ref), mine) + (lang,) for lang, ref in (("ts", BUGGY_TS), ("js", BUGGY_JS))),
                   key=lambda t: t[0])
        n, ratio, lang = best
        if module:
            lang = "ts" if module.lower().endswith((".ts", ".tsx", ".mts")) else "js"
        # the body alone decides "minimal": a student whose own module types the parameters
        # differently keeps the provided body and is not charged for the signature
        nb, rb = changed_lines(code_lines(body_of("\n".join(code_lines(BUGGY_JS)))), code_lines(body_of(fn)))
        measured["lines_changed"] = nb
        measured["provided_variant"] = lang
        if rb < 0.6:
            res.add("B3", "FAIL", "canBook is not the provided function - copy the whole function from "
                                  "buggy/booking.%s first, then make one minimal change per bug" % lang)
        elif nb > MAX_CHANGED:
            res.add("B3", "FAIL", "%d lines of the body differ from the provided one - the deck: implement only "
                                  "one minimal change per bug" % nb)
        elif nb == 0:
            res.add("B3", "FAIL", "canBook is still exactly the provided buggy function")
        else:
            res.add("B3", "PASS", "%d line(s) changed in the body" % nb)

    # B4, B5
    body = "\n".join(code_lines(body_of(fn))) if fn else ""
    if not fn:
        res.add("B4", "ERROR", "no canBook to read")
        res.add("B5", "ERROR", "no canBook to read")
    else:
        loose = re.search(r"\bstart\s*<=\s*\w+\.end\b|\bend\s*>=\s*\w+\.start\b|\b\w+\.end\s*>=\s*start\b|"
                          r"\b\w+\.start\s*<=\s*end\b|\bend\s*<\s*\w+\.start\b|\bstart\s*>\s*\w+\.end\b", body)
        compares = re.search(r"\bstart\s*<\s*\w+\.end\b|\b\w+\.end\s*>\s*start\b|\bstart\s*>=\s*\w+\.end\b|"
                             r"\b\w+\.end\s*<=\s*start\b", body)
        res.add("B4", "PASS" if compares and not loose else "FAIL",
                "the overlap test is strict" if compares and not loose
                else "the loop still treats touching endpoints as a conflict (or the checker cannot read the "
                     "condition - write it as start < b.end && end > b.start, or explain in 9.1)")
        mutates = re.findall(r"\bbookings\s*\.\s*(?:push|splice|sort|unshift|pop|shift|reverse|fill|copyWithin)\s*\(|"
                             r"\bbookings\s*(?:\[[^\]]*\])?\s*=(?!=)|\b\w+\.(?:start|end)\s*=(?!=)", body)
        res.add("B5", "FAIL" if mutates else "PASS",
                "canBook still changes the bookings: " + ", ".join(sorted(set(m.strip() for m in mutates)))
                if mutates else "nothing in canBook changes the bookings")

    # B6
    problems = []
    if os.path.isdir(APP):
        size = 0
        for here, dirs, names in os.walk(APP):
            if "node_modules" in dirs:
                problems.append("%s contains node_modules/ - delete it" % rel(here))
                dirs.remove("node_modules")
            for n in names:
                if n == ".env" or n.startswith(".env."):
                    problems.append("%s/%s must not be committed" % (rel(here), n))
                try:
                    size += os.path.getsize(os.path.join(here, n))
                except OSError:
                    pass
        if size > MAX_EXPORT_MB * 1024 * 1024:
            problems.append("app/ is %.1f MB - commit source files only" % (size / 1048576.0))
    if not root:
        res.add("B6", "ERROR", "nothing to check until app/ holds the project")
    else:
        res.add("B6", "FAIL" if problems else "PASS", "; ".join(problems) if problems else "clean")
    return root, module, sources


# --------------------------------------------------------------------------- S: the suite


def check_suite(res, measured, module, sources):
    suite = find_suite(module)
    measured["suite"] = rel(suite)
    src = read(suite) if suite else None
    tests = tests_in(src) if src else []
    measured["tests_final"] = len(tests)
    measured["tests_in_project"] = sum(len(tests_in(read(p) or "")) for p in (sources or []) if is_test_file(p))
    titles = [t for t, _, _ in tests]
    measured["test_titles"] = titles

    def need(cid):
        if suite is None:
            res.add(cid, "ERROR", "no booking.test.ts / booking.test.js beside %s" % (rel(module) or "the booking module"))
            return False
        return True

    clean = strip_js_comments(src or "")
    if need("S1"):
        probs = []
        if not re.search(r"from\s*['\"]vitest['\"]", clean):
            probs.append("import { test, expect } from 'vitest'")
        if not re.search(r"import\s*\{[^}]*\bcanBook\b[^}]*\}\s*from\s*['\"]\./booking(?:\.[cm]?[jt]sx?)?['\"]", clean):
            probs.append("import { canBook } from './booking'")
        res.add("S1", "FAIL" if probs else "PASS",
                "the suite needs: " + "; ".join(probs) if probs else "%s imports vitest and ./booking" % rel(suite))
    if need("S2"):
        bad = []
        if re.search(r"\b(?:vi|jest)\.(?:mock|doMock|spyOn|fn)\s*\(", clean):
            bad.append("a mock or spy - never mock the booking function")
        for m in sorted(set(m for _, m, _ in tests if m)):
            if re.search(r"\.(skip|only|todo|fails|skipIf|runIf)\b", m):
                bad.append("test%s" % m)
        if re.search(r"\b(?:test|it|describe)\.each\b", clean):
            bad.append("test.each / it.each - one test per case")
        if re.search(r"\b(?:describe|suite)\.(?:skip|only|todo)\b|\bx(?:it|test|describe)\s*\(", clean):
            bad.append("a skipped or focused describe block")
        res.add("S2", "FAIL" if bad else "PASS", "; ".join(bad) if bad else "real function, every test runs")

    by_id = {}
    for title, _, block in tests:
        for i in ids_in(title):
            by_id.setdefault(i, []).append(block)
    if need("S3"):
        missing = [t for t in T_IDS if t not in by_id]
        probs = []
        if missing:
            probs.append("no test named " + ", ".join(missing) + " - bring the Week 07 suite over unchanged")
        if len(tests) < MIN_TESTS:
            probs.append("%d tests - your Week 07 suite (17+) and the two regression tests make %d" % (len(tests), MIN_TESTS))
        res.add("S3", "FAIL" if probs else "PASS", "; ".join(probs) if probs else "T01-T14 present, %d tests" % len(tests))
    if need("S4"):
        blocks_a = by_id.get("BUG-A", [])
        good = [b for b in blocks_a if True in booleans_asserted(b)]
        res.add("S4", "PASS" if good else "FAIL",
                "BUG-A regression test present" if good else
                ("the BUG-A test must assert .toBe(true) - a touching request is Available (AC4)" if blocks_a
                 else "no test named BUG-A - README Part 1, step 5"))
    if need("S5"):
        blocks_b = by_id.get("BUG-B", [])
        good = [b for b in blocks_b if True in booleans_asserted(b) and re.search(r"bookings", b)
                and re.search(r"JSON\.stringify|\.to(?:Strict)?Equal\(|structuredClone|\.toBe\(\s*before", b)]
        res.add("S5", "PASS" if good else "FAIL",
                "BUG-B regression test present" if good else
                ("the BUG-B test must call canBook on an AVAILABLE request (.toBe(true)) and compare the bookings "
                 "with a copy taken before" if blocks_b else "no test named BUG-B - README Part 1, step 5"))


# --------------------------------------------------------------------------- K, E: the skill


def frontmatter(text):
    lines = (text or "").replace("﻿", "").splitlines()
    if not lines or lines[0].rstrip() != "---":
        return None, "the first line must be exactly ---"
    for i in range(1, len(lines)):
        if lines[i].rstrip() == "---":
            meta = {}
            for line in lines[1:i]:
                m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
                if m:
                    meta[m.group(1)] = m.group(2).strip().strip("\"'")
            return meta, "\n".join(lines[i + 1:])
    return None, "no closing --- line after the frontmatter"


def check_skill(res, measured):
    folder_files = os.listdir(SKILL_DIR) if os.path.isdir(SKILL_DIR) else []
    text = read(SKILL) if "SKILL.md" in folder_files else None
    if text is None:
        near = [f for f in folder_files if f.lower().startswith("skill")]
        res.add("K1", "ERROR", ("found %s - the file must be named exactly SKILL.md (uppercase SKILL, no .txt)" % near[0])
                if near else "no skills/bug-detector/SKILL.md")
        for cid in ("K2", "K3", "K4", "K5", "K6"):
            res.add(cid, "ERROR", "no SKILL.md to read")
    else:
        res.add("K1", "PASS", "skills/bug-detector/SKILL.md")
        meta, rest = frontmatter(text)
        if meta is None:
            res.add("K2", "FAIL", rest)
            meta, body = {}, text
        else:
            missing = [k for k in ("name", "description") if not meta.get(k)]
            res.add("K2", "FAIL" if missing else "PASS",
                    "the frontmatter has no " + " or ".join(missing) if missing else "frontmatter with name and description")
            body = rest
        name = meta.get("name", "")
        res.add("K3", "PASS" if name == "bug-detector" else "FAIL",
                "name: bug-detector" if name == "bug-detector"
                else "name must be bug-detector (lowercase, hyphens, the folder's name) - found %r" % name)
        desc = meta.get("description", "")
        ok = bool(re.search(r"\buse (?:it )?when\b", desc, re.I)) and len(desc.split()) >= 10
        res.add("K4", "PASS" if ok else "FAIL",
                "description says when to use it" if ok
                else "the description must say what the skill does and WHEN to use it ('Use when ...'), 10 words or more")
        have = norm(body)
        lost = [s for s in SKILL_STEPS if norm(s) not in have]
        res.add("K5", "FAIL" if lost else "PASS",
                "missing from the procedure: \"%s\"%s" % (lost[0], " (+%d more)" % (len(lost) - 1) if len(lost) > 1 else "")
                if lost else "all seven steps")
        hit = SECRET.search(text)
        res.add("K6", "FAIL" if hit else "PASS",
                "remove what looks like a secret: %s..." % hit.group(0)[:12] if hit else "nothing that looks like a key or password")

    if not os.path.exists(SKILL_ZIP):
        res.add("K7", "ERROR", "no skills/bug-detector.zip - commit the ZIP you uploaded (README Part 2)")
    else:
        try:
            with zipfile.ZipFile(SKILL_ZIP) as z:
                names = [n for n in z.namelist() if not n.startswith("__MACOSX/")]
                measured["zip_names"] = names[:20]
                entry = next((n for n in names if n.replace("\\", "/") == "bug-detector/SKILL.md"), None)
                if entry is None:
                    hint = [n for n in names if n.lower().endswith(("skill.md", "skill.md.txt"))]
                    res.add("K7", "FAIL", "the ZIP must hold bug-detector/SKILL.md - it holds %s"
                            % (", ".join(hint or names[:4]) or "nothing"))
                elif text is not None and norm(z.read(entry).decode("utf-8", "replace")) != norm(text):
                    res.add("K7", "FAIL", "bug-detector/SKILL.md inside the ZIP differs from skills/bug-detector/SKILL.md "
                                          "- zip the folder again after your last edit")
                else:
                    res.add("K7", "PASS", "bug-detector/SKILL.md, same as the committed file")
        except zipfile.BadZipFile:
            res.add("K7", "FAIL", "skills/bug-detector.zip is not a valid ZIP file")

    p = find_image("install")
    why = image_problem(p)
    res.add("E1", "PASS" if not why else ("FAIL" if p else "ERROR"),
            rel(p) if not why else (why if p else "evidence/install.png not found - a screenshot of the upload, "
                                                 "or of the prompt-only simulation"))


# --------------------------------------------------------------------------- R, L: the report


def failing_names(text):
    return [l for l in (text or "").splitlines() if re.match(r"^\s*(×|✗|FAIL\b|❯.*failed)", l)]


def check_runs(res, measured, sec):
    s21 = vitest_summaries(" ".join(blocks(sec.get("2.1", ""))))
    measured["baseline_run"] = s21[-1] if s21 else None
    if not s21:
        res.add("R1", "FAIL", "section 2.1 has no Vitest output - run your Week 07 suite before replacing anything")
    else:
        f = s21[-1]
        res.add("R1", "PASS" if f["failed"] == 0 else "FAIL",
                "%(passed)d passed (%(total)d)" % f if f["failed"] == 0
                else "%d failed on your own code - fix or explain under the block before you start" % f["failed"])

    t22 = " ".join(blocks(sec.get("2.2", "")))
    t23 = " ".join(blocks(sec.get("2.3", "")))
    s22, s23 = vitest_summaries(t22), vitest_summaries(t23)
    measured["buggy_run"] = s22[-1] if s22 else None
    probs = []
    if not s22 or not s22[-1]["failed"]:
        probs.append("2.2: the run of your suite on the provided canBook, with its failures")
    fails = " ".join(failing_names(t23))
    missing = [b for b in ("BUG-A", "BUG-B") if b not in fails]
    if not s23:
        probs.append("2.3: the run with the two regression tests on the buggy code")
    elif missing:
        probs.append("2.3: %s must fail on the buggy code (a failing line naming it)" % " and ".join(missing))
    res.add("R2", "FAIL" if probs else "PASS",
            "section " + "; ".join(probs) if probs else
            "%d failed on the buggy code; BUG-A and BUG-B fail before the fix" % s22[-1]["failed"])

    s82 = vitest_summaries(" ".join(blocks(sec.get("8.2", ""))))
    if not s82:
        res.add("R3", "FAIL", "section 8.2 has no Vitest output of the final suite")
    else:
        f = s82[-1]
        probs = []
        if f["failed"]:
            probs.append("%d failed" % f["failed"])
        have = measured.get("tests_in_project")
        if have and f["total"] != have:
            probs.append("the output reports %d tests, the test files in app/ hold %d - paste the run of the "
                         "suite you committed" % (f["total"], have))
        res.add("R3", "FAIL" if probs else "PASS", "; ".join(probs) if probs else "%(passed)d passed (%(total)d)" % f)

    setup = {r[0].lower(): r[1] for r in table_rows(sec.get("1", "")) if len(r) > 1}
    declared = next((v for k, v in setup.items() if "vitest version" in k and useful(v)), "")
    m = re.search(r"(\d+\.\d+(?:\.\d+)?)", declared)
    measured["vitest_version"] = m.group(1) if m else vitest_version(" ".join(blocks(sec.get("8.2", ""))))


def check_report(res, measured, sec):
    def add(cid, ok, good, bad):
        res.add(cid, "PASS" if ok else "FAIL", good if ok else bad)

    # L1
    setup = {r[0].lower(): r[1] for r in table_rows(sec.get("1", "")) if len(r) > 1}
    need = {"assistant": "the assistant", "exact model": "the exact model", "installed": "where the skill was installed",
            "ran the tests": "where you ran the tests", "vitest version": "the Vitest version", "language": "ts or js"}
    lacking = [say for key, say in need.items() if not any(key in k and useful(v) for k, v in setup.items())]
    add("L1", not lacking, "setup recorded", "section 1 has no value for: " + ", ".join(lacking))

    # L2
    rows = table_rows(sec.get("3", ""))
    logged = [r for r in rows if len(r) >= 6 and re.match(r"^\s*\S", r[0]) and r[0].strip().lower() != "defect"
              and sum(1 for c in r[1:6] if useful(c)) == 5]
    measured["defects_logged"] = len(logged)
    have = {r[0].strip().upper() for r in logged}
    lacking = [b for b in ("BUG-A", "BUG-B") if b not in have]
    add("L2", not lacking, "%d defect(s) logged" % len(logged),
        "section 3: fill every column for " + " and ".join(lacking))

    # L3
    s4 = sec.get("4", "")
    checks = [r for r in table_rows(s4) if len(r) >= 2 and r[0] and not r[0].lower().startswith("check")]
    yes = [r for r in checks if re.sub(r"<!--.*?-->", "", r[1]).strip().lower() == "yes"]
    listing = real_blocks(s4, 1)
    install = word_count(after_marker(s4))
    probs = []
    if len(yes) < 4:
        probs.append("all four checks answered yes (found %d) - fix the file first if one is no" % len(yes))
    if not listing or "SKILL.md" not in " ".join(listing):
        probs.append("the ZIP listing showing bug-detector/SKILL.md")
    if install < 15:
        probs.append("15+ words on the installation (found %d)" % install)
    add("L3", not probs, "checks, listing and installation recorded", "section 4 needs " + "; ".join(probs))

    # L4
    s5 = blocks(sec.get("5", ""))
    sent5 = norm(s5[0]) if s5 else ""
    probs = []
    lost = [q for q in BASELINE_QUESTION if norm(q) not in sent5]
    if lost:
        probs.append("the deck's question as sent (missing: \"%s\")" % lost[0])
    elif len(sent5.split()) < 60:
        probs.append("the input after the question: AC1-AC6, the failing output and canBook")
    if len(s5) < 2 or len(norm(s5[1]).split()) < 30 or PLACEHOLDER.search(s5[1]):
        probs.append("the assistant's answer (30+ words)")
    add("L4", not probs, "question, input and answer", "section 5 needs " + "; ".join(probs))

    # L5
    s6 = blocks(sec.get("6", ""))
    sent6 = norm(s6[0]) if s6 else ""
    probs = []
    lost = [q for q in SKILL_QUESTION if norm(q) not in sent6]
    if lost:
        probs.append("the deck's skill question as sent")
    else:
        def strip_q(text, questions):
            for q in questions:
                text = text.replace(norm(q), " ")
            return norm(text)
        a, b = strip_q(sent5, BASELINE_QUESTION), strip_q(sent6, SKILL_QUESTION)
        ratio = difflib.SequenceMatcher(None, a, b, autojunk=False).ratio() if a and b else 0
        measured["input_similarity"] = round(ratio, 3)
        if ratio < 0.9:
            probs.append("exactly the same input as section 5 (the two differ beyond the question: %.0f%% alike)" % (ratio * 100))
    if len(s6) < 2 or len(norm(s6[1]).split()) < 30 or PLACEHOLDER.search(s6[1]):
        probs.append("the assistant's answer (30+ words)")
    add("L5", not probs, "same input, skill question, answer", "section 6 needs " + "; ".join(probs))

    # L6
    rows = table_rows(sec.get("7", ""))
    done = [c for c in COMPARE if any(r and r[0].strip().lower() == c.lower() and len(r) >= 3
                                      and useful(r[1]) and useful(r[2]) for r in rows)]
    add("L6", len(done) == len(COMPARE), "all five criteria judged",
        "section 7: fill both columns for " + ", ".join(c for c in COMPARE if c not in done))

    # L7
    diffs = 0
    for key in ("8.1", "8.2"):
        text = " \n".join(blocks(sec.get(key, "")))
        if re.search(r"(?m)^\s*-\s*.*\S", text) and re.search(r"(?m)^\s*\+\s*.*\S", text) or \
                re.search(r"(?mi)^\s*(old|before)\s*:", text) and re.search(r"(?mi)^\s*(new|after)\s*:", text) or \
                re.search(r"(?m)^\s*-\s*.*\bbookings\.push\b", text):
            diffs += 1
    measured["diffs"] = diffs
    add("L7", diffs == 2, "a diff for each bug", "section 8: paste the diff of each patch in 8.1 and 8.2 (found %d)" % diffs)

    # L8
    words = word_count(sec.get("9.2", ""))
    add("L8", words >= 20, "%d words" % words, "section 9.2 needs 20 words or more (found %d)" % words)

    # L9
    words = word_count(sec.get("10", ""))
    measured["conclusion_words"] = words
    add("L9", WORDS_MIN <= words <= WORDS_MAX, "%d words" % words,
        "section 10 has %d words, the task asks for %d-%d" % (words, WORDS_MIN, WORDS_MAX))


# --------------------------------------------------------------------------- main


def run():
    res, measured = Results(), {}
    root, module, sources = check_project(res, measured)
    check_suite(res, measured, module, sources)
    check_skill(res, measured)
    text = read(REPORT)
    if text is None:
        for cid in ORDER:
            if cid[0] in "RL":
                res.add(cid, "ERROR", "lab-report.md not found")
    else:
        sec = sections(text)
        check_runs(res, measured, sec)
        check_report(res, measured, sec)
    res.rows = sorted(res.rows, key=lambda r: ORDER.index(r["id"]))
    return res, measured


def print_human(res, measured):
    counts = res.counts()
    print("Week 08 - debugging with a skill: the repair, the tests, the skill, the report\n")
    width = max(len(r["title"]) for r in res.rows)
    for r in res.rows:
        print(("%-6s %-4s %-*s  %s" % (r["verdict"], r["id"], width, r["title"], r["message"])).rstrip())
    print("-" * 78)
    print("SUMMARY pass=%d fail=%d error=%d   (%d checks)"
          % (counts["PASS"], counts["FAIL"], counts["ERROR"], len(res.rows)))
    if counts["FAIL"] or counts["ERROR"]:
        print("Every FAIL or ERROR you keep goes in lab-report.md section 9.1 and in submission.yml known_fails.")
        print("One you report and explain costs you nothing. One you hide costs the whole criterion.")
    else:
        print("Files and shape are clean. Whether the skill helped is your judgement in section 7, not this.")


def main():
    parser = argparse.ArgumentParser(description="Week 08 checker - run from inside week-08/")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    if not os.path.isdir("tests") and not os.path.exists(REPORT) and not os.path.isdir(APP):
        message = "run this from inside your week-08/ folder:  cd week-08 && python tests/check_debugging.py"
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
