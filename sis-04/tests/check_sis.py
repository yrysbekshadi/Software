#!/usr/bin/env python3
"""
check_sis.py - the SIS #04 checker. DO NOT EDIT: the grader runs its own copy over your files.

    python tests/check_sis.py          # from inside sis-04/
    python tests/check_sis.py --json   # machine-readable, for the grading pipeline

What it checks (33 checks):

    A1-A8    your project in app/: the room catalog, the filter, checkRoom, the UI kept apart from
             the rules, AC1-AC5 still in canBook, clean and in scope, a README with the commands
    S1-S7    your tests: real modules, nothing mocked or skipped, 10 or more, and the required IDs
             AC1-AC5, F1-F5, B1-B6 and INT in the test titles
    D1-D2    diagrams/before.puml and diagrams/after.puml
    E1-E3    the five screenshots in evidence/
    R1-R3    the runs you pasted: the baseline, the final run, and the quality table's test numbers
    L1-L10   report.md has its sections filled in

It never runs your tests, never runs your code and never talks to an assistant. It reads files.
The terminal output you paste is YOUR evidence; R2 checks that it is consistent with the tests you
committed. A clean run is the floor, not the grade.

Verdicts:
    PASS   the check found what it was looking for
    FAIL   the content is there but wrong, or not enough of it
    ERROR  it could not check: a file, a folder or a section is missing

Exit codes: 0 = no FAIL and no ERROR - 1 = at least one FAIL or ERROR - 3 = wrong directory.
Standard library only.
"""

import argparse
import hashlib
import json
import os
import re
import struct
import sys

APP = "app"
DIAGRAMS = "diagrams"
EVIDENCE = "evidence"
REPORT = "report.md"

MAX_EXPORT_MB = 5
MIN_IMAGE_BYTES = 3000
MIN_TESTS = 10
MIN_ROOMS = 4
WORDS_MIN, WORDS_MAX = 200, 300
STARTS = ("week-08", "week-07", "sis-03", "starter")
SHOTS = ("filter-match", "filter-empty", "switch-a", "switch-b", "narrow")

CODE_EXT = (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".mts", ".cts", ".vue", ".svelte", ".html")
SCRIPT_EXT = (".ts", ".js", ".tsx", ".jsx", ".mts", ".mjs")
IGNORED_DIRS = (".git", ".bolt", ".vscode", ".idea", "__pycache__", "node_modules", "dist", "coverage")
ROOM_KEYS = ("id", "name", "capacity", "equipment", "blocked", "bookings")

AC_IDS = ["AC%d" % n for n in range(1, 6)]
F_IDS = ["F%d" % n for n in range(1, 6)]
B_IDS = ["B%d" % n for n in range(1, 7)]
ALL_IDS = AC_IDS + F_IDS + B_IDS + ["INT"]
# README section 6: what each boundary test asserts, for the ones that check a single Boolean
B_EXPECT = {"B1": True, "B2": False, "B3": True, "B4": False}

SCOPE = [
    ("network call", r"\bfetch\s*\(|\baxios\b|XMLHttpRequest|new\s+WebSocket|\bEventSource\b"),
    ("browser storage", r"\blocalStorage\b|\bsessionStorage\b|\bindexedDB\b"),
    ("backend or database", r"supabase|firebase|@prisma|\bmongodb\b|\bmongoose\b|\bexpress\s*\("),
    ("login or account", r"\bsignIn\w*\s*\(|\bsign[ -]?in\b|\blog[ -]?in\b|\bpassword\b|\bauth0\b"),
    ("payment", r"\bstripe\b|\bpaypal\b|\bcheckout\s*\("),
]

QUALITY_ROWS = (("tests", "Automated tests passed / total"),
                ("duplicated", "Duplicated logic locations removed"),
                ("structure", "Code structure"),
                ("limitation", "Remaining limitation"))
EXCHANGE_FIELDS = ("Tool and model", "Date", "Purpose", "Problems found", "Changes made", "Verified by")

TITLES = {
    "A1": "project in app/: package.json, src/booking with canBook",
    "A2": "src/rooms: ROOMS with %d+ rooms, every field" % MIN_ROOMS,
    "A3": "src/filter: filterRooms reads capacity and equipment",
    "A4": "checkRoom in src/booking reuses canBook with the chosen room",
    "A5": "the UI imports the rules and holds no room data or rule of its own",
    "A6": "canBook still enforces AC1-AC5",
    "A7": "clean and in scope: no node_modules, .env, network, storage, login",
    "A8": "app/README.md: setup, run and test commands",
    "S1": "test files import vitest and the real modules",
    "S2": "nothing mocked, skipped, focused or table-driven",
    "S3": "%d tests or more" % MIN_TESTS,
    "S4": "regression tests AC1-AC5",
    "S5": "feature tests F1-F5 on filterRooms / checkRoom",
    "S6": "boundary tests B1-B6",
    "S7": "an INT integration or UI behaviour test",
    "D1": "diagrams/before.puml and after.puml are PlantUML",
    "D2": "after.puml names rooms, booking, filter and the UI, and differs",
    "E1": "evidence: filter-match and filter-empty",
    "E2": "evidence: switch-a and switch-b",
    "E3": "evidence: narrow (portrait), five distinct screenshots",
    "R1": "report 1.1: the baseline run",
    "R2": "report 6.3: the final run, all passing, same tests",
    "R3": "report 7: tests passed / total match the two runs",
    "L1": "report 1: assistant, model, starting point, baseline commit",
    "L2": "report 2: repository map and the context as sent",
    "L3": "report 3.1: three or more risks, each with a file or function",
    "L4": "report 3.2-3.3: a plan before editing, one suggestion rejected or modified",
    "L5": "report 4.2: what each screenshot shows",
    "L6": "report 5: responsibilities, two design decisions, duplication",
    "L7": "report 6.1-6.2: the test plan and the commands",
    "L8": "report 7: the quality table, with how each measure was obtained",
    "L9": "report 8: three or more AI exchanges, every field",
    "L10": "report 10: reflection of %d-%d words" % (WORDS_MIN, WORDS_MAX),
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
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r"[‐-―]", "-", text)
    return re.sub(r"\s+", " ", text).strip()


def strip_js_comments(src):
    src = re.sub(r"/\*.*?\*/", " ", src or "", flags=re.S)
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


def image_problem(path, stem):
    if path is None:
        return "evidence/%s.png not found" % stem
    if os.path.getsize(path) < MIN_IMAGE_BYTES:
        return "%s is too small to be a screenshot" % rel(path)
    if image_info(path) is None:
        return "%s is not a real PNG or JPEG" % rel(path)
    return None


def digest(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


# --------------------------------------------------------------------------- reading source


def definition(src, name):
    """The source of `function name(...) {...}` or `const name = (...) => {...}`, braces matched."""
    src = src or ""
    m = re.search(r"(?:export\s+)?(?:async\s+)?function\s+%s\b" % name, src)
    arrow = False
    if not m:
        m = re.search(r"(?:export\s+)?(?:const|let|var)\s+%s\s*(?::[^=]+)?=" % name, src)
        arrow = bool(m)
    if not m:
        return None
    j = m.end()
    if arrow:
        k = src.find("=>", j)
        if k < 0:
            return None
        j = k + 2
        rest = src[j:].lstrip()
        if not rest.startswith("{"):                       # expression body: up to the line's end
            end = src.find(";", j)
            return src[m.start():end if end > 0 else len(src)]
    else:
        depth = 0
        while j < len(src):
            if src[j] == "(":
                depth += 1
            elif src[j] == ")":
                depth -= 1
                if depth == 0:
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


def find_module(root, stem):
    hits = [p for p in walk_files(root)
            if os.path.splitext(os.path.basename(p))[0] == stem and p.endswith(SCRIPT_EXT) and not is_test_file(p)]
    hits.sort(key=lambda p: (0 if "/src/" in rel(p) + "/" else 1, len(p)))
    return hits[0] if hits else None


def array_objects(src, name):
    """The top-level {...} objects of the array literal assigned to `name`."""
    m = re.search(r"\b%s\b[^=]*=\s*\[" % name, src or "")
    if not m:
        return None
    i, depth, start, out = m.end(), 1, None, []
    while i < len(src) and depth:
        ch = src[i]
        if ch in "[{":
            if ch == "{" and depth == 1:
                start = i
            depth += 1
        elif ch in "]}":
            depth -= 1
            if ch == "}" and depth == 1 and start is not None:
                out.append(src[start:i + 1])
                start = None
        i += 1
    return out


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


def ids_in(title):
    return set(re.findall(r"(?<![\w-])(AC[1-5]|F[1-5]|B[1-6]|INT)(?![\w-])", title))


def booleans_asserted(block):
    vals = set()
    for m in re.finditer(r"(\.not)?\.(?:toBe|toEqual|toStrictEqual)\(\s*(true|false)\s*\)", block):
        if not m.group(1):
            vals.add(m.group(2) == "true")
    for m in re.finditer(r"(\.not)?\.toBe(Truthy|Falsy)\(\s*\)", block):
        if not m.group(1):
            vals.add(m.group(2) == "Truthy")
    return vals


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


# --------------------------------------------------------------------------- report.md parsing

PLACEHOLDER = re.compile(r"\(paste here\)|\(write here[^)]*\)|^<.*>$|yes / no|"
                         r"High / Medium / Low|Rejected / Modified", re.I)


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
    rows, lines = [], [l.strip() for l in strip_comments(body).splitlines()]
    for i, line in enumerate(lines):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(re.match(r"^:?-{2,}:?$", c) for c in cells if c) and any(cells):
            continue
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if nxt.startswith("|") and re.match(r"^\|[\s:|-]+\|?$", nxt):
            continue                                       # a header row
        rows.append(cells)
    return rows


def useful(cell):
    cell = re.sub(r"<!--.*?-->", "", cell or "").strip()
    return bool(cell) and not PLACEHOLDER.search(cell)


def blocks(body):
    return re.findall(r"(?:```|~~~~)[^\n]*\n(.*?)(?:```|~~~~)", body or "", re.S)


def real_blocks(body, min_lines=2):
    return [b for b in blocks(body)
            if len([l for l in b.splitlines() if l.strip()]) >= min_lines and not PLACEHOLDER.search(b)]


def strip_comments(body):
    return re.sub(r"<!--.*?-->", " ", body or "", flags=re.S)


def word_count(body):
    body = strip_comments(body)
    body = re.sub(r"(?:```|~~~~).*?(?:```|~~~~)", " ", body, flags=re.S)
    body = "\n".join(l for l in body.splitlines() if not l.lstrip().startswith((">", "|", "#")))
    return len(re.findall(r"[^\W_]+(?:['’-][^\W_]+)*", body))


def label_value(body, label):
    """The text after **Label:** on its line."""
    m = re.search(r"\*\*%s:?\*\*:?\s*(.*)" % re.escape(label), strip_comments(body or ""), re.I)
    return m.group(1).strip() if m else ""


def setup_table(body):
    return {r[0].lower(): r[1] for r in table_rows(body) if len(r) > 1}


def setup_value(setup, key):
    return next((v for k, v in setup.items() if key in k and useful(v)), "")


# --------------------------------------------------------------------------- A: the project


def scope_hits(root):
    hits = []
    for p in walk_files(root):
        low = p.lower()
        if not low.endswith(CODE_EXT) or is_test_file(p):
            continue
        for number, line in enumerate(strip_js_comments(read(p) or "").splitlines(), 1):
            for label, pattern in SCOPE:
                if re.search(pattern, line, re.I):
                    hits.append({"what": label, "where": "%s:%d" % (rel(p), number)})
    return hits


def check_project(res, measured):
    root = project_root(APP)
    measured["app_root"] = rel(root)
    sources = [p for p in walk_files(root) if p.lower().endswith(CODE_EXT)] if root else []
    mods = {stem: (find_module(root, stem) if root else None) for stem in ("booking", "rooms", "filter")}
    measured["modules"] = {k: rel(v) for k, v in mods.items()}
    code = {k: strip_js_comments(read(v) or "") if v else "" for k, v in mods.items()}
    can_book = definition(code["booking"], "canBook")
    check_room = definition(code["booking"], "checkRoom")
    filter_rooms = definition(code["filter"], "filterRooms")

    # A1
    if not root:
        res.add("A1", "ERROR", "no package.json in app/ - bring your project in (README section 3)")
    elif not mods["booking"]:
        res.add("A1", "ERROR", "no src/booking.ts (or .js) in the project - canBook lives there (README section 7)")
    elif not can_book:
        res.add("A1", "FAIL", "%s has no canBook function" % rel(mods["booking"]))
    else:
        res.add("A1", "PASS", "%s, canBook" % rel(mods["booking"]))

    # A2
    objs = array_objects(code["rooms"], "ROOMS") if mods["rooms"] else None
    if not root or not mods["rooms"]:
        res.add("A2", "ERROR", "no src/rooms.ts (or .js) - the catalog goes in its own module")
        measured["rooms"] = None
    elif objs is None:
        res.add("A2", "FAIL", "%s has no `ROOMS = [ ... ]` array" % rel(mods["rooms"]))
        measured["rooms"] = None
    else:
        complete = [o for o in objs if all(re.search(r"\b%s\s*:" % k, o) for k in ROOM_KEYS)]
        ids = [m.group(1) for o in complete for m in [re.search(r"\bid\s*:\s*['\"`]([^'\"`]+)", o)] if m]
        measured["rooms"] = len(objs)
        probs = []
        if len(complete) < len(objs):
            probs.append("%d of %d rooms lack one of: %s" % (len(objs) - len(complete), len(objs), ", ".join(ROOM_KEYS)))
        if len(objs) < MIN_ROOMS:
            probs.append("%d rooms - the brief asks for at least %d" % (len(objs), MIN_ROOMS))
        if len(set(ids)) < len(ids):
            probs.append("two rooms share an id")
        res.add("A2", "FAIL" if probs else "PASS", "; ".join(probs) if probs else "%d rooms, every field" % len(objs))

    # A3
    if not root or not mods["filter"]:
        res.add("A3", "ERROR", "no src/filter.ts (or .js) - the filtering logic goes in its own module")
    elif not filter_rooms:
        res.add("A3", "FAIL", "%s has no filterRooms function" % rel(mods["filter"]))
    else:
        lacks = [w for w in ("capacity", "equipment") if w not in filter_rooms]
        res.add("A3", "FAIL" if lacks else "PASS",
                "filterRooms never reads " + " or ".join(lacks) if lacks else "filterRooms reads capacity and equipment")

    # A4
    if not can_book:
        res.add("A4", "ERROR", "no canBook to build on")
    elif not check_room:
        res.add("A4", "FAIL", "%s has no checkRoom(rooms, roomId, { start, end, now })" % rel(mods["booking"]))
    else:
        probs = [w for w in ("canBook", "blocked", "bookings") if not re.search(r"\b%s\b" % w, check_room)]
        res.add("A4", "FAIL" if probs else "PASS",
                "checkRoom must call canBook with the chosen room's blocked and bookings (missing: %s)"
                % ", ".join(probs) if probs else "checkRoom reuses canBook")

    # A5
    rule_files = set(v for v in mods.values() if v)
    ui = [p for p in sources if p not in rule_files and not is_test_file(p) and p.endswith(SCRIPT_EXT)
          and not os.path.basename(p).startswith(("vite.config", "vitest.config", "setupTests"))]
    ui_src = {p: strip_js_comments(read(p) or "") for p in ui}
    together = "\n".join(ui_src.values())
    if not root:
        res.add("A5", "ERROR", "no project to read")
    else:
        probs = []
        if not re.search(r"\bfilterRooms\b", together):
            probs.append("no UI file uses filterRooms")
        if not re.search(r"\b(?:checkRoom|canBook)\b", together):
            probs.append("no UI file uses checkRoom or canBook")
        for p, src in ui_src.items():
            if re.search(r"\bcapacity\s*:\s*\d", src):
                probs.append("%s holds room data (capacity: ...) - it belongs in rooms" % rel(p))
            if re.search(r"(?:function|const|let)\s+(?:canBook|filterRooms|checkRoom)\b", src):
                probs.append("%s defines a rule function - it belongs in booking or filter" % rel(p))
            if re.search(r"<=?\s*\w+\.end\b|\.capacity\s*[<>]|>\s*120\b|\.equipment\.(?:every|some|includes)\b", src):
                probs.append("%s repeats a booking or filter rule" % rel(p))
        res.add("A5", "FAIL" if probs else "PASS",
                "; ".join(probs[:3]) if probs else "UI in %d file(s), rules imported" % len(ui))
    measured["ui_files"] = [rel(p) for p in ui]

    # A6
    if not can_book:
        res.add("A6", "ERROR", "no canBook to read")
    else:
        body = re.sub(r"\s+", " ", can_book)
        probs = []
        loose = re.search(r"\bstart\s*<=\s*\w+\.end\b|\bend\s*>=\s*\w+\.start\b|\b\w+\.end\s*>=\s*start\b|"
                          r"\b\w+\.start\s*<=\s*end\b", body)
        strict = re.search(r"\bstart\s*<\s*\w+\.end\b|\b\w+\.end\s*>\s*start\b|\bstart\s*>=\s*\w+\.end\b|"
                           r"\b\w+\.end\s*<=\s*start\b", body)
        if loose or not strict:
            probs.append("AC4: the overlap test is not strict (touching must be Available)")
        if not re.search(r">\s*120\b|<=\s*120\b|MAX\w*", body):
            probs.append("AC2: no 120-minute limit")
        if not re.search(r"\bblocked\b", body.split("{", 1)[-1]):
            probs.append("AC3: blocked is never read")
        if re.search(r"\bbookings\s*\.\s*(?:push|splice|sort|unshift|pop|shift|reverse|fill)\s*\(|"
                     r"\bbookings\s*(?:\[[^\]]*\])?\s*=(?!=)", body):
            probs.append("AC5: canBook changes the bookings")
        res.add("A6", "FAIL" if probs else "PASS", "; ".join(probs) if probs else "AC1-AC5 rules in place")

    # A7
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
    hits = scope_hits(root) if root else []
    measured["scope"] = hits
    for h in hits[:3]:
        problems.append("%s at %s" % (h["what"], h["where"]))
    if not root:
        res.add("A7", "ERROR", "nothing to check until app/ holds the project")
    else:
        res.add("A7", "FAIL" if problems else "PASS", "; ".join(problems) if problems else "clean, nothing out of scope")

    # A8
    readme = None
    if root:
        for name in sorted(os.listdir(root)):
            if name.lower() == "readme.md":
                readme = os.path.join(root, name)
    if not root:
        res.add("A8", "ERROR", "no project to read")
    elif not readme:
        res.add("A8", "ERROR", "no README.md in app/ - setup, run and test commands")
    else:
        text = read(readme) or ""
        lacks = []
        if not re.search(r"\b(?:npm|pnpm|yarn)\s+(?:install|ci|i)\b|\bbun\s+install\b", text):
            lacks.append("setup (npm install)")
        if not re.search(r"\bnpm\s+(?:run\s+)?(?:dev|start)\b|\bnpx\s+vite\b|\b(?:pnpm|yarn|bun)\s+(?:run\s+)?dev\b", text):
            lacks.append("run (npm run dev)")
        if not re.search(r"\bvitest\b|\bnpm\s+(?:run\s+)?test\b|\b(?:pnpm|yarn|bun)\s+(?:run\s+)?test\b", text):
            lacks.append("test (npx vitest run)")
        res.add("A8", "FAIL" if lacks else "PASS",
                "%s has no command for: %s" % (rel(readme), ", ".join(lacks)) if lacks else rel(readme))
    return root, sources


# --------------------------------------------------------------------------- S: the tests


def check_suite(res, measured, root, sources):
    files = [p for p in sources if is_test_file(p)]
    measured["test_files"] = [rel(p) for p in files]
    tests = []
    for p in files:
        tests.extend(tests_in(read(p) or ""))
    measured["tests_final"] = len(tests)
    measured["test_titles"] = [t for t, _, _ in tests]
    srcs = {p: strip_js_comments(read(p) or "") for p in files}

    def need(cid):
        if not files:
            res.add(cid, "ERROR", "no *.test.ts / *.test.js file in app/" if root else "no project in app/")
            return False
        return True

    if need("S1"):
        probs = []
        bare = [rel(p) for p, s in srcs.items() if not re.search(r"from\s*['\"]vitest['\"]", s)]
        if bare:
            probs.append("%s does not import from 'vitest'" % bare[0])
        together = "\n".join(srcs.values())
        for mod in ("booking", "filter"):
            if not re.search(r"from\s*['\"](?:\.{1,2}/)+(?:[\w/]*/)?%s(?:\.[cm]?[jt]sx?)?['\"]" % mod, together):
                probs.append("no test imports the real ./%s module" % mod)
        res.add("S1", "FAIL" if probs else "PASS", "; ".join(probs) if probs else "%d test file(s)" % len(files))

    if need("S2"):
        bad = []
        together = "\n".join(srcs.values())
        if re.search(r"\b(?:vi|jest)\.(?:mock|doMock|spyOn|fn)\s*\(", together):
            bad.append("a mock or spy - test the real rules")
        for m in sorted(set(m for _, m, _ in tests if m)):
            if re.search(r"\.(skip|only|todo|fails|skipIf|runIf)\b", m):
                bad.append("test%s" % m)
        if re.search(r"\b(?:test|it|describe)\.each\b", together):
            bad.append("test.each / it.each - one test per case, so each has its own ID")
        if re.search(r"\b(?:describe|suite)\.(?:skip|only|todo)\b|\bx(?:it|test|describe)\s*\(", together):
            bad.append("a skipped or focused describe block")
        res.add("S2", "FAIL" if bad else "PASS", "; ".join(bad) if bad else "every test runs")

    if need("S3"):
        res.add("S3", "PASS" if len(tests) >= MIN_TESTS else "FAIL",
                "%d tests" % len(tests) + ("" if len(tests) >= MIN_TESTS else " - the brief asks for at least %d" % MIN_TESTS))

    by_id = {}
    for title, _, block in tests:
        for i in ids_in(title):
            by_id.setdefault(i, []).append(block)
    measured["ids_found"] = sorted(by_id)

    def calls(block, *names):
        return any(re.search(r"\b%s\s*\(" % n, block) for n in names)

    if need("S4"):
        missing = [i for i in AC_IDS if i not in by_id]
        weak = [i for i in AC_IDS if i in by_id and not any(re.search(r"\bexpect\s*\(", b) for b in by_id[i])]
        probs = (["no test titled " + ", ".join(missing)] if missing else []) + \
                (["%s asserts nothing" % ", ".join(weak)] if weak else [])
        res.add("S4", "FAIL" if probs else "PASS", "; ".join(probs) if probs else "AC1-AC5 each have a test")

    if need("S5"):
        rule = {"F1": ("filterRooms",), "F2": ("filterRooms",), "F3": ("checkRoom", "render"),
                "F4": ("filterRooms", "render"), "F5": ("checkRoom", "render")}
        missing = [i for i in F_IDS if i not in by_id]
        wrong = [i for i in F_IDS if i in by_id and not any(calls(b, *rule[i]) for b in by_id[i])]
        probs = (["no test titled " + ", ".join(missing)] if missing else []) + \
                ["%s must call %s" % (i, " or ".join(rule[i])) for i in wrong]
        res.add("S5", "FAIL" if probs else "PASS", "; ".join(probs) if probs else "F1-F5 each have a test")

    if need("S6"):
        missing = [i for i in B_IDS if i not in by_id]
        probs = ["no test titled " + ", ".join(missing)] if missing else []
        for i, want in B_EXPECT.items():
            if i in by_id and not any(calls(b, "canBook", "checkRoom") and want in booleans_asserted(b) for b in by_id[i]):
                probs.append("%s must call canBook or checkRoom and expect %s" % (i, str(want).lower()))
        for i in ("B5", "B6"):
            if i in by_id and not any(calls(b, "filterRooms") for b in by_id[i]):
                probs.append("%s must call filterRooms" % i)
        res.add("S6", "FAIL" if probs else "PASS", "; ".join(probs) if probs else "B1-B6 each have a test")

    if need("S7"):
        blocks_int = by_id.get("INT", [])
        good = [b for b in blocks_int if (calls(b, "filterRooms") and calls(b, "checkRoom", "canBook")) or calls(b, "render")]
        res.add("S7", "PASS" if good else "FAIL",
                "integration test present" if good else
                ("the INT test must use filterRooms and checkRoom together, or render the page" if blocks_int
                 else "no test titled INT"))


# --------------------------------------------------------------------------- D, E: diagrams, screenshots


def puml(path):
    text = read(path)
    if text is None:
        return None, "missing"
    body = "\n".join(l for l in text.splitlines() if l.strip() and not l.strip().startswith("'"))
    if not re.search(r"@startuml", body) or not re.search(r"@enduml", body):
        return text, "no @startuml ... @enduml"
    inner = re.sub(r"@startuml.*|@enduml.*", "", body)
    if len([l for l in inner.splitlines() if l.strip()]) < 3:
        return text, "still the stub - draw the modules and their dependencies"
    return text, None


def check_diagrams(res, measured):
    before, why_b = puml(os.path.join(DIAGRAMS, "before.puml"))
    after, why_a = puml(os.path.join(DIAGRAMS, "after.puml"))
    if before is None or after is None:
        res.add("D1", "ERROR", "diagrams/%s not found" % ("before.puml" if before is None else "after.puml"))
    else:
        probs = ["before.puml: " + why_b] if why_b else []
        probs += ["after.puml: " + why_a] if why_a else []
        res.add("D1", "FAIL" if probs else "PASS", "; ".join(probs) if probs else "two PlantUML diagrams")
    if after is None or why_a:
        res.add("D2", "ERROR", "no after.puml to read")
        return
    low = after.lower()
    lacks = [w for w in ("rooms", "booking", "filter") if w not in low]
    if not re.search(r"\bapp\b|\bui\b|component|\.tsx\b|\.jsx\b", low):
        lacks.append("the UI (App or a component)")
    same = before is not None and norm(before) == norm(after)
    probs = (["after.puml does not name: " + ", ".join(lacks)] if lacks else []) + \
            (["after.puml is identical to before.puml"] if same else [])
    res.add("D2", "FAIL" if probs else "PASS", "; ".join(probs) if probs else "the four parts are named")


def check_evidence(res, measured):
    found = {s: find_image(s) for s in SHOTS}
    why = {s: image_problem(found[s], s) for s in SHOTS}

    def pair(cid, names):
        bad = [why[n] for n in names if why[n]]
        if bad:
            res.add(cid, "ERROR" if all(found[n] is None for n in names) else "FAIL", "; ".join(bad))
        elif digest(found[names[0]]) == digest(found[names[1]]):
            res.add(cid, "FAIL", "%s and %s are the same file" % names)
        else:
            res.add(cid, "PASS", ", ".join(rel(found[n]) for n in names))

    pair("E1", ("filter-match", "filter-empty"))
    pair("E2", ("switch-a", "switch-b"))
    if why["narrow"]:
        res.add("E3", "ERROR" if found["narrow"] is None else "FAIL", why["narrow"])
    else:
        w, h = image_info(found["narrow"])
        good = [found[s] for s in SHOTS if not why[s]]
        dup = len(set(digest(p) for p in good)) < len(good)
        probs = (["narrow is %dx%d - take it at phone width in portrait" % (w, h)] if h <= w else []) + \
                (["two screenshots are the same file"] if dup else [])
        res.add("E3", "FAIL" if probs else "PASS", "; ".join(probs) if probs else "%s, %dx%d" % (rel(found["narrow"]), w, h))


# --------------------------------------------------------------------------- R, L: the report


def run_from(body):
    text = " ".join(blocks(body))
    s = vitest_summaries(text)
    if s:
        return s[-1], text
    if re.search(r"No test files found", text):
        return {"failed": 0, "passed": 0, "skipped": 0, "todo": 0, "total": 0}, text
    return None, text


def fraction(cell):
    m = re.search(r"(\d+)\s*/\s*(\d+)", cell or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def check_runs(res, measured, sec):
    base, _ = run_from(sec.get("1.1", ""))
    measured["baseline_run"] = base
    measured["tests_original"] = base["total"] if base else None
    if base is None:
        res.add("R1", "FAIL", "section 1.1 has no Vitest output - run the tests of your starting point before "
                              "changing anything (no tests yet: paste the 'No test files found' run)")
    else:
        res.add("R1", "PASS", "%(passed)d passed (%(total)d)" % base if base["total"] else "no tests at the start")

    final, text = run_from(sec.get("6.3", ""))
    measured["final_run"] = final
    have = measured.get("tests_final")
    if final is None or not final["total"]:
        res.add("R2", "FAIL", "section 6.3 has no Vitest output of the final tests")
    else:
        probs = []
        if final["failed"]:
            probs.append("%d failed" % final["failed"])
        if have and final["total"] != have:
            probs.append("the output reports %d tests, the test files in app/ hold %d - paste the run of the "
                         "tests you committed" % (final["total"], have))
        res.add("R2", "FAIL" if probs else "PASS", "; ".join(probs) if probs else "%(passed)d passed (%(total)d)" % final)
    measured["vitest_version"] = vitest_version(text) or vitest_version(" ".join(blocks(sec.get("1.1", ""))))

    row = next((r for r in table_rows(sec.get("7", "")) if r and "tests" in r[0].lower()), None)
    if row is None or len(row) < 3:
        res.add("R3", "FAIL", "section 7 has no 'Automated tests passed / total' row")
        return
    orig, fin = fraction(row[1]), fraction(row[2])
    probs = []
    if orig is None or fin is None:
        probs.append("write both values as passed/total, e.g. 19/19")
    else:
        if base and orig != (base["passed"], base["total"]):
            probs.append("original %d/%d, but 1.1 shows %d/%d" % (orig + (base["passed"], base["total"])))
        if final and final["total"] and fin != (final["passed"], final["total"]):
            probs.append("final %d/%d, but 6.3 shows %d/%d" % (fin + (final["passed"], final["total"])))
    res.add("R3", "FAIL" if probs else "PASS",
            "section 7: " + "; ".join(probs) if probs else "%d/%d -> %d/%d, as the runs show" % (orig + fin))


def check_report(res, measured, sec):
    def add(cid, ok, good, bad):
        res.add(cid, "PASS" if ok else "FAIL", good if ok else bad)

    # L1
    setup = setup_table(sec.get("1", ""))
    need = {"assistant (tool)": "the assistant", "model": "the exact model", "starting point": "the starting point",
            "baseline commit": "the baseline commit", "language": "ts or js", "vitest": "the Vitest version",
            "where i ran": "where you ran the tests"}
    lacking = [say for key, say in need.items() if not setup_value(setup, key)]
    start = setup_value(setup, "starting point").strip("` ").lower()
    commit = setup_value(setup, "baseline commit").strip("` ")
    measured["start_from"] = start or None
    measured["baseline_commit"] = commit or None
    probs = ["no value for: " + ", ".join(lacking)] if lacking else []
    if start and start not in STARTS:
        probs.append("starting point must be one of " + " | ".join(STARTS))
    if commit and not re.match(r"^[0-9a-fA-F]{7,40}$", commit):
        probs.append("baseline commit must be a hash (git rev-parse --short HEAD)")
    add("L1", not probs, "setup recorded, starting from %s" % start, "section 1: " + "; ".join(probs))

    # L2
    s21, s22 = sec.get("2.1", ""), sec.get("2.2", "")
    probs = []
    if not real_blocks(s21, 3):
        probs.append("2.1: the repository map you gave the assistant (3+ lines)")
    sent = real_blocks(s22, 1)
    text = norm(" ".join(sent))
    if not sent or len(text.split()) < 40:
        probs.append("2.2: the context message as sent (40+ words)")
    else:
        lacks = []
        if not (re.search(r"\bAC\s?-?1\b", text) and re.search(r"\bAC\s?-?6\b|AC1\s*[-–]\s*AC6|AC1-6", text)):
            lacks.append("AC1-AC6")
        if not re.search(r"\bF\s?-?1\b|filter|capacity", text, re.I):
            lacks.append("the new requirements (F1-F5)")
        if not re.search(r"\bno\s+(?:login|database|backend|payments?|live api)|fictional|constraint", text, re.I):
            lacks.append("the constraints (no login, no database, fictional data)")
        if lacks:
            probs.append("2.2: the context must include " + ", ".join(lacks))
    add("L2", not probs, "map and context recorded", "section " + "; ".join(probs))

    # L3
    rows = [r for r in table_rows(sec.get("3.1", "")) if len(r) >= 5]
    filled = [r for r in rows if all(useful(c) for c in r[1:5])]
    located = [r for r in filled if re.search(r"\.[cm]?[jt]sx?\b|\w+\s*\(\s*\)", r[2])]
    measured["risks"] = len(filled)
    add("L3", len(located) >= 3, "%d risks, each located" % len(located),
        "section 3.1 needs 3 risks with every column filled and a file or function() in 'Where' (found %d)" % len(located))

    # L4
    plan = [l for l in strip_comments(sec.get("3.2", "")).splitlines() if re.match(r"^\s*\d+[.)]\s+\S", l)]
    plan = [l for l in plan if useful(re.sub(r"^\s*\d+[.)]\s+", "", l))]
    rej = [r for r in table_rows(sec.get("3.3", "")) if len(r) >= 3 and useful(r[0])
           and re.match(r"^\W*(rejected|modified)\W*$", r[1].strip(), re.I) and len(r[2].split()) >= 12]
    probs = []
    if len(plan) < 3:
        probs.append("3.2: a plan of 3 or more numbered steps (found %d)" % len(plan))
    if not rej:
        probs.append("3.3: one suggestion marked Rejected or Modified, with 12+ words of why")
    add("L4", not probs, "plan of %d steps, a suggestion %s" % (len(plan), rej[0][1].strip().lower() if rej else ""),
        "section " + "; ".join(probs))

    # L5
    rows = table_rows(sec.get("4.2", ""))
    done = [s for s in SHOTS if any(r and s in r[0].lower() and len(r) >= 2 and useful(r[1]) and len(r[1].split()) >= 4
                                    for r in rows)]
    lacking = [s for s in SHOTS if s not in done]
    add("L5", not lacking, "all five screenshots described",
        "section 4.2: say what %s shows (4+ words each)" % ", ".join(lacking))

    # L6
    resp = [r for r in table_rows(sec.get("5.1", "")) if len(r) >= 2 and useful(r[0]) and useful(r[1])]
    decisions = [r for r in table_rows(sec.get("5.2", "")) if len(r) >= 3 and useful(r[0]) and useful(r[2])
                 and len(r[2].split()) >= 8]
    dup = [r for r in table_rows(sec.get("5.3", "")) if len(r) >= 2 and useful(r[0]) and useful(r[1])]
    measured["duplicates_removed"] = len(dup)
    probs = []
    if len(resp) < 4:
        probs.append("5.1: 4+ modules with their responsibility (found %d)" % len(resp))
    if len(decisions) < 2:
        probs.append("5.2: 2+ design decisions, each with 8+ words of why (found %d)" % len(decisions))
    if not dup:
        probs.append("5.3: at least one duplicated location you removed")
    add("L6", not probs, "%d modules, %d decisions, %d duplicate(s) removed" % (len(resp), len(decisions), len(dup)),
        "section " + "; ".join(probs))

    # L7
    rows = table_rows(sec.get("6.1", ""))
    planned = set()
    for r in rows:
        if len(r) >= 3 and useful(r[1]) and useful(r[2]):
            planned |= ids_in(r[0]) | ids_in(r[1])
    lacking = [i for i in ALL_IDS if i not in planned]
    cmds = " ".join(blocks(sec.get("6.2", "")))
    probs = []
    if lacking:
        probs.append("6.1: no filled row for " + ", ".join(lacking))
    if not re.search(r"\bvitest\b|\bnpm\s+(?:run\s+)?test\b", cmds):
        probs.append("6.2: the commands you ran (npx vitest run ...)")
    add("L7", not probs, "every required ID planned, commands recorded", "section " + "; ".join(probs))

    # L8
    rows = table_rows(sec.get("7", ""))
    probs = []
    for key, label in QUALITY_ROWS:
        row = next((r for r in rows if r and key in r[0].lower()), None)
        if row is None or len(row) < 4:
            probs.append("the '%s' row" % label)
        elif not (useful(row[2]) and useful(row[3]) and len(row[3].split()) >= 3):
            probs.append("'%s': the final value and how you obtained it" % label)
        elif key != "limitation" and not useful(row[1]):
            probs.append("'%s': the original value" % label)
    add("L8", not probs, "four measures, each with how it was obtained", "section 7 needs " + "; ".join(probs))

    # L9
    exchanges = sorted((k for k in sec if re.match(r"^8\.\d+$", k)), key=lambda k: int(k.split(".")[1]))
    complete = []
    for k in exchanges:
        body = sec[k]
        if all(useful(label_value(body, f)) for f in EXCHANGE_FIELDS):
            bl = real_blocks(body, 1)
            if len(bl) >= 2 and len(norm(bl[1]).split()) >= 20:
                complete.append(k)
    measured["exchanges"] = len(complete)
    add("L9", len(complete) >= 3, "%d complete exchanges" % len(complete),
        "section 8 needs 3+ exchanges with every field, the prompt and the output (20+ words) - found %d" % len(complete))

    # L10
    words = word_count(sec.get("10", ""))
    measured["reflection_words"] = words
    add("L10", WORDS_MIN <= words <= WORDS_MAX, "%d words" % words,
        "section 10 has %d words, the brief asks for %d-%d" % (words, WORDS_MIN, WORDS_MAX))


# --------------------------------------------------------------------------- main


def run():
    res, measured = Results(), {}
    root, sources = check_project(res, measured)
    check_suite(res, measured, root, sources)
    check_diagrams(res, measured)
    check_evidence(res, measured)
    text = read(REPORT)
    if text is None:
        for cid in ORDER:
            if cid[0] in "RL":
                res.add(cid, "ERROR", "report.md not found")
    else:
        sec = sections(text)
        check_runs(res, measured, sec)
        check_report(res, measured, sec)
    res.rows = sorted(res.rows, key=lambda r: ORDER.index(r["id"]))
    return res, measured


def print_human(res, measured):
    counts = res.counts()
    print("SIS #04 - the room catalog, the refactoring, the tests, the report\n")
    width = max(len(r["title"]) for r in res.rows)
    for r in res.rows:
        print(("%-6s %-4s %-*s  %s" % (r["verdict"], r["id"], width, r["title"], r["message"])).rstrip())
    print("-" * 78)
    print("SUMMARY pass=%d fail=%d error=%d   (%d checks)"
          % (counts["PASS"], counts["FAIL"], counts["ERROR"], len(res.rows)))
    if counts["FAIL"] or counts["ERROR"]:
        print("Every FAIL or ERROR you keep goes in report.md section 9 and in submission.yml known_fails.")
        print("One you report and explain costs you nothing. One you hide costs the whole criterion.")
    else:
        print("Files and shape are clean. Whether the analysis and the refactoring are good is read by a person.")


def main():
    parser = argparse.ArgumentParser(description="SIS #04 checker - run from inside sis-04/")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    if not os.path.isdir("tests") and not os.path.exists(REPORT) and not os.path.isdir(APP):
        message = "run this from inside your sis-04/ folder:  cd sis-04 && python tests/check_sis.py"
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
