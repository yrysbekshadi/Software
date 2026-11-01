# SIS #03 — Report: Smart Campus Room Availability Checker

<!-- The ONLY file you write prose in. Keep every numbered heading (## 1. … ## 13.) and every
     ### sub-heading, and the **Label:** words — the checker finds your answers by them.
     Replace every "(write here)" and "(paste here)". Delete these <!-- --> comments if you like. -->

## 1. Setup and reuse

| Item | Value |
| --- | --- |
| Student name | Shadi Yrysbek |
| Student ID | 24B031125 |
| Coding assistant (tool) | ChatGPT (web) |
| Coding assistant model | GPT-6 |
| Bolt.new model | not displayed |
| Bolt project link | https://bolt.new/~/sb1-jw4fikxw?focus=create-project |
| Language | Python |
| Path | A |
| Python v1 from | fresh |
| Web v1 from | fresh |

Both v1 artifacts were generated fresh for this SIS because the earlier Week 05 and Week 06 artifacts were unavailable. The v1 Bolt export is retained separately from the final export. The final Bolt export contains the later UI repair; the original availability helper is unchanged between the two exports. The final package also removes an unused Supabase SDK dependency from the final export after source review; the original export is kept unchanged.

## 2. Baseline — requirements understanding

> Chronology note: this summary was completed after AI-assisted work had already started. It records the project requirements, but it does not claim that the baseline-first commit requirement was met.

### 2.1 Scope in my own words

**Scope:**

This program helps a student check if one classroom is free at a chosen time. It only checks availability. It does not make or confirm a booking. It does not use login, a database, a backend or external services.

### 2.2 The acceptance criteria in my own words

| AC | In my own words |
| --- | --- |
| AC1 | The start and end times must be valid whole minutes. Start must be before end and later than now. |
| AC2 | A requested time can be up to 120 minutes. Exactly 120 minutes is allowed. |
| AC3 | A blocked room is always unavailable. |
| AC4 | A request cannot overlap an existing booking. Touching at an endpoint is allowed. |
| AC5 | The page must clearly show Available or Unavailable and must not change existing bookings. |
| AC6 | The page must show understandable errors and work on a small phone screen. |

### 2.3 Likely failure points

| # | Failure point | AC | How I will check it |
| --- | --- | --- | --- |
| 1 | The program may reject a request that starts exactly when an old booking ends. | AC4 | Check 11:00–12:00 when an existing booking ends at 11:00. |
| 2 | The program may allow a request that starts at the current time. | AC1 | Set now to 09:00 and check a request starting at 09:00. |

### 2.4 The contract

| Parameter | Meaning | Type and allowed values |
| --- | --- | --- |
| `start` | Requested start time | Integer minutes, 0–1439 |
| `end` | Requested end time | Integer minutes, 1–1440; greater than `start` |
| `now` | Current time | Integer minutes after midnight |
| `blocked` | Whether the room is blocked | Boolean (`True` or `False`) |
| `existing` | Current bookings | List of `(start, end)` integer pairs |
| returns | Availability decision | Boolean; `True` only when AC1–AC4 pass, otherwise `False` |

### 2.5 Initial assumptions and manual checks

**Assumptions:**

1. Time is counted in minutes from midnight. For example, 09:00 is 540.
2. A booking includes its start time but not its end time, so two bookings may touch at an endpoint.

**Checked manually:**

- I checked the brief's example values: 09:00 = 540 and 10:00–11:00 = 600–660 minutes. I also reviewed the T1 and T6 boundary examples before testing the function.

## 3. Python v1 review

The fresh v1 is preserved at `code/original/booking_v1.py`. It is intentionally kept unchanged; the following review records its actual branch conditions.

| Branch in v1 (quoted) | AC | Satisfies it? | Why |
| --- | --- | --- | --- |
| `if start < 0 or end > 1440 or start > end:` | AC1 | No | The strict ordering rule is `start < end`; `start == end` slips through because the branch uses `>` rather than `>=`. |
| `if start < now:` | AC1 | No | A start exactly equal to `now` is not rejected. AC1 requires it to be strictly after now; T6 exposes this. |
| `if end - start > 120:` | AC2 | Yes | Durations above 120 are rejected and exactly 120 is allowed. |
| `if blocked:` | AC3 | Yes | A truthy blocked flag immediately rejects the request. |
| `if start <= existing_end and end >= existing_start:` | AC4 | No | Inclusive comparisons incorrectly treat endpoint touching as overlap; T1 is rejected even though it should be available. The loop does check each booking. |
| `return True` | AC5 | Partly | Returns a Boolean and does not mutate `existing`, but it can return True for a request starting exactly now or a zero-length request because earlier AC1 checks are incomplete. |


## 4. Prototype v1 in Bolt.new

**Bolt project:** `https://bolt.new/~/sb1-jw4fikxw?focus=create-project`  
**Model:** not displayed in the visible Bolt interface.  
**Fresh v1 export:** saved under `web/original/` before the focused UI repair.  
**Final export:** saved under `web/final/` after the control-panel repair.

**Prompt as sent:**

~~~~text
Build a responsive, single-page web prototype named “Smart Campus Room Availability Checker”.

Purpose and scope:
- A student checks whether one selected campus room is available for a proposed time interval.
- Use one selected room only (label it “Room A-204”) and fictional, hard-coded booking data.
- The page checks availability only. It must never create, reserve, submit, or confirm a booking.
- Do not add login, sign-in, authentication, backend, database, external API, payments, analytics, or unrelated features.
- No network requests and no browser storage. Keep all demo data in memory and do not mutate the existing bookings during a check.

Implement these fixed acceptance criteria without changing their meaning:
AC1: Candidate times represent integer minutes after midnight and must satisfy 0 <= start < end <= 1440. The start must be strictly after the current time. Use a demo current time of 09:00 (540 minutes) so the supplied acceptance cases can be reproduced consistently.
AC2: Duration must be no more than 120 minutes; exactly 120 minutes is valid.
AC3: If Room A-204 is blocked, every request is Unavailable.
AC4: Reject overlap with any existing booking. Treat intervals as [start, end): touching at an endpoint is NOT overlap. Use the demo booking 10:00–11:00 (600–660 minutes).
AC5: Show a clear, unambiguous “Available” or “Unavailable” result, plus a human-readable reason. Checking must not append, remove, sort, or otherwise mutate existing bookings.
AC6: Give understandable validation messages for invalid time order, past/current start, too-long duration, blocked room and overlap. The page must remain usable at a narrow phone width around 375 px, with labels, controls and result visible without horizontal scrolling.

UI requirements:
- Clean campus-style interface, restrained colors, readable typography and clear spacing.
- Show the selected room, demo current time (09:00), existing demo booking(s), start and end time inputs, a “Check availability” button, and a result area.
- Use native time inputs if appropriate; if the browser cannot represent 24:00, state that the page input cannot test the 1440-minute endpoint rather than silently changing the rule.
- Do not include a “Book”, “Confirm”, or “Reserve” button.
- Keep the implementation simple and self-contained. Do not add features outside this specification.

Before finishing, inspect the generated implementation against AC1–AC6 and explain where each rule is enforced. Do not claim tests were run unless you actually run them.

Test-control addendum:
Add a small “Test setup” section with two controls:
1. “Simulate room blocked”, OFF by default; when ON, every availability request returns Unavailable.
2. “Include second demo booking”, OFF by default; when ON, add a second fictional booking 11:40–12:40 alongside 10:00–11:00 by using a separate derived array and never mutating the original bookings.
These controls only reproduce AC3 and T10; they do not create bookings or add a backend.
~~~~

**Files generated in v1 (`web/original/`):**

| Generated file | Path | Role |
| --- | --- | --- |
| Page entry | `index.html` | Vite page shell and app mount. |
| Project manifest | `package.json` | Front-end scripts and dependencies. |
| Main page | `src/App.tsx` | Room summary, time inputs, result and test controls. |
| Availability rules | `src/lib/availability.ts` | Time parsing, fixed demo data and availability decisions. |
| Test switch component | `src/components/ToggleSwitch.tsx` | Reusable test-control switch. |
| Styling | `src/index.css` | Responsive page styling. |
| App entry | `src/main.tsx` | React application entry point. |

**What was observed in v1:** the page showed Room A-204, current time 09:00 and one fictional booking from 10:00 to 11:00. In the supplied v1 screenshots, 11:00–12:00 showed Available (T1), and 10:30–11:30 showed Unavailable due to overlap (T2). The test controls were visible in the normal page flow and the “Include second demo booking” label did not explicitly identify T10. The time input note said 24:00 cannot be entered.

**Focused repair applied after v1:** the “Test setup” panel was renamed “Assessment Test Controls”, made collapsible with a closed initial state, and given a note that the switches do not create or confirm bookings. The labels now identify T3 and T10; the T10 description explicitly states 11:40–12:40. The final export is under `web/final/` and differs from v1 in `src/App.tsx`.

**Final-export files:** `web/final/index.html`, `web/final/package.json`, `web/final/src/App.tsx`, `web/final/src/lib/availability.ts`, `web/final/src/components/ToggleSwitch.tsx`, `web/final/src/index.css`, and `web/final/src/main.tsx` (plus the Vite/Tailwind/TypeScript configuration and lock file).

**Observed final checks:** the supplied screenshots show T3 (blocked toggle ON with 11:00–12:00 → Unavailable) and T10 (second demo booking ON with 12:00–13:00 → Unavailable because of 11:40–12:40). A responsive preview was captured at 379 × 644 CSS pixels, close to the brief’s ~375 px target. The narrow screenshot shows the page in a narrow portrait viewport; the exact T1 test at that width was not captured. Bolt’s visible response reported that its build and type check passed and that it re-ran T3/T10 and key time-boundary cases; that build claim was not independently repeated locally because npm packages were not available offline.

## 5. Test cases — executed on both artifacts

Python v1 and final were executed against the handout's T1–T11 inputs (base: `now=540`, `blocked=False`, `existing=[(600, 660)]`). T11 records the second call. The page cells below are limited to what is visible in the supplied Bolt screenshots. `Not run` is deliberately not presented as a passing test. T8/T9 are `Not testable` in the page because the native time input stops at 23:59 and cannot express 24:00 or 24:01.

| Case | Name | Input | Expected | Python v1 | Python final | Page v1 | Page final |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T1 | Touching | 660–720 | Available | False | True | Available | Not run |
| T2 | Overlap | 630–690 | Unavailable | False | False | Unavailable | Not run |
| T3 | Blocked | 660–720, blocked | Unavailable | False | False | Not run | Unavailable |
| T4 | Exactly 120 min | 720–840 | Available | True | True | Not run | Not run |
| T5 | 121 min | 720–841 | Unavailable | False | False | Not run | Not run |
| T6 | Starts now | 540–570 | Unavailable | True | False | Not run | Not run |
| T7 | Reversed | 720–660 | Unavailable | False | False | Not run | Not run |
| T8 | Ends at midnight | 1380–1440 | Available | True | True | Not testable | Not testable |
| T9 | Past midnight | 1380–1441 | Unavailable | False | False | Not testable | Not testable |
| T10 | Second booking | 720–780, existing (600–660), (700–760) | Unavailable | False | False | Not run | Unavailable |
| T11 | Same check twice | 660–720, twice | Available | False | True | Not run | Not run |
| T12 | Narrow screen | T1 at ~375 px | Available | n/a | n/a | Not run | Not run |

**Page evidence references:** v1 T1 is shown in `evidence/web-v1.png` (11:00–12:00 → Available); v1 T2 is shown in `evidence/before-1.png` (10:30–11:30 → Unavailable); final T3 is shown in `evidence/t3-final.png`; final T10 is shown in `evidence/t10-final.png`. `evidence/final-narrow.png` is a crop of the user's original responsive preview whose DevTools toolbar displayed 379 × 644. It demonstrates the narrow layout but does not record T1 at that width; therefore T12 remains Not run. The original uncropped capture is preserved in `evidence/source-originals/final-mobile-top.png`.

Do not treat “Not run” as a successful result. The remaining page cases must be run in the browser before the report can claim complete T1–T12 coverage.

## 6. Traceability

| AC | Implementation / file | Test input | Expected | v1 actual | Final actual |
| --- | --- | --- | --- | --- | --- |
| AC1 | Python: `code/booking.py`; page: `web/final/src/lib/availability.ts` (`parseTimeInput`, whole-minute/day/order/current-time guards) | T6–T9; unit tests for reversed, zero-length, negative and day bound | Reject invalid order, out-of-range and start <= now; allow end 1440 in the rule | Python v1 T6 incorrectly True; page v1 24:00 note observed, T8/T9 not testable | Python final T6 False; page final source contains start <= 09:00 and day-range checks; T6 browser case not run |
| AC2 | Python: duration guard in `code/booking.py`; page: `MAX_DURATION_MINUTES` in `web/final/src/lib/availability.ts` | T4–T5 | 120 min True; 121 min False | Python v1 T4 True/T5 False; page cases not run | Python final T4 True/T5 False; page rule inspected, T4/T5 browser cases not run |
| AC3 | Python blocked guard; page `roomBlocked` branch and `Simulate room blocked (T3)` control | T3 | False / Unavailable whenever blocked | Python v1 T3 False; page v1 not recorded | Python final T3 False; final page T3 visibly Unavailable with blocked control ON |
| AC4 | Python strict overlap; page `start < booking.end && booking.start < end` in `web/final/src/lib/availability.ts` | T1–T2 and T10 | Endpoint touching True; all overlap False | Python v1 T1 incorrectly False; page v1 T1 Available and T2 Unavailable were observed | Python final T1 True/T2 False/T10 False; page final T10 visibly Unavailable; T1/T2 final browser cases not run |
| AC5 | Python returns `bool` and never mutates input; page returns `AvailabilityResult` status, maps bookings with `getBookings`, and has no booking-create action | T11 and repeated-check/non-mutation tests | Clear availability result; existing bookings unchanged | Python v1 T11 second call False; page v1 displayed explicit Available/Unavailable labels | Python final T11 second call True; page final displays explicit Available/Unavailable and test controls are documented as non-booking controls; page T11 not run |
| AC6 | `web/final/src/App.tsx`, `src/index.css`, native time inputs and result panel | T12 and validation-message cases | Understandable feedback and usable narrow layout | Page v1 has readable labels and a 24:00 limitation note; T12 not captured | Final page captured at 379 × 644 with a portrait layout and no visible horizontal overflow; exact T1-at-width test and all validation messages not exhaustively run |

**Scope inspection:** the final exported source has no login, database access, network request or browser-storage implementation. The unused `@supabase/supabase-js` dependency was removed from the final package manifest and lock file after this inspection; the v1 export was left unchanged.

## 7. Issue log

| # | Issue | Reproduction | Priority | Prompt / change | Retest result |
| --- | --- | --- | --- | --- | --- |
| 1 | Python v1 rejects a request that starts exactly when the existing booking ends because its overlap comparison is inclusive. | T1: `660–720` with existing `(600, 660)` returns False in Python v1, contrary to AC4. | High | Focused repair prompt: “Replace the inclusive overlap check with a half-open interval overlap check. A candidate overlaps an existing booking only when `start < existing_end and existing_start < end`. Do not change any other rule.” Final code uses strict inequalities. | Observed: Python final T1 returns True; `test_touching_at_existing_end_is_available` passes. |
| 2 | Python v1 allows a request to start at the current time because its guard checks only `start < now`. | T6: `540–570` with `now=540` returns True in Python v1, contrary to AC1. | High | Focused repair prompt: “Change the current-time guard so a request is rejected when `start <= now`; keep the requirement that start must be strictly after now.” Final code uses `if start <= now`. | Observed: Python final T6 returns False; `test_start_equal_to_now_is_rejected` passes. |
| 3 | Python v1 accepts zero-length intervals because it rejects `start > end` but not `start == end`. | AC1: `600–600` returns True in Python v1; AC1 requires `start < end`. | Medium | Focused repair prompt: “Enforce the exact AC1 range `0 <= start < end <= 1440`; reject equal start and end. Do not add a different duration rule.” | Observed: Python final rejects `600–600`; `test_zero_length_interval_is_rejected` passes. |
| 4 | The v1 test-control area was always in the normal page flow and its heading/labels did not make its assessment-only purpose clear. | AC6: v1 preview showed a “Test setup” area and generic switches; the Bolt response also said the T10 definition was not clear to it. | Medium | Focused Bolt prompt: “Rename the section Assessment Test Controls; make it collapsible and closed by default; add a note that the switches do not create or confirm bookings; rename the switches with T3/T10 labels; keep the availability algorithm unchanged.” Final `App.tsx` uses `controlsOpen = false`, explanatory copy and explicit labels. | Observed: final source defaults the panel closed; screenshot shows the updated panel and note. The panel was deliberately opened for the T3/T10 evidence screenshots. |
| 5 | The second demo booking was not clearly connected to T10, which made the test control confusing. | T10: the v1 explanation did not clearly identify the exact second interval for the acceptance case. | Medium | Focused Bolt prompt: “Label this control Add second demo booking (T10) and explain that it adds 11:40–12:40 to the checks, without mutating the original booking list.” | Observed: final label identifies T10 and the time range; with 12:00–13:00 entered and the switch ON, the page shows Unavailable due to overlap 11:40–12:40. |
| 6 | Final manifest carried an unused Supabase SDK dependency despite the no-backend/no-database scope. | AC1–AC6 scope check: `web/final/package.json` included `@supabase/supabase-js`; no source import or database/auth use was found. | Low | Focused cleanup: “Remove only the unused `@supabase/supabase-js` dependency from the final package manifest and lock file. Do not change application code or availability rules.” | Observed: dependency removed from final `package.json` and lockfile. Assumed: runtime logic is unchanged because no source file imported the package; a fresh npm build could not be repeated offline. |

**Before / after:** `evidence/before-1.png` → `evidence/after-1.png` show issues 4 and 5: the earlier visible test-switch context versus the renamed Assessment Test Controls with explicit T3/T10 labels and the non-booking explanation. The raw screenshots are retained under `evidence/source-originals/`.

## 8. Critique decisions

| # | AI claim or recommendation | How I verified it | Decision | Reason (AC or case) |
| --- | --- | --- | --- | --- |
| 1 | The v1 overlap expression treats endpoint contact as overlap. | Executed T1 on `booking_v1.py`: it returned False; executed the same input on final: True. | accept | AC4 says touching at an endpoint is not overlap. |
| 2 | The current-time condition should reject `start == now`, not only starts earlier than now. | Executed T6 on v1 (True) and final (False); the final unit test also checks the boundary. | accept | AC1 says start is strictly after now. |
| 3 | A generic cleanup could add a 15-minute cleaning buffer between bookings. | Compared the suggestion to the fixed contract and exact boundary semantics; such a buffer changes when a valid slot is available. | reject | The brief fixes endpoint touching as available and explicitly says to reject AI suggestions that change the meaning of AC1–AC6. |
| 4 | The code should reject zero-length intervals. | Ran `600–600` against v1 and final; v1 returned True and final returned False. | accept | AC1 requires `start < end`. |
| 5 | The page is responsive and gives validation feedback. | Inspected the final source and the user-provided responsive preview at 379 × 644; the layout is narrow and vertically scrollable, but not every validation message or T1 at that width was run. | modify | AC6 is partially supported by the responsive capture and source; complete the remaining browser cases before claiming full verification. |


## 9. Coding-agent analysis

### 9.1 The loop

| Step | What happened in this assignment |
| --- | --- |
| User goal | Prepare a fresh SIS 03 submission for the Smart Campus availability checker because no Week 05 or Week 06 artifacts were available. |
| Model / plan | The assistant mapped AC1–AC6, planned a small deterministic availability function, boundary tests, a single-room page and explicit no-booking scope. |
| Tool call | ChatGPT generated/reviewed Python and prompts; the local shell assembled and tested artifacts; Bolt.new generated the v1 page and applied a focused test-control UI repair. |
| Observation | Python v1 failed T1/T6/zero-length checks and the final passed the 22-test suite. Page screenshots show v1 T1/T2, final T3/T10 and a 379 × 644 narrow preview. The final Bolt helper file is unchanged from v1; the UI controls changed. |
| Next step | Run the remaining page cases T1–T12 in the browser, record only observed outcomes, then complete the student-only baseline/reflection and the GitHub submission. |
| Human review | A person must decide whether the screenshot evidence matches the exact input, inspect the generated source, approve changes, complete personal writing, and own the final commit and PR. |

### 9.2 Context, tools and permissions

| Tool | Context it used | Tools or permissions | Observed or assumed |
| --- | --- | --- | --- |
| ChatGPT (web), GPT-6 | Assignment handout, starter ZIP, code exports, screenshots and the user's questions. | Generated/reviewed code, tests, prompts and documentation; no direct GitHub push or Bolt account action. | Observed |
| Local container shell | Uploaded ZIP archives, screenshots and extracted source. | Read/write in the working directory; execute Python tests/checkers; update report/package files. | Observed |
| Bolt.new, model label not displayed | Smart Campus project prompt and follow-up UI repair prompt. | Browser preview, generated React/TypeScript files, project download; Publish was visible but not used. | Observed |
| Browser/Bolt account environment | The user’s own logged-in Bolt session and local browser. | Exact model selection, account permissions, server-side retention and any unpublished platform internals were not visible in the supplied screenshots. | Assumed |

### 9.3 Checkpoint and dependability

**Safety checkpoint:** Before accepting the Bolt final, compare `src/lib/availability.ts` and `src/App.tsx` against AC1–AC6; verify no booking-create action, login, network request, browser storage or database was added; ensure the two assessment switches default OFF and never mutate the original booking list. The final source review found no such application behaviour. The final manifest's unused Supabase SDK dependency was removed and the lock file updated. The student should still run the final build in an online environment before submission.

**Reliability, security, responsibility:** The Python function is small and deterministic, but an off-by-one error can label an invalid or conflicting interval as available. The page can look finished while its boundary rules or mobile behaviour remain untested. Excluding a backend and database reduces the prototype's attack surface; unused backend SDKs also create confusion and unnecessary dependencies. A test switch is not a real booking action, and the page must never imply that availability checking reserves a room. AI review is not proof: the exact cases must run independently, screenshots must match their inputs, and the student remains responsible for the tests, permissions, repository history and final defence.

## 10. Reflection

> AI-assisted draft based on the work and observations recorded in this report. The student should review it and change anything that does not match their own experience.

I used AI in two different ways in this project. For Python, ChatGPT helped plan the function, write the first version, review its branches and prepare tests. The tests helped find errors with touching times and a request starting at the current time. With Bolt.new, I described the page and then asked it to make the test controls easier to understand. This was faster, but the first page still needed review. A reliability risk is a wrong time comparison that shows a busy room as free. A usability risk is a confusing control or a layout that does not fit a phone. A security risk would be adding an unnecessary backend or sending data to an external service. I rejected a suggested cleaning buffer because it would change the fixed rules. AI can make mistakes, so a person must check the code, permissions, screenshots and test results. Next, I would run every remaining browser test and verify the final build.

## 11. Appendix A — AI exchanges

**Disclosure note:** B1–B4 record the ChatGPT Plan, Generate, Critique and Repair work for Python. B5–B6 record the fresh Bolt generation and its focused UI repair. The Bolt model label was not displayed in the screenshots. Bolt responses below are explicitly marked as summaries where the full chat transcript was not exported; they are not claimed to be verbatim. B7 records the post-export scope cleanup of an unused dependency.

### B1

- **Tool:** ChatGPT (web)
- **Model:** GPT-6
- **Date:** 2026-11-01
- **Stage:** Plan
- **Source:** this SIS

**Prompt:**

~~~~text
For the fresh SIS 03 Smart Campus can_book task, make an implementation plan that follows the fixed contract exactly. List the validation order, assumptions, overlap formula for half-open intervals, and boundary tests. Do not change AC1–AC6 and do not add booking creation.
~~~~

**Response:**

~~~~text
Plan: (1) Treat start, end and now as integer minute values; reject non-integer values. (2) Enforce 0 <= start < end <= 1440. (3) Enforce start > now, which means rejecting start <= now. (4) Reject durations greater than 120 while allowing exactly 120. (5) Reject immediately when blocked is true. (6) Check every existing interval using half-open overlap: start < existing_end and existing_start < end. This formula allows endpoint touching and rejects partial, contained, containing and identical overlaps. (7) Return a Boolean and do not modify the existing collection.

Assumptions: now is a valid minute within the current day; existing is a collection of valid (start, end) pairs; the brief's interval semantics are [start, end). Boundary tests include start equal to now, one minute after now, start/end equality, 0 and 1440 day bounds, exactly 120 and 121 minutes, both endpoint-touching directions, several existing bookings, and unchanged input data.
~~~~

### B2

- **Tool:** ChatGPT (web)
- **Model:** GPT-6
- **Date:** 2026-11-01
- **Stage:** Generate
- **Source:** this SIS

**Prompt:**

~~~~text
Generate a first Python v1 for can_book(start, end, now, blocked, existing), using only the standard library and the SIS 03 contract. Keep this first version unedited so it can be reviewed branch by branch; do not silently repair it after generation. Return the full source code.
~~~~

**Response:**

~~~~python
def can_book(start, end, now, blocked, existing):
    """Return whether a room booking request appears to be available."""
    if start < 0 or end > 1440 or start > end:
        return False
    if start < now:
        return False
    if end - start > 120:
        return False
    if blocked:
        return False
    for existing_start, existing_end in existing:
        if start <= existing_end and end >= existing_start:
            return False
    return True
~~~~

### B3

- **Tool:** ChatGPT (web)
- **Model:** GPT-6
- **Date:** 2026-11-01
- **Stage:** Critique
- **Source:** this SIS

**Prompt:**

~~~~text
Review the preserved Python v1 against AC1–AC6. Identify concrete conditions that fail boundary cases, explain how to verify each claim, and flag any recommendation that would change the fixed requirements. Do not assume the web prototype has been run.
~~~~

**Response:**

~~~~text
The first range condition uses start > end rather than start >= end, so a zero-length interval such as 600–600 is allowed; this violates AC1. The current-time guard uses start < now, so a request starting exactly at now is allowed; AC1 requires strictly after now. The overlap condition uses <= and >=, so endpoint-touching requests are treated as conflicts; AC4 explicitly allows touching endpoints. The duration condition is correct for AC2 because only durations greater than 120 are rejected. The blocked check is correct for AC3 because it rejects whenever blocked is truthy. The function returns a Boolean and does not mutate the existing list, but AC5 is not enough to compensate for the earlier incorrect decisions. A cleaning buffer would be outside scope and must be rejected because it changes AC4.
~~~~

### B4

- **Tool:** ChatGPT (web)
- **Model:** GPT-6
- **Date:** 2026-11-01
- **Stage:** Repair
- **Source:** this SIS

**Prompt:**

~~~~text
Repair the Python function with the smallest changes needed to satisfy AC1–AC5: reject zero-length or otherwise invalid day ranges, reject start <= now, preserve the 120-minute inclusive maximum, reject blocked rooms, and use strict half-open interval overlap. Keep the signature, use only the standard library, return a Boolean, and do not mutate existing.
~~~~

**Response:**

~~~~python
def can_book(start, end, now, blocked, existing):
    """Check a proposed room interval without creating or changing bookings.

    Times are integer minutes after midnight. The candidate interval is
    [start, end), so two intervals that only touch at an endpoint do not
    overlap. `existing` is read-only from this function's point of view.
    """
    # AC1: accept integer minute values only, within one day, with positive
    # duration and a start strictly later than the current time.
    if any(type(value) is not int for value in (start, end, now)):
        return False
    if not (0 <= start < end <= 1440):
        return False
    if start <= now:
        return False

    # AC2: exactly 120 minutes is allowed; anything longer is not.
    if end - start > 120:
        return False

    # AC3: a blocked room cannot be available for any requested interval.
    if blocked:
        return False

    # AC4: half-open intervals overlap only when each starts before the
    # other one ends. Strict inequalities allow endpoint touching.
    for existing_start, existing_end in existing:
        if start < existing_end and existing_start < end:
            return False

    # AC5: return a Boolean only; do not append, sort, or otherwise mutate
    # the caller's existing-bookings collection.
    return True
~~~~

### B5

- **Tool:** Bolt.new
- **Model:** not displayed
- **Date:** 2026-11-01
- **Stage:** Generate (fresh web v1)
- **Source:** this SIS

**Prompt:**

~~~~text
Build a responsive, single-page Smart Campus Room Availability Checker for one selected room, Room A-204, using fictional in-memory bookings. It must check availability only and never create, reserve or confirm bookings. Do not add login, authentication, backend, database, external API, payments, analytics or unrelated features. Apply AC1–AC6 exactly: integer minute range 0 <= start < end <= 1440 and start > now; maximum duration 120 minutes inclusive; blocked room always Unavailable; half-open overlap where endpoint touching is not overlap; clear Available/Unavailable output without mutation; understandable validation and a narrow ~375px layout. Use demo now 09:00 and one existing booking 10:00–11:00. Add two test-only controls, both OFF by default: a blocked-room switch for T3 and a second fictional booking 11:40–12:40 for T10, using a derived list and never mutating the original booking. State that these controls do not create bookings.
~~~~

**Response:**

~~~~text
Summary (not a verbatim transcript):
Bolt generated a one-page React/TypeScript availability checker for Room A-204. The exported v1 contains the selected room and demo current time (09:00), the fictional existing booking (10:00–11:00), start and end time inputs, a Check availability button, result feedback, and two test switches. The visible Bolt response says the second demo booking is added to a separate list so the original booking is not changed. It also notes that the native time input cannot enter 24:00. The visible response says the T10 definition was not fully clear to Bolt, so the test switches were based on the supplied description. The v1 export is preserved under web/original/ before the later UI repair. The visible first-version response also explained that the hard-coded existing booking remains unchanged and that all availability checks read the available demo-booking list. The export files and the submitted screenshots match the single-page scope, but the page cases not visible in screenshots are not claimed as executed.
~~~~

### B6

- **Tool:** Bolt.new
- **Model:** not displayed
- **Date:** 2026-11-01
- **Stage:** Repair (test-control UI)
- **Source:** this SIS

**Prompt:**

~~~~text
Improve the Test setup section. Rename it “Assessment Test Controls”; make it collapsible and collapsed by default; add a clear note that the controls are only for reproducing assessment test cases and do not create or confirm bookings. Rename the first switch “Simulate room blocked (T3)”. Rename the second “Add second demo booking (T10)” and explain that it adds 11:40–12:40. Keep both switches OFF by default. Do not change the availability algorithm or AC1–AC6. Do not add booking creation, confirmation, login, backend or database. Preserve the responsive layout and retest T3 and T10.
~~~~

**Response:**

~~~~text
Summary (not a verbatim transcript):
Bolt reported that the section was renamed to Assessment Test Controls, the explanation was added, the switches were labelled with T3 and T10, and the original availability rules and page layout were unchanged. Its visible response reported that build and type check passed and that T3, T10 and key time-boundary rules were re-run with expected outcomes. It also stated that it had not checked the page in a browser, so the collapsed animation and narrow-phone layout were not verified by Bolt. The user then supplied screenshots showing T3 as Unavailable when the blocked switch was ON and T10 as Unavailable when the second booking switch was ON. A separate 379 × 644 responsive preview was also supplied. The screenshots show the page at the narrow width, but the exact T1 input was not captured at that width. No claim is made that every T1–T12 browser case was completed. The repair changed the assessment-control presentation, while the helper in src/lib/availability.ts remained identical between the v1 and final exports.
~~~~

### B7

- **Tool:** ChatGPT (web) and local container shell
- **Model:** GPT-6
- **Date:** 2026-11-01
- **Stage:** Repair (post-export scope audit)
- **Source:** this SIS

**Prompt:**

~~~~text
Inspect the final exported Bolt project against the no-backend/no-database scope. Search for unused backend SDK dependencies. If @supabase/supabase-js is present but no source file imports or uses it, remove only that unused dependency from the final package manifest and lock file. Do not change App.tsx, the availability helper, UI behaviour or the v1 export. Report the exact cleanup and any test/build limitation.
~~~~

**Response:**

~~~~text
The final source contained no Supabase import, database client or authentication flow, but package.json still listed @supabase/supabase-js. The unused dependency was removed from the final package.json and package-lock.json only; the v1 export was not changed, and the availability source and page UI were left untouched. A post-cleanup npm install/build could not be independently run in the offline container because a dependency tarball was not cached. The Bolt UI response had previously reported a successful build and type check before this manifest-only cleanup, so the package should be reinstalled and built once more in an online environment before submission.
~~~~



## 12. Appendix B — Test output

### 12.1 Your suite

Command run from `sis-03/code/`: `python -m unittest -v`.

~~~~text
test_121_minutes_is_rejected (test_booking.BookingTests.test_121_minutes_is_rejected) ... ok
test_blocked_room_is_unavailable (test_booking.BookingTests.test_blocked_room_is_unavailable) ... ok
test_candidate_that_contains_existing_booking_is_rejected (test_booking.BookingTests.test_candidate_that_contains_existing_booking_is_rejected) ... ok
test_empty_existing_list_allows_valid_future_slot (test_booking.BookingTests.test_empty_existing_list_allows_valid_future_slot) ... ok
test_end_after_midnight_boundary_is_rejected (test_booking.BookingTests.test_end_after_midnight_boundary_is_rejected) ... ok
test_ending_exactly_at_midnight_is_allowed (test_booking.BookingTests.test_ending_exactly_at_midnight_is_allowed) ... ok
test_exactly_120_minutes_is_allowed (test_booking.BookingTests.test_exactly_120_minutes_is_allowed) ... ok
test_existing_list_is_not_mutated_after_available_check (test_booking.BookingTests.test_existing_list_is_not_mutated_after_available_check) ... ok
test_existing_list_is_not_mutated_after_rejected_check (test_booking.BookingTests.test_existing_list_is_not_mutated_after_rejected_check) ... ok
test_negative_start_is_rejected (test_booking.BookingTests.test_negative_start_is_rejected) ... ok
test_non_integer_candidate_values_are_rejected (test_booking.BookingTests.test_non_integer_candidate_values_are_rejected) ... ok
test_one_minute_after_now_is_allowed (test_booking.BookingTests.test_one_minute_after_now_is_allowed) ... ok
test_partial_overlap_is_unavailable (test_booking.BookingTests.test_partial_overlap_is_unavailable) ... ok
test_result_is_a_real_boolean (test_booking.BookingTests.test_result_is_a_real_boolean) ... ok
test_reversed_times_are_rejected (test_booking.BookingTests.test_reversed_times_are_rejected) ... ok
test_second_existing_booking_is_checked (test_booking.BookingTests.test_second_existing_booking_is_checked) ... ok
test_start_at_midnight_must_still_be_after_now (test_booking.BookingTests.test_start_at_midnight_must_still_be_after_now) ... ok
test_start_equal_to_now_is_rejected (test_booking.BookingTests.test_start_equal_to_now_is_rejected) ... ok
test_start_in_the_past_is_rejected (test_booking.BookingTests.test_start_in_the_past_is_rejected) ... ok
test_touching_at_existing_end_is_available (test_booking.BookingTests.test_touching_at_existing_end_is_available) ... ok
test_touching_at_existing_start_is_available (test_booking.BookingTests.test_touching_at_existing_start_is_available) ... ok
test_zero_length_interval_is_rejected (test_booking.BookingTests.test_zero_length_interval_is_rejected) ... ok

----------------------------------------------------------------------
Ran 22 tests in 0.000s

OK
~~~~

### 12.2 Path B only — three faults you planted

<!-- Path A: leave this table as it is. Path B: three rows — the line you broke, the AC it
     breaks, the test that failed. -->

| # | Line you broke | AC | Test that failed |
| --- | --- | --- | --- |
| 1 | | | |
| 2 | | | |
| 3 | | | |

## 13. Remaining limitations and known fails

| Check ID or limitation | Why it stays | What I would do next |
| --- | --- | --- |
| Baseline-first chronology | Section 2 now contains a short requirements summary, but it was prepared after AI-assisted work had started, so the required order was not met. | Keep the chronology note and do not backdate the baseline commit. |
| Reflection authorship | Section 10 contains an AI-assisted draft; the assignment asks for the student's own reflection. | Review and rewrite the draft in the student's own words before submission. |
| C1/C4 — incomplete page test matrix | The screenshots establish v1 T1/T2 and final T3/T10 only. Other browser cases have not been recorded; T8/T9 cannot be entered with the native time input. | Run T1–T12 on both v1 and final in the browser. Record exact results. Mark T8/T9 Not testable only with the input limitation explanation. |
| T12 — narrow-width case | The final responsive screenshot shows a 379 × 644 preview, but it does not capture T1 (11:00–12:00) at that width. | Set T1 exactly at the 379 px preview, click Check availability, capture the Available result, and replace the current narrow screenshot if needed. |
| Final npm build after dependency cleanup | The unused Supabase dependency was removed from the final manifest/lock file, but npm could not install fully in the offline container. | In an online environment, run `npm ci`, `npm run typecheck`, `npm run build` from `web/final/` and record the real output. |
| D2–D5/D13 — identity and Git | Student details, real repository commit hash, commit chronology and open PR are not in a ZIP export. | Fill `submission.yml` with real details; commit the baseline first where possible while honestly disclosing the chronology deviation, make 3+ authored commits, push branch `sis-03`, open but do not merge the PR. |
| E2/E3 — screenshot handling | The raw user screenshots are preserved in `evidence/source-originals/`; `final-narrow.png` is a crop isolating the 379 px portrait preview so it is portrait-shaped. | Keep the raw capture and describe the crop accurately; capture a clean portrait device screenshot if the instructor requires a full-screen original. |
| Timing deviation | Python and AI-assisted report drafts were prepared before the required baseline-first commit. | Do not claim that a later commit repairs the order. Ask the instructor how to record this deviation. |

**Current state:** the archive contains both Bolt exports, Python artifacts and the supplied screenshot evidence. It is not yet submission-ready: remaining browser cases, online build, student review of baseline/reflection, GitHub identity details, real commits and an open PR are still required.

