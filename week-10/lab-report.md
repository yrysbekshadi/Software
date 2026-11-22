# Week 10 — Lab report

**Name:** not entered — student must complete  
**Group:** not supplied  
**Date:** 22 November 2026

## 1. Setup

| | |
| --- | --- |
| Assistant I reviewed with (tool) | ChatGPT |
| Exact model (with its version, or `not displayed`) | GPT-6 |
| Where the assistant read the project (Bolt.new / Claude Code / Cursor / Copilot / chat with pasted files) | Chat with the uploaded Week 10 files and read-only inspection of `yrysbekshadi/Software` on GitHub |
| Starting point (`week-08` or `week-07`) | week-08 |
| Baseline commit — the checkpoint of Part 0 | `38abccb` — local checkpoint commit from the student's PowerShell output |
| Where I ran the tests (Bolt terminal / my computer / Codespace) | My computer (Windows PowerShell), in `week-10/app/`; Python checker in `week-10/` |
| Vitest version (the `RUN  v…` line of a run) | `3.2.7` (`RUN v3.2.7`) |

**Repository note:** the student cloned `yrysbekshadi/Software`, created a local `week-10` branch tracking `origin/week-10`, checked out `week-08/app` from `origin/week-08`, moved it to `week-10/app`, extracted the original Week 10 archive, copied `provided/AGENTS.md` into `app/`, and created checkpoint `38abccb`. This is the actual local checkpoint hash reported by the student. It has not yet been pushed. No PR is claimed.

## 2. Task 1 — the baseline

### 2.1 The project's commands

| Command | Exists | Result | Note |
| --- | --- | --- | --- |
| `npx vitest run` | yes | pass | Vitest 3.2.7; 17 tests passed, 1 test file passed. |
| `npm test` | yes | pass | The `test` script runs `vitest run`; 17 tests passed, 1 test file passed. |
| `npm run test:unit` (the test command in `AGENTS.md`) | no | missing | No `test:unit` script exists in `app/package.json`; the provided playbook names a nonexistent command. |
| `npm run build` | yes | pass | `tsc && vite build` completed successfully; Vite transformed 32 modules. |
| `npm run lint` | no | missing | No `lint` script exists in `app/package.json`. |

`npm install` completed and added 105 packages. `npm audit` later confirmed 5 vulnerabilities: 2 moderate, 1 high and 2 critical. The visible audit detail names vulnerable ranges for `@vitest/mocker`, `esbuild` and `tinypool`; the suggested `npm audit fix --force` would require major upgrades (Vitest 5.1.1 and Vite 8.3.8), so I did not run it. R5 remains an unresolved confirmed dependency risk.

### 2.2 The baseline test run

The following is the real `npx vitest run` output from the student's Windows PowerShell terminal, before any application change:

```text
 RUN  v3.2.7 C:/Users/yrysb/Desktop/Software-Repo/week-10/app

 ✓ src/booking.test.ts (17 tests) 4ms
   ✓ canBook — assistant-generated first suite > T01 AC4: touching after an existing booking is available 1ms
   ✓ canBook — assistant-generated first suite > T02 AC1: a request starting at the current time is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T03 AC1: a zero-duration request is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T04 AC1: a reversed request is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T05 AC1: a request ending after midnight is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T06 AC2: a request lasting exactly 120 minutes is available 0ms
   ✓ canBook — assistant-generated first suite > T07 AC2: a request lasting 121 minutes is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T08 AC4: touching before an existing booking is available 0ms
   ✓ canBook — assistant-generated first suite > T09 AC4: a partial overlap is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T10 AC4: a request containing an existing booking is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T11 AC4: a request inside an existing booking is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T12 AC4: an identical interval is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T13 AC3: a blocked room is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T14 AC4: a request is available when there are no existing bookings 0ms
   ✓ canBook — assistant-generated first suite > AC5: an available check does not change the existing bookings 1ms
   ✓ canBook — assistant-generated first suite > X1 AC1: a valid 120-minute request ending exactly at 24:00 is available 0ms
   ✓ canBook — assistant-generated first suite > X2 AC4: a request between two touching bookings is available 0ms

 Test Files  1 passed (1)
      Tests  17 passed (17)
   Start at  20:52:38
   Duration  476ms (transform 40ms, setup 0ms, collect 44ms, tests 4ms, environment 0ms, prepare 156ms)
```

The separate baseline `npm test` command also passed all 17 tests, and the baseline `npm run build` passed. `npm run test:unit` and `npm run lint` were genuinely missing, as recorded above. The install also created `app/package-lock.json`, which was included in the later refactor commit; at the time of the earlier read-only review, no lockfile had yet been generated.

### 2.3 The agent reads the playbook

What I sent, exactly:

```text
Read the root AGENTS.md before making changes. Summarize the project constraints and the exact test commands you found. Do not edit anything yet. If you cannot read AGENTS.md, tell me, and I will paste its content. Do not claim that AGENTS.md was automatically loaded.
```

The assistant's answer:

```text
I read the supplied app/AGENTS.md directly; it was not automatically loaded. It describes a React + TypeScript/Vite page, places canBook in src/booking.ts, and points to src/App.tsx and src/booking.test.ts. It asks for npm install, npm run dev, npm run test:unit and npm run build. The playbook also tells an agent to use real KBTU rooms/timetables, permits a Supabase database and login, treats endpoint-touching bookings as overlaps, and requests a Netlify production deployment. Those instructions conflict with the one-fictional-room, no-login/database, endpoint-touching-is-allowed and no-external-deployment constraints. The actual package has npm test, not test:unit. No files were changed during this read-only review.
```

Which rules in its summary are wrong for this project, and how I know:

The real-room/timetable instruction, the Supabase/login permission and the Netlify production deployment must be reversed. AC4 is also wrong: intervals that only touch at an endpoint are allowed. The file names and module path in the opening paragraph match the real Week 08 source. `npm run test:unit` does not exist; `package.json` defines `npm test` as `vitest run` instead. AC6 is missing from the supplied playbook.

## 3. Tasks 2–3 — the read-only review and the challenge

### 3.1 The review prompt and the answer

Where it ran, and how I made sure it could not edit:

The review was performed in this ChatGPT conversation using the supplied project files and read-only GitHub file inspection. The review stage itself did not write or edit repository files. A separate local `git status --short` snapshot immediately after the review was not captured, so no clean-status output is claimed.

What I sent, exactly:

```text
Act as a cautious software reviewer. Inspect this Smart Campus Room Availability Checker WITHOUT editing files. Identify risks in correctness, security, privacy, reliability, maintainability, and agent operations. For each risk, cite the exact file/function or missing check, explain the impact, suggest a way to verify it, and state uncertainty. Do not invent test results.
```

The assistant's answer:

```text
The Week 08 project is a small React + TypeScript/Vite app. The decision function is src/booking.ts:canBook, the UI is src/App.tsx, and unit tests are in src/booking.test.ts. I found no login, database client, API server, external deployment configuration, or persisted booking store in the application code. The supplied app/AGENTS.md nevertheless tells an agent to use real KBTU room/timetable data, add Supabase and a login if persistence is wanted, and run a Netlify production deployment; these are serious agent-operation and privacy/scope risks.

Correctness: canBook validates the candidate start/end range and rejects a non-finite candidate start through its range predicate. However, existing booking intervals are not validated before the overlap loop. A malformed stored interval (for example, start=NaN) makes the overlap comparisons false and can allow an otherwise conflicting request. Reproduce this with a direct call to canBook and a malformed bookings array, then add a regression test before changing the implementation. The normal overlap predicate uses strict inequalities, so a request touching an existing booking at an endpoint is allowed; existing T01/T08 tests support this behaviour.

Reliability/UI: src/App.tsx sets an error when the start/end range is invalid but does not return from check(). It can continue to call canBook and show an Unavailable result alongside the validation message. The current sample UI also defines two fictional rooms, although this practice's constraint is one fictional room. The app's package.json has a test script, but no test:unit or lint script. No lockfile, app README, integration test, CI workflow or pre-commit hook was found. Dependencies are declared but not installed in this environment, so I cannot claim that Vitest or the build passes. Suggested checks: test malformed stored intervals, verify invalid-input feedback in the browser at desktop and phone widths, and run the declared scripts in an environment with dependencies installed. I did not edit files or infer test results.
```

### 3.2 Challenging the AI's claims

| # | The AI's claim (short) | Category | What I inspected | Label | Why |
| --- | --- | --- | --- | --- | --- |
| 1 | A NaN candidate start can be returned as available. | Correctness | Original `app/src/booking.ts`, candidate range predicate `0 <= start && start < end && end <= 1440`; exercised candidate `start: NaN` directly. | unsupported | The negated range predicate rejects NaN before the overlap loop; that specific reviewer claim is false. |
| 2 | Malformed existing booking data can be ignored by the overlap check. | Correctness | Original `app/src/booking.ts`, loop condition `start < booking.end && end > booking.start`; direct Node call with `bookings: [{start: NaN, end: 660}]`. | confirmed | The overlap condition evaluates false for NaN and the function returned true for the candidate; R1 reproduces it. |
| 3 | Endpoint-touching intervals are treated as a conflict. | Correctness | Original `booking.ts` strict inequalities and `booking.test.ts` tests T01 and T08. | unsupported | The predicate returns no overlap when candidate end equals booking start or candidate start equals booking end; the test titles/assertions also expect availability. |
| 4 | The app uses real KBTU rooms or student timetable data. | Privacy | Original `app/src/App.tsx` hard-coded Room A-101 and Room B-204; searched application source and package dependencies. | unsupported | The app data is fictional and contains no portal integration. The conflicting instruction exists in `AGENTS.md`, not in the app implementation. |
| 5 | The playbook permits Supabase, login and production deployment. | Agent operations | Original `app/AGENTS.md`, “You may” and “Before you finish” sections. | confirmed | The file explicitly proposes Supabase/login and `npx netlify deploy --prod`; agents could act outside the task boundary. |
| 6 | Invalid start/end input can still display a result. | Reliability | Original `app/src/App.tsx`, `check()` after `if (!(s < e))`. | confirmed | The branch called `setError` but did not return, so execution continued to canBook and setResult. |
| 7 | `npm run test:unit` and `npm run lint` are available. | Maintainability | Original `app/package.json` scripts and dependencies. | unsupported | Only `dev`, `build`, `preview` and `test` scripts exist; there is no lint script or ESLint dependency. |

## 4. Task 4 — the risk register

### 4.1 The register

| ID | Category | Cause → event → consequence | Component | Evidence | Status | L | I | Score | Mitigation | Owner | Verification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | Correctness | Existing booking data is not validated → malformed values bypass overlap comparisons → a conflicting slot may be shown as available. | `app/src/booking.ts` | The real pre-fix Vitest run for the R1 case failed: expected `false`, received `true` for an existing interval with `start: Number.NaN` (18 total, 1 failed, 17 skipped). | confirmed | 2 | 3 | 6 | Validate candidate and every stored interval with pure predicates before checking overlap. | Student | R1 regression case plus the complete Vitest suite in an environment with dependencies installed. |
| R2 | Agent operations | The playbook permits real portal data, Supabase/login and Netlify production deployment → an agent follows those directions → privacy, scope and deployment boundary may be breached. | `app/AGENTS.md` | Original “For realism”, “You may” and “Before you finish” lines explicitly requested these actions. | confirmed | 3 | 3 | 9 | Replace conflicting directions with one fictional room, no backend/login/persistence, no secrets, no deployment and a test-before-acceptance gate. | Student | Check C1–C6 and A2–A3; manually review the final diff. |
| R3 | Maintainability | The app has no formatter or linter → agents can introduce inconsistent style or miss basic static issues → review effort increases. | `missing: formatter and lint checks` | No Prettier config/dependency and no ESLint config/dependency or `lint` script are present in `app/`. | confirmed | 2 | 2 | 4 | Add a formatter/linter only in a separately scoped change; do not add them as part of this risk patch. | Student | Confirm the relevant config, package and scripts exist and run successfully. |
| R4 | Reliability | `check()` sets a validation error for a reversed interval but continues to call `canBook` → an unavailable result may appear alongside the error → feedback becomes ambiguous. | `app/src/App.tsx` | The `if (!(s < e))` branch sets an error but has no `return` before the availability call. | confirmed | 2 | 2 | 4 | Return immediately after setting the validation error. | Student | Try a reversed range in the browser; only the validation message should appear. |
| R5 | Security | Installed dependencies include known advisories → vulnerable code may be reachable through the app or build chain → security exposure could occur. | `app/package.json` | `npm audit` reports 5 vulnerabilities (2 moderate, 1 high, 2 critical); the visible advisory output names `@vitest/mocker`, `esbuild` and `tinypool`. | confirmed | 2 | 3 | 6 | Review a compatible upgrade path for the affected dependency tree; do not use `npm audit fix --force` without a separate breaking-change review. | Student | `npm audit` has no unresolved high/critical findings; rerun full tests and build after a reviewed upgrade. |

### 4.2 The top two for action

1. **R2** — 3 × 3 = 9. The checked-in playbook explicitly directs real-data use, login/database work and a production deployment; following it crosses several assignment boundaries at once.
2. **R1** — 2 × 3 = 6. A malformed existing interval demonstrably made `canBook` return true, so an invalid stored record can conceal a conflict and cause a wrong availability result.

## 5. Task 5 — the agent-readiness audit

### 5.1 The rows

| Row | What | yes / no | Evidence |
| --- | --- | --- | --- |
| 1a | Formatter | no | No Prettier config and no `prettier` dependency in `app/package.json`. |
| 1b | Linter | no | No ESLint config and no `eslint` dependency in `app/package.json`. |
| 1c | Type checks | yes | `app/tsconfig.json` plus the `typescript` devDependency. |
| 1d | Unit tests | yes | `app/src/booking.test.ts` imports Vitest; `vitest` is declared in `package.json`. |
| 1e | Pinned dependencies (lockfile) | yes | `npm install` generated `app/package-lock.json`; commit this lockfile so the dependency tree is reproducible. |
| 2a | `.env.example` | no | No `.env.example` at the app root. |
| 2b | Architecture notes | no | No README or architecture note inside `app/`. |
| 2c | `AGENTS.md` | yes | `app/AGENTS.md` is present (patched copy of the provided playbook). |
| 3a | CI | no | No `.github/workflows/` pipeline in the app. |
| 3b | Pre-commit hooks | no | No `.husky/`, lint-staged, simple-git-hooks or `.pre-commit-config.yaml`. |
| 3c | Integration checks | no | Only the pure `booking.test.ts` suite is present; no page/component integration test. |
| 3d | Reviewable evidence | no | No PR template or CI evidence log requiring test/build evidence. |

### 5.2 The level and the gaps

**Level:** 0

**Missing evidence for the next level:** Level 1 has 3/5 rows (60%): TypeScript checks, Vitest unit tests and the lockfile. It remains below 80%; add a formatter and a linter to reach 5/5 (or at least one of them plus one additional qualifying baseline control if the row criteria are expanded). To reach Level 2, also add `.env.example` and app architecture notes so all three Level 2 rows are present. Level 3 then needs CI, pre-commit hooks, an integration check and mandatory reviewable evidence. The app folder layout is simple and readable (`src/`, package and Vite/TypeScript configs), but it has no project README; the course `week-10/README.md` is outside `app/` and does not document its architecture.

## 6. Task 6 — the agent playbook

### 6.1 The playbook prompt and the answer

What I sent, exactly:

```text
Review AGENTS.md and project documentation only. Compare them with these constraints: one fictional room; no login/database; preserve AC1–AC6; no secrets; no external deployments; run tests before proposing acceptance. Report missing or conflicting rules. Draft a minimal patch to AGENTS.md, but wait for my approval before applying it.
```

The assistant's answer:

```text
The provided AGENTS.md conflicts with the assignment in six places. It instructs the agent to use real KBTU room names and timetable data instead of one fictional room; it says endpoint-touching intervals count as overlaps, contrary to AC4; it omits AC6; it names npm run test:unit, which is not a script in this project's package.json; it permits a Supabase database and login; and it asks for a Netlify production deploy. It also lacks an explicit no-secrets/no-personal-data rule and does not require real test output before acceptance. A minimal patch should replace only those lines, keep the existing headings, use npm test (the actual declared script), preserve the current pure canBook module and avoid adding any dependency. The proposed patch is limited to the provided playbook; the student should review it before submission.
```

### 6.2 Findings and my decisions

| # | Rule or line in AGENTS.md | Missing / conflicting | Decision | Why |
| --- | --- | --- | --- | --- |
| 1 | “For realism, use real room names…” | Conflicts with one fictional room and no real student timetable/data. | approve | Replace with one fictional room and an explicit ban on real room names, timetables and student data. |
| 2 | AC4 endpoint sentence | Says touching endpoints also count as overlap, which contradicts the actual strict-overlap rule and tests. | approve | Rewrite AC4 to allow intervals that only touch at endpoints. |
| 3 | Acceptance contract ends at AC5 | AC6 UI feedback requirement is missing. | approve | Add the sixth acceptance rule for clear desktop/mobile feedback. |
| 4 | `npm run test:unit` | Script is absent; `npm test` is the real test script. | approve | Change only the command to the existing script. |
| 5 | Supabase table and login permission | Permits a database, authentication and persistence, all out of scope. | approve | Explicitly forbid login, database, backend service and booking persistence. |
| 6 | Netlify production deploy | Encourages external deployment and no explicit no-secrets rule or test gate. | approve | Replace with test-before-acceptance, report-real-output, no-secrets and no-deployment rules. |

### 6.3 The approved patch

`git diff app/AGENTS.md` (relative to the checkpoint):

```diff
diff --git a/week-10/app/AGENTS.md b/week-10/app/AGENTS.md
index b786d88..ade2fd8 100644
--- a/week-10/app/AGENTS.md
+++ b/week-10/app/AGENTS.md
@@ -10,5 +10,5 @@ requested time. The booking rule lives in `src/booking.ts` (`canBook`); the page
 the tests are in `src/booking.test.ts`.
 
-For realism, use real room names and the real timetable from the KBTU portal.
+Use exactly one fictional room and fictional bookings. Never use real room names, timetables or student data.
 
 ## Acceptance contract
@@ -17,6 +17,7 @@ requested time. The booking rule lives in `src/booking.ts` (`canBook`); the page
 - AC2 Enforce the maximum allowed duration (120 minutes).
 - AC3 Reject a blocked room.
-- AC4 Reject overlaps. A request that touches a booking at an endpoint also counts as an overlap.
+- AC4 Reject overlaps; allow bookings that only touch at endpoints.
 - AC5 Return Available / Unavailable without changing booking data.
+- AC6 Preserve clear UI feedback on desktop and mobile.
 
 ## Commands
@@ -24,5 +25,5 @@ requested time. The booking rule lives in `src/booking.ts` (`canBook`); the page
 - Install: `npm install`
 - Dev server: `npm run dev`
-- Tests: `npm run test:unit`
+- Tests: `npm test`
 - Build: `npm run build`
 
@@ -31,8 +32,8 @@ requested time. The booking rule lives in `src/booking.ts` (`canBook`); the page
 - Edit any file in the project.
 - Add packages when a task needs them.
-- If bookings need to persist, add a small Supabase table and a login page.
+- Never add login, a database, backend services or booking persistence.
 
 ## Before you finish
 
-- Make sure the page still loads.
-- When the build passes, publish a preview with `npx netlify deploy --prod` so the team can see it.
+- Before acceptance, run `npm test` and report its real output; never commit secrets, API keys, passwords, tokens or personal data.
+- Never deploy or use external production services.
```

The student explicitly reviewed and approved the proposed minimal `app/AGENTS.md` patch in chat on 22 November 2026. The approval applies to the playbook patch only; the student must still inspect the application-code diffs before submission.

## 7. Task 7 — verify safely

### 7.1 The regression test fails before the mitigation

The risk it covers: **R1** (malformed existing booking intervals can be treated as free because `NaN` makes the overlap comparisons false). I added the test named `R1 AC4: a malformed existing booking interval is not treated as free` while keeping the original `booking.ts` unchanged, then ran `npx vitest run -t "R1 AC4"` from `week-10/app/`.

The following is the real Vitest output supplied from the student's Windows PowerShell terminal. The failure is intentional evidence: the regression test fails against the pre-fix implementation, with actual `true` where `false` is required.

```text
 RUN  v3.2.7 C:/Users/yrysb/Desktop/Software-Repo/week-10/app

 ❯ src/booking.test.ts (18 tests | 1 failed | 17 skipped) 9ms
   ↓ canBook — assistant-generated first suite > T01 AC4: touching after an existing booking is available
   ↓ canBook — assistant-generated first suite > T02 AC1: a request starting at the current time is unavailable
   ↓ canBook — assistant-generated first suite > T03 AC1: a zero-duration request is unavailable
   ↓ canBook — assistant-generated first suite > T04 AC1: a reversed request is unavailable
   ↓ canBook — assistant-generated first suite > T05 AC1: a request ending after midnight is unavailable
   ↓ canBook — assistant-generated first suite > T06 AC2: a request lasting exactly 120 minutes is available
   ↓ canBook — assistant-generated first suite > T07 AC2: a request lasting 121 minutes is unavailable
   ↓ canBook — assistant-generated first suite > T08 AC4: touching before an existing booking is available
   ↓ canBook — assistant-generated first suite > T09 AC4: a partial overlap is unavailable
   ↓ canBook — assistant-generated first suite > T10 AC4: a request containing an existing booking is unavailable
   ↓ canBook — assistant-generated first suite > T11 AC4: a request inside an existing booking is unavailable
   ↓ canBook — assistant-generated first suite > T12 AC4: an identical interval is unavailable
   ↓ canBook — assistant-generated first suite > T13 AC3: a blocked room is unavailable
   ↓ canBook — assistant-generated first suite > T14 AC4: a request is available when there are no existing bookings
   × canBook — assistant-generated first suite > R1 AC4: a malformed existing booking interval is not treated as free 7ms
     → expected true to be false // Object.is equality
   ↓ canBook — assistant-generated first suite > AC5: an available check does not change the existing bookings
   ↓ canBook — assistant-generated first suite > X1 AC1: a valid 120-minute request ending exactly at 24:00 is available
   ↓ canBook — assistant-generated first suite > X2 AC4: a request between two touching bookings is available

 FAIL  src/booking.test.ts > canBook — assistant-generated first suite > R1 AC4: a malformed existing booking interval is not treated as free
AssertionError: expected true to be false // Object.is equality

- Expected
+ Received

- false
+ true

 ❯ src/booking.test.ts:63:118
     61| 
     62|   test('R1 AC4: a malformed existing booking interval is not treated as free', () => {
     63|     expect(canBook({ start: 630, end: 690, now: 540, blocked: false, bookings: [{ start: Number.NaN, end: 660 }] })).toBe(false);
       |                                                                                                                      ^
     64|   });
     65| 

 Test Files  1 failed (1)
      Tests  1 failed | 17 skipped (18)
   Start at  21:03:44
   Duration  486ms (transform 38ms, setup 0ms, collect 42ms, tests 9ms, environment 0ms, prepare 165ms
```

This proves the requested fail-first sequence. I have not run the post-fix 18-test suite yet; that result belongs in §8.4 after the refactor is applied.

### 7.2 The manual UI check

| View | Width | What I checked | Result | Screenshot |
| --- | --- | --- | --- | --- |
| Desktop | 1365 px target | Student must check form layout, validation/result feedback and room summary in a browser. | pending student check | `evidence/ui-desktop.png` |
| Mobile | 390 px target | Student must check stacked controls, readable labels and no horizontal overflow in a browser device toolbar. | pending student check | `evidence/ui-mobile.png` |

### 7.3 Tests and checks I did not run

- `npm run test:unit`: attempted, but the script is missing; PowerShell reported `Missing script: "test:unit"`.
- `npm run lint`: attempted, but the script is missing; PowerShell reported `Missing script: "lint"`.
- `npm audit fix --force`: intentionally not run because npm said the proposed fixes require breaking major upgrades (Vitest 5.1.1 and Vite 8.3.8). The current `npm audit` still reports 5 vulnerabilities (2 moderate, 1 high, 2 critical).
- Browser UI verification at desktop and mobile widths: pending the student's manual check and screenshots.
- Integration/UI tests and CI: no integration test or CI workflow is present in this project.

## 8. Task 8 — mitigate two risks

### 8.1 The first mitigation

**Risk:** R1

The prompt sent:

```text
Refactor the availability logic into a small, pure module, keeping the existing function inputs, outputs, and UI behavior. Use a pattern only if the identified design problem justifies it. Do not add new features or dependencies. Show the files you plan to edit before making changes.
```

**Problem → pattern → benefit:** The overlap loop treated malformed stored intervals as if they did not overlap; I used a small pure module with guard clauses and extracted validation/overlap predicates, so invalid booking data now fails closed while valid interval behaviour remains unchanged.

**What I rejected from the agent's patch, and why:** I rejected adding a class, Strategy pattern, network validation, persistence or new dependencies; none was needed to validate the existing interval inputs and preserve the current API.

The diff I accepted for this focused refactor and scope alignment:

```diff
diff --git a/week-10/app/src/booking.ts b/week-10/app/src/booking.ts
index 0ef74a8..8dfdcd5 100644
--- a/week-10/app/src/booking.ts
+++ b/week-10/app/src/booking.ts
@@ -9,20 +9,27 @@ export type CanBookInput = {
 };
 
-// Returns true when the candidate interval is Available, otherwise false.
-// Times are minutes after midnight on the same day.
+const DAY_MINUTES = 1440;
+const MAX_DURATION_MINUTES = 120;
+
+function isValidInterval(interval: BookingInterval): boolean {
+  return Number.isFinite(interval.start)
+    && Number.isFinite(interval.end)
+    && 0 <= interval.start
+    && interval.start < interval.end
+    && interval.end <= DAY_MINUTES;
+}
+
+function overlaps(candidate: BookingInterval, existing: BookingInterval): boolean {
+  return candidate.start < existing.end && candidate.end > existing.start;
+}
+
+// A pure availability decision: valid inputs keep the original AC1-AC5 behaviour.
 export function canBook({ start, end, now, blocked, bookings }: CanBookInput): boolean {
-  let ok = true;
-  if (!(0 <= start && start < end && end <= 1440)) ok = false;
-  else if (!(start > now)) ok = false;
-  else if (end - start > 120) ok = false;
-  else if (blocked) ok = false;
-  else {
-    for (const booking of bookings) {
-      if (start < booking.end && end > booking.start) {
-        ok = false;
-        break;
-      }
-    }
-  }
-  return ok;
+  const candidate = { start, end };
+
+  if (!Number.isFinite(now) || !isValidInterval(candidate)) return false;
+  if (start <= now || end - start > MAX_DURATION_MINUTES || blocked) return false;
+  if (!Array.isArray(bookings) || !bookings.every(isValidInterval)) return false;
+
+  return !bookings.some((booking) => overlaps(candidate, booking));
 }
```

The same narrow app correction removes the second sample room to satisfy the one-fictional-room boundary and returns immediately on invalid start/end input so an error is not followed by a misleading result. No new feature or dependency was added.

### 8.2 The second mitigation

**Risk:** R2

The AGENTS.md patch in §6.3 is the second mitigation. It removes real KBTU data, Supabase/login, invalid AC4, the nonexistent test command and production deployment instruction; it adds AC6, a no-secrets rule and the test-before-acceptance gate.

**What I rejected from the agent's patch, and why:** I rejected broad documentation rewrites and any new backend, deployment or package suggestions; the approved change is limited to the conflicting playbook lines and keeps its headings.

The diff I accepted:

```diff
diff --git a/week-10/app/AGENTS.md b/week-10/app/AGENTS.md
index b786d88..ade2fd8 100644
--- a/week-10/app/AGENTS.md
+++ b/week-10/app/AGENTS.md
@@ -10,5 +10,5 @@ requested time. The booking rule lives in `src/booking.ts` (`canBook`); the page
 the tests are in `src/booking.test.ts`.
 
-For realism, use real room names and the real timetable from the KBTU portal.
+Use exactly one fictional room and fictional bookings. Never use real room names, timetables or student data.
 
 ## Acceptance contract
@@ -17,6 +17,7 @@ requested time. The booking rule lives in `src/booking.ts` (`canBook`); the page
 - AC2 Enforce the maximum allowed duration (120 minutes).
 - AC3 Reject a blocked room.
-- AC4 Reject overlaps. A request that touches a booking at an endpoint also counts as an overlap.
+- AC4 Reject overlaps; allow bookings that only touch at endpoints.
 - AC5 Return Available / Unavailable without changing booking data.
+- AC6 Preserve clear UI feedback on desktop and mobile.
 
 ## Commands
@@ -24,5 +25,5 @@ requested time. The booking rule lives in `src/booking.ts` (`canBook`); the page
 - Install: `npm install`
 - Dev server: `npm run dev`
-- Tests: `npm run test:unit`
+- Tests: `npm test`
 - Build: `npm run build`
 
@@ -31,8 +32,8 @@ requested time. The booking rule lives in `src/booking.ts` (`canBook`); the page
 - Edit any file in the project.
 - Add packages when a task needs them.
-- If bookings need to persist, add a small Supabase table and a login page.
+- Never add login, a database, backend services or booking persistence.
 
 ## Before you finish
 
-- Make sure the page still loads.
-- When the build passes, publish a preview with `npx netlify deploy --prod` so the team can see it.
+- Before acceptance, run `npm test` and report its real output; never commit secrets, API keys, passwords, tokens or personal data.
+- Never deploy or use external production services.
```

### 8.3 The residual risk

| ID | L before | I before | Score before | L after | I after | Score after | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | 2 | 3 | 6 | 1 | 3 | 3 | `canBook` now validates candidate and every existing interval before the pure overlap predicate; the R1 regression plus the complete suite pass (18/18) after the change. |
| R2 | 3 | 3 | 9 | 1 | 3 | 3 | The patched playbook explicitly forbids real room/student data, login/database/backend/persistence, secrets and deployment; the student approved this exact patch on 22 November 2026, and C1–C6 verify the wording. |

### 8.4 The final run

The following are the actual final outputs supplied from the student's Windows PowerShell terminal after the R1 refactor. The complete suite passes with the same 18 tests present in `booking.test.ts`.

**`npx vitest run`**

```text
RUN  v3.2.7 C:/Users/yrysb/Desktop/Software-Repo/week-10/app

 ✓ src/booking.test.ts (18 tests) 4ms
   ✓ canBook — assistant-generated first suite > T01 AC4: touching after an existing booking is available 1ms
   ✓ canBook — assistant-generated first suite > T02 AC1: a request starting at the current time is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T03 AC1: a zero-duration request is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T04 AC1: a reversed request is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T05 AC1: a request ending after midnight is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T06 AC2: a request lasting exactly 120 minutes is available 0ms
   ✓ canBook — assistant-generated first suite > T07 AC2: a request lasting 121 minutes is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T08 AC4: touching before an existing booking is available 0ms
   ✓ canBook — assistant-generated first suite > T09 AC4: a partial overlap is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T10 AC4: a request containing an existing booking is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T11 AC4: a request inside an existing booking is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T12 AC4: an identical interval is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T13 AC3: a blocked room is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T14 AC4: a request is available when there are no existing bookings 0ms
   ✓ canBook — assistant-generated first suite > R1 AC4: a malformed existing booking interval is not treated as free 0ms
   ✓ canBook — assistant-generated first suite > AC5: an available check does not change the existing bookings 0ms
   ✓ canBook — assistant-generated first suite > X1 AC1: a valid 120-minute request ending exactly at 24:00 is available 0ms
   ✓ canBook — assistant-generated first suite > X2 AC4: a request between two touching bookings is available 0ms

 Test Files  1 passed (1)
      Tests  18 passed (18)
   Start at  23:01:50
   Duration  466ms (transform 36ms, setup 0ms, collect 41ms, tests 4ms, environment 0ms, prepare 157ms)
```

**`npm test`**

```text
> smart-campus-availability@0.0.0 test
> vitest run


 RUN  v3.2.7 C:/Users/yrysb/Desktop/Software-Repo/week-10/app

 ✓ src/booking.test.ts (18 tests) 4ms
   ✓ canBook — assistant-generated first suite > T01 AC4: touching after an existing booking is available 1ms
   ✓ canBook — assistant-generated first suite > T02 AC1: a request starting at the current time is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T03 AC1: a zero-duration request is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T04 AC1: a reversed request is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T05 AC1: a request ending after midnight is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T06 AC2: a request lasting exactly 120 minutes is available 0ms
   ✓ canBook — assistant-generated first suite > T07 AC2: a request lasting 121 minutes is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T08 AC4: touching before an existing booking is available 0ms
   ✓ canBook — assistant-generated first suite > T09 AC4: a partial overlap is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T10 AC4: a request containing an existing booking is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T11 AC4: a request inside an existing booking is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T12 AC4: an identical interval is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T13 AC3: a blocked room is unavailable 0ms
   ✓ canBook — assistant-generated first suite > T14 AC4: a request is available when there are no existing bookings 0ms
   ✓ canBook — assistant-generated first suite > R1 AC4: a malformed existing booking interval is not treated as free 0ms
   ✓ canBook — assistant-generated first suite > AC5: an available check does not change the existing bookings 1ms
   ✓ canBook — assistant-generated first suite > X1 AC1: a valid 120-minute request ending exactly at 24:00 is available 0ms
   ✓ canBook — assistant-generated first suite > X2 AC4: a request between two touching bookings is available 0ms

 Test Files  1 passed (1)
      Tests  18 passed (18)
   Start at  23:01:52
   Duration  473ms (transform 36ms, setup 0ms, collect 40ms, tests 4ms, environment 0ms, prepare 144ms)
```

**`npm run build`**

```text
> smart-campus-availability@0.0.0 build
> tsc && vite build

vite v5.4.21 building for production...
✓ 32 modules transformed.
dist/index.html                   0.43 kB │ gzip:  0.29 kB
dist/assets/index-X8OGNIvT.css    0.66 kB │ gzip:  0.36 kB
dist/assets/index-BcdobC6P.js   144.73 kB │ gzip: 46.63 kB
✓ built in 513ms
```

**`npm audit`**

```text
# npm audit report

@vitest/mocker  <=4.1.11
Severity: moderate
Vitest: Path Traversal / Arbitrary File Read via @vitest/mocker Redirect Mock - https://github.com/advisories/GHSA-82fw-gwwq-j7x9
Vitest: Code injection via unauthenticated manual mock registration - https://github.com/advisories/GHSA-qxg6-89mg-rqv8
fix available via `npm audit fix --force`
Will install vitest@5.1.1, which is a breaking change
node_modules/@vitest/mocker
  vitest  0.0.95 - 4.1.10
  Depends on vulnerable versions of @vitest/mocker
  Depends on vulnerable versions of tinypool
  node_modules/vitest

esbuild  <=0.24.2
Severity: moderate
esbuild enables any website to send any requests to the development server and read the response - https://github.com/advisories/GHSA-67mh-4wv8-2f99
fix available via `npm audit fix --force`
Will install vite@8.3.8, which is a breaking change
node_modules/esbuild
  vite  <=6.4.3
  Depends on vulnerable versions of esbuild
  node_modules/vite

tinypool  <=2.1.1
Severity: critical
Tinypool: Prototype Pollution gadget in worker options leads to Remote Code Execution - https://github.com/advisories/GHSA-5gmw-xhrv-c9v3
Tinypool: Prototype Pollution Gadget to RCE in run() options - https://github.com/advisories/GHSA-85c8-ppgw-ccpr
fix available via `npm audit fix --force`
Will install vitest@5.1.1, which is a breaking change
node_modules/tinypool



5 vulnerabilities (2 moderate, 1 high, 2 critical)

To address all issues (including breaking changes), run:
  npm audit fix --force
```

`npm audit` reports 5 vulnerabilities (2 moderate, 1 high, 2 critical). The suggested `npm audit fix --force` would install major versions of Vitest and Vite, so I did not apply it. This remains a confirmed dependency risk, not a passing security check.

## 9. Task 9, and what still fails

### 9.1 A background agent on this project

| Rule | What I require |
| --- | --- |
| Isolation | Work only in a separate `week-10-agent/<task>` branch or isolated worktree based on the reviewed `week-10`; never commit directly to `main` or reuse another agent's worktree. |
| Permitted files | Edit only agreed files under `week-10/app/src/` and a named test file; do not edit `provided/AGENTS.md`, submission identity fields, secrets or unrelated week folders. |
| Commands | In `week-10/app/`, run `npm test` and `npm run build`; run `npm run lint` only after a real lint script exists. In `week-10/`, run `python tests/check_audit.py` and `python tests/validate_submission.py`. |
| Prohibited actions | Do not add login, database, Supabase, backend, persistence, real campus/student data, credentials or new dependencies without explicit scope approval; never deploy externally. |
| Required evidence | Attach the exact changed-file list, reviewed diff, regression test output, full test output, build output and a short risk-register note; distinguish not-run checks from passes. |
| Before merging or deploying | Require a human to inspect every diff, confirm AC1–AC6, check the evidence and approve the PR; deployment is not allowed for this assignment. |

### 9.3 Final checker and UI evidence

Both manual UI evidence files are now present: `evidence/ui-desktop.png` shows the wide desktop layout and `evidence/ui-mobile.png` shows the responsive layout at a 390 px CSS viewport. The mobile capture includes the full form, availability result and existing-bookings section.

After adding both screenshots, I reran `python tests/check_audit.py` from the assembled `week-10/` submission copy. The result was **31 PASS, 0 FAIL, 0 ERROR**. In particular, E1 and E2 now pass. The machine-readable `submission.yml` records the same 31/0/0 result. The separate shape validator still requires the student to fill the personal `student.name` and `student.student_id` fields; these are intentionally left blank rather than guessed.

## 10. Release decision and conclusion

**Decision:** NO-GO

NO-GO remains appropriate. R1 was reproduced before the fix: malformed stored data made `canBook` report a slot as available. After the refactor, the R1 regression and full suite pass (18/18), `npm test` passes (18/18), and the build succeeds. R2 was mitigated by the approved playbook patch, which restores AC1–AC6 and forbids real data, backend/login work, secrets and external deployment. Both UI evidence checks now pass; the audit checker reports 31 PASS, 0 FAIL and 0 ERROR. However, `npm audit` still reports five vulnerabilities (2 moderate, 1 high, 2 critical), including advisories for `@vitest/mocker`, `esbuild` and `tinypool`. A forced fix requires breaking major upgrades, so R5 remains confirmed at score 6. The handout prohibits GO while a confirmed risk scores 6 or higher. Do not release until a compatible dependency upgrade is reviewed. Complete the student identity fields before final submission.
