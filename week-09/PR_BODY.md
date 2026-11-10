## What this PR does

Turns canBook into the tool `check_room`: a name, a description, and an input schema in `tool/check_room.json`. Twelve fixed calls are checked by `tests/check_tool.py`. Three fresh chats produced `calls/r1.json`, `calls/r2.json`, and `calls/r3.txt`.

## How to check

```bash
cd week-09
python tests/check_tool.py
python tests/validate_submission.py
```

`check_tool.py` is 30 PASS, 0 FAIL, 0 ERROR. `validate_submission.py` passes once this branch is pushed.

## Decisions

R2 is a real call even though the room is blocked and the interval is 150 minutes. R3 was a question, not a guess. A7 and A8 are block. The checkpoint before the week-09 files is `23d8110` on main, restored with `git reset --hard 23d8110`.

## AI use

Level D. Grok drafted the schema and the report. Three fresh Grok chats wrote the files in `calls/`, saved unedited. Disclosed in `AI_USAGE.md`. `definition_written_by_me` is no.

## Left open

The PR stays open and is not merged. Student: Shadi Yrysbek, 24B031125, GitHub `yrysbekshadi`.
