# Assumptions:

# - Numeric values include int, float, and other Real-like standard-library numeric types,

# but bool is explicitly invalid.

# - pass_mark is validated the same way as marks: numeric, not bool, and within 0–100.

# - Tests use assert statements and do not add any CLI or file I/O.

from numbers import Real

def analyze_marks(marks, pass_mark=50):

if not isinstance(marks, list):

raise ValueError("marks must be a non-empty list")

```
```

```
```

if not marks:
    raise ValueError("marks must be a non-empty list")

if isinstance(pass_mark, bool) or not isinstance(pass_mark, Real):
    raise ValueError("pass_mark must be numeric")

if not 0 <= pass_mark <= 100:
    raise ValueError("pass_mark must be between 0 and 100")

for mark in marks:
    if isinstance(mark, bool) or not isinstance(mark, Real):
        raise ValueError("marks must contain only numeric values")

    if not 0 <= mark <= 100:
        raise ValueError("marks must be between 0 and 100")

average = sum(marks) / len(marks)
highest = max(marks)
lowest = min(marks)
passed = sum(mark >= pass_mark for mark in marks)
pass_rate = round(passed / len(marks) * 100, 2)

return {
    "average": average,
    "highest": highest,
    "lowest": lowest,
    "pass_rate": pass_rate
}

# Tests

# 1. One mark
assert analyze_marks([75]) == {
"average": 75.0,
"highest": 75,
"lowest": 75,
"pass_rate": 100.0
}

# 2. Decimal marks
result = analyze_marks([55.5, 70.25, 80.75])

assert result["average"] == 68.83333333333333
assert result["highest"] == 80.75
assert result["lowest"] == 55.5
assert result["pass_rate"] == 100.0

# 3. Custom pass_mark
assert analyze_marks([40, 60, 80], 70) == {
"average": 60.0,
"highest": 80,
"lowest": 40,
"pass_rate": 33.33
}

# Example
assert analyze_marks([40, 60, 80], 50) == {
"average": 60.0,
"highest": 80,
"lowest": 40,
"pass_rate": 66.67
}

# 4. Empty list
try:

analyze_marks([])

assert False

except ValueError:

pass

# 5. Text value
try:

analyze_marks([40, "60", 80])

assert False

except ValueError:

pass

# 6. Values below 0 or above 100
try:

analyze_marks([-1, 50, 80])

assert False

except ValueError:

pass

try:

analyze_marks([40, 50, 101])

assert False

except ValueError:

pass

# Additional validation tests

# bool mark is invalid
try:

analyze_marks([40, True, 80])

assert False

except ValueError:

pass

# bool pass_mark is invalid
try:

analyze_marks([40, 60], True)

assert False

except ValueError:

pass

# pass_mark outside valid range
try:

analyze_marks([40, 60], 101)

assert False

except ValueError:

pass

try:

analyze_marks([40, 60], -1)

assert False

except ValueError:

pass
