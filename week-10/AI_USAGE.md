# AI Usage Disclosure — Week 10

Required by the course academic policy (Generative AI use level **D — AI-integrated**). ChatGPT helped inspect the project, challenge reviewer claims, score risks, draft the playbook patch, propose the regression test and refactor, and prepare report/declaration text. The student remains responsible for reviewing, testing and defending every change.

| Tool | Exact model / plan | Used for | Which files or sections it touched |
| --- | --- | --- | --- |
| ChatGPT | GPT-6 | Read-only inspection of the supplied assignment and the `week-08/app` files; reviewer-style risk analysis and claim challenge | `lab-report.md` §§2–5; no repository files were edited during the read-only review itself. |
| ChatGPT | GPT-6 | Audit of the provided playbook and a minimal patch proposal | `app/AGENTS.md`, `lab-report.md` §6 |
| ChatGPT | GPT-6 | Regression-test proposal, pure-module refactor and small scope/UI corrections | `app/src/booking.test.ts`, `app/src/booking.ts`, `app/src/App.tsx` |
| ChatGPT | GPT-6 | Drafting the evidence-based report, disclosure and machine-readable declaration | `lab-report.md`, `AI_USAGE.md`, `submission.yml` |

**The Task 2 review ran in a mode where the assistant could not edit:** yes. The review was performed in a chat and by read-only GitHub source inspection. A local `git status --short` snapshot immediately after that review was not captured, so I do not claim that a local clean-status output was observed.

**I labelled every claim in `lab-report.md` §3.2 after inspecting the cited source myself:** yes. The labels are tied to the actual `week-08/app` source and the recorded baseline run.

**I personally reviewed and approved the `app/AGENTS.md` playbook patch:** yes, in chat on 22 November 2026. **I personally reviewed every application-code diff (`App.tsx`, `booking.ts`, `booking.test.ts`) before accepting it:** not yet confirmed; I inspected the displayed diffs for `AGENTS.md`, `booking.ts` and `App.tsx`, and I must personally review the regression-test diff and re-check the complete changed-file list before submission.

**I used another assistant as well:** no.

**Every terminal result in `lab-report.md` is based on an actual run and its result is not altered:** yes. The baseline Vitest (17/17), baseline `npm test`, baseline build, missing-script outputs, pre-fix R1 fail-first output, final Vitest (18/18), final `npm test` (18/18), final build and `npm audit` summary were supplied from my Windows PowerShell terminal. The `npm audit` report remains a finding: five vulnerabilities are unresolved; no forced upgrade was run.

**I can explain the risk scores, mitigations and release decision without the assistant:** not yet confirmed — I must personally review and be ready to defend each item before submitting.

**Anything I accepted from AI without fully understanding it:** The guard clauses and interval-validation logic in `app/src/booking.ts`, the one-room/UI changes in `app/src/App.tsx`, and every changed line in `app/AGENTS.md` must be reviewed by me before I treat the changes as accepted.

Signed: student to complete
Date: 2026-11-22
