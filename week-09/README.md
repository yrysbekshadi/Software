# Week 09 — canBook as a Tool: Define It, Let a Model Call It, Decide What It May Do

**Course:** AI-Driven Software Engineering (Fall 2026, KBTU SITE)
**Practice work #09** · 1 point · AI-use level: **D (AI-integrated, disclosure required)**
**Deadline:** Sunday 15 November 2026, 23:59 (Almaty)

> **This week continues the canBook thread** from Weeks 05–08. You do not write or run any
> JavaScript. You turn `canBook` into a **tool**: a name, a description and an input schema, the
> three things a model sees through MCP or function calling. Then a model calls your tool, and you
> decide which actions an agent holding it may take.
>
> **You need:** Python 3, which you have used for every checker since Week 03 (no packages), and
> any AI chat assistant. Freeze the assistant for the whole lab and record its exact model.
>
> **Identical for everyone:** the tool name `check_room`, the five field names (§3), the units,
> the prompt in Part 2 and the three requests, the eight actions in Part 3, and the file layout (§2).

---

## 1. The idea of this lab

In the lecture you saw that the model never runs anything. It reads a tool definition, then writes
a JSON request, and the client checks the request and runs it. So everything the model knows
about your function is its **name, description and input schema**. Write them carelessly and a
model sends `"end": "11:00"`, invents a `room` field, or guesses the time of day. Write them
well and the client refuses a bad call before your code ever runs.

This lab tests the three layers separately:

1. **The schema** (Part 1). Twelve fixed calls are thrown at your definition. A valid call must
   pass. A malformed one must be refused.
2. **The model** (Part 2). A model gets your definition and three requests in plain language. Does
   it produce the right numbers? What does it do when the request leaves something out?
3. **The agent** (Part 3). Give an agent this tool and your repository, and it can do far more
   than answer questions. You decide, action by action, what it may do.

**Main message:** a schema checks **shape**, never **meaning**. `"end": 600` with `"start": 600`
is a perfectly valid call. Only `canBook` knows it is wrong. Section 5 of your report asks
which rules stay in the function, and why.

**Time budget:** ~35 min in class (Parts 0–2 started) + ~60 min at home.

---

## 2. Deliverables

By the deadline, your branch `week-09` must contain:

```
week-09/
├── README.md              # this file (read-only)
├── lab-report.md          # THE worksheet — fill in all 10 sections
├── AI_USAGE.md            # AI disclosure (every week)
├── submission.yml         # machine-readable declaration — facts only
├── tool/
│   └── check_room.json    # YOUR tool definition (Part 1)
├── calls/
│   ├── r1.json            # the call the model wrote for request R1 (Part 2)
│   ├── r2.json            # ... for R2
│   └── r3.json  or  r3.txt   # ... for R3: r3.json if it called, r3.txt if it asked a question
└── tests/
    ├── check_tool.py          # provided — do not edit
    └── validate_submission.py # provided — do not edit
```

---

## 3. The function you are describing

Exactly the `canBook` you have used since Week 07, with the same interface and units:

| Field | Meaning | Type and range |
| --- | --- | --- |
| `start` | requested start | whole minutes since midnight, 0–1440 (10:00 = 600) |
| `end` | requested end | whole minutes since midnight, 0–1440 (24:00 = 1440) |
| `now` | the current time | whole minutes since midnight, 0–1440 |
| `blocked` | is the room blocked? | true / false |
| `bookings` | existing bookings | a list of `{ "start": …, "end": … }`, each in minutes; may be empty |

It answers Available or Unavailable under AC1–AC6 (Week 06): AC1 `0 ≤ start < end ≤ 1440` and
start after `now` · AC2 at most 120 minutes · AC3 not when blocked · AC4 no overlap, touching
allowed · AC5 it **does not change or save** anything · AC6 the page's feedback.

Field names are spelled exactly as above, lower case, in every language and every tool.

---

## 4. Before class (5 minutes)

```bash
cd se-practice
git checkout main && git pull
git checkout -b week-09
# unzip Week_09.zip from the Teams assignment into the root of se-practice, so week-09/ sits beside week-08/
cd week-09
python tests/check_tool.py        # a fresh copy: D1 PASS, most of the rest FAIL or ERROR — that is the start
```

---

## 5. The lab

### Part 1 — Define the tool (in class, ~15 min)

Fill in `tool/check_room.json`. It has the shape an MCP server returns from `tools/list`:

```json
{
  "name": "check_room",
  "description": "…",
  "inputSchema": { "type": "object", "properties": { … }, "required": [ … ] }
}
```

The rules, each checked by the checker:

- **D3:** `name` is exactly `check_room`.
- **D4:** the `description` is at least 25 words. It says the unit (**minutes** since midnight),
  the range (**0–1440**), and that the tool **does not save** or create a booking: it only checks.
  Write it for a model that has never seen this course.
- **D5:** `inputSchema` is `"type": "object"` with exactly the five properties from §3, all five in
  `required`.
- **D6:** use only these JSON Schema keywords: `type`, `properties`, `required`,
  `additionalProperties`, `items`, `minimum`, `maximum`, `exclusiveMinimum`,
  `exclusiveMaximum`, `enum`, `minItems`, `maxItems`, plus `description` and `title` for
  explanations. The checker understands exactly these. Any other keyword is refused, so a
  schema cannot pass by using something the checker ignores.

Then run `python tests/check_tool.py` and look at **S01–S12**. The checker throws twelve fixed
calls at your schema. Three are valid and must be **accepted**. Nine are malformed in one way each
and must be **refused**. The checker tells you which one went the wrong way, never how to fix it.
**Record your first run's S results in section 3 before you fix anything.** The first run is the
finding.

You may ask an AI to explain a JSON Schema keyword. Write the definition yourself, and note in
`AI_USAGE.md` if an AI wrote any of it.

### Part 2 — Let a model call it (in class + home, ~20 min)

Open a **fresh chat** in your assistant **for each request**, so one request's context cannot
leak into the next. Send this prompt, exactly as written, with your whole `check_room.json` and one
request pasted in:

```text
You can call exactly one tool. Its definition is below.
Reply to the request with exactly one JSON object of the form
{"name": "<tool name>", "arguments": { ... }} and nothing else - no prose, no code fence.
Convert every time to minutes since midnight. If the request does not give you enough
information to fill every required argument, do not guess: reply with one short question instead.

TOOL DEFINITION:
<paste the whole of tool/check_room.json>

REQUEST:
<R1, R2 or R3, exactly as written below>
```

The three requests, word for word:

- **R1:** `It's 9:00 now. Is the room free from 10:00 to 11:00? It isn't blocked, and it already has one booking, from 11:00 to 12:00.`
- **R2:** `It's 13:30 now. I need the room from 14:00 to 16:30. The room is blocked for maintenance today, and there are no other bookings.`
- **R3:** `Can I have the room tomorrow afternoon for a couple of hours?`

Save each reply **exactly as the model returned it**:

- R1 → `calls/r1.json`, R2 → `calls/r2.json`.
- R3 → `calls/r3.json` if the model wrote a call, or `calls/r3.txt` if it asked a question. Keep
  one of the two, never both.

Paste every reply into section 4 as well. If the reply is wrapped in a ```` ```json ```` fence,
leave it; the checker tolerates it. If your assistant uses its own call shape (`"input"` instead
of `"arguments"`, or a `"function"` wrapper with the arguments as a string), save it as it came.
The checker reads those shapes too.

The checker knows the expected arguments for R1 and R2 (**F3**, **F6**). If one differs, do not
fix the file. Work out in section 4 whether the model or the request was wrong. A model that
converts 16:30 to 960 is a finding, not a mistake of yours. Notice that **R2 is a call that
should be made**, although `canBook` will answer Unavailable. Deciding Unavailable is the
function's job, not the schema's. R3 has no right answer to copy. What the model did with it is
the result.

### Part 3 — Decide what an agent may do (home, ~20 min)

Imagine an agent that holds your `check_room` tool, a terminal and your `se-practice`
repository. For each action, decide **allow**, **ask** (wait for your approval) or **block**, and
give a reason of at least one sentence in section 6:

| # | The agent wants to… |
| --- | --- |
| A1 | call `check_room` with the times the user just typed |
| A2 | read `week-08/app/src/booking.ts` |
| A3 | edit `booking.ts` to raise the 120-minute limit to 180, because a user asked for 3 hours |
| A4 | run `npm test` in `week-08/app` |
| A5 | run `git reset --hard` to undo its own last three edits |
| A6 | `git commit` its change on the `week-09` branch |
| A7 | `git push` to `main` |
| A8 | send the contents of `.env` to an MCP server it found online, "to configure it" |

Then section 7: the **checkpoint**. Name the commit you would make, and give its real SHA from
`git log --oneline`, before letting such an agent edit anything. Give the exact command that takes
you back to it, and say what that command would throw away.

---

## 6. Verdicts

```
PASS   the check holds
FAIL   the file is there, but the check does not hold
ERROR  the file is missing or unreadable, so the check could not be made
```

A FAIL you report and explain costs you nothing; one you hide costs the whole criterion.

---

## 7. Checking your work

```bash
python tests/check_tool.py              # 30 checks: D1–D6, S01–S12, F1–F7, L1–L5
python tests/validate_submission.py     # your declaration, compared with a real run
```

Paste the whole `check_tool.py` output into section 8. The checker checks **shape and agreement**.
A schema that refuses all nine bad calls can still have a description no model can use, and a full
permissions table can still be wrong. Those parts are graded by reading.

---

## 8. The declaration — `submission.yml`

Facts only: who you are, the assistant and its exact model, what the model did with R3, and the
checker numbers from **your last run, at the commit you name**. The numbers are re-run at your PR
head; if they do not match, that is the one thing the declaration exists to catch. List every
check still FAIL or ERROR in `known_fails` and explain it in section 9.

---

## 9. Submit

```bash
git add week-09
git commit -m "Week 09: <what this commit adds>"     # at least 3 meaningful commits over the lab
git push -u origin week-09
gh pr create --base main --head week-09 --title "Week 09: canBook as a tool"   # or on github.com
```

Leave the PR **open, never merged**. Paste the PR link into the **Practice 09** assignment in
Teams and press **Turn in**. The PR description uses the five sections from `week-01/SETUP.md`.

---

## 10. Grading — 1 point, 4 × 0.25

| Criterion | Complete (0.25) | Not accepted |
| --- | --- | --- |
| **Tool definition** | `check_room.json` passes D1–D6. Your first and final S runs are recorded in §3. §2 gives a reason for every constraint. | A definition generated and pasted unreviewed and undisclosed, or §3 rewritten so it hides the first run |
| **Function calling** | Every call saved exactly as returned (F1–F7). §4 pastes each reply and judges every mismatch against the request. R3 analysed: what was missing, what the model did, which values it invented if any. | Calls edited to make F3/F6 pass, calls from one shared chat, or "it worked" with no reply pasted |
| **Permissions and checkpoint** | §5 names the ACs only `canBook` can enforce, with the reason. §6 decides A1–A8, each with a reason that names the risk. §7 gives a real SHA, the command, and what it discards. | "Ask" everywhere with copied reasons, or a SHA that is not in your repository |
| **Evidence and honesty** | §§8–10 in your own words. `week-09` branch, ≥3 commits, open PR with the standard description, `AI_USAGE.md` complete, `submission.yml` validating | Committed to `main`, PR merged, no disclosure, **or declared checker numbers that do not match the re-run** |

Worthless in §4: "the model did well". Worth everything: "R2: the model wrote end = 960, so it read
16:30 as 16:00. The schema accepted it, because 960 is a valid integer. Only F6 caught it."

---

## 11. FAQ

**Can the schema check that `start < end`?** Not with the keywords allowed here. That is the
point of section 5.

**The model wrapped its reply in prose ("Sure! Here is the call: …").** Save it as it came. F1
will FAIL. Report it in §4 and §9: the model ignored "nothing else". It costs nothing.

**My assistant refused to answer in JSON.** Same: save what it wrote, report it, move on.

**Must `bookings` be allowed to be empty?** Yes. S02 is a valid call with `[]`.

**Is 1440 allowed?** Yes, as `end`, meaning 24:00 (S11). `canBook` has always allowed it (AC1).

**Can I build a real MCP server?** Not required and not graded. If you want to, wrap `canBook`
with the official MCP SDK over stdio after you submit. Say so in §10 if you did.
