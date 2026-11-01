# AI Usage Disclosure — SIS #03

AI use is required by the assignment (Level D). The submitted materials must disclose every tool that contributed to the work. The student remains responsible for checking, understanding and defending all submitted work. ChatGPT contributed substantially to the Python implementation, test suite, analysis and report drafting; this work is not represented as unaided student work.

| Tool | Exact model / plan | Used for | Which files it touched | Reused from |
| --- | --- | --- | --- | --- |
| ChatGPT (web) | GPT-6 | Plan, fresh Python v1, branch review, final Python implementation, unit-test design, code critique, Bolt prompt drafting, report updates, baseline summary and reflection draft, and post-export scope review | `report.md`, `code/original/booking_v1.py`, `code/booking.py`, `code/test_booking.py`, `BOLT_PROMPT_TO_PASTE.md`, `AI_USAGE.md`, final `web/final/package.json` and `web/final/package-lock.json` cleanup | this SIS |
| Bolt.new | Model label not displayed in the visible session | Fresh one-page web v1, then focused repair of the Assessment Test Controls UI; build/typecheck status and T3/T10 behaviour were reported in its visible response | `web/original/`, `web/final/`, with user-captured screenshots in `evidence/` | fresh |
| Local shell / Python | Local runtime; no model | Extracted ZIPs, compared v1/final source, ran Python tests and SIS checker, assembled exports and copied/cropped user screenshots | `web/original/`, `web/final/`, `report.md`, `submission.yml`, `evidence/` | this SIS |

**The assistant wrote, or helped write, my tests in `code/`:** yes. ChatGPT drafted the tests. Expected values were derived from AC1–AC5 and T1–T11 in the supplied handout, then the Python suite was run locally.

**`code/original/` and `web/original/` hold the first versions as generated/exported:** yes. The Python v1 is preserved from the Generate response. The Bolt v1 export was retained before the later UI repair; the final export is separate. The v1 export itself was not edited. The final export received a manifest-only cleanup to remove an unused Supabase SDK dependency after source review.

**Screenshots are unedited:** no. The supplied original screenshots are preserved unchanged in `evidence/source-originals/`; `final-narrow.png` is a crop of the original 379 × 644 responsive preview to isolate the portrait device area. No UI content was redrawn or composited.

**Every result in report.md section 5 was actually run or seen:** no. Python T1–T11 were executed locally. For the page, the supplied screenshots show v1 T1/T2 and final T3/T10 only. The remaining page cases are marked Not run; T8/T9 are Not testable through the native time input. The 379 px mobile layout was captured, but T1 was not recorded at that width.

**Everything submitted can be explained and defended:** not yet confirmed by the student. The student must inspect the source, test cases, report and screenshots before submission and be ready to explain each decision.

**Anything accepted from AI without fully understanding it:** this must be answered by the student after reviewing the function, tests, Bolt code and scope cleanup. Do not leave it blank if any part remains unclear.

Student-provided identity: Shadi Yrysbek (24B031125).

Student contribution recorded from this conversation: supplied the course brief and starter project; used the Bolt.new interface to generate and download the web project; provided screenshots of the v1, T3, T10 and narrow viewport; supplied the Bolt export ZIPs. ChatGPT generated/reviewed the Python code and tests, analyzed the exports, drafted report content and assembled this package. The student must verify these descriptions and remove or correct anything inaccurate.

Signed: Shadi Yrysbek — pending the student's final review and approval.
Date: 2026-11-01
