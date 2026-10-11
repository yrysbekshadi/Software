# Week 05 — AI-Assisted Coding: `can_book`

**Name:** Shadi Yrysbek  
**Group:** Not provided in the supplied files  
**Date:** 2026-10-12

## 1. Setup

| | |
| --- | --- |
| Assistant (tool) | ChatGPT |
| **Exact** model name | GPT-6 |
| Language and version | Python 3.13.5 (verification environment; check `python --version` in the repository you submit) |
| Path | A |
| My Week 04 declaration for touching bookings | allowed (provisional; verify against `week-04/submission.yml`) |

The earlier draft records the Week 04 choice as `allowed`, but `week-04/submission.yml` was not included in the supplied files, so this value still needs confirmation against the actual repository. AC4 in this lab explicitly allows touching endpoints. Before submitting, follow the handout workflow in a new chat and replace this draft plan/code/report evidence if the unchanged prompts produce different output.

---

## 2. Task 1 — the plan

**AI-generated plan used for this draft (not a transcript of a separate new-chat prompt run):**

```text
1. Reject the request unless 0 <= start < end <= 1440 (AC1).
2. Reject the request unless start > now (AC1).
3. Reject the request if end - start > 120; exactly 120 minutes is allowed (AC2).
4. Reject the request if blocked is True (AC3).
5. For every (booking_start, booking_end) in existing, reject if start < booking_end and end > booking_start. This detects overlap while allowing endpoints to touch (AC4).
6. If none of the checks rejects the request, return the Boolean True; otherwise return the Boolean False. Do not sort, append to, remove from, or otherwise modify existing (AC5 and the contract).

Boundary cases: start == end; start > end; start below 0; end == 1440 and end > 1440; start == now and start == now + 1; duration == 120 and 121; blocked room; partial, contained, containing and identical overlaps; touching at either endpoint; empty and multiple unsorted existing bookings; verify the input list remains unchanged.
```

**What the plan invented or changed.**

| # | What the plan said | What the contract or the AC says | What I did |
| --- | --- | --- | --- |
| 1 | No extra rule; each check is tied to AC1–AC5 or the input-unchanged contract. | AC1 defines bounds and future start; AC2 duration; AC3 blocked; AC4 overlap; AC5 Boolean result and unchanged list. | Kept the plan. Boundary cases are tests, not additional booking rules. |

**Boundary cases the assistant suggested that I kept as tests:**

- Zero-length and reversed intervals, day bounds, start equal to `now` and one minute after `now`.
- Duration of exactly 120 minutes and 121 minutes.
- Partial, contained, containing, identical and touching intervals; empty, multiple and unsorted existing bookings.
- Input-list immutability and Boolean return type.

---

## 3. Task 2 — the first version (v1), read before it was run

v1 is saved as `code/original/booking_v1.py` and has not been edited during this preparation: **yes**. Transparency note: this copy came from the AI-prepared draft in this conversation; I did not create the required separate fresh chat and capture the answer to PROMPT 2 there. Do not describe it as a transcript of that workflow.

**AC map.**

| # | Line in v1 | AC it implements | Correct as written? If not, why |
| --- | --- | --- | --- |
| 1 | `if not (0 <= start < end <= 1440): return False` | AC1 | Yes: enforces start/end order and day bounds. |
| 2 | `if start <= now: return False` | AC1 | Yes: only a start strictly later than `now` is accepted. |
| 3 | `if end - start > 120: return False` | AC2 | Yes: rejects durations over 120 and allows exactly 120. |
| 4 | `if blocked: return False` | AC3 | Yes: a blocked room is rejected. |
| 5 | `if start < booking_end and end > booking_start: return False` | AC4 | Yes: rejects overlap; strict comparisons allow touching endpoints. |
| 6 | `return True` after the loop | AC5 | Yes: reached only if every required check passed. |
| 7 | The function returns literal `False` on rejection and never mutates `existing`. | AC5 / contract | Yes: the result is a Boolean and the list is only read. |

**Anything in v1 that no AC asks for** (extra validation, a buffer between bookings, logging, saving the booking, a different return type):

- None observed. The implementation does not add a buffer, save anything, sort the list, or change the return type.

---

## 4. Task 3 — my tests

Base input for every row unless the row says otherwise: `now=540, blocked=False, existing=[(600, 660)]`.

| # | Test name | Request (start, end) | What differs from the base input | Expected | AC | Result on v1 | Result on final |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `test_touching_at_existing_end_is_allowed` | (660, 720) | none | True | AC4 | True | True |
| 2 | `test_overlap_is_rejected` | (630, 690) | none | False | AC4 | False | False |
| 3 | `test_blocked_room_is_rejected` | (660, 720) | `blocked=True` | False | AC3 | False | False |
| 4 | `test_exactly_120_minutes_is_allowed` | (720, 840) | none | True | AC2 | True | True |
| 5 | `test_121_minutes_is_rejected` | (720, 841) | none | False | AC2 | False | False |
| 6 | `test_starting_at_now_is_rejected` | (540, 570) | none | False | AC1 | False | False |
| 7 | `test_zero_length_is_rejected` | (700, 700) | `existing=[]` | False | AC1 | False | False |
| 8 | `test_reversed_interval_is_rejected` | (720, 700) | `existing=[]` | False | AC1 | False | False |
| 9 | `test_end_at_1440_is_allowed` | (1380, 1440) | `existing=[]` | True | AC1 | True | True |
| 10 | `test_end_after_1440_is_rejected` | (1380, 1441) | `existing=[]` | False | AC1 | False | False |
| 11 | `test_negative_start_is_rejected` | (-1, 30) | `now=0, existing=[]` | False | AC1 | False | False |
| 12 | `test_start_one_minute_after_now_is_allowed` | (541, 571) | none | True | AC1 | True | True |
| 13 | `test_overlap_from_left_is_rejected` | (570, 630) | none | False | AC4 | False | False |
| 14 | `test_booking_inside_existing_is_rejected` | (615, 645) | none | False | AC4 | False | False |
| 15 | `test_booking_containing_existing_is_rejected` | (570, 690) | none | False | AC4 | False | False |
| 16 | `test_identical_interval_is_rejected` | (600, 660) | none | False | AC4 | False | False |
| 17 | `test_touching_at_existing_start_is_allowed` | (570, 600) | none | True | AC4 | True | True |
| 18 | `test_second_booking_is_checked` | (720, 780) | `existing=[(600, 660), (700, 760)]` | False | AC4 | False | False |
| 19 | `test_empty_existing_list_allows_valid_request` | (600, 660) | `existing=[]` | True | AC4 | True | True |
| 20 | `test_unsorted_existing_list_is_not_modified` | (780, 840) | unsorted list of 3 bookings | True | AC5 / contract | True | True |
| 21 | `test_rejected_request_does_not_modify_existing` | (610, 650) | unsorted list of 3 bookings | False | AC5 / contract | False | False |
| 22 | `test_result_is_boolean` | (660, 720) | checks result type | True (`bool`) | AC5 | `bool` | `bool` |
| 23 | `test_one_minute_booking_at_day_end_is_allowed` | (1439, 1440) | `now=1438, existing=[]` | True | AC1, AC2 | True | True |
| 24 | `test_non_integer_time_is_outside_contract_and_not_validated` | (600.5, 660) | `start` is non-integer; outside contract | True in this Python implementation | outside contract; documented in §9.2 | True | True |

---

## 5. Task 4 — debugging with evidence

v1 passed all ten checker groups and all contract-based tests. Following the handout's instruction for this case, I added a valid final-slot edge case and did not change the implementation.

| # | Input (the full call) | Expected | Actual | Cause (quote the line) | Fix | Who proposed the fix |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `can_book(1439, 1440, now=1438, blocked=False, existing=[])` | `True` | `True` | `if not (0 <= start < end <= 1440):` permits `end == 1440`; `if start <= now: return False` does not reject `start=1439` when `now=1438`; the duration is 1 minute, the room is unblocked, and there are no existing bookings. | No code change: the observed result follows AC1–AC5. | ChatGPT assisted with the test; the result was verified by running the suite. |

**The debug prompt I sent, and the assistant's answer** (leave the block empty if you did not use it):

```text
Not used. v1 passed the contract checks; I followed the handout instruction to add an edge case and explain why no code change was needed.
```

---

## 6. Task 5 — the critique

**AI critique used for review (the required separate fresh-chat PROMPT 4 workflow was not performed):**

```text
1. The range check does not explicitly test that start and end are integers. This concerns the contract's integer-time statement, but the contract does not define behaviour for non-integer inputs.
2. The function does not validate the types of now, blocked, or existing. The contract explicitly says now is valid, blocked is Boolean, and existing contains valid tuples, so these are preconditions rather than required validation behaviour.
3. The overlap condition uses strict comparisons on both sides. This is correct: it rejects actual overlap while allowing endpoints to touch, as AC4 requires.
```

| # | Suggestion | accept / reject | Reason — cite the AC or the contract line | Suite after the change |
| --- | --- | --- | --- | --- |
| 1 | Add explicit integer checks for `start` and `end`. | reject | The contract defines the inputs as integer minutes but leaves non-integer behaviour open; the handout asks us to declare that decision in §9.2. Extra validation is not needed to satisfy AC1–AC5. | 23 tests, OK; no code change. |
| 2 | Validate `now`, `blocked`, and the shape of `existing`. | reject | The contract guarantees `now` is valid, `blocked` is Boolean, and `existing` contains valid tuples. No AC requires validation of inputs outside those stated preconditions. | 23 tests, OK; no code change. |
| 3 | Keep strict overlap comparisons. | accept | AC4 says touching endpoints are allowed. `start < booking_end and end > booking_start` is false when either endpoint merely touches. This was already correct, so no code change was needed. | 23 tests, OK; no code change. |

---

## 7. Change log — v1 to final

| # | What changed (the line, before → after) | Why | Evidence: the test or check that moved |
| --- | --- | --- | --- |
| 1 | No implementation change: `code/booking.py` remains identical to `code/original/booking_v1.py`. Added `test_one_minute_booking_at_day_end_is_allowed` to the test suite. | v1 satisfied AC1–AC5; the new valid edge case checks a one-minute booking ending at 1440. A separate float test documents the chosen `not-handled` behaviour for input outside the contract. | Checker F1–F10 all PASS; 24-test suite is green; M1–M10 all PASS. |

---

## 8. Evidence — real output

### 8.1 My suite, final run

```text
test_121_minutes_is_rejected (test_booking.BookingTests.test_121_minutes_is_rejected) ... ok
test_blocked_room_is_rejected (test_booking.BookingTests.test_blocked_room_is_rejected) ... ok
test_booking_containing_existing_is_rejected (test_booking.BookingTests.test_booking_containing_existing_is_rejected) ... ok
test_booking_inside_existing_is_rejected (test_booking.BookingTests.test_booking_inside_existing_is_rejected) ... ok
test_empty_existing_list_allows_valid_request (test_booking.BookingTests.test_empty_existing_list_allows_valid_request) ... ok
test_end_after_1440_is_rejected (test_booking.BookingTests.test_end_after_1440_is_rejected) ... ok
test_end_at_1440_is_allowed (test_booking.BookingTests.test_end_at_1440_is_allowed) ... ok
test_exactly_120_minutes_is_allowed (test_booking.BookingTests.test_exactly_120_minutes_is_allowed) ... ok
test_identical_interval_is_rejected (test_booking.BookingTests.test_identical_interval_is_rejected) ... ok
test_negative_start_is_rejected (test_booking.BookingTests.test_negative_start_is_rejected) ... ok
test_non_integer_time_is_outside_contract_and_not_validated (test_booking.BookingTests.test_non_integer_time_is_outside_contract_and_not_validated) ... ok
test_one_minute_booking_at_day_end_is_allowed (test_booking.BookingTests.test_one_minute_booking_at_day_end_is_allowed) ... ok
test_overlap_from_left_is_rejected (test_booking.BookingTests.test_overlap_from_left_is_rejected) ... ok
test_overlap_is_rejected (test_booking.BookingTests.test_overlap_is_rejected) ... ok
test_rejected_request_does_not_modify_existing (test_booking.BookingTests.test_rejected_request_does_not_modify_existing) ... ok
test_result_is_boolean (test_booking.BookingTests.test_result_is_boolean) ... ok
test_reversed_interval_is_rejected (test_booking.BookingTests.test_reversed_interval_is_rejected) ... ok
test_second_booking_is_checked (test_booking.BookingTests.test_second_booking_is_checked) ... ok
test_start_one_minute_after_now_is_allowed (test_booking.BookingTests.test_start_one_minute_after_now_is_allowed) ... ok
test_starting_at_now_is_rejected (test_booking.BookingTests.test_starting_at_now_is_rejected) ... ok
test_touching_at_existing_end_is_allowed (test_booking.BookingTests.test_touching_at_existing_end_is_allowed) ... ok
test_touching_at_existing_start_is_allowed (test_booking.BookingTests.test_touching_at_existing_start_is_allowed) ... ok
test_unsorted_existing_list_is_not_modified (test_booking.BookingTests.test_unsorted_existing_list_is_not_modified) ... ok
test_zero_length_is_rejected (test_booking.BookingTests.test_zero_length_is_rejected) ... ok

----------------------------------------------------------------------
Ran 24 tests in 0.000s

OK
```

### 8.2 The checker, final run

```text
Week 05 - can_book: the function, your tests, the evidence   (Path A)

PASS   F1   the six cases from the task table           6 of 6 cases
PASS   F2   AC1 time order and day bounds               5 of 5 cases
PASS   F3   AC1 the start is in the future              5 of 5 cases
PASS   F4   AC2 at most 120 minutes                     3 of 3 cases
PASS   F5   AC3 a blocked room accepts nothing          2 of 2 cases
PASS   F6   AC4 every kind of overlap is rejected       5 of 5 cases
PASS   F7   AC4 touching endpoints are allowed          3 of 3 cases
PASS   F8   AC4 every existing booking is checked       4 of 4 cases
PASS   F9   AC5 the result is a real Boolean            3 of 3 cases
PASS   F10  AC5 the inputs are left unchanged           2 of 2 cases
PASS   O1   the assistant's first version is kept       v1 kept (14 lines)
PASS   S1   your suite has at least 11 tests            24 tests
PASS   S2   your suite is green on your own code        24 tests, OK
PASS   M1   your tests catch a fault in AC1             caught by test_starting_at_now_is_rejected
PASS   M2   your tests catch a fault in AC1             caught by test_end_after_1440_is_rejected
PASS   M3   your tests catch a fault in AC1             caught by test_zero_length_is_rejected
PASS   M4   your tests catch a fault in AC2             caught by test_exactly_120_minutes_is_allowed
PASS   M5   your tests catch a fault in AC3             caught by test_blocked_room_is_rejected
PASS   M6   your tests catch a fault in AC4             caught by test_touching_at_existing_end_is_allowed, test_touching_at_existing_start_is_allowed
PASS   M7   your tests catch a fault in AC4             caught by test_rejected_request_does_not_modify_existing, test_second_booking_is_checked
PASS   M8   your tests catch a fault in AC4             caught by test_booking_containing_existing_is_rejected
PASS   M9   your tests catch a fault in AC5             caught by test_unsorted_existing_list_is_not_modified
PASS   M10  your tests catch a fault in AC5             caught by test_rejected_request_does_not_modify_existing, test_unsorted_existing_list_is_not_modified
PASS   L1   report 1: tool, model and language          tool, model and language recorded
PASS   L2   report 2: the plan, and what you corrected  plan pasted, 1 row(s) on what you corrected or verified
PASS   L3   report 3: v1 mapped to AC1-AC4              7 conditions mapped, AC1-AC4 all present
PASS   L4   report 4: at least 11 of your tests listed  24 tests listed
PASS   L5   report 5: debugging evidence                1 row(s) of input / expected / actual
PASS   L6   report 6: the critique, each point judged   critique pasted, 3 points judged
PASS   L7   report 7: change log                        1 change-log row(s)
PASS   L8   report 8.1: real output of your suite       suite output pasted
PASS   L9   report 10: conclusion of 120-180 words      161 words
------------------------------------------------------------------------------
v1 (code/original/booking_v1.py): passes F1 F2 F3 F4 F5 F6 F7 F8 F9 F10 - fails nothing - identical to your final: yes
SUMMARY pass=32 fail=0 error=0   (32 checks)
Behaviour and shape are clean. This says nothing about the quality of your review.
```

### 8.3 Path B only — three faults I planted myself

Not applicable — Path A (Python); the supplied checker tests the function directly.

---

## 9. What still fails, and what the contract does not say

### 9.1 Checks I am keeping as FAIL or ERROR

None in the function, suite, or mutant checks (F1–F10, S1–S2, M1–M10). The last checker run included below reports all 32 checks as PASS. The submission validator's `checker.commit` check remains pending until this folder is committed on the actual `week-05` branch in the student's `se-practice` repository; that Git-specific value is not fabricated here.

| Check | Why it stays |
| --- | --- |
| none | No behavioural FAIL or ERROR is being kept. |

### 9.2 Outside the contract

The contract says times are integer minutes, but it does not define behaviour for non-integer values. This Python function does not explicitly reject a float such as `600.5`; the comparison checks accept it if the other conditions pass. I record the assumption as `not-handled`: non-integer input is outside the contract, so I do not add extra validation that the acceptance criteria did not request. The dedicated test documents the observed behaviour but is not used to catch mutant faults.

### 9.3 A bound that never decides

The lower bound `0 <= start` can never be the only failed part of AC1. Since `now` is guaranteed to be at least 0, any negative `start` is also not greater than `now`, so the future-start condition `start > now` fails as well.

---

## 10. Conclusion (120–180 words)

The overlap condition is `start < booking_end and end > booking_start`. The first comparison checks whether the request begins before the existing booking ends; the second checks whether it ends after that booking starts. Only when both are true do the intervals share time and the request is rejected. Because both comparisons are strict, endpoints may touch, as AC4 requires. No mutant survived the final checker run, so I cannot honestly name a fault that the final suite missed. Input mutation needed special attention: tests checking only the Boolean result would not detect a function that silently sorted or edited `existing`. The two immutability tests compare the list with a copy before and after both an accepted and a rejected request. I also documented that float behaviour is outside the contract; this Python function currently accepts `600.5`, and I did not add unrequested validation. Before submission, I still need to explain these decisions independently and complete the required fresh-chat workflow.
