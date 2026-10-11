# AI Usage Disclosure — Week 05

Required by the course policy (Generative AI use level **D — AI-integrated**). AI assistance is expected for this task; I remain responsible for the correctness, testing, review, and explanation of everything submitted.

| Tool | Exact model | Used for | Files touched or drafted |
| --- | --- | --- | --- |
| ChatGPT | GPT-6 | Implementation plan and boundary-case ideas | `lab-report.md` |
| ChatGPT | GPT-6 | Initial `can_book` implementation; it was preserved as the v1 snapshot and copied to the working file | `code/original/booking_v1.py`, `code/booking.py` |
| ChatGPT | GPT-6 | Test-case design, test table, review critique, debugging explanation, report wording, submission declaration | `code/test_booking.py`, `lab-report.md`, `AI_USAGE.md`, `submission.yml` |

**The assistant wrote or helped write my tests:** yes. Their expected values were determined from AC1–AC5 and the handout's six examples. I then ran the suite and the supplied checker in this environment. The final suite contains 24 tests; one test uses a float solely to document observed Python behaviour for an input outside the contract and is not used to claim a specification requirement.

**`code/original/` holds the assistant-generated first version without edits during this preparation:** yes. Important limitation: the required workflow in a separate fresh chat, with the specification block and unchanged prompts sent in order, has not been performed by me through the user's account. The report must not be represented as a transcript of that workflow. The saved v1 is the preserved AI-generated draft already supplied in this conversation.

**Can I explain and defend every line without AI right now?** Not yet verified. I must personally review the code, the interval-overlap logic, each expected test result, and the report before submitting.

**Anything accepted without full independent understanding:** The assistant drafted the implementation and the written review. I need to independently verify the strict overlap comparisons and the reasoning in sections 5, 6, and 9 of `lab-report.md` before claiming that I can defend them.

Signed: Shadi Yrysbek
Date: 2026-10-12
