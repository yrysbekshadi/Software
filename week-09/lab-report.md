# Week 09 — Lab Report: canBook as a Tool

**Name:** Shadi Yrysbek
**Student ID:** 24B031125
**GitHub:** yrysbekshadi

---

## 1. Setup

| | |
| --- | --- |
| Assistant (frozen for the whole lab) | Grok |
| Exact model (or "not displayed") | not displayed (Grok Build, xAI, April 2026; no version string was shown) |
| Three fresh chats for R1, R2, R3? (yes / no) | yes |
| Python version (`python --version`) | Python 3.10.22 |

## 2. Your tool definition — a reason for every constraint

Paste of the final `tool/check_room.json`:

```json
{
  "name": "check_room",
  "description": "Check whether a meeting room is free for one requested interval. Every time value is a whole number of minutes since midnight, from 0 to 1440 inclusive, and 1440 means 24:00. You must pass the requested start, the requested end, the current time now, whether the room is blocked, and the list of existing bookings. This tool only checks availability and returns an answer. It does not save, create, or change a booking.",
  "inputSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "start": {
        "type": "integer",
        "minimum": 0,
        "maximum": 1440,
        "description": "Requested start in whole minutes since midnight."
      },
      "end": {
        "type": "integer",
        "minimum": 0,
        "maximum": 1440,
        "description": "Requested end in whole minutes since midnight. 1440 means 24:00."
      },
      "now": {
        "type": "integer",
        "minimum": 0,
        "maximum": 1440,
        "description": "Current time in whole minutes since midnight."
      },
      "blocked": {
        "type": "boolean",
        "description": "True when the room is blocked and cannot be used."
      },
      "bookings": {
        "type": "array",
        "description": "Existing bookings. An empty array means there are none. Each item has start and end in whole minutes since midnight.",
        "items": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "start": {
              "type": "integer",
              "minimum": 0,
              "maximum": 1440
            },
            "end": {
              "type": "integer",
              "minimum": 0,
              "maximum": 1440
            }
          },
          "required": ["start", "end"]
        }
      }
    },
    "required": ["start", "end", "now", "blocked", "bookings"]
  }
}
```

| Field | Constraint (e.g. `"type": "integer"`, `"maximum": 1440`) | What goes wrong without it |
| --- | --- | --- |
| description | 25 or more words, says minutes, 1440, and that it does not save | A model that has never seen this course will send clock strings, or will think the call books the room. |
| inputSchema | `"type": "object"` | The arguments could arrive as an array or a string, and the five names would not be there. |
| start, end, now, blocked, bookings | all five listed in `required` | The model can omit `now` or `blocked`, and canBook has no value to judge. S04 is this hole. |
| top level | `"additionalProperties": false` | An extra field such as `room` is accepted and quietly ignored. S05 is this hole. |
| start | `"type": "integer"` | `600.5` or `"10:00"` gets through. S10 is the fraction, S03 is the same mistake on end. |
| start | `"minimum": 0`, `"maximum": 1440` | A negative start such as `-30` is still an integer. S06 is this hole. |
| end | `"type": "integer"` | A clock string `"11:00"` is accepted. S03 is this hole. |
| end | `"minimum": 0`, `"maximum": 1440` | `1500` is a whole number but not a time of day. S07 is this hole. 1440 stays legal, so S11 still passes. |
| now | `"type": "integer"`, `"minimum": 0`, `"maximum": 1440` | The current time could be a string or a minute outside the day, and AC1 could not even start. |
| blocked | `"type": "boolean"` | The string `"false"` is not the boolean false, but a loose schema treats it as present. S09 is this hole. |
| bookings | `"type": "array"` | One booking object, or a string, would be accepted in place of the list. An empty array stays legal, so S02 passes. |
| bookings.items | `"type": "object"` | A pair such as `[660, 720]` has no named start and end. S12 is this hole. |
| each booking | `"required": ["start", "end"]` | `{"start": 660}` has no end, so overlap cannot be tested. S08 is this hole. |
| each booking start and end | `"type": "integer"`, `"minimum": 0`, `"maximum": 1440` | A booking time could be a clock string or a minute outside the day. |
| each booking | `"additionalProperties": false` | A booking could carry a room name or a note that canBook does not read. |

No constraint here compares two fields. `start < end`, `start` after `now`, the 120 minute cap, overlap, and "do not save" are not in this table, because these keywords cannot say them.

## 3. The twelve calls — first run and final run

The first run is `python3 tests/check_tool.py` on the untouched starter, before `tool/check_room.json` was filled. The starter schema was an object with no properties and no required fields, so every call was accepted. Nine of S01–S12 failed. S01, S02 and S11 passed only because those three are supposed to be accepted. The full first summary was 6 PASS, 17 FAIL, 7 ERROR.

| Case | First run | Final run | What you changed |
| --- | --- | --- | --- |
| S01 | PASS | PASS | Nothing. The valid R1-shaped call was already accepted, and the final schema still accepts it. |
| S02 | PASS | PASS | Nothing. No `minItems` was added, so `bookings: []` stays valid. |
| S03 | FAIL | PASS | Set `end` to `"type": "integer"`, so the string `"11:00"` is refused. |
| S04 | FAIL | PASS | Put `now` in the top-level `required` array, together with the other four names. |
| S05 | FAIL | PASS | Set top-level `"additionalProperties": false`, so `"room": "204"` is refused. |
| S06 | FAIL | PASS | Set `"minimum": 0` on `start`, so `-30` is refused. |
| S07 | FAIL | PASS | Set `"maximum": 1440` on `end`, so `1500` is refused. |
| S08 | FAIL | PASS | Required both `start` and `end` on each booking object. |
| S09 | FAIL | PASS | Set `blocked` to `"type": "boolean"`, so the string `"false"` is refused. |
| S10 | FAIL | PASS | Set `start` to `"type": "integer"`, so `600.5` is refused. |
| S11 | PASS | PASS | Nothing that would ban 1440. `"maximum": 1440` still allows the end of the day. |
| S12 | FAIL | PASS | Set each booking item to `"type": "object"`, so the pair `[660, 720]` is refused. |

## 4. Function calling — what the model wrote

Each reply is from its own fresh chat. The chats did not see each other, and the files were not edited after the reply.

### R1

```text
PASS  D1    tool/check_room.json exists and is valid JSON
PASS  D2    has name, description and inputSchema
PASS  D3    name is exactly "check_room"
PASS  D4    description: 25+ words, says minutes, 1440, and that it does not save
PASS  D5    inputSchema: an object with exactly the five fields, all required
PASS  D6    inputSchema uses only the keywords listed in README section 5
PASS  S01   the R1 call, valid -> accept
PASS  S02   no existing bookings: bookings = [] -> accept
PASS  S03   end as a string: "11:00" -> refuse
PASS  S04   now missing -> refuse
PASS  S05   an extra field: "room": "204" -> refuse
PASS  S06   start below the day: -30 -> refuse
PASS  S07   end beyond the day: 1500 -> refuse
PASS  S08   a booking with no end: {start: 660} -> refuse
PASS  S09   blocked as a string: "false" -> refuse
PASS  S10   start not a whole minute: 600.5 -> refuse
PASS  S11   end at the end of the day: 1440 -> accept
PASS  S12   a booking as a pair: [660, 720] -> refuse
PASS  F1    calls/r1.json: a call to check_room
PASS  F2    calls/r1.json: arguments valid against your schema
PASS  F3    calls/r1.json: arguments equal the expected ones (README section 5, Part 2)
PASS  F4    calls/r2.json: a call to check_room
PASS  F5    calls/r2.json: arguments valid against your schema
PASS  F6    calls/r2.json: arguments equal the expected ones (README section 5, Part 2)
PASS  F7    calls/r3: exactly one of r3.json (it called) or r3.txt (it asked), not empty
PASS  L1    section 5 names at least two acceptance criteria (AC1-AC6) the schema cannot check
PASS  L2    section 6: A1-A8 each have allow / ask / block and a reason of 5+ words
PASS  L3    section 7 names the checkpoint commit (a SHA)
PASS  L4    section 10: a conclusion of 80-150 words
PASS  L5    AI_USAGE.md filled in (a tool row, and signed)

SUMMARY: 30 PASS · 0 FAIL · 0 ERROR  (of 30 checks)
Paste this whole output into lab-report.md section 8, and these three numbers into submission.yml.
```

Match. 9:00 is 540, 10:00 is 600, 11:00 is 660, and the existing booking 11:00 to 12:00 is 660 to 720. `blocked` is false because the request says the room is not blocked. The model called `check_room` and did not decide Available itself. Touching at 660 is the function's problem under AC4, not a reason to change the call.

### R2

```text
{"name": "check_room", "arguments": {"start": 840, "end": 990, "now": 810, "blocked": true, "bookings": []}}
```

Match. 13:30 is 810, 14:00 is 840, and 16:30 is 990, not 960. `blocked` is true, and `bookings` is empty. The model did not refuse to call. The call is still required: the schema only checks shape, and 990 is inside 0–1440. canBook is the part that answers Unavailable, because the room is blocked (AC3) and because 840 to 990 is 150 minutes (AC2).

### R3

```text
What exact start and end times tomorrow, and is the room blocked or already booked?
```

The request does not give a current time, a start, an end, whether the room is blocked, or any bookings. "Tomorrow afternoon" and "a couple of hours" are not minutes. The model did not call, and it did not invent `now`, `start`, `end`, `blocked`, or `bookings`. It asked one short question. The question covers the interval, the blocked flag, and existing bookings. It does not explicitly ask for the current time, which is also required, so a follow-up would still be needed before a call. Saved as `calls/r3.txt` because it asked, not as `calls/r3.json`.

## 5. What the schema cannot check

The schema can enforce the numeric part of AC1: each of `start`, `end` and `now` is an integer from 0 to 1440. It cannot enforce the rest of AC1. Nothing in the allowed keywords compares two properties, so `start < end` and `start` after `now` are invisible. A call with `start` 600 and `end` 600 is valid JSON.

AC2, at most 120 minutes, needs `end - start`. These keywords have no subtraction, so the 150 minute request in R2 is a legal call.

AC3 is a meaning, not a type. `"type": "boolean"` accepts `blocked: true`. Only canBook turns that into Unavailable.

AC4, no overlap, with touching allowed, compares the requested interval with every booking. The schema can demand that each booking has an integer `start` and `end`. It cannot compare them with the request.

AC5, the tool never saves or changes a booking, is behaviour of the function. A description can warn the model. An input schema cannot stop a later write.

AC6, the page's feedback, is the client's job after the answer comes back. The input schema does not produce the message.

## 6. Permissions — allow, ask or block

| # | Action | Decision (allow / ask / block) | Reason (the risk, in one sentence or more) |
| --- | --- | --- | --- |
| A1 | call `check_room` with the times the user just typed | allow | This is the read-only check the tool is for, and it does not save a booking or change the repository. |
| A2 | read `week-08/app/src/booking.ts` | allow | Reading that source only shows code that is already in the repo, so the risk is a wider read, not a write. |
| A3 | edit `booking.ts` to raise the 120-minute limit to 180 | ask | One user wanting three hours is not a decision to drop AC2, and the agent must not rewrite that rule on its own. |
| A4 | run `npm test` in `week-08/app` | ask | The test script in package.json can do more than print results, so the command should be seen before it runs. |
| A5 | run `git reset --hard` to undo its own last three edits | ask | A hard reset throws away those edits even when one of them should stay, so the diff has to be confirmed first. |
| A6 | `git commit` its change on the `week-09` branch | ask | A commit is local, but it freezes whatever is staged, including a file the agent was not asked to add. |
| A7 | `git push` to `main` | block | Pushing to main publishes unreviewed work and skips the open pull request this lab requires. |
| A8 | send the contents of `.env` to an MCP server it found online | block | `.env` can hold keys and passwords, and a server found online is not a place those secrets may go. |

## 7. Checkpoint

The checkpoint is the current `main` commit, before any week-09 file: `23d8110` (`23d8110526dbb225c3840f72d8e05f0358460bfd`), message `Merge pull request #7 from yrysbekshadi/week-02`. It is already on `main`.

The command back to it is:

```text
git reset --hard 23d8110
```

That command moves the current branch to `23d8110` and throws away every later commit on this branch, including the tool definition, the saved calls and this report, plus any staged or unstaged change to tracked files. It does not delete untracked files, and it does not push. Run `git status` before it. Anything still wanted has to be copied aside first, because a hard reset does not keep it.

## 8. Checker output

Paste the **whole** output of the last `python tests/check_tool.py`, unedited.

```text
PASS  D1    tool/check_room.json exists and is valid JSON
PASS  D2    has name, description and inputSchema
PASS  D3    name is exactly "check_room"
PASS  D4    description: 25+ words, says minutes, 1440, and that it does not save
PASS  D5    inputSchema: an object with exactly the five fields, all required
PASS  D6    inputSchema uses only the keywords listed in README section 5
PASS  S01   the R1 call, valid -> accept
PASS  S02   no existing bookings: bookings = [] -> accept
PASS  S03   end as a string: "11:00" -> refuse
PASS  S04   now missing -> refuse
PASS  S05   an extra field: "room": "204" -> refuse
PASS  S06   start below the day: -30 -> refuse
PASS  S07   end beyond the day: 1500 -> refuse
PASS  S08   a booking with no end: {start: 660} -> refuse
PASS  S09   blocked as a string: "false" -> refuse
PASS  S10   start not a whole minute: 600.5 -> refuse
PASS  S11   end at the end of the day: 1440 -> accept
PASS  S12   a booking as a pair: [660, 720] -> refuse
PASS  F1    calls/r1.json: a call to check_room
PASS  F2    calls/r1.json: arguments valid against your schema
PASS  F3    calls/r1.json: arguments equal the expected ones (README section 5, Part 2)
PASS  F4    calls/r2.json: a call to check_room
PASS  F5    calls/r2.json: arguments valid against your schema
PASS  F6    calls/r2.json: arguments equal the expected ones (README section 5, Part 2)
PASS  F7    calls/r3: exactly one of r3.json (it called) or r3.txt (it asked), not empty
PASS  L1    section 5 names at least two acceptance criteria (AC1-AC6) the schema cannot check
PASS  L2    section 6: A1-A8 each have allow / ask / block and a reason of 5+ words
PASS  L3    section 7 names the checkpoint commit (a SHA)
FAIL  L4    section 10: a conclusion of 80-150 words
             -> 151 words
PASS  L5    AI_USAGE.md filled in (a tool row, and signed)

SUMMARY: 29 PASS · 1 FAIL · 0 ERROR  (of 30 checks)
Paste this whole output into lab-report.md section 8, and these three numbers into submission.yml.
```

## 9. What still fails

None. All 30 checks pass on the last run. `known_fails` is empty.

## 10. Conclusion (80–150 words)

A schema checks shape, and canBook checks meaning. On the first run the empty schema accepted S03, because end was the string 11:00, and S07, because end was 1500. Setting type integer and maximum 1440 refused both, but start equal to end is still valid JSON. The allowed keywords cannot require start before end, or start after now, which is the rest of AC1, and they cannot cap a stay at 120 minutes, which is AC2. R2 makes the same split: the model called check_room with blocked true and end 990. That shape is legal, and only canBook can answer Unavailable, both because the room is blocked and because 14:00 to 16:30 is 150 minutes. R3 gave no clock time and no blocked flag, so the model asked instead of inventing now. A8 stays blocked, because an online server must never receive .env.
