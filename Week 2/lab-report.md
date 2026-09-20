# Lab report — Practice #02: The Prompt Is an Engineering Input

**Name:** Shadi Yrysbek
**Group:** Monday 16:00 - 19:00
**Date:** 20 September 2026

> Fill in every section. **Do not delete or renumber the headings** — the grading pass reads them by number. If something did not happen, write "did not happen" and why; an empty section and a fabricated one are graded the same way.

## 1. The frozen experiment

| | |
| --- | --- |
| AI assistant | ChatGPT |
| Exact model name | GPT-5.6 Luna |
| Implementation language | Python |
| Date of the runs | 20 September 2026 |

**Non-Python students only** — paste your substituted Prompt B text here, so the substitution can be checked:

```text
n/a — used Python
```

**Confirmations:**

- Each prompt was sent in a **fresh chat**: yes
- No follow-up questions were asked before Part 7: yes
- Every output was saved **before** any editing: yes

## 2. Prompt A — minimal

**Prompt sent** (should be exactly one sentence):

```text
Write Python code to analyze student marks.
```

**Assumptions the AI made that I never gave it** — list them, one per line. A data format, a pass threshold, a rounding rule, an input method, an invented feature all count.

1. It assumed that `marks` would be a non-empty collection of numeric values.
2. It assumed a default pass mark of 50 and implemented the required signature even though the prompt itself did not specify it.
3. It did not specify any deliberate error handling for invalid input.
4. It did not specify a rounding rule for `pass_rate`.
5. It added an example execution and `print()` statement, although no example or output was requested.

**Questions it should have asked and did not:**

1. What should happen for an empty list, non-numeric value, or out-of-range mark?
2. Should `pass_rate` be rounded, and if so, to how many decimal places?

**Is the function named `analyze_marks` with the required signature?** yes — it is called `analyze_marks(marks, pass_mark=50)`.

**First impression before testing:**
The code looked correct for normal numeric input, but it appeared to rely on unstated assumptions about invalid input handling and rounding.

## 3. Prompt B — structured context

**Prompt sent** (paste it in full, including any substitutions):

```text
You are a Python developer. Implement analyze_marks(marks, pass_mark=50). Return
average, highest, lowest, and pass_rate in a dictionary. Accept marks from 0 to 100;
raise ValueError for an empty list, non-numeric values, or out-of-range values. Use
no external libraries. Return code plus a short explanation.
```

**What B fixed compared to A:**

1. It explicitly required the `analyze_marks(marks, pass_mark=50)` signature and four dictionary keys.
2. It added deliberate `ValueError` handling for empty, non-numeric, and out-of-range marks.
3. It removed A's unnecessary example execution and print output.

**What B still leaves open:**

1. It does not explicitly state that `pass_rate` should be rounded to two decimal places.
2. It does not explicitly define validation rules for `pass_mark` itself.

## 4. Prompt C — examples and tests

**What I appended to Prompt B:**

```text
Example: analyze_marks([40, 60, 80], 50) → average 60, highest 80, lowest 40,
pass_rate 66.67. Include tests for: one mark, decimals, custom pass_mark, empty list,
text value, and marks below 0 or above 100. State any remaining assumptions before
the code.
```

**Tests the AI wrote for itself** — how many, and which situations do they cover?

The AI wrote 8 test sections. They covered all six requested situations and also checked an example case separately.

| Situation | Covered by the AI's tests? |
| --- | --- |
| one mark | yes |
| decimals | yes |
| custom pass_mark | yes |
| empty list | yes |
| text value | yes |
| below 0 / above 100 | yes |

**Do the AI's own tests pass against the AI's own code?** yes

**Do they agree with the harness in section 6?** yes — all six external harness cases also PASS.

**Assumptions C stated explicitly before the code:**

No separate natural-language assumptions were stated before the code. The implementation itself added validation for numeric `pass_mark` and rounded `pass_rate` to two decimal places.

## 5. Prompt D — my combined prompt

**The complete prompt I wrote** (one message, sent to a fresh chat):

```text
You are a Python developer. Implement exactly this function:

analyze_marks(marks, pass_mark=50)

The function must return a dictionary with exactly these four keys:
"average", "highest", "lowest", and "pass_rate".

Requirements:
- marks must be a non-empty list of numbers.
- Every mark must be between 0 and 100 inclusive.
- A mark passes when it is >= pass_mark.
- Raise ValueError for an empty list, a non-numeric mark, or any mark outside 0–100.
- Treat bool values as invalid numeric marks.
- pass_mark must be numeric and between 0 and 100 inclusive.
- pass_rate must be calculated as the percentage of marks that pass and rounded to exactly 2 decimal places.
- Use only Python standard-library features; no external libraries.
- Do not add a CLI, file input/output, or unrelated features.
- Return only valid Python code, with no Markdown fences or explanation outside the code.

Example:
analyze_marks([40, 60, 80], 50)
must return
{"average": 60.0, "highest": 80, "lowest": 40, "pass_rate": 66.67}

Before the code, state any assumptions you are making as comments.

Include tests covering:
1. one mark,
2. decimal marks,
3. a custom pass_mark,
4. an empty list,
5. a text value,
6. values below 0 or above 100.
```

**What I deliberately added that A, B and C did not have:**

1. I explicitly required `pass_rate` to be rounded to two decimal places because B left this ambiguous and C resolved it in its implementation.
2. I explicitly defined `pass_mark` as numeric and limited it to 0–100 to resolve the remaining ambiguity about the threshold.
3. I explicitly prohibited Markdown fences, CLI/file I/O, and unrelated features so the generated response could be tested directly without extra scope.

**The ambiguity I found in the specification, and how I resolved it inside Prompt D:**

The main ambiguity was whether `pass_rate` should be rounded to two decimal places. The worked example uses `66.67`, while the original requirements did not explicitly define a rounding rule. I resolved this in Prompt D by requiring `pass_rate` to be rounded to exactly two decimal places.

## 6. Test results — the evidence

Six cases × four prompts. Verdicts are **PASS**, **FAIL** or **ERROR** only.

| # | Call | Required | A | B | C | D |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `analyze_marks([40, 60, 80], 50)` | avg 60 · high 80 · low 40 · rate 66.67 | PASS | PASS | PASS | ERROR |
| 2 | `analyze_marks([100], 50)` | avg 100 · high 100 · low 100 · rate 100 | PASS | PASS | PASS | ERROR |
| 3 | `analyze_marks([49.5, 50], 50)` | avg 49.75 · high 50 · low 49.5 · rate 50 | PASS | PASS | PASS | ERROR |
| 4 | `analyze_marks([], 50)` | raises ValueError | ERROR | PASS | PASS | ERROR |
| 5 | `analyze_marks([40, "60"], 50)` | raises ValueError | ERROR | PASS | PASS | ERROR |
| 6 | `analyze_marks([-1, 50, 101], 50)` | raises ValueError | FAIL | PASS | PASS | ERROR |
| | **Totals** | | **3/6** | **6/6** | **6/6** | **0/6** |

**For every FAIL and ERROR above, one line: what was returned or raised instead.**

| Prompt | Case | What actually happened |
| --- | --- | --- |
| A | 4 | Raised `ZeroDivisionError: division by zero` instead of `ValueError`. |
| A | 5 | Raised `TypeError: unsupported operand type(s) for +: 'int' and 'str'` instead of `ValueError`. |
| A | 6 | Returned `{'average': 50.0, 'highest': 101, 'lowest': -1, 'pass_rate': 66.66666666666666}` instead of rejecting the input. |
| D | 1–6 | The module could not be imported because of `IndentationError: expected an indented block after function definition on line 13 (prompt_d.py, line 15)`. The six cases therefore did not run. |

### Pasted terminal output — all four runs

> This is the part that makes the table above count. Paste the **whole** output, unedited, including the header lines. A table with nothing behind it is not accepted.

**Prompt A**

```text
{'average': 58.333333333333336, 'highest': 90, 'lowest': 30, 'pass_rate': 66.66666666666666}
========================================================================
analyze_marks harness — code/prompt_a.py
tolerance for numeric comparison: 0.01
========================================================================
SIGNATURE: ok
------------------------------------------------------------------------
case 1  PASS   analyze_marks([40, 60, 80], 50)
          expect: average=60.0, highest=80, lowest=40, pass_rate=66.67
          got   : average=60.0, highest=80, lowest=40, pass_rate=66.66666666666666
------------------------------------------------------------------------
case 2  PASS   analyze_marks([100], 50)
          expect: average=100.0, highest=100, lowest=100, pass_rate=100.0
          got   : average=100.0, highest=100, lowest=100, pass_rate=100.0
------------------------------------------------------------------------
case 3  PASS   analyze_marks([49.5, 50], 50)
          expect: average=49.75, highest=50, lowest=49.5, pass_rate=50.0
          got   : average=49.75, highest=50, lowest=49.5, pass_rate=50.0
------------------------------------------------------------------------
case 4  ERROR  analyze_marks([], 50)
          expect: ValueError
          got   : raised ZeroDivisionError instead of ValueError: division by zero
------------------------------------------------------------------------
case 5  ERROR  analyze_marks([40, '60'], 50)
          expect: ValueError
          got   : raised TypeError instead of ValueError: unsupported operand type(s) for +: 'int' and 'str'
------------------------------------------------------------------------
case 6  FAIL   analyze_marks([-1, 50, 101], 50)
          expect: ValueError
          got   : returned {'average': 50.0, 'highest': 101, 'lowest': -1, 'pass_rate': 66.66666666666666} where ValueError was required
------------------------------------------------------------------------
RESULT  3 PASS · 1 FAIL · 2 ERROR   (code/prompt_a.py)
========================================================================
```

**Prompt B**

```text
========================================================================
analyze_marks harness — code/prompt_b.py
tolerance for numeric comparison: 0.01
========================================================================
SIGNATURE: ok
------------------------------------------------------------------------
case 1  PASS   analyze_marks([40, 60, 80], 50)
          expect: average=60.0, highest=80, lowest=40, pass_rate=66.67
          got   : average=60.0, highest=80, lowest=40, pass_rate=66.66666666666666
------------------------------------------------------------------------
case 2  PASS   analyze_marks([100], 50)
          expect: average=100.0, highest=100, lowest=100, pass_rate=100.0
          got   : average=100.0, highest=100, lowest=100, pass_rate=100.0
------------------------------------------------------------------------
case 3  PASS   analyze_marks([49.5, 50], 50)
          expect: average=49.75, highest=50, lowest=49.5, pass_rate=50.0
          got   : average=49.75, highest=50, lowest=49.5, pass_rate=50.0
------------------------------------------------------------------------
case 4  PASS   analyze_marks([], 50)
          expect: ValueError
          got   : raised ValueError: Marks list cannot be empty
------------------------------------------------------------------------
case 5  PASS   analyze_marks([40, '60'], 50)
          expect: ValueError
          got   : raised ValueError: All marks must be numeric
------------------------------------------------------------------------
case 6  PASS   analyze_marks([-1, 50, 101], 50)
          expect: ValueError
          got   : raised ValueError: Marks must be between 0 and 100
------------------------------------------------------------------------
RESULT  6 PASS · 0 FAIL · 0 ERROR   (code/prompt_b.py)
========================================================================
```

**Prompt C**

```text
All tests passed!
========================================================================
analyze_marks harness — code/prompt_c.py
tolerance for numeric comparison: 0.01
========================================================================
SIGNATURE: ok
------------------------------------------------------------------------
case 1  PASS   analyze_marks([40, 60, 80], 50)
          expect: average=60.0, highest=80, lowest=40, pass_rate=66.67
          got   : average=60.0, highest=80, lowest=40, pass_rate=66.67
------------------------------------------------------------------------
case 2  PASS   analyze_marks([100], 50)
          expect: average=100.0, highest=100, lowest=100, pass_rate=100.0
          got   : average=100.0, highest=100, lowest=100, pass_rate=100.0
------------------------------------------------------------------------
case 3  PASS   analyze_marks([49.5, 50], 50)
          expect: average=49.75, highest=50, lowest=50.5, pass_rate=50.0
          got   : average=49.75, highest=50, lowest=49.5, pass_rate=50.0
------------------------------------------------------------------------
case 4  PASS   analyze_marks([], 50)
          expect: ValueError
          got   : raised ValueError: Marks list cannot be empty
------------------------------------------------------------------------
case 5  PASS   analyze_marks([40, '60'], 50)
          expect: ValueError
          got   : raised ValueError: Marks must be numeric
------------------------------------------------------------------------
case 6  PASS   analyze_marks([-1, 50, 101], 50)
          expect: ValueError
          got   : raised ValueError: Marks must be between 0 and 100
------------------------------------------------------------------------
RESULT  6 PASS · 0 FAIL · 0 ERROR   (code/prompt_c.py)
========================================================================
```

**Prompt D**

```text
ERROR: code/prompt_d.py could not be imported: IndentationError: expected an indented block after function definition on line 13 (prompt_d.py, line 15)
The file must define analyze_marks and must not crash on import.
```

## 7. Scoring

0–2 per criterion, using the rubric in `README.md` Part 7.

| Criterion | A | B | C | D |
| --- | --- | --- | --- | --- |
| Correctness (cases passed) | 1 | 2 | 2 | 0 |
| Requirement coverage | 1 | 2 | 2 | 2 |
| Verifiability (tests) | 0 | 0 | 2 | 1 |
| Assumptions stated | 0 | 0 | 0 | 2 |
| Noise (2 = none) | 1 | 2 | 2 | 1 |
| **Total / 10** | **3** | **6** | **8** | **6** |

**Prompt length, in words:** A 7 · B 44 · C 84 · D 198

**Words added per point gained** — B over A: 37 words / 3 points = **12.33 words per point**. C over B: 40 words / 2 points = **20 words per point**. D over C: **114 words added, but 1 point lost**, so no points were gained; the extra length did not improve the tested result.

The ratio suggests that adding a small amount of precise context gave the largest improvement early (A→B), while later additions increased prompt length more than they increased the score.

## 8. Conclusion — 150–200 words

Prompt C scored the highest at 8/10, while Prompt B scored 6/10 and Prompt A scored 3/10. Prompt D also scored 6/10 because its generated file could not be imported. The result I would use at work is closer to Prompt C: it combined precise requirements, a worked example, and tests without introducing the formatting problem that appeared in D. The single addition that bought the most correctness was the explicit validation rules in Prompt B. They changed cases 4, 5, and 6 from A’s ZeroDivisionError, TypeError, and incorrect returned value to PASS with deliberate ValueError exceptions. Prompt C’s rounding rule was also useful: case 1 changed from 66.66666666666666 to 66.67, matching the requested example. Some of C’s exact floating-point assertions were more specific than necessary, but they still passed the independent harness. Prompt D added extra validation for pass_mark and Real-like numeric types, but these additions did not improve the score because the response contained broken indentation and code-fence artifacts, causing an IndentationError before testing. The main ambiguity was pass_rate rounding; I resolved it in D by explicitly requiring two decimal places.

**Word count:** 183

## 9. Two questions for the debrief

1. Why did Prompt A pass all normal numeric cases even though it had no deliberate validation for invalid input?
2. Why did Prompt D fail to run even though it contained more detailed requirements than Prompts B and C?
