#!/usr/bin/env python3
"""
validate_submission.py — checks the shape of week-03/submission.yml.

    python tests/validate_submission.py                # from inside week-03/
    python tests/validate_submission.py --json         # machine-readable, for the grading pipeline
    python tests/validate_submission.py --file path/to/submission.yml

It checks SHAPE, never QUALITY. A green run means the file can be read and graded,
not that the work is good.

Verdicts, same vocabulary as check_requirements.py:
    PASS   the field is present and well-formed
    FAIL   the field is present but wrong
    ERROR  the file is missing, unreadable, or the field is absent entirely

Exit codes: 0 = no FAIL and no ERROR · 1 = at least one FAIL or ERROR · 2 = file
missing or unparseable · 3 = wrong working directory.

Standard library only. No pip install, no YAML package: this file understands the
restricted subset of YAML that submission.yml uses, and refuses anything else with a
line number.
"""

import argparse
import json
import os
import re
import sys

# The number of checks tests/check_requirements.py runs. The three numbers a student
# reports under `checker:` must add up to this. CONFIRM AGAINST THE SHIPPED CHECKER
# BEFORE RELEASING — if that file changes, change this constant with it.
TOTAL_CHECKS = 23

USER_STORY_MIN, USER_STORY_MAX = 6, 8
REQUIRED_CRITERIA_SETS = 3

ID_TOKEN = re.compile(r"\b(?:US|AC|UC)-\d{2}\b")
UC_ID = re.compile(r"^UC-\d{2}$")
US_ID = re.compile(r"^US-\d{2}$")
STUDENT_ID = re.compile(r"^\d{2}[A-Za-z]\d{6}$")
GITHUB_LOGIN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38}$")
SHORT_SHA = re.compile(r"^[0-9a-fA-F]{7,40}$")
HAS_VERSION = re.compile(r"[0-9]")
PLACEHOLDER = re.compile(
    r"(^<.*>$)|(\bTODO\b)|(\bFIXME\b)|(\byour name\b)|(\bfill in\b)|(^\.\.\.$)",
    re.IGNORECASE,
)

BARE_TOOL_NAMES = {
    "chatgpt", "gpt", "claude", "gemini", "copilot", "github copilot",
    "deepseek", "grok", "mistral", "llama", "qwen", "perplexity", "cursor",
}

YES_NO = {"yes", "no"}
ALLOWED_DECISION = {"allowed", "not-allowed"}


# --------------------------------------------------------------------------- parsing


class ParseError(Exception):
    pass


def parse_restricted_yaml(text):
    """Parse the subset used by submission.yml.

    Supported, and nothing else:
        key: value                      at column 0
        key:                            at column 0, followed by an indented block of
          subkey: value                 two-space `subkey: value` lines
        key:                            or an indented block of `- item` lines
          - item
        key: []                         an explicitly empty list
    Comments start with # . Tabs are refused.
    """
    root = {}
    current_key = None
    current_kind = None  # "map" | "list"
    lines = text.splitlines()

    for n, raw in enumerate(lines, start=1):
        if "\t" in raw:
            raise ParseError(f"line {n}: tab character — use spaces, two per level")

        line = raw.split("#", 1)[0].rstrip() if not _in_quotes_hash(raw) else raw.rstrip()
        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip(" "))
        body = line.strip()

        if indent == 0:
            if body.startswith("- "):
                raise ParseError(f"line {n}: list item at column 0, outside any key")
            if ":" not in body:
                raise ParseError(f"line {n}: expected `key:` or `key: value`, got {body!r}")
            key, _, value = body.partition(":")
            key, value = key.strip(), value.strip()
            if not key:
                raise ParseError(f"line {n}: empty key")
            if key in root:
                raise ParseError(f"line {n}: duplicate key {key!r}")
            if value == "[]":
                root[key] = []
                current_key, current_kind = None, None
            elif value == "":
                root[key] = None  # resolved by the block below it, if any
                current_key, current_kind = key, None
            else:
                root[key] = _scalar(value)
                current_key, current_kind = None, None
            continue

        if current_key is None:
            raise ParseError(f"line {n}: indented line does not belong to any key")
        if indent != 2:
            raise ParseError(f"line {n}: indent is {indent}, expected exactly 2")

        if body.startswith("-"):
            item = body[1:].strip()
            if current_kind is None:
                root[current_key], current_kind = [], "list"
            elif current_kind != "list":
                raise ParseError(f"line {n}: list item inside a block of `key: value` lines")
            root[current_key].append(_scalar(item) if item else None)
        else:
            if ":" not in body:
                raise ParseError(f"line {n}: expected `key: value`, got {body!r}")
            key, _, value = body.partition(":")
            key, value = key.strip(), value.strip()
            if current_kind is None:
                root[current_key], current_kind = {}, "map"
            elif current_kind != "map":
                raise ParseError(f"line {n}: `key: value` inside a list block")
            if key in root[current_key]:
                raise ParseError(f"line {n}: duplicate key {key!r}")
            root[current_key][key] = [] if value == "[]" else _scalar(value)

    return root


def _in_quotes_hash(raw):
    """True when a # appears inside quotes and must not start a comment."""
    idx = raw.find("#")
    if idx == -1:
        return False
    before = raw[:idx]
    return before.count('"') % 2 == 1 or before.count("'") % 2 == 1


def _scalar(value):
    if value == "":
        return None
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [] if not inner else [p.strip().strip("\"'") for p in inner.split(",")]
    return value


# --------------------------------------------------------------------------- checks


class Report:
    def __init__(self):
        self.rows = []

    def add(self, verdict, field, message):
        self.rows.append({"verdict": verdict, "field": field, "message": message})

    def ok(self, field, message="present and well-formed"):
        self.add("PASS", field, message)

    def fail(self, field, message):
        self.add("FAIL", field, message)

    def error(self, field, message):
        self.add("ERROR", field, message)

    def note(self, field, message):
        self.add("NOTE", field, message)

    def counts(self):
        out = {"PASS": 0, "FAIL": 0, "ERROR": 0, "NOTE": 0}
        for row in self.rows:
            out[row["verdict"]] += 1
        return out

    def clean(self):
        c = self.counts()
        return c["FAIL"] == 0 and c["ERROR"] == 0


def get(doc, path):
    """get(doc, 'student.github') -> value or None."""
    node = doc
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def missing(value):
    return value is None or (isinstance(value, str) and not value.strip())


def looks_like_placeholder(value):
    return isinstance(value, str) and bool(PLACEHOLDER.search(value.strip()))


def as_int(value):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def require_text(rep, doc, path, extra=None):
    value = get(doc, path)
    if value is None and not _key_exists(doc, path):
        rep.error(path, "field is absent from the file")
        return None
    if missing(value):
        rep.fail(path, "left empty")
        return None
    if looks_like_placeholder(value):
        rep.fail(path, f"still a placeholder: {value!r}")
        return None
    if extra:
        problem = extra(value)
        if problem:
            rep.fail(path, problem)
            return None
    rep.ok(path, str(value))
    return value


def _key_exists(doc, path):
    node = doc
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return False
        node = node[part]
    return True


def validate(doc):
    rep = Report()

    # 1. identity of the file itself
    if as_int(get(doc, "schema")) != 1:
        rep.fail("schema", "must be 1 — do not edit this line")
    else:
        rep.ok("schema", "1")

    week = get(doc, "week")
    if str(week) != "03":
        rep.fail("week", f"must be \"03\", got {week!r}")
    else:
        rep.ok("week", "03")

    # 2. student
    require_text(rep, doc, "student.name")
    require_text(
        rep, doc, "student.student_id",
        lambda v: None if STUDENT_ID.match(str(v)) else
        f"does not look like a KBTU student ID (expected e.g. 24B031016), got {v!r}",
    )
    require_text(
        rep, doc, "student.github",
        lambda v: None if GITHUB_LOGIN.match(str(v)) else
        f"not a GitHub username — give the username only, not a URL: {v!r}",
    )

    # 3. assistant
    require_text(rep, doc, "assistant.tool")
    require_text(
        rep, doc, "assistant.model",
        lambda v: (
            "a tool name is not a model name — give the exact model with its version"
            if str(v).strip().lower() in BARE_TOOL_NAMES or not HAS_VERSION.search(str(v))
            else None
        ),
    )

    # 4. counts
    stories = as_int(get(doc, "counts.user_stories"))
    if stories is None:
        if not _key_exists(doc, "counts.user_stories"):
            rep.error("counts.user_stories", "field is absent from the file")
        elif missing(get(doc, "counts.user_stories")):
            rep.fail("counts.user_stories", "left empty")
        else:
            rep.fail("counts.user_stories", "not a number")
    elif not (USER_STORY_MIN <= stories <= USER_STORY_MAX):
        rep.fail(
            "counts.user_stories",
            f"the task asks for {USER_STORY_MIN}-{USER_STORY_MAX} stories, you declared {stories} — "
            "if you deliberately kept a different number, say why in lab-report.md",
        )
    else:
        rep.ok("counts.user_stories", str(stories))

    sets = as_int(get(doc, "counts.acceptance_criteria_sets"))
    if sets is None:
        if not _key_exists(doc, "counts.acceptance_criteria_sets"):
            rep.error("counts.acceptance_criteria_sets", "field is absent from the file")
        else:
            rep.fail("counts.acceptance_criteria_sets", "left empty or not a number")
    elif sets != REQUIRED_CRITERIA_SETS:
        rep.fail(
            "counts.acceptance_criteria_sets",
            f"the task fixes this at {REQUIRED_CRITERIA_SETS}, you declared {sets}",
        )
    else:
        rep.ok("counts.acceptance_criteria_sets", str(sets))

    # 5. checker numbers — reported, then re-run by the instructor at your commit
    nums = {}
    for name in ("pass", "fail", "error"):
        value = as_int(get(doc, f"checker.{name}"))
        if value is None:
            if not _key_exists(doc, f"checker.{name}"):
                rep.error(f"checker.{name}", "field is absent from the file")
            else:
                rep.fail(f"checker.{name}", "left empty — run the checker and report the result")
        elif value < 0:
            rep.fail(f"checker.{name}", "negative")
        else:
            nums[name] = value
    if len(nums) == 3:
        total = sum(nums.values())
        if total != TOTAL_CHECKS:
            rep.fail(
                "checker",
                f"{nums['pass']} + {nums['fail']} + {nums['error']} = {total}, "
                f"but check_requirements.py runs {TOTAL_CHECKS} checks — report the run as it happened",
            )
        else:
            rep.ok("checker", f"{nums['pass']} PASS · {nums['fail']} FAIL · {nums['error']} ERROR")
            if nums["fail"] == 0 and nums["error"] == 0:
                rep.note(
                    "checker",
                    "you are claiming a clean run — it will be re-run at your commit, so make sure it is true",
                )

    require_text(
        rep, doc, "checker.commit",
        lambda v: None if SHORT_SHA.match(str(v)) else
        f"not a commit hash — use `git rev-parse --short HEAD`, got {v!r}",
    )

    # 6. the two ambiguities the scenario deliberately leaves open
    for field in ("overlap_touching_bookings", "exactly_two_hours"):
        path = f"assumptions.{field}"
        value = get(doc, path)
        if not _key_exists(doc, path):
            rep.error(path, "field is absent from the file")
        elif missing(value):
            rep.fail(path, "not decided — either answer is accepted, no answer is not")
        elif str(value).strip().lower() not in ALLOWED_DECISION:
            rep.fail(path, f"must be one of {sorted(ALLOWED_DECISION)}, got {value!r}")
        else:
            rep.ok(path, str(value))

    # 7. traceability
    for path, pattern, label in (
        ("traceability.use_cases_not_covered", UC_ID, "UC-nn"),
        ("traceability.stories_not_traced", US_ID, "US-nn"),
    ):
        value = get(doc, path)
        if not _key_exists(doc, path):
            rep.error(path, "field is absent — an empty list [] is a valid answer, a missing key is not")
            continue
        if value is None:
            value = []
        if not isinstance(value, list):
            rep.fail(path, f"must be a list, e.g. [{label.replace('nn', '05')}]")
            continue
        bad = [item for item in value if not pattern.match(str(item).strip())]
        if bad:
            rep.fail(path, f"these are not {label} IDs: {bad}")
        else:
            rep.ok(path, "[]" if not value else ", ".join(str(v) for v in value))

    both_empty = not get(doc, "traceability.use_cases_not_covered") and \
        not get(doc, "traceability.stories_not_traced")
    if both_empty:
        rep.note(
            "traceability",
            "you are claiming full coverage in both directions — that is rare on a first pass, "
            "and it is checked",
        )

    # 8. review findings — specificity is enforced mechanically, quality is not
    findings = get(doc, "review_findings")
    if not _key_exists(doc, "review_findings"):
        rep.error("review_findings", "field is absent from the file")
    else:
        items = [str(f).strip() for f in (findings or []) if f is not None and str(f).strip()]
        if len(items) < 3:
            rep.fail("review_findings", f"three or more required, found {len(items)}")
        else:
            rep.ok("review_findings", f"{len(items)} findings")
        for i, item in enumerate(items, start=1):
            path = f"review_findings[{i}]"
            if looks_like_placeholder(item):
                rep.fail(path, f"still a placeholder: {item!r}")
            elif len(item) < 40:
                rep.fail(path, f"too short to be a finding ({len(item)} chars) — say what, where, and why")
            elif not ID_TOKEN.search(item):
                rep.fail(path, "names no ID — a finding points at a US-nn, AC-nn or UC-nn")
            else:
                rep.ok(path, item[:60] + ("…" if len(item) > 60 else ""))

    # 9. honesty — an honest "no" is never a failure here
    explain = get(doc, "honesty.can_explain_everything_submitted")
    if not _key_exists(doc, "honesty.can_explain_everything_submitted"):
        rep.error("honesty.can_explain_everything_submitted", "field is absent from the file")
    elif missing(explain) or str(explain).strip().lower() not in YES_NO:
        rep.fail("honesty.can_explain_everything_submitted", "answer yes or no")
    else:
        rep.ok("honesty.can_explain_everything_submitted", str(explain))
        if str(explain).strip().lower() == "no":
            rep.note(
                "honesty.can_explain_everything_submitted",
                "an honest no costs you nothing here — name the part in lab-report.md",
            )

    disclosed = get(doc, "honesty.ai_usage_disclosed")
    if not _key_exists(doc, "honesty.ai_usage_disclosed"):
        rep.error("honesty.ai_usage_disclosed", "field is absent from the file")
    elif missing(disclosed) or str(disclosed).strip().lower() not in YES_NO:
        rep.fail("honesty.ai_usage_disclosed", "answer yes or no")
    elif str(disclosed).strip().lower() == "no":
        rep.fail(
            "honesty.ai_usage_disclosed",
            "AI_USAGE.md is required every week — fill it in, then set this to yes",
        )
    else:
        rep.ok("honesty.ai_usage_disclosed", "yes")

    return rep


# --------------------------------------------------------------------------- output


def print_human(rep, path):
    print(f"submission.yml — {path}")
    print("-" * 72)
    width = max(len(r["field"]) for r in rep.rows) if rep.rows else 10
    for row in rep.rows:
        print(f"{row['verdict']:<6} {row['field']:<{width}}  {row['message']}")
    print("-" * 72)
    c = rep.counts()
    print(f"{c['PASS']} PASS · {c['FAIL']} FAIL · {c['ERROR']} ERROR · {c['NOTE']} note")
    if rep.clean():
        print("Shape is fine. This says nothing about whether the work is good.")
    else:
        print("Fix the FAIL and ERROR lines above, then run this again before you push.")


def main():
    parser = argparse.ArgumentParser(description="Validate week-03/submission.yml")
    parser.add_argument("--file", default="submission.yml", help="path to submission.yml")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    path = args.file
    if not os.path.exists(path):
        message = (
            f"{path} not found. Run this from inside week-03/, or pass --file. "
            "The file ships with the lab — do not rename it."
        )
        if args.json:
            print(json.dumps({"ok": False, "reason": "missing", "message": message}))
        else:
            print("ERROR  " + message)
        return 2

    with open(path, encoding="utf-8") as handle:
        text = handle.read()

    try:
        doc = parse_restricted_yaml(text)
    except ParseError as exc:
        message = f"{path} cannot be parsed — {exc}"
        if args.json:
            print(json.dumps({"ok": False, "reason": "unparseable", "message": message}))
        else:
            print("ERROR  " + message)
            print("       Keep the shape the template ships with: two-space indents, no tabs.")
        return 2

    rep = validate(doc)

    if args.json:
        print(json.dumps({
            "ok": rep.clean(),
            "counts": rep.counts(),
            "rows": rep.rows,
            "declared": {
                "student_id": get(doc, "student.student_id"),
                "github": get(doc, "student.github"),
                "tool": get(doc, "assistant.tool"),
                "model": get(doc, "assistant.model"),
                "commit": get(doc, "checker.commit"),
                "checker": {
                    "pass": as_int(get(doc, "checker.pass")),
                    "fail": as_int(get(doc, "checker.fail")),
                    "error": as_int(get(doc, "checker.error")),
                },
                "assumptions": get(doc, "assumptions"),
                "traceability": get(doc, "traceability"),
                "findings": get(doc, "review_findings"),
            },
        }, ensure_ascii=False, indent=2))
    else:
        print_human(rep, path)

    return 0 if rep.clean() else 1


if __name__ == "__main__":
    sys.exit(main())
