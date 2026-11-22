# Smart Campus Room Availability Checker

React + TypeScript + Vite application for the SIS #04 assignment. It uses a fixed fictional catalog of five rooms; no database, network API, login or browser storage is used.

## Setup

```bash
npm install
```

## Run

```bash
npm run dev
```

Open the local Vite URL printed in the terminal (usually http://localhost:5173).

## Test and build

```bash
npx vitest run
npm run build
```

The Vitest suite is in `src/booking.test.ts` and `src/filter.test.ts`. Tests use fixed catalogs independent of the demo `ROOMS` data.

## Source structure

| File | Responsibility |
|---|---|
| `src/rooms.ts` | Room type and fictional ROOMS catalog |
| `src/filter.ts` | filterRooms: F1 capacity and F2 all selected equipment |
| `src/booking.ts` | canBook (AC1–AC5), checkRoom (F3/F5), shared time constants |
| `src/time.ts` | time parsing and formatting |
| `src/App.tsx` | page state and wiring only |
| `src/components/` | filter panel, room list/empty state, check form and result banner |
| `src/*.test.ts` | requirement-labelled Vitest tests |

Blocked rooms remain visible with a label; booking availability is decided separately by `checkRoom`.
