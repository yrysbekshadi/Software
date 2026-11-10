# AI Usage Disclosure — Week 09

Required by the course academic policy (Generative AI use level **D — AI-integrated**).
You are responsible for the accuracy, testing and integrity of everything you submit,
including anything an AI tool produced.

| Tool | Exact model / plan | Used for | Which files it touched |
| --- | --- | --- | --- |
| Grok | not displayed (Grok Build, xAI, April 2026) | Part 2 — three separate fresh chats, one per request, wrote the replies saved in calls/ | calls/r1.json, calls/r2.json, calls/r3.txt |
| Grok | not displayed (Grok Build, xAI, April 2026) | Drafted the tool schema, the constraint table, the permission decisions, and this disclosure, at the student's request | tool/check_room.json, lab-report.md, AI_USAGE.md, submission.yml |

**I wrote `tool/check_room.json` myself:** no
Grok drafted the schema. It was then checked with `python3 tests/check_tool.py`. The first run was recorded before that schema replaced the starter. Every keyword in it is one the checker allows, and S01–S12 were re-run after the edit.

**I used an AI to explain a JSON Schema keyword or a check:** yes
Grok used `additionalProperties`, `minimum`, `maximum`, and `items` to make S03–S10 and S12 fail closed, and kept `maximum` at 1440 so S11 still passes. No keyword outside the README list was used.

**Every reply in `calls/` and in lab-report.md section 4 is exactly what the model returned:** yes

**Every terminal output in lab-report.md was pasted from a real run, unedited:** yes

**Anything I accepted from the AI without fully understanding it:**
The schema, the section 5 and 6 prose, and the conclusion were drafted by Grok because the student asked for the lab to be done. The calls were not hand-corrected. Before this is submitted, the student should be able to explain why S07 needs a maximum, why R2 is still a call, and why A7 and A8 are block.

Signed: Shadi Yrysbek
Date: 10 November 2026
