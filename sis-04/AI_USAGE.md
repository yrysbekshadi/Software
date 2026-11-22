# AI usage disclosure — SIS #04

AI use level: D (required by the assignment). All AI-generated material must be reviewed and verified by the student.

## Tools and models used

| Tool / model | Dates / provenance | Work used or retained |
|---|---|---|
| Claude.ai — Claude Sonnet 5.5 | The `AI_USAGE.md` bundled inside the supplied `sis-04-package(1).zip` records use on 2026-11-10 to 2026-11-11 (UTC). | The archive says Claude drafted analysis/plan text, wrote the room catalog, filter and booking changes, refactored the page into components, wrote tests and diagrams, generated five Playwright screenshots, and drafted report sections. This disclosure is based on that archive; I did not directly inspect the original Claude conversation. |
| ChatGPT — GPT-6 | This conversation, 2026-11-22 to 2026-11-23 (Asia/Almaty). | Inspected the handout, repository baseline and uploaded archives; compared package options; selected the implementation package; reviewed requirements and source; prepared this report/disclosure and identified what still needs real execution. |

## Files affected by AI-generated work

- `app/src/rooms.ts`, `app/src/filter.ts`, `app/src/booking.ts`
- `app/src/App.tsx`, `app/src/time.ts`, `app/src/components/*.tsx`, `app/src/index.css`
- `app/src/booking.test.ts`, `app/src/filter.test.ts`
- `app/README.md`, `diagrams/after.puml`, `report.md`, `submission.yml`
- `evidence/*.jpg` (the supplied package's disclosure says these were captured by Claude's headless Chromium/Playwright process, not by the student using `npm run dev`)

The unchanged baseline in `app/` was copied from `week-08/app` before the implementation commit. Week 08's `canBook` decisions were preserved when adding `checkRoom` and shared constants.

## Test and evidence honesty

- The supplied package states its 27-test result used a Vitest stand-in, **not the real Vitest runner**. That output is not represented as a real Vitest run here.
- In this environment, `npm install --offline` and `npx --offline vitest run` both failed with `ENOTCACHED`, because dependencies were not cached and npm registry access was unavailable.
- No real Vitest pass count or `npm run build` result is claimed here.
- The five screenshots are package-provided evidence. Their provenance is stated in `report.md` §4.2. They should be recaptured from the committed app in a local browser or Codespace before final grading.

## Student verification still required

Install dependencies on a connected machine, run baseline and final Vitest suites and `npm run build`, capture and verify the five screenshots, run both supplied Python scripts, complete the 200–300 word reflection in the student's own words, fill in personal identity details, and confirm that every submitted module and test can be explained and defended.
