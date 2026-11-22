#!/usr/bin/env python3
"""
validate_submission.py - checks the shape of sis-04/submission.yml. DO NOT EDIT.

    python tests/validate_submission.py                # from inside sis-04/
    python tests/validate_submission.py --json         # machine-readable, for the grading pipeline
    python tests/validate_submission.py --file path/to/submission.yml

It checks SHAPE, never QUALITY. A green run means the file can be read and graded, not that
the work is good. It runs tests/check_sis.py itself, so the numbers you declare are compared
with a real run, and the number of checks is never typed in by hand.

Verdicts, same vocabulary as check_sis.py:
    PASS   the field is present and well-formed
    FAIL   the field is present but wrong
    ERROR  the field is absent, or the checker could not be run to compare with

Exit codes: 0 = no FAIL and no ERROR - 1 = at least one FAIL or ERROR - 2 = file missing or
unparseable - 3 = wrong working directory.

Standard library only. No pip install, no YAML package: this file understands the restricted
subset of YAML that submission.yml uses, and refuses anything else with a line number.
"""

import argparse
import json
import os
import re
import subprocess
import sys

CHECKER = os.path.join("tests", "check_sis.py")

STUDENT_ID = re.compile(r"^\d{2}[A-Za-z]\d{6}$")
GITHUB_LOGIN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38}$")
SHORT_SHA = re.compile(r"^[0-9a-fA-F]{7,40}$")
CHECK_ID = re.compile(r"^[ASDERL]\d{1,2}$")
NAMES_SOMETHING = re.compile(r"\bAC\s?-?[1-6]\b|\bF[1-5]\b|\bB[1-6]\b|\bINT\b|"
                             r"\b[\w/.-]+\.(?:[cm]?[jt]sx?|md|puml)\b|\b(?:canBook|checkRoom|filterRooms|ROOMS)\b")
PLACEHOLDER = re.compile(r"(^<.*>$)|(\bTODO\b)|(\bFIXME\b)|(\byour name\b)|(^\.\.\.$)", re.I)

BARE_TOOL_NAMES = {
    "chatgpt", "gpt", "claude", "gemini", "copilot", "github copilot", "bolt", "bolt.new",
    "deepseek", "grok", "mistral", "llama", "qwen", "perplexity", "cursor", "lovable", "v0",
    "claude code", "codex",
}
NOT_DISPLAYED = ("not displayed", "not-displayed")
HONESTY = ("baseline_unchanged", "runs_unedited", "no_invented_metrics", "ai_usage_disclosed")
STARTS = ("week-08", "week-07", "sis-03", "starter")
LANGUAGES = ("ts", "js")
COUNTS = (("rooms", "rooms"), ("tests_original", "tests_original"), ("tests_final", "tests_final"),
          ("risks", "risks"), ("exchanges", "exchanges"))

TITLES = {
    "D1": "schema and assignment",
    "D2": "student.name and student.group",
    "D3": "student.student_id",
    "D4": "student.github",
    "D5": "assistant.tool",
    "D6": "assistant.model is an exact model name or not displayed",
    "D7": "project: starting point, baseline commit, language, Vitest",
    "D8": "checker numbers add up",
    "D9": "checker numbers match a run made now",
    "D10": "checker.commit",
    "D11": "known_fails lists exactly what still fails",
    "D12": "counts match the files and report.md",
    "D13": "review_findings: three, each naming what it is about",
    "D14": "honesty block answered",
}


# --------------------------------------------------------------------------- parsing


class ParseError(Exception):
    pass


def strip_comment(line):
    quote = None
    for i, ch in enumerate(line):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            return line[:i]
    return line


def scalar(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [scalar(part) for part in inner.split(",") if part.strip()] if inner else []
    return value


def parse(text):
    """Parse the subset submission.yml uses, and nothing else:

        key: value            at column 0
        key:                  at column 0, followed by two-space-indented lines that are
          subkey: value       either all `subkey: value`
          - item              or all `- item`
        key: [a, b]  /  []    a one-line list, at either level

    Comments start with # . Tabs are refused.
    """
    doc, current = {}, None
    for number, raw in enumerate(text.splitlines(), 1):
        if "\t" in raw[:len(raw) - len(raw.lstrip())]:
            raise ParseError("line %d: indented with a tab - use two spaces" % number)
        line = strip_comment(raw).rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        body = line.strip()
        if indent == 0:
            key, sep, value = body.partition(":")
            if not sep or not re.match(r"^[A-Za-z_][\w-]*$", key.strip()):
                raise ParseError("line %d: expected `key: value`, got %r" % (number, body[:40]))
            key = key.strip()
            if value.strip():
                doc[key], current = scalar(value), None
            else:
                doc[key], current = None, key
        elif indent == 2:
            if current is None:
                raise ParseError("line %d: indented line with no `key:` above it" % number)
            if body.startswith("-"):
                if doc[current] is None:
                    doc[current] = []
                if not isinstance(doc[current], list):
                    raise ParseError("line %d: a `- item` inside a block of `key: value` lines" % number)
                item = body[1:].strip()
                if item:
                    doc[current].append(scalar(item))
            else:
                key, sep, value = body.partition(":")
                if not sep:
                    raise ParseError("line %d: expected `key: value`, got %r" % (number, body[:40]))
                if doc[current] is None:
                    doc[current] = {}
                if not isinstance(doc[current], dict):
                    raise ParseError("line %d: a `key: value` inside a list" % number)
                doc[current][key.strip()] = scalar(value)
        else:
            raise ParseError("line %d: indent must be 0 or 2 spaces, found %d" % (number, indent))
    return doc


def get(doc, dotted):
    """Value at `a.b`, or KeyError (the class, as a marker) when the key is not there at all."""
    node = doc
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return KeyError
        node = node[part]
    return node


def empty(value):
    return value is None or value is KeyError or (isinstance(value, str) and (
        not value.strip() or bool(PLACEHOLDER.search(value.strip()))))


def natural(check_id):
    """F2 before F10."""
    return (check_id[:1], int(check_id[1:]) if check_id[1:].isdigit() else 0)


def as_int(value):
    return int(value) if isinstance(value, str) and re.match(r"^\d+$", value.strip()) else None


# --------------------------------------------------------------------------- validation


class Report:
    def __init__(self):
        self.rows = []

    def add(self, cid, verdict, message):
        self.rows.append({"id": cid, "title": TITLES[cid], "verdict": verdict, "message": message})

    def counts(self):
        return {v: sum(1 for r in self.rows if r["verdict"] == v) for v in ("PASS", "FAIL", "ERROR")}

    def clean(self):
        c = self.counts()
        return c["FAIL"] == 0 and c["ERROR"] == 0


def text_field(rep, cid, doc, key, problem=None):
    value = get(doc, key)
    if value is KeyError:
        rep.add(cid, "ERROR", "%s: the key is missing" % key)
    elif empty(value) or not isinstance(value, str):
        rep.add(cid, "FAIL", "%s is empty" % key)
    else:
        why = problem(value.strip()) if problem else None
        rep.add(cid, "FAIL" if why else "PASS", why or "%s: %s" % (key, value.strip()))


def run_checker(folder):
    """Run the shipped checker over this folder and return its --json result, or None."""
    if not os.path.exists(os.path.join(folder, CHECKER)):
        return None
    try:
        proc = subprocess.run([sys.executable, CHECKER, "--json"], cwd=folder,
                              capture_output=True, text=True, timeout=80)
        return json.loads(proc.stdout)
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def validate(doc, folder):
    rep = Report()
    run = run_checker(folder)
    now = run.get("counts") if run else None
    measured = (run or {}).get("measured") or {}

    # D1
    schema, assignment = get(doc, "schema"), get(doc, "assignment")
    ok = str(schema) == "1" and assignment == "sis-04"
    rep.add("D1", "PASS" if ok else "FAIL",
            "schema 1, assignment sis-04" if ok else "schema must be 1 and assignment \"sis-04\" - do not edit these")

    # D2
    name, group = get(doc, "student.name"), get(doc, "student.group")
    lacks = [k for k, v in (("student.name", name), ("student.group", group)) if empty(v) or not isinstance(v, str)]
    rep.add("D2", ("ERROR" if name is KeyError or group is KeyError else "FAIL") if lacks else "PASS",
            "empty: " + ", ".join(lacks) if lacks else "name and group filled")

    # D3-D5
    text_field(rep, "D3", doc, "student.student_id",
               lambda v: None if STUDENT_ID.match(v) else "%r is not a KBTU student ID (shape: 00X000000)" % v)
    text_field(rep, "D4", doc, "student.github",
               lambda v: None if GITHUB_LOGIN.match(v) else "give the GitHub username only, not a URL")
    text_field(rep, "D5", doc, "assistant.tool")

    # D6
    text_field(rep, "D6", doc, "assistant.model",
               lambda v: None if v.lower() in NOT_DISPLAYED else (
                   "%r is a tool name, not a model - give the exact model with its version, or: not displayed" % v
                   if v.lower() in BARE_TOOL_NAMES or not re.search(r"\d", v) else None))

    # D7
    probs = []
    start = get(doc, "project.start_from")
    if start not in STARTS:
        probs.append("project.start_from must be one of: " + " | ".join(STARTS))
    elif measured.get("start_from") and measured["start_from"] != start:
        probs.append("project.start_from says %s, report.md section 1 says %s" % (start, measured["start_from"]))
    base = get(doc, "project.baseline_commit")
    if not isinstance(base, str) or not SHORT_SHA.match(base.strip()):
        probs.append("project.baseline_commit must be a commit hash")
    elif measured.get("baseline_commit") and not (
            measured["baseline_commit"].lower().startswith(base.lower()) or base.lower().startswith(measured["baseline_commit"].lower())):
        probs.append("project.baseline_commit says %s, report.md section 1 says %s" % (base, measured["baseline_commit"]))
    if get(doc, "project.language") not in LANGUAGES:
        probs.append("project.language must be ts or js")
    vit = get(doc, "project.vitest")
    vm = re.search(r"(\d+\.\d+(?:\.\d+)?)", vit) if isinstance(vit, str) else None
    seen = measured.get("vitest_version")
    if not vm:
        probs.append("project.vitest must be the version from the RUN line, e.g. 3.2.4")
    elif seen and not (str(seen).startswith(vm.group(1)) or vm.group(1).startswith(str(seen))):
        probs.append("project.vitest says %s, the run in report.md says %s" % (vm.group(1), seen))
    rep.add("D7", "FAIL" if probs else "PASS",
            "; ".join(probs) if probs else "from %s at %s, %s, Vitest %s" % (start, base, get(doc, "project.language"), vm.group(1)))

    # D8-D9
    nums = {k: as_int(get(doc, "checker." + k)) for k in ("pass", "fail", "error")}
    if now is None:
        rep.add("D8", "ERROR", "tests/check_sis.py could not be run - is it next to this file, unedited?")
        rep.add("D9", "ERROR", "no checker run to compare with")
    elif any(v is None for v in nums.values()):
        rep.add("D8", "FAIL", "checker.pass / fail / error must all be whole numbers")
        rep.add("D9", "FAIL", "nothing to compare")
    else:
        total, said = sum(now.values()), sum(nums.values())
        rep.add("D8", "PASS" if said == total else "FAIL",
                "pass + fail + error = %d" % said
                + ("" if said == total else ", but the checker runs %d checks on your files" % total))
        same = (nums["pass"], nums["fail"], nums["error"]) == (now["PASS"], now["FAIL"], now["ERROR"])
        rep.add("D9", "PASS" if same else "FAIL",
                "declared %d/%d/%d, a run now gives %d/%d/%d" % (
                    nums["pass"], nums["fail"], nums["error"], now["PASS"], now["FAIL"], now["ERROR"])
                + ("" if same else " - run the checker again and copy its numbers"))

    # D10
    commit = get(doc, "checker.commit")
    if commit is KeyError:
        rep.add("D10", "ERROR", "checker.commit: the key is missing")
    elif empty(commit) or not SHORT_SHA.match(str(commit)):
        rep.add("D10", "FAIL", "checker.commit must be the hash from git rev-parse --short HEAD, got %r" % (commit,))
    else:
        rep.add("D10", "PASS", "checker.commit: %s" % commit)

    # D11
    known = get(doc, "checker.known_fails")
    if known is KeyError:
        rep.add("D11", "ERROR", "checker.known_fails: the key is missing - write [] if nothing fails")
    elif not isinstance(known, list):
        rep.add("D11", "FAIL", "known_fails must be a list on one line, e.g. [E3] or []")
    elif run is None:
        rep.add("D11", "ERROR", "no checker run to compare with")
    else:
        bad = [x for x in known if not CHECK_ID.match(str(x))]
        failing = sorted((r["id"] for r in run.get("rows", []) if r["verdict"] != "PASS"), key=natural)
        listed = sorted(set(str(x) for x in known), key=natural)
        if bad:
            rep.add("D11", "FAIL", "known_fails holds things that are not check IDs: %s" % bad)
        elif listed != failing:
            rep.add("D11", "FAIL", "known_fails lists %s, the checker fails %s" % (listed or "[]", failing or "[]"))
        else:
            rep.add("D11", "PASS", "known_fails matches the checker: %s" % (listed or "[]"))

    # D12
    probs = []
    for key, mkey in COUNTS:
        value = as_int(get(doc, "counts." + key))
        found = measured.get(mkey)
        if value is None:
            probs.append("counts.%s must be a whole number" % key)
        elif found is not None and found != value:
            probs.append("counts.%s says %d, your files say %d" % (key, value, found))
    rep.add("D12", "FAIL" if probs else "PASS", "; ".join(probs) if probs else "counts filled and match")

    # D13
    findings = get(doc, "review_findings")
    findings = [str(f) for f in findings if str(f).strip()] if isinstance(findings, list) else []
    weak = [f for f in findings if len(f) < 25 or not NAMES_SOMETHING.search(f)]
    ok = len(findings) >= 3 and not weak
    rep.add("D13", "PASS" if ok else "FAIL",
            "%d review findings" % len(findings) if ok
            else "review_findings needs 3 or more lines, each naming an F-rule, an AC, a B-test, INT or a file "
                 "(found %d, %d too thin)" % (len(findings), len(weak)))

    # D14
    missing = [k for k in HONESTY if get(doc, "honesty." + k) not in ("yes", "no")]
    rep.add("D14", "FAIL" if missing else "PASS",
            "must be yes or no: " + ", ".join(missing) if missing else "honesty block answered")
    return rep


# --------------------------------------------------------------------------- main


def print_human(rep, path):
    print("SIS #04 submission.yml - shape only, never quality   (%s)\n" % path)
    width = max(len(r["title"]) for r in rep.rows)
    for r in rep.rows:
        print(("%-6s %-4s %-*s  %s" % (r["verdict"], r["id"], width, r["title"], r["message"])).rstrip())
    c = rep.counts()
    print("-" * 78)
    print("SUMMARY pass=%d fail=%d error=%d   (%d checks)" % (c["PASS"], c["FAIL"], c["ERROR"], len(rep.rows)))


def main():
    parser = argparse.ArgumentParser(description="Validate sis-04/submission.yml")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--file", default="submission.yml")
    args = parser.parse_args()

    if args.file == "submission.yml" and not os.path.exists("submission.yml") and not os.path.isdir("tests"):
        msg = "run this from inside your sis-04/ folder:  cd sis-04 && python tests/validate_submission.py"
        print(json.dumps({"ok": False, "error": msg}) if args.json else "ERROR: " + msg)
        return 3
    if not os.path.exists(args.file):
        msg = "%s not found - copy it from SIS_04.zip" % args.file
        print(json.dumps({"ok": False, "error": msg}) if args.json else "ERROR: " + msg)
        return 2
    try:
        doc = parse(open(args.file, encoding="utf-8").read())
    except ParseError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}) if args.json else "ERROR: %s, %s" % (args.file, exc))
        return 2

    folder = os.path.dirname(os.path.abspath(args.file))
    rep = validate(doc, folder)

    def val(key):
        value = get(doc, key)
        return None if value is KeyError else value

    if args.json:
        print(json.dumps({
            "ok": rep.clean(),
            "counts": rep.counts(),
            "total": len(rep.rows),
            "rows": rep.rows,
            "declared": {
                "student_id": val("student.student_id"),
                "github": val("student.github"),
                "group": val("student.group"),
                "tool": val("assistant.tool"),
                "model": val("assistant.model"),
                "project": val("project"),
                "commit": val("checker.commit"),
                "checker": {k: as_int(val("checker." + k)) for k in ("pass", "fail", "error")},
                "known_fails": val("checker.known_fails"),
                "counts": val("counts"),
                "findings": val("review_findings"),
            },
        }, ensure_ascii=False, indent=2))
    else:
        print_human(rep, args.file)
    return 0 if rep.clean() else 1


if __name__ == "__main__":
    sys.exit(main())
