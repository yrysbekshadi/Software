#!/usr/bin/env python3
"""
check_requirements.py — 23 structural checks over week-03/requirements/.

    python tests/check_requirements.py          # from inside week-03/
    python tests/check_requirements.py --json   # machine-readable, for the grading pipeline

It checks SHAPE, never QUALITY. It cannot tell whether a user story is worth writing; it can
tell whether it has a role, a goal, a reason, a priority and an assumption, whether your IDs
resolve, and whether your diagram connects an actor to a function no person triggers.

A clean run is the floor, not the grade.

Verdicts:
    PASS   the check found what it was looking for
    FAIL   the artifact is there but the check did not pass
    ERROR  the artifact is missing or unreadable, so the check could not run

Exit codes: 0 = no FAIL and no ERROR · 1 = at least one FAIL or ERROR · 2 = wrong directory.
Standard library only.
"""

import argparse
import json
import os
import re
import sys

REQ = "requirements"
FILES = {
    "stories": os.path.join(REQ, "user-stories.md"),
    "criteria": os.path.join(REQ, "acceptance-criteria.md"),
    "diagram": os.path.join(REQ, "use-cases.puml"),
    "trace": os.path.join(REQ, "traceability.md"),
}

USE_CASES = [
    ("UC-01", "View availability"),
    ("UC-02", "Book room"),
    ("UC-03", "Cancel booking"),
    ("UC-04", "Block or unblock room"),
    ("UC-05", "Review usage"),
    ("UC-06", "Send confirmation"),
]
ACTORS = ("Student", "Administrator")

OUT_OF_SCOPE = [
    "payment", "pay for", "fee", "fine", "penalty", "refund",
    "check-in", "checkin", "qr code", "attendance",
    "maintenance", "cleaning", "repair",
    "sms", "push notification", "reminder",
    "sign up", "signup", "register an account", "password", "authentication",
    "waiting list", "waitlist", "queue",
]
FORBIDDEN_IN_DIAGRAM = [
    "database", "db", "screen", "page", "form", "button", "login", "log in",
    "sign in", "server", "api", "table", "class", "controller", "ui",
]
NEGATIVE_WORDS = [
    "not ", "cannot", "can't", "no ", "reject", "refus", "error", "invalid",
    "blocked", "past", "overlap", "exceed", "more than", "longer than",
    "already", "fail", "denied", "prevent", "unavailable",
]

RE_US = re.compile(r"\bUS-(\d{2})\b")
RE_AC = re.compile(r"\bAC-(\d{2})\b")
RE_UC = re.compile(r"\bUC-(\d{2})\b")
RE_STORY_SENTENCE = re.compile(
    r"as\s+an?\s+(.{2,40}?)\s*,\s*i\s+want\s+(.{3,}?)\s*,\s*so\s+that\s+(.{3,})",
    re.IGNORECASE | re.DOTALL,
)
RE_PRIORITY = re.compile(r"priority\s*:?\s*\**\s*(high|medium|low)", re.IGNORECASE)
RE_ASSUMPTION = re.compile(r"assumption\s*:?\s*\**\s*(.+)", re.IGNORECASE)
RE_TODO = re.compile(r"\bTODO\b|\bFIXME\b|<story title>|<your name>", re.IGNORECASE)


class Result:
    def __init__(self):
        self.rows = []

    def add(self, verdict, check_id, title, message):
        self.rows.append({
            "verdict": verdict, "id": check_id, "title": title, "message": message,
        })

    def ok(self, cid, title, message=""):
        self.add("PASS", cid, title, message)

    def fail(self, cid, title, message):
        self.add("FAIL", cid, title, message)

    def error(self, cid, title, message):
        self.add("ERROR", cid, title, message)

    def counts(self):
        out = {"PASS": 0, "FAIL": 0, "ERROR": 0}
        for row in self.rows:
            out[row["verdict"]] += 1
        return out


def read(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return None


def split_stories(text):
    """Return {id: block} for every US-nn heading in the file, in order."""
    marks = [(m.group(0), m.start()) for m in RE_US.finditer(text)]
    blocks, seen = {}, set()
    for i, (sid, start) in enumerate(marks):
        if sid in seen:
            continue
        seen.add(sid)
        end = marks[i + 1][1] if i + 1 < len(marks) else len(text)
        blocks[sid] = text[start:end]
    return blocks


def contains_any(haystack, needles):
    low = haystack.lower()
    return [n for n in needles if n in low]


# --------------------------------------------------------------- user stories (7)


def check_stories(res, text):
    title = "user-stories.md"
    if text is None:
        for cid in range(1, 8):
            res.error(f"US-{cid}", title, "requirements/user-stories.md is missing")
        return {}

    leftovers = RE_TODO.findall(text)
    if leftovers:
        res.fail("US-1", title, f"{len(leftovers)} TODO placeholder(s) left in the file")
    else:
        res.ok("US-1", title, "no placeholders left")

    stories = split_stories(text)
    ids = sorted(stories)
    if not 6 <= len(stories) <= 8:
        res.fail("US-2", title, f"{len(stories)} stories found, the task asks for 6 to 8")
    elif ids != [f"US-{i:02d}" for i in range(1, len(ids) + 1)]:
        res.fail("US-2", title, f"IDs are not sequential from US-01: {', '.join(ids)}")
    else:
        res.ok("US-2", title, f"{len(stories)} stories, IDs US-01…{ids[-1]}")

    bad = [sid for sid, block in stories.items() if not RE_STORY_SENTENCE.search(block)]
    if bad:
        res.fail("US-3", title, f"no 'As a …, I want …, so that …' sentence in: {', '.join(sorted(bad))}")
    elif stories:
        res.ok("US-3", title, "every story has the required sentence shape")
    else:
        res.fail("US-3", title, "no stories to check")

    bad = [sid for sid, block in stories.items() if not RE_PRIORITY.search(block)]
    if bad:
        res.fail("US-4", title, f"no High/Medium/Low priority in: {', '.join(sorted(bad))}")
    elif stories:
        res.ok("US-4", title, "every story has a priority")
    else:
        res.fail("US-4", title, "no stories to check")

    bad = []
    for sid, block in stories.items():
        match = RE_ASSUMPTION.search(block)
        if not match or len(match.group(1).strip().strip("*").strip()) < 10:
            bad.append(sid)
    if bad:
        res.fail("US-5", title, f"no assumption, or an empty one, in: {', '.join(sorted(bad))}")
    elif stories:
        res.ok("US-5", title, "every story declares an assumption")
    else:
        res.fail("US-5", title, "no stories to check")

    wrong_roles = {}
    for sid, block in stories.items():
        match = RE_STORY_SENTENCE.search(block)
        if not match:
            continue
        role = match.group(1).strip().strip("*[]").lower()
        if not any(actor.lower() in role for actor in ACTORS):
            wrong_roles[sid] = match.group(1).strip()
    if wrong_roles:
        res.fail(
            "US-6", title,
            "roles other than Student/Administrator: "
            + ", ".join(f"{k} ({v})" for k, v in sorted(wrong_roles.items())),
        )
    elif stories:
        res.ok("US-6", title, "only Student and Administrator appear as roles")
    else:
        res.fail("US-6", title, "no stories to check")

    found = contains_any(text, OUT_OF_SCOPE)
    if found:
        res.fail(
            "US-7", title,
            "out-of-scope vocabulary: " + ", ".join(sorted(set(found)))
            + " — either the assistant widened the scenario, or say why in lab-report.md",
        )
    else:
        res.ok("US-7", title, "nothing from the out-of-scope list appears")

    return stories


# ---------------------------------------------------------- acceptance criteria (7)


def check_criteria(res, text, story_ids):
    title = "acceptance-criteria.md"
    if text is None:
        for cid in range(1, 8):
            res.error(f"AC-{cid}", title, "requirements/acceptance-criteria.md is missing")
        return set()

    leftovers = RE_TODO.findall(text)
    if leftovers:
        res.fail("AC-1", title, f"{len(leftovers)} TODO placeholder(s) left in the file")
    else:
        res.ok("AC-1", title, "no placeholders left")

    # story blocks: every "## …US-nn…" heading starts one
    heads = [m for m in re.finditer(r"^#{1,4}\s*.*US-\d{2}.*$", text, re.MULTILINE)]
    blocks = []
    for i, head in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        blocks.append((RE_US.search(head.group(0)).group(0), text[head.start():end]))

    referenced = {sid for sid, _ in blocks}
    if len(blocks) != 3:
        res.fail("AC-2", title, f"{len(blocks)} story sections found, the task fixes this at 3")
    elif not referenced <= set(story_ids):
        missing = sorted(referenced - set(story_ids))
        res.fail("AC-2", title, f"these IDs do not exist in user-stories.md: {', '.join(missing)}")
    else:
        res.ok("AC-2", title, "three sections, all naming real stories: " + ", ".join(sorted(referenced)))

    all_ac = RE_AC.findall(text)
    dupes = {a for a in all_ac if all_ac.count(a) > 1}
    per_block = {sid: set(RE_AC.findall(body)) for sid, body in blocks}
    bad_counts = {sid: len(ids) for sid, ids in per_block.items() if not 3 <= len(ids) <= 5}
    if dupes:
        res.fail("AC-3", title, f"duplicate criterion IDs: AC-{', AC-'.join(sorted(dupes))}")
    elif bad_counts:
        res.fail(
            "AC-3", title,
            "3 to 5 criteria per story required — "
            + ", ".join(f"{k}: {v}" for k, v in sorted(bad_counts.items())),
        )
    elif per_block:
        res.ok("AC-3", title, "every section has 3 to 5 uniquely numbered criteria")
    else:
        res.fail("AC-3", title, "no criteria found")

    criteria = re.split(r"^#{1,6}\s*AC-\d{2}.*$|^\s*\*{0,2}AC-\d{2}\*{0,2}\s*[:.]", text, flags=re.MULTILINE)[1:]
    incomplete = 0
    for body in criteria:
        low = body.lower()
        if not ("given" in low and "when" in low and "then" in low):
            incomplete += 1
    if not criteria:
        res.fail("AC-4", title, "no AC-nn criteria found to check")
    elif incomplete:
        res.fail("AC-4", title, f"{incomplete} criterion/criteria missing a Given, a When or a Then")
    else:
        res.ok("AC-4", title, f"all {len(criteria)} criteria are complete Given/When/Then")

    happy_only = [sid for sid, body in blocks if not contains_any(body, NEGATIVE_WORDS)]
    if not blocks:
        res.fail("AC-5", title, "no story sections to check")
    elif happy_only:
        res.fail(
            "AC-5", title,
            "no validation, error or boundary case in: " + ", ".join(sorted(happy_only)),
        )
    else:
        res.ok("AC-5", title, "every section covers an invalid or boundary case")

    head = text[:heads[0].start()] if heads else text
    assumption_lines = [
        line.strip(" -*\t") for line in head.splitlines()
        if line.strip().startswith(("-", "*")) and len(line.strip()) > 12
    ]
    if "assumption" not in head.lower():
        res.fail("AC-6", title, "no Assumptions section before the criteria")
    elif len(assumption_lines) < 2:
        res.fail("AC-6", title, f"the Assumptions section lists {len(assumption_lines)} item(s)")
    else:
        res.ok("AC-6", title, f"{len(assumption_lines)} assumptions listed before the criteria")

    low_head = head.lower()
    overlap_settled = ("overlap" in low_head or "touch" in low_head or "ends exactly" in low_head)
    duration_settled = ("two hour" in low_head or "2 hour" in low_head or "duration" in low_head)
    if overlap_settled and duration_settled:
        res.ok("AC-7", title, "both open questions are settled in the assumptions")
    else:
        unsettled = []
        if not overlap_settled:
            unsettled.append("the overlap question (R3)")
        if not duration_settled:
            unsettled.append("the two-hour question (R2)")
        res.fail(
            "AC-7", title,
            "the assumptions do not settle " + " and ".join(unsettled)
            + " — either answer is accepted, no answer is not",
        )

    return set(RE_AC.findall(text))


# ------------------------------------------------------------------- diagram (6)


def check_diagram(res, text):
    title = "use-cases.puml"
    if text is None:
        for cid in range(1, 7):
            res.error(f"PU-{cid}", title, "requirements/use-cases.puml is missing")
        return

    leftovers = RE_TODO.findall(text)
    if leftovers:
        res.fail("PU-1", title, f"{len(leftovers)} TODO placeholder(s) left in the file")
    elif "@startuml" not in text or "@enduml" not in text:
        res.fail("PU-1", title, "no @startuml/@enduml block — paste the PlantUML source, not the image")
    else:
        res.ok("PU-1", title, "valid PlantUML block, no placeholders")

    declared = re.findall(r"^\s*actor\s+:?\"?([A-Za-z0-9 _]+)\"?:?", text, re.MULTILINE)
    names = {d.strip() for d in declared}
    extra = {n for n in names if n not in ACTORS}
    if not {"Student", "Administrator"} <= names:
        res.fail("PU-2", title, f"actors found: {sorted(names) or 'none'} — both Student and Administrator are required")
    elif extra:
        res.fail("PU-2", title, f"extra actor(s) outside the scenario: {', '.join(sorted(extra))}")
    else:
        res.ok("PU-2", title, "exactly two actors: Student, Administrator")

    low = text.lower()
    missing = [name for _, name in USE_CASES if name.lower() not in low]
    if missing:
        res.fail("PU-3", title, "use case(s) missing: " + ", ".join(missing))
    else:
        res.ok("PU-3", title, "all six use cases present")

    if re.search(r"^\s*(rectangle|package)\b.*\{", text, re.MULTILINE):
        res.ok("PU-4", title, "system boundary present")
    else:
        res.fail("PU-4", title, "no rectangle/package boundary — the actors must sit outside a boundary")

    body = "\n".join(
        line for line in text.splitlines() if not line.strip().startswith("'")
    )
    found = []
    for term in FORBIDDEN_IN_DIAGRAM:
        if re.search(rf"\b{re.escape(term)}\b", body, re.IGNORECASE):
            found.append(term)
    if found:
        res.fail("PU-5", title, "screens/databases/internals in the diagram: " + ", ".join(sorted(set(found))))
    else:
        res.ok("PU-5", title, "no screens, databases or internal components")

    aliases = {}
    for match in re.finditer(r"usecase\s+\"([^\"]+)\"\s+as\s+(\w+)", text):
        aliases[match.group(2)] = match.group(1)
    for match in re.finditer(r"\((.+?)\)\s+as\s+(\w+)", text):
        aliases[match.group(2)] = match.group(1)

    def resolve(token):
        token = token.strip().strip('"').strip()
        if token.startswith("(") and token.endswith(")"):
            token = token[1:-1].strip()
        return aliases.get(token, token)

    problems = []
    for line in body.splitlines():
        arrow = re.search(r"^(.*?)\s*(<?-{1,2}(?:up|down|left|right)?-?>?)\s*(.*?)\s*$", line.strip())
        if not arrow or "-" not in arrow.group(2):
            continue
        left, right = resolve(arrow.group(1)), resolve(arrow.group(3))
        if not left or not right:
            continue
        pair = {left, right}
        actor = pair & set(ACTORS)
        if not actor:
            continue
        target = (pair - set(ACTORS)).pop() if len(pair - set(ACTORS)) == 1 else None
        if not target:
            continue
        actor = actor.pop()
        if target.lower() == "send confirmation":
            problems.append(f"{actor} → Send confirmation (no person triggers it; the system does)")
        if actor == "Student" and target.lower() in ("review usage", "block or unblock room"):
            problems.append(f"Student → {target} (that is the Administrator's responsibility)")
    if problems:
        res.fail("PU-6", title, "; ".join(sorted(set(problems))))
    else:
        res.ok("PU-6", title, "no unjustified actor associations found")


# -------------------------------------------------------------- traceability (3)


def check_trace(res, text, story_ids, criteria_ids):
    title = "traceability.md"
    if text is None:
        for cid in range(1, 4):
            res.error(f"TR-{cid}", title, "requirements/traceability.md is missing")
        return

    leftovers = RE_TODO.findall(text)
    rows = [line for line in text.splitlines() if line.strip().startswith("|") and RE_UC.search(line)]
    covered_ucs = {RE_UC.search(row).group(0) for row in rows}
    expected = {uid for uid, _ in USE_CASES}
    if leftovers:
        res.fail("TR-1", title, f"{len(leftovers)} TODO placeholder(s) left in the table")
    elif covered_ucs != expected:
        res.fail("TR-1", title, f"table rows for: {', '.join(sorted(expected - covered_ucs))} are missing")
    else:
        res.ok("TR-1", title, "all six use cases have a row")

    used_us = set(RE_US.findall(text))
    used_ac = set(RE_AC.findall(text))
    dangling_us = sorted(f"US-{n}" for n in used_us if f"US-{n}" not in story_ids)
    dangling_ac = sorted(f"AC-{n}" for n in used_ac if f"AC-{n}" not in criteria_ids)
    if dangling_us or dangling_ac:
        res.fail(
            "TR-2", title,
            "IDs that exist nowhere else: " + ", ".join(dangling_us + dangling_ac),
        )
    else:
        res.ok("TR-2", title, "every ID in the table resolves")

    unlisted = sorted(sid for sid in story_ids if sid not in {f"US-{n}" for n in used_us})
    if not story_ids:
        res.fail("TR-3", title, "no stories to trace")
    elif unlisted:
        res.fail(
            "TR-3", title,
            "stories that appear nowhere in the table: " + ", ".join(unlisted)
            + " — list them under 'Stories that belong to no use case' if that is the finding",
        )
    else:
        res.ok("TR-3", title, "every story appears in the table")


# ------------------------------------------------------------------------ main


def run():
    res = Result()
    texts = {key: read(path) for key, path in FILES.items()}
    stories = check_stories(res, texts["stories"])
    criteria_ids = check_criteria(res, texts["criteria"], set(stories))
    criteria_ids = {f"AC-{n}" for n in criteria_ids}
    check_diagram(res, texts["diagram"])
    check_trace(res, texts["trace"], set(stories), criteria_ids)
    return res


def main():
    parser = argparse.ArgumentParser(description="23 structural checks over week-03/requirements/")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not os.path.isdir(REQ):
        message = ("requirements/ not found — run this from inside week-03/: "
                   "cd week-03 && python tests/check_requirements.py")
        print(json.dumps({"ok": False, "reason": "wrong-directory"}) if args.json else "ERROR  " + message)
        return 2

    res = run()
    counts = res.counts()

    if args.json:
        print(json.dumps({"ok": counts["FAIL"] == 0 and counts["ERROR"] == 0,
                          "counts": counts, "rows": res.rows}, ensure_ascii=False, indent=2))
    else:
        width = max(len(r["title"]) for r in res.rows)
        for row in res.rows:
            line = f"{row['verdict']:<6} {row['id']:<5} {row['title']:<{width}}  {row['message']}"
            print(line.rstrip())
        print("-" * 72)
        print(f"{counts['PASS']} PASS · {counts['FAIL']} FAIL · {counts['ERROR']} ERROR   "
              f"({len(res.rows)} checks)")
        if counts["FAIL"] or counts["ERROR"]:
            print("Every FAIL goes in lab-report.md section 9 with what you decided about it.")
            print("A FAIL you report and explain costs you nothing. One you hide costs the criterion.")
        else:
            print("Shape is clean. This says nothing about whether the requirements are good.")

    return 0 if counts["FAIL"] == 0 and counts["ERROR"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
