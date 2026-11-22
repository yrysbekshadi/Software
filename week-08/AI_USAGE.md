# AI Usage Disclosure — Week 08

AI use is permitted and expected in this lab (Level D), but every use must be disclosed. This file records the preparation performed in this ChatGPT conversation. The student must update it if additional tools or assistants are used.

| Tool | Exact model / plan | Used for | Which files it touched |
| --- | --- | --- | --- |
| ChatGPT | GPT-6 (model label shown in this conversation) | Read the uploaded Practice #07/#08 handouts and archive; inspected the public GitHub repository using read-only access; prepared the starter-derived app, tests, fixed reference implementation, skill reference text, report draft, prompt template and this disclosure. | `app/**`, `buggy/**` retained from instructor ZIP, `tests/**` retained from instructor ZIP, `skills/bug-detector/SKILL.md`, `skills/bug-detector.zip`, `lab-report.md`, `AI_USAGE.md`, `submission.yml`, `NEXT_STEPS.md`, `diagnosis-input-template.txt` |

**Project provenance:** No Week 06 project or completed Week 07 project was found in the supplied `yrysbekshadi/Software` repository. The included Smart Campus app is derived from the instructor-provided Week 07 `starter/`, which Practice #07 explicitly permits when no Week 06 project is available. It is not represented as the student's Week 06 project.

**Skill requirement:** The `SKILL.md` included here is an AI-created reference copy of the exact text in the handout. It was NOT typed by the student. To comply with the instructor's “type it by hand” requirement, the student must open a plain-text editor, manually retype the text, read it, save it as exactly `SKILL.md`, and regenerate `skills/bug-detector.zip`. Do not answer “yes” to the manual typing check until that is done.

**Diagnostics:** The two deck questions have not yet been run in separate fresh chats. No chat transcript is fabricated in `lab-report.md`. The student must collect both answers using the identical acceptance criteria, actual BUG-A failing output, and provided buggy function; only the question changes.

**Testing and evidence:** `npm install` was attempted in the preparation container and timed out while reaching the package registry. No Vitest run, browser screenshot, skill installation screenshot, mutation trial, Git commit or Pull Request is claimed. All placeholders and “not yet run” notes must be replaced only with the student's actual outputs.

**Patches:** The final `app/src/booking.ts` contains the two required one-line repairs: strict interval-overlap comparisons for BUG-A and removal of the bookings-array mutation for BUG-B. The student must reproduce both failures on the copied buggy function first, then apply/commit each fix separately and verify it locally.

Signed: Shadi Yrysbek (review and update before submission)  
Date: 8 November 2026
