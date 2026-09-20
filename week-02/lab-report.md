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

---

## 4. Prompt C — examples and tests

**What I appended to Prompt B:**

```text
Example: analyze_marks([40, 60, 80], 50) → average 60, highest 80, lowest 40,
pass_rate 66.67. Include tests for: one mark, decimals, custom pass_mark, empty list,
text value, and marks below 0 or above 100. State any remaining assumptions before
the code.
```

**Tests the AI wrote for itself** — how many, and which situations do they cover?

The AI wrote 8 test sections. They covered all six requested situations and also checked the worked example.

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

No separate assumptions were stated before the code. The implementation itself added validation for numeric `pass_mark` and rounded `pass_rate` to two decimal places.

## 5. Prompt D — my combined prompt

**The complete prompt I wrote** (one message, sent to a fresh chat):

```text
You are a Python developer  Сделай функцию analyze_marks(marks, pass_mark=50  ) Функция должна возвращать словарь с четырьмя ключами: "average", "highest", "lowest" и "pass_rate" каждая оценка должна быть в диапазоне от 0 до 100 включительно  предмет считается пройденным если она >= pass_mark если оценка не соответствует требованием вызывай ValueError pass_rate должен рассчитываться как процент пройденных оценок и округляться до двух знаков после запятой Используйте только возможности стандартной библиотеки Example: analyze_marks([40, 60, 80], 50) → average 60, highest 80, lowest 40, pass_rate 66.67. Include tests for: one mark, decimals, custom pass_mark, empty list, text value, and marks below 0 or above 100. State any remaining assumptions before the code.
```

**What I deliberately added that A, B and C did not have:**

1. I explicitly required `pass_rate` to be rounded to two decimal places because the example showed `66.67` while B did not define a rounding rule.
2. I made the threshold rule explicit with `>= pass_mark`, resolving the boundary condition for a mark exactly equal to the pass mark.
3. I combined the validation, standard-library constraint, worked example, and required tests into one prompt instead of relying on separate follow-up clarification.

**The ambiguity I found in the specification, and how I resolved it inside Prompt D:**

The main ambiguity was the rounding rule for `pass_rate`. The example uses `66.67`, but the original structured prompt did not explicitly state how many decimal places to return. I resolved this by requiring `pass_rate` to be rounded to two decimal places. I also made the equality condition explicit: a mark equal to `pass_mark` passes because the rule is `>=`.

## 6. Test results — the evidence

Six cases × four prompts. Verdicts are **PASS**, **FAIL** or **ERROR** only.

| # | Call | Required | A | B | C | D |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `analyze_marks([40, 60, 80], 50)` | avg 60 · high 80 · low 40 · rate 66.67 | PASS | PASS | PASS | PASS |
| 2 | `analyze_marks([100], 50)` | avg 100 · high 100 · low 100 · rate 100 | PASS | PASS | PASS | PASS |
| 3 | `analyze_marks([49.5, 50], 50)` | avg 49.75 · high 50 · low 49.5 · rate 50 | PASS | PASS | PASS | PASS |
| 4 | `analyze_marks([], 50)` | raises ValueError | ERROR | PASS | PASS | PASS |
| 5 | `analyze_marks([40, "60"], 50)` | raises ValueError | ERROR | PASS | PASS | PASS |
| 6 | `analyze_marks([-1, 50, 101], 50)` | raises ValueError | FAIL | PASS | PASS | PASS |
| | **Totals** | | **3/6** | **6/6** | **6/6** | **6/6** |

**For every FAIL and ERROR above, one line: what was returned or raised instead.**

| Prompt | Case | What actually happened |
| --- | --- | --- |
| A | 4 | Raised `ZeroDivisionError: division by zero` instead of `ValueError`. |
| A | 5 | Raised `TypeError: unsupported operand type(s) for +: 'int' and 'str'` instead of `ValueError`. |
| A | 6 | Returned `{'average': 50.0, 'highest': 101, 'lowest': -1, 'pass_rate': 66.66666666666666}` instead of rejecting the input. |

### Pasted terminal output — all four runs

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
          expect: average=49.75, highest=50, lowest=49.5, pass_rate=50.0
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
All tests passed!
========================================================================
analyze_marks harness — code/prompt_d.py
tolerance for numeric comparison: 0.01
========================================================================
SIGNATURE: ok
------------------------------------------------------------------------
case 1  PASS   analyze_marks([40, 60, 80], 50)
          expect: average=60.0, highest=80, lowest=40, pass_rate=66.67
          got   : average=60, highest=80, lowest=40, pass_rate=66.67
------------------------------------------------------------------------
case 2  PASS   analyze_marks([100], 50)
          expect: average=100.0, highest=100, lowest=100, pass_rate=100.0
          got   : average=100, highest=100, lowest=100, pass_rate=100.0
------------------------------------------------------------------------
case 3  PASS   analyze_marks([49.5, 50], 50)
          expect: average=49.75, highest=50, lowest=49.5, pass_rate=50.0
          got   : average=49.75, highest=50, lowest=49.5, pass_rate=50
------------------------------------------------------------------------
case 4  PASS   analyze_marks([], 50)
          expect: ValueError
          got   : raised ValueError: marks must not be empty
------------------------------------------------------------------------
case 5  PASS   analyze_marks([40, '60'], 50)
          expect: ValueError
          got   : raised ValueError: every mark must be a number
------------------------------------------------------------------------
case 6  PASS   analyze_marks([-1, 50, 101], 50)
          expect: ValueError
          got   : raised ValueError: every mark must be between 0 and 100
------------------------------------------------------------------------
RESULT  6 PASS · 0 FAIL · 0 ERROR   (code/prompt_d.py)
========================================================================
```

## 7. Scoring

0–2 per criterion, using the rubric in `README.md` Part 7.

| Criterion | A | B | C | D |
| --- | --- | --- | --- | --- |
| Correctness (cases passed) | 1 | 2 | 2 | 2 |
| Requirement coverage | 0 | 2 | 2 | 2 |
| Verifiability (tests) | 0 | 0 | 2 | 2 |
| Assumptions stated | 0 | 0 | 0 | 0 |
| Noise (2 = none) | 1 | 2 | 1 | 1 |
| **Total / 10** | **2** | **6** | **7** | **7** |

**Prompt length, in words:** A **7** · B **44** · C **84** · D **106**

**Words added per point gained** — B over A, C over B, D over C. One line on what that ratio says:

B added 37 words for 4 points (+9.25 words/point); C added 40 words for 1 point (+40 words/point); D added 22 words for 0 points (+∞ words/point). This shows that extra prompt length produced diminishing returns after B, and the additional words in D did not improve the external six-case score beyond C.

## 8. Conclusion — 150–200 words

Prompts C and D tied for the highest score at 7/10. Both passed all six external cases, but D is the prompt I would actually use at work because it combines the useful requirements into one message and resolves the two main ambiguities I found. The single addition that bought the most correctness was explicit validation. From A to B, case 4 changed from ERROR because of ZeroDivisionError to PASS with ValueError for an empty list. The same validation addition also fixed case 5, where A raised TypeError for the text value, and case 6, where A accepted marks outside 0–100. C's worked example and required tests then made rounding explicit in the implementation and produced 66.67 exactly. One piece of noise in C was the extra “All tests passed!” print, because the external harness already supplied the real measurement. D also added some extra validation, such as rejecting boolean marks and validating pass_mark, which did not affect any of the six scored cases. The main ambiguity was the rounding rule for pass_rate; I resolved it by requiring rounding to two decimal places and by stating that marks equal to pass_mark pass because the condition is >=.

**Word count:** 175

## 9. Two questions for the debrief

1. Why did Prompt B fix cases 4–6 even though it was still much shorter than C and D?
2. When does adding more detail to a prompt stop improving the result and start adding noise or new failure modes?
