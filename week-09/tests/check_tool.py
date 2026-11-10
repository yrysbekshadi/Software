#!/usr/bin/env python3
"""
check_tool.py - Week 09 checker: canBook as a tool. DO NOT EDIT.

    python tests/check_tool.py            # from inside week-09/
    python tests/check_tool.py --json     # machine-readable, for the grading pipeline

What it checks (30 checks):
    D1-D6    tool/check_room.json - the definition itself (README section 5, Part 1)
    S01-S12  twelve fixed calls thrown at YOUR input schema - must it accept or refuse each one?
    F1-F7    calls/r1.json, calls/r2.json, calls/r3.* - the calls a model wrote (Part 2)
    L1-L5    lab-report.md and AI_USAGE.md - sections 5, 6, 7, 10 and the disclosure

It checks SHAPE and AGREEMENT, never QUALITY. A schema that refuses all twelve bad calls can still
come with a description nobody can use, and a permissions table can be full and wrong. Those are
the grader's to read.

Verdicts:
    PASS   the check holds
    FAIL   the file is there, but the check does not hold
    ERROR  the file is missing or unreadable, so the check could not be made

Exit codes: 0 = all PASS - 1 = at least one FAIL or ERROR - 3 = wrong working directory.
Standard library only.
"""

import argparse
import json
import os
import re
import sys

TOOL = os.path.join("tool", "check_room.json")
CALLS = "calls"
REPORT = "lab-report.md"
AI_USAGE = "AI_USAGE.md"

FIELDS = ["start", "end", "now", "blocked", "bookings"]

# Keywords this checker understands (README section 5). Anything else is refused by D6, so that a
# schema never passes here by using a keyword this file silently ignores.
VALIDATING = {"type", "properties", "required", "additionalProperties", "items", "minimum", "maximum",
              "exclusiveMinimum", "exclusiveMaximum", "enum", "minItems", "maxItems"}
ANNOTATIONS = {"description", "title", "$schema", "examples", "default"}

BASE = {"start": 600, "end": 660, "now": 540, "blocked": False, "bookings": [{"start": 660, "end": 720}]}


def with_(**kw):
    d = json.loads(json.dumps(BASE))
    for k, v in kw.items():
        if v is _DROP:
            d.pop(k, None)
        else:
            d[k] = v
    return d


_DROP = object()

# (id, what, arguments, should the schema ACCEPT it?)
CASES = [
    ("S01", "the R1 call, valid", with_(), True),
    ("S02", "no existing bookings: bookings = []", with_(bookings=[]), True),
    ("S03", 'end as a string: "11:00"', with_(end="11:00"), False),
    ("S04", "now missing", with_(now=_DROP), False),
    ("S05", 'an extra field: "room": "204"', dict(with_(), room="204"), False),
    ("S06", "start below the day: -30", with_(start=-30), False),
    ("S07", "end beyond the day: 1500", with_(end=1500), False),
    ("S08", "a booking with no end: {start: 660}", with_(bookings=[{"start": 660}]), False),
    ("S09", 'blocked as a string: "false"', with_(blocked="false"), False),
    ("S10", "start not a whole minute: 600.5", with_(start=600.5), False),
    ("S11", "end at the end of the day: 1440", with_(start=1380, end=1440, bookings=[]), True),
    ("S12", "a booking as a pair: [660, 720]", with_(bookings=[[660, 720]]), False),
]

EXPECTED = {
    "r1": {"start": 600, "end": 660, "now": 540, "blocked": False, "bookings": [{"start": 660, "end": 720}]},
    "r2": {"start": 840, "end": 990, "now": 810, "blocked": True, "bookings": []},
}

DECISIONS = {"allow", "ask", "block"}
ACTIONS = ["A%d" % i for i in range(1, 9)]


# ------------------------------------------------------------------------------ a small validator

class SchemaError(Exception):
    pass


def _is_type(v, t):
    if t == "object":
        return isinstance(v, dict)
    if t == "array":
        return isinstance(v, list)
    if t == "string":
        return isinstance(v, str)
    if t == "boolean":
        return isinstance(v, bool)
    if t == "null":
        return v is None
    if t == "integer":
        if isinstance(v, bool):
            return False
        return isinstance(v, int) or (isinstance(v, float) and v.is_integer())
    if t == "number":
        return isinstance(v, (int, float)) and not isinstance(v, bool)
    raise SchemaError("unknown type %r" % t)


def errors(value, schema, path="$"):
    """Return a list of reasons `value` does not satisfy `schema` (empty = valid)."""
    if schema is True or schema == {}:
        return []
    if schema is False:
        return ["%s: not allowed" % path]
    if not isinstance(schema, dict):
        raise SchemaError("%s: a schema must be an object" % path)
    out = []
    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_is_type(value, t) for t in types):
            return ["%s: expected %s" % (path, "/".join(types))]
    if "enum" in schema and value not in schema["enum"]:
        out.append("%s: not one of %s" % (path, schema["enum"]))
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            out.append("%s: below minimum %s" % (path, schema["minimum"]))
        if "maximum" in schema and value > schema["maximum"]:
            out.append("%s: above maximum %s" % (path, schema["maximum"]))
        if "exclusiveMinimum" in schema and value <= schema["exclusiveMinimum"]:
            out.append("%s: not above %s" % (path, schema["exclusiveMinimum"]))
        if "exclusiveMaximum" in schema and value >= schema["exclusiveMaximum"]:
            out.append("%s: not below %s" % (path, schema["exclusiveMaximum"]))
    if isinstance(value, dict):
        props = schema.get("properties", {})
        for r in schema.get("required", []):
            if r not in value:
                out.append("%s: %s is required" % (path, r))
        for k, v in value.items():
            if k in props:
                out += errors(v, props[k], "%s.%s" % (path, k))
            else:
                ap = schema.get("additionalProperties", True)
                if ap is False:
                    out.append("%s: %s is not allowed" % (path, k))
                elif isinstance(ap, dict):
                    out += errors(v, ap, "%s.%s" % (path, k))
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            out.append("%s: fewer than %s items" % (path, schema["minItems"]))
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            out.append("%s: more than %s items" % (path, schema["maxItems"]))
        if "items" in schema:
            for i, v in enumerate(value):
                out += errors(v, schema["items"], "%s[%d]" % (path, i))
    return out


def unknown_keywords(schema, path="inputSchema"):
    found = []
    if isinstance(schema, dict):
        for k, v in schema.items():
            if k == "properties" and isinstance(v, dict):
                for name, sub in v.items():
                    found += unknown_keywords(sub, "%s.properties.%s" % (path, name))
            elif k in ("items", "additionalProperties") and isinstance(v, dict):
                found += unknown_keywords(v, "%s.%s" % (path, k))
            elif k not in VALIDATING and k not in ANNOTATIONS:
                found.append("%s.%s" % (path, k))
    return found


# ------------------------------------------------------------------------------ reading files

def read_json_loose(path):
    """JSON from a file, tolerating a ```json fence around it (models love those)."""
    with open(path, encoding="utf-8-sig") as f:
        text = f.read().strip()
    m = re.match(r"^```[a-zA-Z]*\s*\n(.*)\n```\s*$", text, re.S)
    if m:
        text = m.group(1)
    return json.loads(text)


def normalise_call(obj):
    """Accept {"name", "arguments"}, Anthropic's {"name", "input"}, OpenAI's {"function": {...}}
    with arguments as a JSON string, or a {"tool_calls": [...]} wrapper with one call."""
    if isinstance(obj, dict) and isinstance(obj.get("tool_calls"), list) and len(obj["tool_calls"]) == 1:
        obj = obj["tool_calls"][0]
    if isinstance(obj, dict) and isinstance(obj.get("function"), dict):
        obj = obj["function"]
    if not isinstance(obj, dict) or "name" not in obj:
        raise ValueError('not a call: expected {"name": ..., "arguments": {...}}')
    args = obj.get("arguments", obj.get("input", obj.get("parameters")))
    if isinstance(args, str):
        args = json.loads(args)
    if not isinstance(args, dict):
        raise ValueError("arguments is not an object")
    return obj["name"], args


def sections(text):
    """{number: body} for every '## N.' heading."""
    out = {}
    parts = re.split(r"^##\s+(\d+)\.", text, flags=re.M)
    for i in range(1, len(parts) - 1, 2):
        out[int(parts[i])] = parts[i + 1].split("\n", 1)[1] if "\n" in parts[i + 1] else ""
    return out


def strip_comments(s):
    return re.sub(r"<!--.*?-->", "", s, flags=re.S)


def words(s):
    return re.findall(r"[A-Za-zА-Яа-яЁё0-9']+", s)


# ------------------------------------------------------------------------------ the checks

def run():
    res = []

    def add(cid, title, verdict, detail=""):
        res.append({"id": cid, "title": title, "verdict": verdict, "detail": detail})

    # ---- D: the definition
    tool, schema, schema_ok = None, None, False
    try:
        tool = read_json_loose(TOOL)
        if not isinstance(tool, dict):
            raise ValueError("the top level is not an object")
        add("D1", "tool/check_room.json exists and is valid JSON", "PASS")
    except FileNotFoundError:
        add("D1", "tool/check_room.json exists and is valid JSON", "ERROR", "file not found")
    except (ValueError, json.JSONDecodeError) as e:
        add("D1", "tool/check_room.json exists and is valid JSON", "FAIL", str(e))

    titles = {
        "D2": "has name, description and inputSchema",
        "D3": 'name is exactly "check_room"',
        "D4": "description: 25+ words, says minutes, 1440, and that it does not save",
        "D5": "inputSchema: an object with exactly the five fields, all required",
        "D6": "inputSchema uses only the keywords listed in README section 5",
    }
    if tool is None:
        for cid, t in titles.items():
            add(cid, t, "ERROR", "no readable tool definition")
    else:
        missing = [k for k in ("name", "description", "inputSchema") if k not in tool]
        add("D2", titles["D2"], "FAIL" if missing else "PASS", ("missing: " + ", ".join(missing)) if missing else "")
        add("D3", titles["D3"], "PASS" if tool.get("name") == "check_room" else "FAIL",
            "" if tool.get("name") == "check_room" else "name is %r" % tool.get("name"))
        desc = tool.get("description") if isinstance(tool.get("description"), str) else ""
        probs = []
        if len(words(desc)) < 25:
            probs.append("%d words" % len(words(desc)))
        if not re.search(r"minute", desc, re.I):
            probs.append("no unit (minutes)")
        if "1440" not in desc:
            probs.append("no 1440")
        if not re.search(r"\b(not|never|n't)\b[^.]{0,40}\b(save|saves|store|stores|book|books|reserve|reserves|create|creates|change|changes|modify|modifies)\b", desc, re.I):
            probs.append("does not say that it does not save a booking")
        add("D4", titles["D4"], "FAIL" if probs else "PASS", "; ".join(probs))
        schema = tool.get("inputSchema")
        probs = []
        if not isinstance(schema, dict):
            probs.append("inputSchema is not an object")
        else:
            if schema.get("type") != "object":
                probs.append('type is not "object"')
            props = schema.get("properties") if isinstance(schema.get("properties"), dict) else {}
            if sorted(props) != sorted(FIELDS):
                probs.append("properties are %s, expected %s" % (sorted(props), FIELDS))
            req = schema.get("required") if isinstance(schema.get("required"), list) else []
            if sorted(req) != sorted(FIELDS):
                probs.append("required is %s" % req)
        add("D5", titles["D5"], "FAIL" if probs else "PASS", "; ".join(probs))
        if isinstance(schema, dict):
            unk = unknown_keywords(schema)
            add("D6", titles["D6"], "FAIL" if unk else "PASS", ("not supported: " + ", ".join(unk)) if unk else "")
            schema_ok = not unk
        else:
            add("D6", titles["D6"], "ERROR", "no inputSchema object")

    # ---- S: twelve calls against the student's schema
    for cid, what, args, accept in CASES:
        title = "%s -> %s" % (what, "accept" if accept else "refuse")
        if not schema_ok:
            add(cid, title, "ERROR", "no usable inputSchema (see D1, D6)")
            continue
        try:
            errs = errors(args, schema)
        except SchemaError as e:
            add(cid, title, "ERROR", "schema could not be applied: %s" % e)
            continue
        if accept and errs:
            add(cid, title, "FAIL", "your schema refused a valid call: " + errs[0])
        elif not accept and not errs:
            add(cid, title, "FAIL", "your schema accepted it")
        else:
            add(cid, title, "PASS", (errs[0] if errs else ""))

    # ---- F: the calls a model wrote
    for n, (a, b, c) in (("r1", ("F1", "F2", "F3")), ("r2", ("F4", "F5", "F6"))):
        path = os.path.join(CALLS, n + ".json")
        t1, t2, t3 = ("%s: a call to check_room" % path, "%s: arguments valid against your schema" % path,
                      "%s: arguments equal the expected ones (README section 5, Part 2)" % path)
        try:
            name, args = normalise_call(read_json_loose(path))
        except FileNotFoundError:
            for cid, t in ((a, t1), (b, t2), (c, t3)):
                add(cid, t, "ERROR", "file not found")
            continue
        except (ValueError, json.JSONDecodeError) as e:
            add(a, t1, "FAIL", str(e))
            add(b, t2, "ERROR", "no readable call")
            add(c, t3, "ERROR", "no readable call")
            continue
        add(a, t1, "PASS" if name == "check_room" else "FAIL", "" if name == "check_room" else "name is %r" % name)
        if not schema_ok:
            add(b, t2, "ERROR", "no usable inputSchema (see D1, D6)")
        else:
            try:
                errs = errors(args, schema)
                add(b, t2, "FAIL" if errs else "PASS", errs[0] if errs else "")
            except SchemaError as e:
                add(b, t2, "ERROR", str(e))
        exp = EXPECTED[n]
        diff = [k for k in sorted(set(exp) | set(args)) if args.get(k, "<missing>") != exp.get(k, "<absent>")]
        add(c, t3, "FAIL" if diff else "PASS", ("differs in: " + ", ".join(diff)) if diff else "")
    have = [p for p in ("r3.json", "r3.txt") if os.path.isfile(os.path.join(CALLS, p))
            and os.path.getsize(os.path.join(CALLS, p)) > 0]
    t7 = "calls/r3: exactly one of r3.json (it called) or r3.txt (it asked), not empty"
    if len(have) == 1:
        add("F7", t7, "PASS", have[0])
    elif not have:
        add("F7", t7, "ERROR", "neither calls/r3.json nor calls/r3.txt")
    else:
        add("F7", t7, "FAIL", "both files exist - keep only what the model actually returned")

    # ---- L: the worksheet and the disclosure
    try:
        with open(REPORT, encoding="utf-8") as f:
            sec = sections(strip_comments(f.read()))
    except FileNotFoundError:
        sec = None
    lt = {
        "L1": "section 5 names at least two acceptance criteria (AC1-AC6) the schema cannot check",
        "L2": "section 6: A1-A8 each have allow / ask / block and a reason of 5+ words",
        "L3": "section 7 names the checkpoint commit (a SHA)",
        "L4": "section 10: a conclusion of 80-150 words",
    }
    if sec is None:
        for cid, t in lt.items():
            add(cid, t, "ERROR", "lab-report.md not found")
    else:
        acs = set(re.findall(r"\bAC\s?-?([1-6])\b", sec.get(5, "")))
        add("L1", lt["L1"], "PASS" if len(acs) >= 2 else "FAIL",
            "found: " + (", ".join("AC" + a for a in sorted(acs)) or "none"))
        rows = {}
        for line in sec.get(6, "").splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells and re.fullmatch(r"A[1-8]", cells[0]):
                rows[cells[0]] = cells
        bad = []
        for a in ACTIONS:
            cells = rows.get(a)
            if not cells or len(cells) < 4:
                bad.append(a + " missing")
                continue
            if cells[2].lower().strip("* ") not in DECISIONS:
                bad.append(a + " decision")
            elif len(words(cells[3])) < 5:
                bad.append(a + " reason")
        add("L2", lt["L2"], "FAIL" if bad else "PASS", ", ".join(bad))
        has_sha = re.search(r"\b[0-9a-f]{7,40}\b", sec.get(7, ""))
        add("L3", lt["L3"], "PASS" if has_sha else "FAIL", "" if has_sha else "no 7-40 character commit hash in section 7")
        n = len(words(sec.get(10, "")))
        add("L4", lt["L4"], "PASS" if 80 <= n <= 150 else "FAIL", "%d words" % n)
    t5 = "AI_USAGE.md filled in (a tool row, and signed)"
    try:
        with open(AI_USAGE, encoding="utf-8") as f:
            au = strip_comments(f.read())
        signed = re.search(r"^Signed:\s*(.+)$", au, re.M)
        signed_ok = bool(signed) and "<your name>" not in signed.group(1) and signed.group(1).strip()
        row = re.search(r"^\|\s*[^|\s][^|]*\|\s*[^|\s][^|]*\|\s*Part 2", au, re.M)
        add("L5", t5, "PASS" if signed_ok and row else "FAIL",
            "" if signed_ok and row else ("not signed" if not signed_ok else "the Part 2 row has no tool and model"))
    except FileNotFoundError:
        add("L5", t5, "ERROR", "AI_USAGE.md not found")

    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if not os.path.isfile("README.md") or not os.path.isdir("tests") or not os.path.isfile(os.path.join("tests", "check_tool.py")):
        print("Run this from inside your week-09/ folder:  cd week-09  &&  python tests/check_tool.py", file=sys.stderr)
        sys.exit(3)
    res = run()
    counts = {v: sum(r["verdict"] == v for r in res) for v in ("PASS", "FAIL", "ERROR")}
    if a.json:
        print(json.dumps({"week": "09", "rows": res, "counts": counts, "total": len(res)}, indent=2))
    else:
        for r in res:
            line = "%-5s %-5s %s" % (r["verdict"], r["id"], r["title"])
            if r["detail"] and r["verdict"] != "PASS":
                line += "\n             -> " + r["detail"]
            print(line)
        print()
        print("SUMMARY: %d PASS · %d FAIL · %d ERROR  (of %d checks)" % (counts["PASS"], counts["FAIL"], counts["ERROR"], len(res)))
        print("Paste this whole output into lab-report.md section 8, and these three numbers into submission.yml.")
    sys.exit(0 if counts["FAIL"] == 0 and counts["ERROR"] == 0 else 1)


if __name__ == "__main__":
    main()
