# Week 08 — Lab report

**Name:** Shadi Yrysbek  
**Group:** not provided  
**Date:** 8 November 2026

This package starts from the permitted Week 07 `starter/` project because no Week 06 project or completed Week 07 project was present in the supplied repository. Do not describe it as a continuation of a Week 06 app. Replace every pending item with your own verified run/evidence before submission.

---

## 1. Setup

| | |
| --- | --- |
| Assistant I debugged with (tool) | ChatGPT |
| Exact model (with its version, or `not displayed`) | GPT-6 (model label displayed in this conversation) |
| Where the skill was installed (ChatGPT / Claude web / Claude Code / prompt-only simulation) | Prompt-only simulation — not yet performed; use this fallback if a skill upload is unavailable. |
| Where I ran the tests (Bolt terminal / my computer / Codespace) | Not yet run by the student; run in the local computer terminal or Codespace. |
| Vitest version (the `RUN  v…` line of a run) | Not recorded — no successful Vitest run is available yet. |
| Language of my booking module (`ts` or `js`) — the file I copied from `buggy/` | ts |

---

## 2. Task 1 — baseline, buggy code, failing tests

### 2.1 My Week 07 suite on my own code

**Pending actual Vitest output.** The app and 17-case Week 07 final suite are included. The two Week 08 regression tests are supplied separately in `regression-tests-snippet.ts.txt` so they can be added after the buggy function has been copied, preserving the required sequence. Run `npx vitest run` in `week-08/app/` before replacing the function, then paste the full, unedited output here.

```text
NOT RUN — paste the real `npx vitest run` output here.
```

### 2.2 The same suite on the provided canBook

**Pending actual Vitest output.** Copy the entire function from `buggy/booking.ts` into `app/src/booking.ts` without changing it, then run the same suite. Restore the repaired final version only after recording the failures.

```text
NOT RUN — paste the real `npx vitest run` output with the provided buggy function here.
```

### 2.3 One failing test per bug

After copying the supplied buggy function, append the two blocks from `regression-tests-snippet.ts.txt` inside the existing test `describe` block. The 17 original tests plus the two regression tests make 19. Both BUG-A and BUG-B must fail on the supplied buggy function before either fix. The exact output must come from your own terminal run.

```text
NOT RUN — paste the real run showing both BUG-A and BUG-B failing here.
```

---

## 3. Defect log

The `Actual` column below is a source-level prediction from the supplied function, **not a recorded Vitest result**. Replace it with the actual observed result after running the tests.

| Defect | Test ID | Input | Expected | Actual | Suspected cause (line and why) |
| --- | --- | --- | --- | --- | --- |
| BUG-A | BUG-A | Request 660–780; bookings 600–660 and 780–840; now 540; not blocked | true: both endpoints touch but do not overlap (AC4) | Source predicts false: inclusive comparisons treat either touching endpoint as overlap; not yet run | `if (start <= b.end && end >= b.start) return false;` uses `<=` and `>=`, so equality is incorrectly considered overlap. |
| BUG-B | BUG-B | Request 720–780; booking 600–660; now 540; not blocked | true and the bookings array unchanged (AC5) | Source predicts true return value but mutates the array by appending the new interval; not yet run | `bookings.push({ start, end });` mutates the caller's input even though the function is only checking availability. |

---

## 4. Tasks 2–3 — the skill

**The checks from the deck, before you zip it.** The file below is supplied as a reference copy. The assignment says to type it by hand; retype it yourself in a plain-text editor before you claim the check is complete.

| Check | yes / no |
| --- | --- |
| The file is plain UTF-8 text, named exactly `SKILL.md` (not `SKILL.md.txt`) | yes |
| The first and the closing YAML delimiter are exactly three hyphens: `---` | yes |
| `name` is lowercase with hyphens, and `description` says WHEN to use it | yes |
| I read the whole file once: no passwords, API keys or private student data | no — student must read and manually retype it |

**The contents of `skills/bug-detector.zip`.** This is the package listing of the reference ZIP; regenerate it after manually retyping your file.

```text
bug-detector/SKILL.md
```

**Installation.** Not yet installed or simulated. If ChatGPT/Claude skill upload is unavailable, follow the instructor's prompt-only fallback in a fresh chat: paste the hand-typed SKILL.md as the first message, explicitly state that it is a prompt-only simulation, then ask the deck's skill question. Save the actual screenshot as `evidence/install.png`; no screenshot is fabricated in this package.

---

## 5. Task 4 — without the skill

Use a fresh chat with no skill enabled. The input template is also saved in `diagnosis-input-template.txt`. Replace its failure-output placeholder with the real BUG-A failure from §2.3. Paste exactly what you send, then paste the answer unedited.

```text
Find the root cause of the failed room-booking test. Propose minimal patch and regression test. Do not edit code.

ACCEPTANCE CRITERIA (AC1–AC6)

AC1: Accept a candidate interval only when 0 ≤ start < end ≤ 1440 and start is after the supplied current time.
AC2: Reject a booking longer than 120 minutes.
AC3: Reject the request when the selected room is blocked.
AC4: Reject any interval that overlaps an existing booking; touching endpoints are allowed.
AC5: Show a clear Available / Unavailable decision without changing the existing booking data.
AC6: The page remains usable at desktop and narrow/mobile width and gives understandable validation feedback.

FAILING TEST OUTPUT

[REPLACE THIS NOTE WITH THE REAL BUG-A FAILING VITEST OUTPUT FROM §2.3. Use the exact same output in both chats.]

PROVIDED canBook CODE

export function canBook({ start, end, now, blocked, bookings }: {
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
} 
```

**The assistant's answer, pasted unedited:**

```text
PENDING — paste the actual answer from your fresh chat. Do not submit this note as an assistant transcript.
```

---

## 6. Task 5 — with the skill

Use a second fresh chat with the hand-typed skill enabled, or with the prompt-only simulation. Keep the AC1–AC6, failing output, and buggy function byte-for-byte the same as §5; only the question changes.

```text
Use the bug-detector skill to diagnose the failed room-booking test.

ACCEPTANCE CRITERIA (AC1–AC6)

AC1: Accept a candidate interval only when 0 ≤ start < end ≤ 1440 and start is after the supplied current time.
AC2: Reject a booking longer than 120 minutes.
AC3: Reject the request when the selected room is blocked.
AC4: Reject any interval that overlaps an existing booking; touching endpoints are allowed.
AC5: Show a clear Available / Unavailable decision without changing the existing booking data.
AC6: The page remains usable at desktop and narrow/mobile width and gives understandable validation feedback.

FAILING TEST OUTPUT

[REPLACE THIS NOTE WITH THE REAL BUG-A FAILING VITEST OUTPUT FROM §2.3. Use the exact same output in both chats.]

PROVIDED canBook CODE

export function canBook({ start, end, now, blocked, bookings }: {
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
} 
```

**The assistant's answer, pasted unedited:**

```text
PENDING — paste the actual answer from your second fresh chat. Do not submit this note as an assistant transcript.
```

Did the environment show that the skill was invoked? not shown — no skill invocation has been observed yet.

---

## 7. Comparison — judged against the actual code

Fill both columns only after reading the two real answers in §§5–6. Judge each answer against `buggy/booking.ts` and the actual failing tests, not against the other answer.

| Criterion | No skill | With skill |
| --- | --- | --- |
| Correct root cause | | |
| Reproducible test | | |
| Minimal proposed patch | | |
| Unsupported claims | | |
| Clarity of explanation | | |

**Which bugs did each answer find?**

Pending actual transcripts. Do not infer that the skill is better merely because it was enabled.

---

## 8. Task 6 — repair and regression

The final `app/src/booking.ts` in this package contains the two minimal changes below. To earn the reproduction evidence, you must first copy the provided buggy function over it and record the red tests, then restore/apply each fix in its own commit and record the real runs.

### 8.1 The BUG-A patch

The prepared baseline still has the pre-Week-08 function; apply this one-line change only after the BUG-A failure has been recorded.

```diff
-    if (start <= b.end && end >= b.start) return false;
+    if (start < b.end && end > b.start) return false;
```

**Real targeted BUG-A run and full-suite output:** not yet run. Run the BUG-A test first, then `npx vitest run`, and paste the actual terminal output here.

### 8.2 The BUG-B patch and the final run

Apply this separate one-line deletion only after BUG-A has been fixed and tested.

```diff
-  bookings.push({ start, end });
```

**Real targeted BUG-B run and final full-suite output:** not yet run. After BUG-A is fixed, run the BUG-B test; then remove the mutation line, run `npx vitest run`, and paste the actual output. The final committed suite must contain the same 19 tests.

---

## 9. What still fails, and what AI-assisted debugging cannot do

### 9.1 Checks I am keeping as FAIL or ERROR

I ran the supplied static checker on this prepared baseline from `week-08/`. It reported **19 PASS, 11 FAIL, 1 ERROR (31 checks)**. These are the current package-stage results, before the student runs Vitest, inserts the regression tests, retypes the skill, or collects actual chats/screenshots. Rerun the checker after completing the lab and update this table and `submission.yml` with the then-current IDs.

| Check | Why it stays |
| --- | --- |
| B3 | The app currently contains the extracted Week 07 implementation. The Week 08 provided function has not yet been copied into it and repaired with only two minimal changes. |
| S3 | The baseline suite has 17 cases; add BUG-A and BUG-B to reach the required 19. |
| S4 | The BUG-A regression test is provided in `regression-tests-snippet.ts.txt` but has not yet been added to the suite. |
| S5 | The BUG-B regression test is provided in `regression-tests-snippet.ts.txt` but has not yet been added to the suite. |
| E1 | The required `evidence/install.png` is intentionally absent; capture the real skill-install or prompt-only simulation screen. |
| R1 | No real Vitest baseline output has been pasted yet. |
| R2 | The suite has not been run with the supplied buggy function and regression tests; no failing output is claimed. |
| R3 | No final green Vitest output has been produced yet. |
| L3 | The student has not yet read and manually retyped the skill file or recorded the actual installation/simulation. |
| L4 | The fresh-chat answer without the skill has not been collected; the prepared input still contains a placeholder for the real failure output. |
| L5 | The fresh-chat answer with the skill has not been collected; the prepared input still contains a placeholder for the real failure output. |
| L6 | The comparison columns are intentionally blank until both actual chat answers have been collected. |

### 9.2 One limitation of AI-assisted debugging

In this preparation environment, `npm install` timed out while trying to reach the package registry, so Vitest could not be installed or run here. Static inspection can predict the two defects, but it cannot replace a real failing test, prove the fixes, show that the UI works in a browser, or establish what a separate fresh chat actually answered.

---

## 10. Conclusion (80–150 words)

**Draft for the student to rewrite or confirm after the real runs and comparison.**

The two defects affect different parts of the booking decision. BUG-A comes from treating equal endpoints as an overlap, even though AC4 allows bookings to touch. BUG-B comes from appending the candidate interval to the caller's bookings array, which violates AC5 because checking availability must not change existing data. The two regression tests are designed to expose these behaviors separately: one checks a touching request, and the other checks that an available request leaves the array unchanged. The final suite can provide evidence for its nineteen tested cases, but it cannot establish every possible booking behavior or replace the five manual UI checks. Whether the debugging skill improved the diagnosis must be decided from the two actual chat answers.
