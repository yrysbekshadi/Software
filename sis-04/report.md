# SIS #04 — Report

## 1. Setup and starting point

| Item | Value |
|---|---|
| Assistant (tool) | ChatGPT |
| Assistant model | GPT-6 |
| Starting point | week-08 |
| Baseline commit | `e0a6302` |
| Language (ts or js) | ts |
| Vitest version | ^3.2.4 declared in package.json; v3.2.7 installed and used in actual test runs |
| Where I ran the tests | Attempted in the provided execution container; npm registry access and a cached Vitest package were unavailable |

### 1.1 Baseline run

Command: `npx vitest run`

Environment: Windows PowerShell
Vitest: v3.2.7

```text
RUN v3.2.7 C:/Users/yrysb/Desktop/Software-Repo-baseline/sis-04/app

✓ src/booking.test.ts (17 tests) 4ms

Test Files  1 passed (1)
Tests       17 passed (17)
Duration    588ms
```

## 2. Context for the assistant

### 2.1 Repository map at baseline

```text
sis-04/app/
  index.html              Vite HTML shell; mounts #root and loads src/main.tsx
  package.json            React 18, Vite, TypeScript, Vitest; dev/build/test scripts
  tsconfig.json           strict TypeScript configuration
  vite.config.ts          Vite React plugin configuration
  src/
    App.tsx               page state, two-room catalog, room selection, time conversion, check handler and UI
    booking.ts            canBook({ start, end, now, blocked, bookings })
    booking.test.ts       existing canBook regression tests
    main.tsx              React entry point and global CSS import
    index.css             page layout and responsive rules
```

### 2.2 Context message used for the analysis

The following context was assembled from the course brief and repository inspection in this conversation. It was not sent as a separate fresh-chat message; this is a workflow deviation from the handout and is recorded rather than hidden.

```text
I am extending my Week 08 Smart Campus Room Availability Checker in sis-04/app. The baseline repository map is: index.html is the Vite page shell; package.json defines React, Vite, TypeScript and Vitest scripts; tsconfig.json enables strict TypeScript; vite.config.ts enables React; src/main.tsx mounts App and imports index.css; src/index.css holds layout and responsive styles; src/App.tsx currently contains the Room type, a two-room catalog, React state, time parsing, the check handler and the page UI; src/booking.ts contains canBook; src/booking.test.ts contains existing regression tests.

Preserve AC1–AC6: reject invalid/past time ranges; enforce a 120-minute maximum; reject blocked rooms; reject overlaps but allow endpoint-touching; do not mutate booking data; keep feedback clear and responsive on desktop/mobile. Add F1–F5: capacity >= attendees; every selected equipment item must exist in a room; blocked rooms must never be reported available; show a clear empty state; changing the selected room must refresh the result using that room's own bookings.

Use at least four fictional rooms with id, name, capacity, equipment, blocked and bookings. Required modules/signatures are rooms.ts with Room and ROOMS; filter.ts with filterRooms(rooms, { attendees, equipment }); booking.ts retaining canBook and adding checkRoom(rooms, roomId, { start, end, now }); App.tsx and components import the modules and contain no catalog or rules. Constraints: no login, payments, live APIs, database, browser storage or non-fictional data. Please give a numbered small-step plan and maintainability risks with precise file/function evidence; do not rewrite the app wholesale.
```

## 3. Codebase analysis

### 3.1 Maintainability risks

| # | Risk | Where (file / function) | Evidence from the unchanged Week 08 baseline | Priority |
|---|---|---|---|---|
| 1 | Room catalog and Room type are embedded in the UI and only describe two rooms. | `src/App.tsx`, `Room` and `ROOMS` | The local type has only id, name, blocked and bookings; the two objects are in the same file. No independent rooms.ts exists. | High |
| 2 | A page-level blocked checkbox is passed to canBook, while each room also has a blocked field that the check handler does not use. | `src/App.tsx`, `App()` and `check()` | The global blocked state controls the checkbox and is passed to canBook; the selected room contributes only its bookings. | High |
| 3 | Changing the selected room does not invalidate the previous result. | `src/App.tsx`, room select handler | The handler calls setRoomId(...), while setResult(null) occurs in check(), not in the room-change handler. | High |
| 4 | UI time-range validation duplicates booking validation and the day-end boundary. | `src/App.tsx`, `check()`; `src/booking.ts`, `canBook()` | check() checks start/end for an error message and uses 1440; canBook independently checks the valid range. | Medium |
| 5 | Time parsing and formatting are embedded in the page instead of reusable helpers. | `src/App.tsx`, `toMinutes()` and `fmt()` | The page owns both conversion helpers; a second component would need to duplicate or move them. | Medium |

### 3.2 Numbered improvement plan

1. Preserve the unchanged Week 08 app in app/ and record the baseline Vitest run before code changes.
2. Add a typed fictional catalog in src/rooms.ts with at least four complete rooms.
3. Add tests for capacity and ALL-equipment behavior, then implement filterRooms in src/filter.ts.
4. Keep canBook behavior unchanged and add checkRoom in src/booking.ts, delegating to the selected room's own blocked flag and bookings.
5. Add fixed-catalog tests for AC1–AC5, F1–F5, B1–B6 and INT.
6. Wire the page to the modules, remove page-level blocked state and derive availability from the selected room to prevent stale feedback.
7. Split filter, room-list, check-form and result markup into UI components; move time conversion/formatting into time.ts.
8. Add the after diagram, verify the code and tests on a connected environment, capture five screenshots, run the checker and validator, and record measured results.

### 3.3 One AI suggestion rejected or modified

| Suggestion | Decision | Why |
|---|---|---|
| Use equipment.some(...) so a room matches when it has at least one selected item. | Modified | F2 says ALL selected equipment is required, so filter.ts uses equipment.every(...); T19 checks that a room with only one of two selected items is excluded. |

## 4. Feature extension

### 4.1 What I added

src/rooms.ts contains five fictional rooms. Each has an id, name, capacity, equipment list, blocked flag and its own bookings. The catalog is A-101 (12 seats; projector and whiteboard), B-204 (30 seats; projector, whiteboard and video call), C-310 (8 seats; whiteboard and computers), D-015 (60 seats; projector and video call), and E-120 (20 seats; projector, whiteboard and computers; blocked).

filterRooms applies F1 (capacity >= attendees) and F2 (equipment.every(...)). Blocked rooms remain visible with a Blocked label; checkRoom handles availability and passes the selected room's own blocked and bookings to canBook. If no room matches, RoomList displays an empty state. The page stores the last time request and calculates availability from the currently selected room on every render, so changing rooms refreshes the result without pressing Check again.

### 4.2 Demonstration

The five JPEG screenshots in this folder came with the supplied sis-04-package(1).zip. Its AI_USAGE.md says they were captured by Claude Sonnet 5.5 using headless Chromium/Playwright from an esbuild bundle, not by the student using npm run dev. They are disclosed as package-provided evidence and should be replaced with fresh local/Codespace captures before final grading if possible.

| Screenshot | What it shows |
|---|---|
| evidence/filter-match.jpg | 15 attendees with projector and whiteboard selected; B-204 and blocked E-120 remain because both match capacity/equipment. |
| evidence/filter-empty.jpg | 40 attendees with whiteboard selected; zero rooms match and the page displays the F4 empty-state message. |
| evidence/switch-a.jpg | No filters, A-101 selected, current time 09:00 and request 10:30–11:30; result is Unavailable because A-101 is booked 10:00–11:00. |
| evidence/switch-b.jpg | The same 10:30–11:30 request with B-204 selected; result becomes Available because B-204 is only booked 13:00–14:30. |
| evidence/narrow.jpg | Portrait phone viewport; 15 attendees and projector + whiteboard; fields stack vertically and the page remains readable. |

## 5. Refactoring

### 5.1 Module responsibilities after

| Module or component | Responsibility |
|---|---|
| src/rooms.ts | Room type, five-room ROOMS catalog and EQUIPMENT_OPTIONS; data only. |
| src/booking.ts | canBook preserves AC1–AC5; checkRoom delegates using the chosen room's own data; shared range constants/helpers. |
| src/filter.ts | filterRooms implements F1 capacity and F2 ALL-equipment matching. |
| src/time.ts | Parses time input and formats times/ranges for display. |
| src/App.tsx | Owns page state and connects modules/components; no room literals or booking/filter rule. |
| src/components/FilterPanel.tsx | Attendee input and required-equipment checkboxes. |
| src/components/RoomList.tsx | Matching room list, selected state, blocked label and F4 empty state. |
| src/components/CheckForm.tsx | Current/start/end fields, 24:00 option, validation feedback and Check action. |
| src/components/ResultBanner.tsx | Clear Available/Unavailable result for selected room and time range. |
| src/booking.test.ts | 17 fixed-catalog tests for original booking rules and chosen-room checks. |
| src/filter.test.ts | 10 fixed-catalog tests for filtering and integration. |

### 5.2 Design decisions

| Decision | Alternative | Why |
|---|---|---|
| Derive availability from selected room and stored time request on every render. | Store a boolean and reset it on selection/filter events. | Stored results can become stale when a filter hides a room or the user changes rooms; a derived value enforces F5 and is exercised by T14/T15. |
| Keep blocked rooms visible with a Blocked label. | Hide blocked rooms inside filterRooms. | F1/F2 define the filter by seats/equipment; blocked status belongs to checkRoom/F3. Showing the room explains why it cannot be booked and lets T27 test both visibility and unavailability. |
| Share isValidRange, DAY_END and MAX_DURATION from booking.ts. | Repeat range checks and constants in the UI. | One source prevents UI messages and canBook from drifting while retaining AC1–AC5 decisions. |

### 5.3 Duplication removed

| Before | After |
|---|---|
| App.tsx and booking.ts repeated the start/end validity decision. | isValidRange() in booking.ts is shared by canBook and CheckForm. |
| App.tsx and booking.ts repeated the end-of-day boundary 1440. | DAY_END in booking.ts is the single shared boundary. |
| App.tsx held a global blocked state alongside each room's blocked field. | The room catalog is the single source; checkRoom forwards the selected room status. |

## 6. Automated tests

### 6.1 Test plan

| ID | Test title(s) | Input → expected result |
|---|---|---|
| AC1 | T01 AC1, T02 AC1, T03 AC1 | Equal/reversed/past intervals are rejected; a future free interval is accepted. |
| AC2 | T04 AC2 B1, T05 AC2 B2 | Exactly 120 minutes → true; 121 minutes → false. |
| AC3 | T06 AC3 | Blocked room unavailable even when its time interval is free. |
| AC4 | T07 AC4 B3, T08 AC4 B3, T09 AC4 B4, T10 AC4 B4, T11 AC4 B4 | Endpoint touching → true; overlaps → false. |
| AC5 | T12 AC5, T17 AC5 F5 | Booking arrays and room catalog remain unchanged. |
| F1 | T18 F1 | Rooms below attendee count are excluded. |
| F2 | T19 F2, T20 F2, T21 F2 | ALL selected equipment must be present; no selection imposes no restriction. |
| F3 | T13 F3, T27 INT F3 | A blocked room is never available. |
| F4 | T22 F4, T23 F4 | No capacity/equipment match returns an empty list. |
| F5 | T14 F5, T15 F5, T16 F5 | Same interval checked against chosen room's bookings; unknown id → false. |
| B1 | T04 AC2 B1 | 120-minute boundary → true. |
| B2 | T05 AC2 B2 | 121-minute boundary → false. |
| B3 | T07 AC4 B3, T08 AC4 B3 | Touching before/after an existing booking → true. |
| B4 | T09 AC4 B4, T10 AC4 B4, T11 AC4 B4 | Overlapping intervals → false. |
| B5 | T24 B5 | Capacity equal to attendees is included. |
| B6 | T25 B6 | Capacity one below attendees is excluded. |
| INT | T26 INT, T27 INT F3 | Filter results are checked using each returned room's own data. |

### 6.2 Commands

The baseline and final Vitest suites and the production build were executed successfully in Windows PowerShell. The actual results are recorded in sections 1.1 and 6.3.

```bash
cd sis-04/app
npm install
npx vitest run
npm run build
cd ../..
python tests/check_sis.py
```

### 6.3 Final run

Command: `npx vitest run`

Environment: Windows PowerShell
Vitest: v3.2.7

```text
RUN v3.2.7 C:/Users/yrysb/Desktop/Software-Repo/sis-04/app

✓ src/booking.test.ts (17 tests) 4ms
✓ src/filter.test.ts (10 tests) 4ms

Test Files  2 passed (2)
Tests       27 passed (27)
Duration    535ms
```

## 7. Quality evaluation

| Measure | Original | Final | How I obtained it |
|---|---|---|---|
| Automated tests passed / total | 17/17 | 27/27 | Ran `npx vitest run` in the original baseline and final app. Baseline: 17 passed, 1 test file. Final: 27 passed, 2 test files. |
| Duplicated logic locations removed | 0 refactored | 3 consolidated | Compared baseline App.tsx and booking.ts with the final modules. Three duplicated or conflicting logic locations were consolidated, as listed in section 5.3. |
| Code structure | 5 files in app/src | 13 files in app/src | Counted source files in the original baseline and final app/src directories. |
| Remaining limitation | Two-room catalog, no capacity/equipment filters, global blocked checkbox and stale result after room switching. | Room catalog and bookings are fictional and stored in memory; no persistent storage or live campus data. | Compared the original App.tsx with the final rooms.ts and booking.ts. |

**Build verification:** `npm run build` — PASS. TypeScript compilation succeeded; Vite 5.4.21 transformed 39 modules and completed the production build in 551 ms.

**Dependency note:** Both `npm install` runs reported 5 vulnerabilities: 2 moderate, 1 high and 2 critical. No forced dependency upgrades were applied.

## 8. AI evidence appendix

### 8.1 Exchange 1

**Tool and model:** ChatGPT, GPT-6
**Date:** 2026-11-22 (Asia/Almaty)
**Purpose:** Interpret the assignment and begin inspecting the supplied archives and repository.
**Problems found:** The uploaded ZIPs contain different variants and the final package still needs real verification.
**Changes made:** Identified the branch/folder/PR requirements and compared the uploaded package contents.
**Verified by:** Read the two-page handout and inspected the ZIP folder structures; no test output was invented.

**Prompt:**
```text
SIS #04 - AI-Assisted Software Evolution, Refactoring and Quality Improvement. Extend the working Smart Campus checker with a 4+ room catalog, filters, separate modules, AC1-AC6 preservation, 10+ tests and evidence. Report is sis-04/report.md. Submit the Pull Request URL, not the repository URL. No file uploads or email.
```

**Output used:**
```text
The assistant planned to inspect the uploaded ZIP packages and GitHub repository, identify a legitimate starting point, verify what artifacts were actually present, and avoid inventing tests, screenshots, metrics or AI exchanges. The handout requires a baseline commit, analysis before app/src edits, a 4+ room catalog, F1-F5, refactoring, 10+ tests and an open PR.
```

### 8.2 Exchange 2

**Tool and model:** ChatGPT, GPT-6
**Date:** 2026-11-23 (Asia/Almaty)
**Purpose:** Select one uploaded package and decide how to use it with the real Week 08 baseline.
**Problems found:** The selected package's README says its 27-test run used a Vitest stand-in, not the real Vitest runner; its five screenshots were generated by the package author.
**Changes made:** Selected sis-04-package(1).zip as the implementation source, retaining the actual Week 08 project as the baseline and disclosing screenshot provenance.
**Verified by:** Inspected READ-FIRST.md, sandbox-verification/README.txt, staged overlays and screenshot files in the selected archive.

**Prompt:**
```text
выбери один и давай сделаем этот sis4
```

**Output used:**
```text
The assistant selected sis-04-package(1).zip as the implementation source because it contains the staged room catalog, filter, booking logic, UI components, tests, diagrams and browser screenshots. The assistant also noted that the real Week 08 app must remain the unchanged baseline, and that package-provided screenshots and test limitations must be disclosed.
```

### 8.3 Exchange 3

**Tool and model:** ChatGPT, GPT-6
**Date:** 2026-11-23 (Asia/Almaty)
**Purpose:** Continue implementation and validate the source package's test claims.
**Problems found:** Neither the package sandbox nor this execution environment supplied a real Vitest run; npm packages were unavailable offline.
**Changes made:** Kept the implementation and tests, recorded the actual ENOTCACHED failures and did not claim 27/27.
**Verified by:** Attempted npm install --offline and npx --offline vitest run; inspected the resulting errors, modules and screenshots.

**Prompt:**
```text
выбери один и давай сделаем этот sis4
```

**Output used:**
```text
The assistant found the package's complete implementation path: rooms, booking and filter modules, a refactored App with separate UI components, 27 requirement-labelled tests, before/after PlantUML diagrams and five Playwright screenshots. The assistant warned that the stand-in test result must not be represented as Vitest, and that a connected npm install plus real test/build run remain necessary.
```

## 9. Checker results and known fails

I ran `python tests/check_sis.py` from the sis-04 directory after completing the implementation and updating the report.

Final checker result:

- PASS: 33
- FAIL: 0
- ERROR: 0

All 33 automated structural and documentation checks passed.

Earlier failures R1, R2 and R3 were resolved after running the real baseline and final Vitest suites and recording their results. L10 was resolved by completing the 200–300 word AI reflection. A7 was resolved by removing the generated node_modules directory.

No known checker failures remain.

## 10. AI reflection (Task 6)

During SIS #04 I used ChatGPT to understand the assignment, inspect my Week 08 codebase, list maintainability risks and plan the changes. The original App.tsx mixed room data, page state, time handling and UI. This made the new filter and booking features harder to add safely. I also used material from the supplied package; its AI disclosure already recorded earlier Claude assistance, so I recorded that fact in AI_USAGE.md instead of presenting everything as my own work.The assistant helped me extract the room catalogue, filtering logic, booking rules and UI components. One important decision was the equipment filter. A room must satisfy every selected equipment item, not just one. The assistant first suggested .some(). I rejected that suggestion, kept the .every() check and confirmed that the corresponding test rejects a room that only partially matches the required set. I also verified that a blocked room cannot be booked and that switching the selected room uses that room’s own bookings.I did not trust the package’s original test claim (it used a Vitest stand-in). I installed the dependencies and ran the real Vitest suite: the baseline passed 17/17 tests and the final version passed 27/27. npm run build completed successfully. npm reported five dependency vulnerabilities; I deliberately did not force an upgrade because it could introduce breaking changes close to the deadline.The work showed me that generated code still needs independent evidence — running the tests and the build myself — rather than accepting a plausible explanation. The application still uses only fictional in-memory data. Immediate next steps are to capture fresh screenshots from my local build, inspect the remaining dependency warnings, and complete the final checker and submission validation.
