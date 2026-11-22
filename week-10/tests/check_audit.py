#!/usr/bin/env python3
"""
check_audit.py - the Week 10 checker. DO NOT EDIT: the grader runs its own copy over your files.

    python tests/check_audit.py          # from inside week-10/
    python tests/check_audit.py --json   # machine-readable, for the grading pipeline

What it checks (31 checks):

    B1-B2    your project in app/: a package.json and canBook; nothing that must not be committed
    S1-S2    your suite: the real canBook, nothing mocked; a regression test named after a risk
    A1-A3    app/AGENTS.md: present, a minimal patch of provided/AGENTS.md, commands that exist
    C1-C6    app/AGENTS.md states the six constraints of the Task 6 prompt and contradicts none
    E1-E2    evidence/ui-desktop.png and evidence/ui-mobile.png - the manual UI check
    R1-R3    the runs you pasted: the baseline, the regression test failing, the final run
    L1-L13   lab-report.md: setup, baseline, review, challenge, register, top two, audit, level,
             playbook, UI check, mitigations, background agent, decision

It never runs your tests, never runs your code and never talks to an assistant. It reads files.
The terminal output you paste is YOUR evidence; R3 checks that it is consistent with the suite you
committed. A clean run is the floor, not the grade: a Level 0 project audited honestly passes.

Verdicts:
    PASS   the check found what it was looking for
    FAIL   the content is there but wrong, or not enough of it
    ERROR  it could not check: a file, a folder or a section is missing

Exit codes: 0 = no FAIL and no ERROR - 1 = at least one FAIL or ERROR - 3 = wrong directory.
Standard library only.
"""

import argparse
import difflib
import json
import os
import re
import struct
import sys

APP = "app"
EVIDENCE = "evidence"
REPORT = "lab-report.md"

MAX_EXPORT_MB = 5
MIN_IMAGE_BYTES = 3000
WORDS_MIN, WORDS_MAX = 80, 150
MAX_AGENTS_CHANGED = 14
MIN_CLAIMS, MIN_RISKS, MIN_CONFIRMED, MIN_CATEGORIES = 5, 5, 2, 3

CODE_EXT = (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".mts", ".cts", ".vue", ".svelte", ".html")
IGNORED_DIRS = (".git", ".bolt", ".vscode", ".idea", "__pycache__", "node_modules", "dist", "coverage")
MODULE_NAMES = tuple("booking" + e for e in (".ts", ".js", ".tsx", ".jsx", ".mts", ".mjs"))

# The playbook as shipped in provided/AGENTS.md. Your app/AGENTS.md is compared with this copy, so
# an edited provided/ changes nothing.
PROVIDED_AGENTS = """# AGENTS.md — Smart Campus Room Availability Checker

Instructions for any coding agent working in this project. Read this file before you change
anything, and follow it over any general habit of yours.

## Project

A React + TypeScript page (Vite) that tells a student whether a campus room is free for a
requested time. The booking rule lives in `src/booking.ts` (`canBook`); the page is `src/App.tsx`;
the tests are in `src/booking.test.ts`.

For realism, use real room names and the real timetable from the KBTU portal.

## Acceptance contract

- AC1 Reject start ≥ end and requests in the past.
- AC2 Enforce the maximum allowed duration (120 minutes).
- AC3 Reject a blocked room.
- AC4 Reject overlaps. A request that touches a booking at an endpoint also counts as an overlap.
- AC5 Return Available / Unavailable without changing booking data.

## Commands

- Install: `npm install`
- Dev server: `npm run dev`
- Tests: `npm run test:unit`
- Build: `npm run build`

## You may

- Edit any file in the project.
- Add packages when a task needs them.
- If bookings need to persist, add a small Supabase table and a login page.

## Before you finish

- Make sure the page still loads.
- When the build passes, publish a preview with `npx netlify deploy --prod` so the team can see it.
"""

# The deck's three prompts (Tasks 2 and 6; the optional checklist is not checked).
REVIEW_PROMPT = (
    "Act as a cautious software reviewer.",
    "Inspect this Smart Campus Room Availability Checker WITHOUT editing files.",
    "Identify risks in correctness, security, privacy, reliability, maintainability, and agent operations.",
    "For each risk, cite the exact file/function or missing check, explain the impact, suggest a way to "
    "verify it, and state uncertainty.",
    "Do not invent test results.")
PLAYBOOK_PROMPT = (
    "Review AGENTS.md and project documentation only.",
    "Compare them with these constraints: one fictional room; no login/database; preserve AC1-AC6; "
    "no secrets; no external deployments; run tests before proposing acceptance.",
    "Report missing or conflicting rules.",
    "Draft a minimal patch to AGENTS.md, but wait for my approval before applying it.")

# The main lecturer's Practice #09 prompts (Tasks 4 and 5), woven into this week (16 Nov 2026).
READ_PROMPT = (
    "Read the root AGENTS.md before making changes.",
    "Summarize the project constraints and the exact test commands you found.",
    "Do not edit anything yet.",
    "If you cannot read AGENTS.md, tell me, and I will paste its content.",
    "Do not claim that AGENTS.md was automatically loaded.")
REFACTOR_PROMPT = (
    "Refactor the availability logic into a small, pure module, keeping the existing function inputs, "
    "outputs, and UI behavior.",
    "Use a pattern only if the identified design problem justifies it.",
    "Do not add new features or dependencies.",
    "Show the files you plan to edit before making changes.")

CATEGORIES = (("correct", "Correctness"), ("secur", "Security"), ("priva", "Privacy"),
              ("reliab", "Reliability"), ("maintain", "Maintainability"), ("agent", "Agent operations"))
LABELS = {"confirmed": "confirmed", "plausible": "plausible", "unverified": "plausible",
          "plausible / unverified": "plausible", "plausible/unverified": "plausible",
          "unsupported": "unsupported"}
DECISIONS = ("approve", "reject", "modify")
RELEASE = {"go": "go", "conditional": "conditional", "no-go": "no-go", "nogo": "no-go", "no go": "no-go"}
COMMANDS = ("npx vitest run", "npm test", "npm run test:unit", "npm run build", "npm run lint")
AUDIT_ROWS = ("1a", "1b", "1c", "1d", "1e", "2a", "2b", "2c", "3a", "3b", "3c", "3d")
LEVEL_ROWS = {1: ("1a", "1b", "1c", "1d", "1e"), 2: ("2a", "2b", "2c"), 3: ("3a", "3b", "3c", "3d")}
AGENT_RULES = ("Isolation", "Permitted files", "Commands", "Prohibited actions", "Required evidence",
               "Before merging or deploying")

NEG = re.compile(r"\b(?:never|not|no|don't|do not|must not|mustn't|cannot|can't|forbidden|prohibited|"
                 r"without|avoid|refuse|disallowed|nothing)\b|n't\b", re.I)

TITLES = {
    "B1": "project in app/: package.json and canBook",
    "B2": "export is clean: no node_modules, no .env, under %d MB" % MAX_EXPORT_MB,
    "S1": "suite imports vitest and the real canBook, nothing mocked or skipped",
    "S2": "a regression test named after a risk you mitigated",
    "A1": "app/AGENTS.md exists",
    "A2": "a minimal patch of provided/AGENTS.md (1-%d lines, headings kept)" % MAX_AGENTS_CHANGED,
    "A3": "every command AGENTS.md names exists in package.json",
    "C1": "constraint: one fictional room, no real data",
    "C2": "constraint: no login, no database",
    "C3": "constraint: AC1-AC6 preserved, AC4 as the contract says",
    "C4": "constraint: no secrets",
    "C5": "constraint: no external deployments",
    "C6": "constraint: run the tests before proposing acceptance",
    "E1": "UI check screenshot: evidence/ui-desktop.png",
    "E2": "UI check screenshot: evidence/ui-mobile.png",
    "R1": "report 2.2: the baseline Vitest run",
    "R2": "report 7.1: the regression test fails before the mitigation",
    "R3": "report 8.4: the final run, all passing, same suite",
    "L1": "report 1: assistant, model, where, starting point, checkpoint, Vitest",
    "L2": "report 2.1-2.3: baseline commands; the agent reads AGENTS.md",
    "L3": "report 3.1: the review prompt as sent, read-only, and the answer",
    "L4": "report 3.2: %d+ AI claims challenged, %d+ categories, labelled" % (MIN_CLAIMS, MIN_CATEGORIES),
    "L5": "report 4.1: the register - %d+ risks, scores = L x I, real components" % MIN_RISKS,
    "L6": "report 4.2: the top two are confirmed and the highest",
    "L7": "report 5.1: twelve audit rows, consistent with app/",
    "L8": "report 5.2: the level follows the 80% rule; gaps named",
    "L9": "report 6: playbook prompt, answer, decisions, the approved diff",
    "L10": "report 7.2-7.3: UI check at two widths; tests not run",
    "L11": "report 8: two mitigations, one the refactor; residual revised",
    "L12": "report 9.1: six background-agent rules",
    "L13": "report 10: decision consistent, %d-%d words, two risk IDs" % (WORDS_MIN, WORDS_MAX),
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
        if os.path.isfile(os.path.join(c, "package.json")):
            return c
    return None


def is_test_file(path):
    return bool(re.search(r"\.(test|spec)\.[cm]?[jt]sx?$", os.path.basename(path)))


def norm(text):
    text = (text or "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
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


def package_json(root):
    try:
        return json.loads(read(os.path.join(root, "package.json")) or "")
    except ValueError:
        return None


def deps(pkg):
    out = {}
    for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        if isinstance((pkg or {}).get(key), dict):
            out.update(pkg[key])
    return out


def scripts(pkg):
    s = (pkg or {}).get("scripts")
    return s if isinstance(s, dict) else {}


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


def failing_names(text):
    return [l for l in (text or "").splitlines() if re.match(r"^\s*(×|✗|FAIL\b|❯.*failed)", l)]


# --------------------------------------------------------------------------- lab-report.md parsing

PLACEHOLDER = re.compile(r"\(paste here\)|\(write here[^)]*\)|\(the refactor prompt[^)]*\)|^<.*>$|yes / no|GO / CONDITIONAL / NO-GO|"
                         r"^\s*R\?\s*$|\(0, 1, 2 or 3", re.I)


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


def clean_cell(cell):
    return re.sub(r"<!--.*?-->", "", cell or "").strip().strip("*`").strip()


def useful(cell):
    cell = clean_cell(cell)
    return bool(cell) and not PLACEHOLDER.search(cell)


def blocks(body):
    return re.findall(r"```[^\n]*\n(.*?)```", body or "", re.S)


def strip_comments(body):
    return re.sub(r"<!--.*?-->", " ", body or "", flags=re.S)


def word_count(body):
    body = strip_comments(body)
    body = re.sub(r"```.*?```", " ", body, flags=re.S)
    body = "\n".join(l for l in body.splitlines() if not l.lstrip().startswith((">", "|", "#")))
    return len(re.findall(r"[^\W_]+(?:['’-][^\W_]+)*", body))


def after_marker(body, marker="Write below this line"):
    return body.split(marker, 1)[1] if marker in (body or "") else (body or "")


def as_int(cell):
    m = re.match(r"^\s*(\d+)\s*$", clean_cell(cell))
    return int(m.group(1)) if m else None


def category_of(cell):
    low = clean_cell(cell).lower()
    for key, name in CATEGORIES:
        if key in low:
            return name
    return None


def risk_ids(text):
    return re.findall(r"\bR(\d{1,2})\b", text or "")


def is_diff(text):
    return bool(re.search(r"(?m)^\s*-(?!--)\s*\S", text or "") and re.search(r"(?m)^\s*\+(?!\+\+)\s*\S", text or ""))


def contains_prompt(sent, prompt):
    have = norm(sent)
    return [s for s in prompt if norm(s) not in have]


# --------------------------------------------------------------------------- B, S: the project


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


def check_project(res, measured):
    root = project_root(APP)
    measured["app_root"] = rel(root)
    module = find_module(root) if root else None
    measured["module"] = rel(module)
    src = strip_js_comments(read(module) or "") if module else ""
    if not root:
        res.add("B1", "ERROR", "no package.json in app/ - bring your Week 08 app/ over (README Part 0)")
    elif not module:
        res.add("B1", "ERROR", "no booking.ts / booking.js in the project")
    elif not re.search(r"\bfunction\s+canBook\b|\bcanBook\s*=", src):
        res.add("B1", "FAIL", "%s does not define canBook" % rel(module))
    else:
        res.add("B1", "PASS", "%s, canBook" % rel(module))

    problems = []
    if os.path.isdir(APP):
        size = 0
        for here, dirs, names in os.walk(APP):
            if "node_modules" in dirs:
                problems.append("%s contains node_modules/ - delete it" % rel(here))
                dirs.remove("node_modules")
            for n in names:
                if n == ".env" or (n.startswith(".env.") and n != ".env.example"):
                    problems.append("%s/%s must not be committed" % (rel(here), n))
                try:
                    size += os.path.getsize(os.path.join(here, n))
                except OSError:
                    pass
        if size > MAX_EXPORT_MB * 1024 * 1024:
            problems.append("app/ is %.1f MB - commit source files only" % (size / 1048576.0))
    if not root:
        res.add("B2", "ERROR", "nothing to check until app/ holds the project")
    else:
        res.add("B2", "FAIL" if problems else "PASS", "; ".join(problems) if problems else "clean")
    return root, module


def check_suite(res, measured, root, module, mitigated):
    suite = find_suite(module)
    measured["suite"] = rel(suite)
    src = read(suite) if suite else None
    tests = tests_in(src) if src else []
    measured["tests_in_project"] = sum(len(tests_in(read(p) or "")) for p in walk_files(root) if is_test_file(p)) \
        if root else 0
    clean = strip_js_comments(src or "")
    if suite is None:
        res.add("S1", "ERROR", "no booking.test.ts / booking.test.js beside %s" % (rel(module) or "the booking module"))
        res.add("S2", "ERROR", "no suite to read")
        return
    bad = []
    if not re.search(r"from\s*['\"]vitest['\"]", clean):
        bad.append("import { test, expect } from 'vitest'")
    if not re.search(r"import\s*\{[^}]*\bcanBook\b[^}]*\}\s*from\s*['\"]\./booking(?:\.[cm]?[jt]sx?)?['\"]", clean):
        bad.append("import { canBook } from './booking'")
    if re.search(r"\b(?:vi|jest)\.(?:mock|doMock|spyOn)\s*\(", clean):
        bad.append("no mock or spy of the booking module")
    for m in sorted(set(m for _, m, _ in tests if m)):
        if re.search(r"\.(skip|only|todo|fails|skipIf|runIf)\b", m):
            bad.append("no test%s" % m)
    if re.search(r"\b(?:describe|suite)\.(?:skip|only|todo)\b|\bx(?:it|test|describe)\s*\(", clean):
        bad.append("no skipped or focused describe block")
    res.add("S1", "FAIL" if bad else "PASS",
            "the suite needs: " + "; ".join(bad) if bad else "%s: %d tests, real canBook" % (rel(suite), len(tests)))

    titled = {}
    for p in walk_files(root):
        if is_test_file(p):
            for title, _, _ in tests_in(read(p) or ""):
                for rid in risk_ids(title):
                    titled.setdefault("R" + rid, title)
    measured["risk_tests"] = sorted(titled)
    hit = [r for r in mitigated if r in titled]
    if not mitigated:
        res.add("S2", "FAIL", "no mitigated risk IDs in report 8.1-8.2 to look for")
    elif not hit:
        res.add("S2", "FAIL", "no test title names %s - add the regression test of Part 7, its title starting "
                              "with the risk ID" % " or ".join(mitigated))
    else:
        res.add("S2", "PASS", "%s: \"%s\"" % (hit[0], titled[hit[0]][:60]))


# --------------------------------------------------------------------------- A, C: the playbook


def agent_lines(text):
    return [l.strip() for l in (text or "").splitlines() if l.strip()]


def headings(text):
    return [norm(l) for l in agent_lines(text) if l.startswith("#")]


def changed_lines(a, b):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    n = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            n += max(i2 - i1, j2 - j1)
    return n, sm.ratio()


def permitted(lines, pattern, exclude=None):
    """Lines that mention `pattern` without forbidding it."""
    out = []
    for l in lines:
        probe = re.sub(exclude, " ", l, flags=re.I) if exclude else l
        if re.search(pattern, probe, re.I) and not NEG.search(probe):
            out.append(l)
    return out


def forbidden(lines, pattern):
    return [l for l in lines if re.search(pattern, l, re.I) and NEG.search(l)]


def check_agents(res, measured, root):
    path = os.path.join(root, "AGENTS.md") if root else os.path.join(APP, "AGENTS.md")
    text = read(path)
    if text is None:
        res.add("A1", "ERROR", "no app/AGENTS.md - copy provided/AGENTS.md into app/ (README Part 0, step 4)")
        for cid in ("A2", "A3", "C1", "C2", "C3", "C4", "C5", "C6"):
            res.add(cid, "ERROR", "no app/AGENTS.md to read")
        measured["agents_lines_changed"] = None
        return
    res.add("A1", "PASS", rel(path))
    lines = agent_lines(text)

    # A2
    n, ratio = changed_lines([norm(l) for l in agent_lines(PROVIDED_AGENTS)], [norm(l) for l in lines])
    measured["agents_lines_changed"] = n
    lost = [h for h in headings(PROVIDED_AGENTS) if h not in headings(text)]
    if n == 0:
        res.add("A2", "FAIL", "app/AGENTS.md is still exactly the provided file - apply the patch you approved (Part 6)")
    elif lost:
        res.add("A2", "FAIL", "a patch keeps the headings - missing: %s" % lost[0])
    elif n > MAX_AGENTS_CHANGED:
        res.add("A2", "FAIL", "%d lines changed - the prompt asks for a minimal patch, at most %d" % (n, MAX_AGENTS_CHANGED))
    else:
        res.add("A2", "PASS", "%d line(s) changed, headings kept" % n)

    # A3
    pkg = package_json(root) if root else None
    if pkg is None:
        res.add("A3", "ERROR", "no readable app/package.json to compare the commands with")
    else:
        have_scripts, have_deps = scripts(pkg), deps(pkg)
        bad = []
        for l in lines:
            if NEG.search(l):
                continue
            for m in re.finditer(r"\bnpm\s+run\s+([\w:.-]+)", l):
                if m.group(1) not in have_scripts:
                    bad.append("npm run %s (no such script)" % m.group(1))
            for m in re.finditer(r"\bnpm\s+(test|t|start)\b(?!:)", l):
                key = "test" if m.group(1) in ("test", "t") else "start"
                if key not in have_scripts:
                    bad.append("npm %s (no %s script)" % (m.group(1), key))
            for m in re.finditer(r"\bnpx\s+([\w@./-]+)", l):
                tool = {"tsc": "typescript"}.get(m.group(1), m.group(1))
                if tool not in have_deps:
                    bad.append("npx %s (%s is not in package.json)" % (m.group(1), tool))
        bad = sorted(set(bad))
        res.add("A3", "FAIL" if bad else "PASS",
                "AGENTS.md names commands that do not exist: " + "; ".join(bad) if bad
                else "every command it names exists")

    # C1 one fictional room, no real data
    real = permitted(lines, r"\breal\s+(?:room|timetable|name|student|data|schedule)|\bKBTU portal\b")
    fict = [l for l in lines if re.search(r"\bfictional|\bfake\b|\bmade[- ]up\b|\binvented\b", l, re.I)]
    one = [l for l in lines if re.search(r"\b(?:one|single|1)\s+(?:fictional\s+)?room\b", l, re.I)]
    probs = (["permits real data: \"%s\"" % real[0][:70]] if real else []) + \
            ([] if fict else ["no rule that the data is fictional"]) + ([] if one else ["no rule of one room"])
    res.add("C1", "FAIL" if probs else "PASS", "; ".join(probs) if probs else "one fictional room")

    # C2 no login, no database
    perm = permitted(lines, r"\blog\s?in\b|\bsign[- ]?in\b|\bauth(?:entication|orization|\b)|\bdatabase|\bsupabase|\bfirebase|\bsql\b|\bbackend\b")
    lg = forbidden(lines, r"\blog\s?in\b|\bsign[- ]?in\b|\bauth(?:entication|orization|\b)")
    db = forbidden(lines, r"\bdatabase|\bsupabase|\bfirebase|\bsql\b|\bbackend\b|\bpersist")
    probs = (["permits it: \"%s\"" % perm[0][:70]] if perm else []) + \
            ([] if lg else ["no rule forbidding a login"]) + ([] if db else ["no rule forbidding a database"])
    res.add("C2", "FAIL" if probs else "PASS", "; ".join(probs) if probs else "login and database forbidden")

    # C3 AC1-AC6, AC4 as the contract says
    acs = {}
    for l in lines:
        for m in re.finditer(r"\bAC\s?-?([1-6])\b(?!\s*[-–]\s*AC)", l):
            acs.setdefault(m.group(1), []).append(l)
    missing = [("AC" + k) for k in "123456" if k not in acs]
    ac4 = " ".join(acs.get("4", []))
    probs = []
    if missing:
        probs.append("not listed: " + ", ".join(missing))
    if ac4 and (re.search(r"also counts as an? overlap", ac4, re.I)
                or not re.search(r"\ballow|\bavailable|\bpermitted|\bonly touch|\bnot\b[^.]*\boverlap|"
                                 r"\bno(?:t)? (?:a )?conflict", ac4, re.I)):
        probs.append("AC4 must say that touching at an endpoint is allowed (the contract), not an overlap")
    res.add("C3", "FAIL" if probs else "PASS", "; ".join(probs) if probs else "AC1-AC6 listed, AC4 allows touching")

    # C4 no secrets
    secret = r"\bsecret|\bapi[ _-]?keys?\b|\bpasswords?\b|\btokens?\b|\bcredentials?\b|\.env\b"
    perm = permitted(lines, secret, exclude=r"\.env\.example")
    rule = forbidden(lines, secret)
    probs = (["permits it: \"%s\"" % perm[0][:70]] if perm else []) + ([] if rule else ["no rule forbidding secrets"])
    res.add("C4", "FAIL" if probs else "PASS", "; ".join(probs) if probs else "secrets forbidden")

    # C5 no external deployments
    dep = r"\bdeploy|\bnetlify\b|\bvercel\b|\bpublish|\bgithub pages\b|\bproduction\b|--prod\b"
    perm = permitted(lines, dep)
    rule = forbidden(lines, r"\bdeploy|\bpublish|\bproduction\b")
    probs = (["permits it: \"%s\"" % perm[0][:70]] if perm else []) + ([] if rule else ["no rule forbidding deployment"])
    res.add("C5", "FAIL" if probs else "PASS", "; ".join(probs) if probs else "deployment forbidden")

    # C6 tests before acceptance
    gate = [l for l in lines if re.search(r"\btest", l, re.I)
            and re.search(r"\bbefore\b|\bmust pass\b|\ball (?:the )?tests pass|\bgreen\b|\buntil\b", l, re.I)
            and not re.search(r"\bnever run\b|\bdo not run\b|\bdon't run\b", l, re.I)]
    res.add("C6", "PASS" if gate else "FAIL",
            "\"%s\"" % gate[0][:70] if gate else "no rule that the tests must run (and pass) before a change is "
                                                  "proposed as done")


# --------------------------------------------------------------------------- R, L: the report


def check_setup(res, sec):
    setup = {r[0].lower(): r[1] for r in table_rows(sec.get("1", "")) if len(r) > 1}
    need = {"assistant i": "the assistant", "exact model": "the exact model", "read the project": "where it read the project",
            "starting point": "the starting point", "baseline commit": "the baseline commit",
            "ran the tests": "where you ran the tests", "vitest version": "the Vitest version"}
    lacking = [say for key, say in need.items() if not any(key in k and useful(v) for k, v in setup.items())]
    start = next((clean_cell(v) for k, v in setup.items() if "starting point" in k), "")
    commit = next((clean_cell(v) for k, v in setup.items() if "baseline commit" in k), "")
    if start and useful(start) and not re.search(r"\bweek-0[78]\b", start):
        lacking.append("a starting point of week-08 or week-07")
    if commit and useful(commit) and not re.search(r"\b[0-9a-f]{7,40}\b", commit):
        lacking.append("the baseline commit as a hash")
    res.add("L1", "FAIL" if lacking else "PASS",
            "section 1 needs: " + ", ".join(lacking) if lacking else "setup recorded")


def check_baseline(res, measured, sec):
    rows = table_rows(sec.get("2.1", ""))
    done, probs = 0, []
    for cmd in COMMANDS:
        row = next((r for r in rows if r and norm(clean_cell(r[0])).startswith(cmd)), None)
        if row is None or len(row) < 3:
            probs.append(cmd)
            continue
        ex, result = clean_cell(row[1]).lower(), clean_cell(row[2]).lower()
        if ex in ("yes", "no") and result in ("pass", "fail", "missing", "not run"):
            done += 1
        else:
            probs.append(cmd)
    probs = ["2.1: exists (yes/no) and result (pass/fail/missing/not run) for " + ", ".join(probs)] if probs else []
    s23 = sec.get("2.3", "")
    b = blocks(s23)
    lost = contains_prompt(b[0] if b else "", READ_PROMPT)
    if lost:
        probs.append("2.3: the read-AGENTS.md prompt exactly as sent (missing: \"%s\")" % lost[0][:50])
    if len(b) < 2 or len(norm(b[1]).split()) < 20 or PLACEHOLDER.search(b[1]):
        probs.append("2.3: the assistant's answer (20+ words)")
    if word_count(after_marker(s23)) < 8:
        probs.append("2.3: which rules in its summary are wrong (8+ words)")
    res.add("L2", "FAIL" if probs else "PASS", "section " + "; ".join(probs) if probs
            else "five commands recorded; the agent's summary of AGENTS.md judged")

    s22 = vitest_summaries(" ".join(blocks(sec.get("2.2", ""))))
    measured["baseline_run"] = s22[-1] if s22 else None
    if not s22:
        res.add("R1", "FAIL", "section 2.2 has no Vitest output - run npx vitest run before any change")
    else:
        f = s22[-1]
        res.add("R1", "PASS", "%(passed)d passed, %(failed)d failed (%(total)d)" % f)


def check_review(res, measured, sec):
    s31 = sec.get("3.1", "")
    b = blocks(s31)
    where = word_count(after_marker(s31).split("What you sent")[0])
    probs = []
    if where < 5:
        probs.append("where it ran and how it could not edit (5+ words, found %d)" % where)
    lost = contains_prompt(b[0] if b else "", REVIEW_PROMPT)
    if lost:
        probs.append("the deck's prompt exactly as sent (missing: \"%s\")" % lost[0][:60])
    if len(b) < 2 or len(norm(b[1]).split()) < 50 or PLACEHOLDER.search(b[1]):
        probs.append("the assistant's answer (50+ words)")
    res.add("L3", "FAIL" if probs else "PASS", "section 3.1 needs " + "; ".join(probs) if probs
            else "prompt as sent, read-only, answer")

    good, cats = 0, set()
    for r in table_rows(sec.get("3.2", "")):
        if len(r) < 6 or not re.match(r"^\d+$", clean_cell(r[0])):
            continue
        label = LABELS.get(clean_cell(r[4]).lower())
        cat = category_of(r[2])
        if useful(r[1]) and cat and useful(r[3]) and label and useful(r[5]):
            good += 1
            cats.add(cat)
    measured["claims_challenged"] = good
    probs = []
    if good < MIN_CLAIMS:
        probs.append("%d complete rows, %d needed (claim, category, what you inspected, label, why)" % (good, MIN_CLAIMS))
    if len(cats) < MIN_CATEGORIES:
        probs.append("%d categories, %d needed" % (len(cats), MIN_CATEGORIES))
    res.add("L4", "FAIL" if probs else "PASS", "section 3.2: " + "; ".join(probs) if probs
            else "%d claims, %d categories" % (good, len(cats)))


def component_real(cell, root):
    c = clean_cell(cell)
    if re.match(r"^missing\b", c, re.I):
        return len(c.split()) >= 2
    if not root:
        return False
    names = set(os.path.relpath(p, root).replace(os.sep, "/") for p in walk_files(root))
    bases = set(os.path.basename(n) for n in names)
    for tok in re.findall(r"[\w./-]+\.(?:tsx?|jsx?|mjs|cjs|json|md|css|html|ya?ml)\b", c):
        tok = tok.lstrip("./")
        if tok.startswith("app/"):
            tok = tok[4:]
        if tok in names or os.path.basename(tok) in bases:
            return True
    return False


def check_register(res, measured, sec, root):
    register, probs, cats = {}, [], set()
    for r in table_rows(sec.get("4.1", "")):
        if not r or not re.match(r"^R\d{1,2}$", clean_cell(r[0])):
            continue
        rid = clean_cell(r[0])
        if len(r) < 12 or not any(useful(c) for c in r[1:]):
            continue
        cells = r[:12]
        miss = [n for n, c in zip(("category", "cause", "component", "evidence", "status", "L", "I", "score",
                                   "mitigation", "owner", "verification"), cells[1:]) if not useful(c)]
        status = LABELS.get(clean_cell(cells[5]).lower())
        lv, iv, sc = as_int(cells[6]), as_int(cells[7]), as_int(cells[8])
        cat = category_of(cells[1])
        register[rid] = {"status": status, "L": lv, "I": iv, "score": sc}
        if miss:
            probs.append("%s: empty %s" % (rid, ", ".join(miss)))
            continue
        if cat:
            cats.add(cat)
        else:
            probs.append("%s: category must be one of the prompt's six" % rid)
        if status not in ("confirmed", "plausible"):
            probs.append("%s: status must be confirmed or plausible (unsupported claims stay in 3.2)" % rid)
        if lv not in (1, 2, 3) or iv not in (1, 2, 3):
            probs.append("%s: L and I are 1-3" % rid)
        elif sc != lv * iv:
            probs.append("%s: score %s is not %d x %d" % (rid, clean_cell(cells[8]), lv, iv))
        if not component_real(cells[3], root):
            probs.append("%s: component \"%s\" is not a file in app/ nor 'missing: <check>'" % (rid, clean_cell(cells[3])[:40]))
    confirmed = [k for k, v in register.items() if v["status"] == "confirmed"]
    measured["risks_registered"] = len(register)
    measured["risks_confirmed"] = len(confirmed)
    measured["register"] = register
    if len(register) < MIN_RISKS:
        probs.insert(0, "%d risks, %d needed" % (len(register), MIN_RISKS))
    if len(confirmed) < MIN_CONFIRMED:
        probs.append("%d confirmed, %d needed" % (len(confirmed), MIN_CONFIRMED))
    if len(cats) < MIN_CATEGORIES:
        probs.append("%d categories, %d needed" % (len(cats), MIN_CATEGORIES))
    res.add("L5", "FAIL" if probs else "PASS", "section 4.1: " + "; ".join(probs[:3]) + (" (+%d more)" % (len(probs) - 3)
            if len(probs) > 3 else "") if probs else "%d risks, %d confirmed, %d categories" % (len(register), len(confirmed), len(cats)))

    # L6
    lines = [l for l in strip_comments(sec.get("4.2", "")).splitlines() if re.match(r"^\s*[12]\.", l)]
    top, probs = [], []
    for l in lines:
        ids = risk_ids(l)
        if ids:
            top.append(("R" + ids[0], len(re.findall(r"[^\W_]+", re.sub(r"\*\*R\d+\*\*|R\d+", " ", l))) - 1))
    measured["top_two"] = [t for t, _ in top[:2]]
    if len(top) < 2:
        res.add("L6", "FAIL", "section 4.2 needs two risk IDs, one per line")
        return register
    (a, wa), (b, wb) = top[:2]
    for rid in (a, b):
        if rid not in register:
            probs.append("%s is not in the register" % rid)
        elif register[rid]["status"] != "confirmed":
            probs.append("%s is not confirmed" % rid)
    if a == b:
        probs.append("two different risks")
    if min(wa, wb) < 6:
        probs.append("the evidence that justifies each score (6+ words each)")
    if not probs:
        sa, sb = register[a]["score"] or 0, register[b]["score"] or 0
        if sa < sb:
            probs.append("highest score first: %s scores %d, %s %d" % (a, sa, b, sb))
        higher = [k for k in confirmed if k not in (a, b) and (register[k]["score"] or 0) > min(sa, sb)]
        if higher:
            probs.append("%s is confirmed and scores higher than your second" % higher[0])
    res.add("L6", "FAIL" if probs else "PASS", "section 4.2: " + "; ".join(probs) if probs else "%s, %s" % (a, b))
    return register


def audit_facts(root):
    """What the files in app/ show for the rows the checker can see."""
    pkg = package_json(root) or {}
    blob = json.dumps(pkg)
    files = set(os.path.basename(p) for p in walk_files(root))
    top = set(os.listdir(root))
    tests = any(is_test_file(p) for p in walk_files(root))
    return {
        "1a": bool([f for f in files if f.startswith(".prettierrc") or f.startswith("prettier.config")]) or "prettier" in blob,
        "1b": bool([f for f in files if f.startswith(".eslintrc") or f.startswith("eslint.config")]) or "eslint" in blob,
        "1c": "tsconfig.json" in top and "typescript" in deps(pkg),
        "1d": tests and "vitest" in deps(pkg),
        "1e": bool(top & {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb", "bun.lock"}),
        "2a": ".env.example" in top,
        "2c": "AGENTS.md" in top,
        "3b": ".husky" in top or ".pre-commit-config.yaml" in top or
              any(k in blob for k in ("lint-staged", "simple-git-hooks", "\"husky\"")),
    }


def check_audit(res, measured, sec, root):
    rows = {clean_cell(r[0]).lower(): r for r in table_rows(sec.get("5.1", "")) if r}
    answers, probs = {}, []
    for rid in AUDIT_ROWS:
        r = rows.get(rid)
        ans = clean_cell(r[2]).lower() if r and len(r) >= 4 else ""
        if ans not in ("yes", "no") or not useful(r[3]):
            probs.append(rid)
        else:
            answers[rid] = ans == "yes"
    measured["audit_answers"] = {k: ("yes" if v else "no") for k, v in answers.items()}
    if probs:
        res.add("L7", "FAIL", "section 5.1: yes / no and the evidence for rows " + ", ".join(probs))
    elif not root:
        res.add("L7", "ERROR", "no project in app/ to compare the rows with")
    else:
        facts = audit_facts(root)
        measured["audit_files"] = {k: ("yes" if v else "no") for k, v in facts.items()}
        wrong = ["%s says %s, app/ shows %s" % (k, "yes" if answers[k] else "no", "yes" if v else "no")
                 for k, v in facts.items() if answers.get(k) != v]
        res.add("L7", "FAIL" if wrong else "PASS",
                "rows that disagree with your files: " + "; ".join(wrong) if wrong else "twelve rows, consistent with app/")

    # L8
    body = strip_comments(sec.get("5.2", ""))
    m = re.search(r"Level:\**\s*\**\s*([0-3])\b", body)
    computed = 0
    if len(answers) == len(AUDIT_ROWS):
        for lvl in (1, 2, 3):
            rows_l = LEVEL_ROWS[lvl]
            if sum(answers[r] for r in rows_l) / float(len(rows_l)) >= 0.8:
                computed = lvl
            else:
                break
    measured["level_computed"] = computed if len(answers) == len(AUDIT_ROWS) else None
    gaps = word_count(body.split("Missing evidence", 1)[1]) if "Missing evidence" in body else 0
    probs = []
    if not m:
        probs.append("the level as one digit after **Level:**")
    elif len(answers) == len(AUDIT_ROWS) and int(m.group(1)) != computed:
        probs.append("your rows give Level %d by the 80%% rule, not %s" % (computed, m.group(1)))
    if gaps < 10 and not (m and m.group(1) == "3"):
        probs.append("the missing evidence for the next level (10+ words, found %d)" % gaps)
    measured["level_declared"] = int(m.group(1)) if m else None
    res.add("L8", "FAIL" if probs else "PASS", "section 5.2 needs " + "; ".join(probs) if probs
            else "Level %d, gaps named" % computed)


def check_playbook(res, sec):
    b = blocks(sec.get("6.1", ""))
    probs = []
    lost = contains_prompt(b[0] if b else "", PLAYBOOK_PROMPT)
    if lost:
        probs.append("the deck's prompt exactly as sent (missing: \"%s\")" % lost[0][:60])
    if len(b) < 2 or len(norm(b[1]).split()) < 30 or PLACEHOLDER.search(b[1]):
        probs.append("the assistant's answer (30+ words)")
    decided = [r for r in table_rows(sec.get("6.2", "")) if len(r) >= 5 and re.match(r"^\d+$", clean_cell(r[0]))
               and useful(r[1]) and useful(r[2]) and clean_cell(r[3]).lower() in DECISIONS and useful(r[4])]
    if len(decided) < 4:
        probs.append("four or more findings in 6.2 with approve / reject / modify and why (found %d)" % len(decided))
    diff = " \n".join(blocks(sec.get("6.3", "")))
    if not is_diff(diff):
        probs.append("the diff of app/AGENTS.md in 6.3")
    res.add("L9", "FAIL" if probs else "PASS", "section 6 needs " + "; ".join(probs) if probs
            else "prompt, answer, %d decisions, diff" % len(decided))


def check_verify(res, measured, sec, mitigated):
    s71 = sec.get("7.1", "")
    covers = risk_ids(strip_comments(s71).split("```")[0])
    rid = "R" + covers[0] if covers else None
    run = " ".join(blocks(s71))
    fails = " ".join(failing_names(run))
    summ = vitest_summaries(run)
    if not rid:
        res.add("R2", "FAIL", "section 7.1: name the risk the test covers (The risk it covers: **R3**)")
    elif not summ or not summ[-1]["failed"]:
        res.add("R2", "FAIL", "section 7.1 needs a real run in which the new test fails")
    elif not re.search(r"\b%s\b" % rid, fails):
        res.add("R2", "FAIL", "section 7.1: no failing line names %s - the regression test must fail before the "
                              "mitigation" % rid)
    elif mitigated and rid not in mitigated:
        res.add("R2", "FAIL", "%s is not one of the two risks you mitigated in section 8" % rid)
    else:
        res.add("R2", "PASS", "%s fails before the mitigation" % rid)

    rows = {clean_cell(r[0]).lower(): r for r in table_rows(sec.get("7.2", "")) if r}
    probs = []
    for view in ("desktop", "mobile"):
        r = rows.get(view)
        if not r or len(r) < 4 or not all(useful(c) for c in r[1:4]):
            probs.append("the %s row (width, what you checked, result)" % view)
    if word_count(sec.get("7.3", "")) < 1:
        probs.append("7.3: the tests you did not run, or none")
    res.add("L10", "FAIL" if probs else "PASS", "section 7 needs " + "; ".join(probs) if probs
            else "two widths checked, tests not run listed")


def mitigated_ids(sec):
    out = []
    for key in ("8.1", "8.2"):
        m = re.search(r"Risk:\**\s*\**\s*R(\d{1,2})\b", strip_comments(sec.get(key, "")))
        out.append("R" + m.group(1) if m else None)
    return out


def check_mitigations(res, measured, sec, register):
    ids = mitigated_ids(sec)
    probs = []
    for key, rid in zip(("8.1", "8.2"), ids):
        body = strip_comments(sec.get(key, ""))
        if not rid:
            probs.append("%s: the risk ID (**Risk:** R3)" % key)
            continue
        if rid not in register:
            probs.append("%s: %s is not in the register" % (key, rid))
        elif register[rid]["status"] != "confirmed":
            probs.append("%s: %s is not confirmed" % (key, rid))
        rejected = body.split("and why:", 1)[1].split("The diff", 1)[0] if "and why:" in body else ""
        if word_count(rejected) < 3:
            probs.append("%s: what you rejected from the agent's patch (or 'nothing', with why)" % key)
        if not is_diff(" \n".join(blocks(body))):
            probs.append("%s: the diff you approved" % key)
    if ids[0] and ids[0] == ids[1]:
        probs.append("two different risks")
    refactor = [key for key in ("8.1", "8.2") if not contains_prompt(" ".join(blocks(sec.get(key, ""))), REFACTOR_PROMPT)]
    test_risk = risk_ids(strip_comments(sec.get("7.1", "")).split("```")[0])
    if not refactor:
        probs.append("the refactor prompt (README Part 8) as sent, in 8.1 or 8.2")
    else:
        key = refactor[0]
        body = strip_comments(sec.get(key, ""))
        why = body.split("pattern → benefit:", 1)[1].split("What I rejected", 1)[0] if "pattern → benefit:" in body else ""
        if word_count(why) < 15:
            probs.append("%s: the problem → pattern → benefit line (15+ words)" % key)
        rid = ids[0 if key == "8.1" else 1]
        if test_risk and rid and rid != "R" + test_risk[0]:
            probs.append("%s: the refactor mitigates %s, but the regression test of 7.1 covers R%s" % (key, rid, test_risk[0]))
    measured["refactor_section"] = refactor[0] if refactor else None
    after = {}
    for r in table_rows(sec.get("8.3", "")):
        if len(r) < 8 or not re.match(r"^R\d{1,2}$", clean_cell(r[0])):
            continue
        rid = clean_cell(r[0])
        nums = [as_int(c) for c in r[1:7]]
        if None in nums or not useful(r[7]):
            probs.append("8.3: %s needs six numbers and the evidence" % rid)
            continue
        lb, ib, sb, la, ia, sa = nums
        reg = register.get(rid)
        if reg and (lb, ib, sb) != (reg["L"], reg["I"], reg["score"]):
            probs.append("8.3: %s before (%d x %d = %d) differs from the register" % (rid, lb, ib, sb))
        if la not in (1, 2, 3) or ia not in (1, 2, 3) or sa != la * ia:
            probs.append("8.3: %s after must be L x I with L and I 1-3" % rid)
        elif sa > sb:
            probs.append("8.3: %s scores higher after the mitigation" % rid)
        after[rid] = sa
    for rid in ids:
        if rid and rid not in after and not any(p.startswith("8.3: %s" % rid) for p in probs):
            probs.append("8.3: a residual row for %s" % rid)
    measured["mitigated"] = [i for i in ids if i]
    measured["residual"] = after
    res.add("L11", "FAIL" if probs else "PASS", "section 8 needs " + "; ".join(probs[:3]) +
            (" (+%d more)" % (len(probs) - 3) if len(probs) > 3 else "") if probs
            else "%s and %s mitigated, residual revised" % tuple(ids))
    return after

def check_final(res, measured, sec):
    s84 = vitest_summaries(" ".join(blocks(sec.get("8.4", ""))))
    if not s84:
        res.add("R3", "FAIL", "section 8.4 has no Vitest output of the final suite")
        return
    f = s84[-1]
    measured["final_run"] = f
    probs = []
    if f["failed"]:
        probs.append("%d failed" % f["failed"])
    have = measured.get("tests_in_project")
    if have and f["total"] != have:
        probs.append("the output reports %d tests, the test files in app/ hold %d - paste the run of the "
                     "suite you committed" % (f["total"], have))
    res.add("R3", "FAIL" if probs else "PASS", "; ".join(probs) if probs else "%(passed)d passed (%(total)d)" % f)


def check_background(res, sec):
    rows = {clean_cell(r[0]).lower(): r for r in table_rows(sec.get("9.1", "")) if r}
    thin = []
    for name in AGENT_RULES:
        r = rows.get(name.lower())
        if not r or len(r) < 2 or not useful(r[1]) or len(re.findall(r"[^\W_]+", clean_cell(r[1]))) < 6:
            thin.append(name)
    res.add("L12", "FAIL" if thin else "PASS", "section 9.1: 6+ words for " + ", ".join(thin) if thin
            else "six rules")


def check_decision(res, measured, sec, register, after):
    body = sec.get("10", "")
    m = re.search(r"Decision:\**\s*\**\s*([A-Za-z -]+?)\s*(?:\*\*|$)", strip_comments(body), re.M)
    word = RELEASE.get(m.group(1).strip().lower()) if m else None
    measured["release"] = word
    current = {k: after.get(k, v["score"] or 0) for k, v in register.items() if v["status"] == "confirmed"}
    high = sorted(k for k, s in current.items() if s >= 6)
    text = after_marker(body, "Write your conclusion below this line")
    words = word_count(text)
    measured["conclusion_words"] = words
    named = sorted(set("R" + i for i in risk_ids(strip_comments(text))) & set(register))
    probs = []
    if not word:
        probs.append("one decision after **Decision:** - GO, CONDITIONAL or NO-GO")
    elif word == "go" and high:
        probs.append("GO is not allowed while %s still score%s 6 or more" % (", ".join(high), "" if len(high) > 1 else "s"))
    if not WORDS_MIN <= words <= WORDS_MAX:
        probs.append("%d words, the task asks for %d-%d" % (words, WORDS_MIN, WORDS_MAX))
    if len(named) < 2:
        probs.append("name two or more risk IDs from your register")
    res.add("L13", "FAIL" if probs else "PASS", "section 10: " + "; ".join(probs) if probs
            else "%s, %d words, %s" % (word.upper(), words, ", ".join(named[:4])))


# --------------------------------------------------------------------------- main


def run():
    res, measured = Results(), {}
    root, module = check_project(res, measured)
    text = read(REPORT)
    sec = sections(text) if text is not None else {}
    mitigated = [i for i in mitigated_ids(sec) if i] if sec else []
    check_suite(res, measured, root, module, mitigated)
    check_agents(res, measured, root)
    for cid, stem in (("E1", "ui-desktop"), ("E2", "ui-mobile")):
        p = find_image(stem)
        why = image_problem(p)
        res.add(cid, "PASS" if not why else ("FAIL" if p else "ERROR"),
                rel(p) if not why else (why if p else "evidence/%s.png not found - the manual UI check (Part 7)" % stem))
    if text is None:
        for cid in ORDER:
            if cid[0] in "RL":
                res.add(cid, "ERROR", "lab-report.md not found")
    else:
        check_setup(res, sec)
        check_baseline(res, measured, sec)
        check_review(res, measured, sec)
        register = check_register(res, measured, sec, root)
        check_audit(res, measured, sec, root)
        check_playbook(res, sec)
        check_verify(res, measured, sec, mitigated)
        after = check_mitigations(res, measured, sec, register)
        check_final(res, measured, sec)
        check_background(res, sec)
        check_decision(res, measured, sec, register, after)
    res.rows = sorted(res.rows, key=lambda r: ORDER.index(r["id"]))
    return res, measured


def print_human(res, measured):
    counts = res.counts()
    print("Week 10 - risk review: the project, the playbook, the evidence, the report\n")
    width = max(len(r["title"]) for r in res.rows)
    for r in res.rows:
        print(("%-6s %-4s %-*s  %s" % (r["verdict"], r["id"], width, r["title"], r["message"])).rstrip())
    print("-" * 78)
    print("SUMMARY pass=%d fail=%d error=%d   (%d checks)"
          % (counts["PASS"], counts["FAIL"], counts["ERROR"], len(res.rows)))
    if measured.get("agents_lines_changed") is not None:
        print("AGENTS.md lines changed (submission.yml counts.agents_lines_changed): %d" % measured["agents_lines_changed"])
    if counts["FAIL"] or counts["ERROR"]:
        print("Every FAIL or ERROR you keep goes in lab-report.md section 9.3 and in submission.yml known_fails.")
        print("One you report and explain costs you nothing extra. One you hide costs the whole criterion.")
    else:
        print("Files and shape are clean. Whether your risks are the right ones is the grader's reading, not this.")


def main():
    parser = argparse.ArgumentParser(description="Week 10 checker - run from inside week-10/")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    if not os.path.isdir("tests") and not os.path.exists(REPORT) and not os.path.isdir(APP):
        message = "run this from inside your week-10/ folder:  cd week-10 && python tests/check_audit.py"
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
