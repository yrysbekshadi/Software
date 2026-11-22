# SIS #04 — Report

## 1. Setup and starting point

| Item | Value |
|---|---|
| Assistant | ChatGPT |
| Model | GPT-6 |
| Starting point | week-08 |
| Baseline commit | e0a6302a2977c6e0892f3110bd63b8f4c5afb254 |
| Language | TypeScript |
| Vitest version | 3.2.4 (declared in package.json; confirm from the RUN line) |
| Test environment | Not run yet in this environment |

### 1.1 Baseline run

Not run yet. Do not treat the existing week-08 tests as a measured baseline until `npx vitest run` is executed from `sis-04/app`. Paste the exact terminal output here.

## 2. Context for the assistant

### 2.1 Repository map at baseline

```text
sis-04/app/
  index.html              Vite HTML shell
  package.json            React 18, Vite, TypeScript, Vitest 3.2.4
  tsconfig.json           strict TypeScript configuration
  vite.config.ts          Vite React plugin
  src/
    App.tsx               page state, room selection, time parsing, booking call and UI
    booking.ts            canBook(start/end/now numeric minutes, blocked, bookings)
    booking.test.ts       existing canBook regression tests
    main.tsx              React entry point
    index.css             page layout and responsive styles
No rooms.ts or filter.ts exists in the baseline.
```

### 2.2 Context message

I am evolving the existing Week 08 Smart Campus Room Availability Checker. Baseline source is committed unchanged in `sis-04/app/`.

Preserve AC1–AC6: reject invalid/past time ranges; maximum duration 120 minutes; blocked rooms unavailable; overlaps rejected but endpoint-touching allowed; booking data immutable; clear responsive feedback.

Add F1–F5: capacity >= attendees; room contains ALL selected equipment; blocked rooms never available; clear empty state; selected-room changes refresh the result and check that room's own bookings.

Constraints: fictional data only; no login, payments, live APIs or database. Required modules/signatures: `rooms.ts` with `Room` and `ROOMS`; `filter.ts` with `filterRooms(rooms, { attendees, equipment })`; `booking.ts` retains `canBook({ start, end, now, blocked, bookings })` and adds `checkRoom(rooms, roomId, { start, end, now })`. UI imports modules and contains no room catalog or booking rules. Plan small steps; do not rewrite the app wholesale.

## 3. Codebase analysis (before app/src changes)

### 3.1 Maintainability risks

| # | Risk | Location | Evidence from baseline | Priority |
|---|---|---|---|---|
| 1 | Room data is embedded in the UI | `src/App.tsx`, `ROOMS` | Two room objects are declared in the component file; no reusable catalog module | High |
| 2 | Blocked state is global UI state rather than room data | `src/App.tsx`, `blocked` state and `check()` | One checkbox state is passed to canBook for whichever room is selected; it cannot represent per-room blocked status | High |
| 3 | The selected room is not derived from a typed catalog module | `src/App.tsx`, `room` lookup | Room type is local to App and only includes id, name, blocked, bookings; capacity/equipment are absent | High |
| 4 | Availability feedback can become stale after input changes | `src/App.tsx`, state setters | Changing room/time/blocked inputs does not consistently clear the previous result | Medium |
| 5 | Time parsing is UI-local | `src/App.tsx`, `toMinutes` | Conversion is coupled to the page; future components could duplicate it | Medium |
| 6 | Availability logic is only partly separated | `src/booking.ts` and `App.tsx` | canBook is imported, but App still owns room selection/data and request validation feedback | Medium |

### 3.2 Numbered improvement plan

1. Preserve this baseline commit and run its existing Vitest suite; record the exact output.
2. Add a fixed fictional catalog with at least four typed rooms in `src/rooms.ts`.
3. Add `filterRooms` in `src/filter.ts`; use capacity comparison and an ALL-equipment check.
4. Keep `canBook` behavior in `src/booking.ts`, then add `checkRoom` that delegates using the selected room's own blocked flag and bookings.
5. Add requirement-labelled tests for AC1–AC5, F1–F5, B1–B6 and INT before wiring the UI.
6. Refactor the page into UI components; clear result feedback when inputs or selected room change.
7. Add before/after diagrams, capture five real screenshots, run Vitest/build/checker/validator and record exact output.

### 3.3 AI suggestion rejected or modified

Pending a real assistant recommendation and my verification. Do not fill this section with a hypothetical exchange.

## 4–10. Remaining work

Not yet completed. Record feature details, refactoring decisions, real test output, measured quality, at least three genuine AI exchanges, and a 200–300 word personal reflection only after completing and verifying those activities.
