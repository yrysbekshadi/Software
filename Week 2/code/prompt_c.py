def analyze_marks(marks, pass_mark=50):
    if not marks:
        raise ValueError("Marks list cannot be empty")

    for mark in marks:
        if isinstance(mark, bool) or not isinstance(mark, (int, float)):
            raise ValueError("Marks must be numeric")

        if mark < 0 or mark > 100:
            raise ValueError("Marks must be between 0 and 100")

    if isinstance(pass_mark, bool) or not isinstance(pass_mark, (int, float)):
        raise ValueError("pass_mark must be numeric")

    average = sum(marks) / len(marks)
    highest = max(marks)
    lowest = min(marks)
    pass_rate = round(
        sum(mark >= pass_mark for mark in marks) / len(marks) * 100,
        2
    )

    return {
        "average": average,
        "highest": highest,
        "lowest": lowest,
        "pass_rate": pass_rate
    }


# Tests

# 1. Normal example
assert analyze_marks([40, 60, 80], 50) == {
    "average": 60.0,
    "highest": 80,
    "lowest": 40,
    "pass_rate": 66.67
}

# 2. One mark
assert analyze_marks([75]) == {
    "average": 75.0,
    "highest": 75,
    "lowest": 75,
    "pass_rate": 100.0
}

# 3. Decimal marks
assert analyze_marks([50.5, 70.5, 90.0]) == {
    "average": 70.33333333333333,
    "highest": 90.0,
    "lowest": 50.5,
    "pass_rate": 100.0
}

# 4. Custom pass_mark
assert analyze_marks([40, 60, 80], 70) == {
    "average": 60.0,
    "highest": 80,
    "lowest": 40,
    "pass_rate": 33.33
}

# 5. Empty list
try:
    analyze_marks([])
    assert False
except ValueError:
    pass

# 6. Text value
try:
    analyze_marks([40, "60", 80])
    assert False
except ValueError:
    pass

# 7. Mark below 0
try:
    analyze_marks([-10, 50, 80])
    assert False
except ValueError:
    pass

# 8. Mark above 100
try:
    analyze_marks([50, 80, 110])
    assert False
except ValueError:
    pass

print("All tests passed!")
