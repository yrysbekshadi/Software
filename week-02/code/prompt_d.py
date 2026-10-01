def analyze_marks(marks, pass_mark=50):
    # Проверяем, что marks — список
    if not isinstance(marks, list):
        raise ValueError("marks must be a list")

    # Список не должен быть пустым
    if len(marks) == 0:
        raise ValueError("marks must not be empty")

    # Проверяем pass_mark
    if isinstance(pass_mark, bool) or not isinstance(pass_mark, (int, float)):
        raise ValueError("pass_mark must be a number")

    if not 0 <= pass_mark <= 100:
        raise ValueError("pass_mark must be between 0 and 100")

    # Проверяем каждую оценку
    for mark in marks:
        if isinstance(mark, bool) or not isinstance(mark, (int, float)):
            raise ValueError("every mark must be a number")

        if not 0 <= mark <= 100:
            raise ValueError("every mark must be between 0 and 100")

    average = round(sum(marks) / len(marks), 2)
    highest = max(marks)
    lowest = min(marks)

    passed = sum(mark >= pass_mark for mark in marks)
    pass_rate = round((passed / len(marks)) * 100, 2)

    return {
        "average": average,
        "highest": highest,
        "lowest": lowest,
        "pass_rate": pass_rate
    }


# =========================
# Tests
# =========================

# 1. Example
assert analyze_marks([40, 60, 80], 50) == {
    "average": 60,
    "highest": 80,
    "lowest": 40,
    "pass_rate": 66.67
}

# 2. One mark
assert analyze_marks([75]) == {
    "average": 75,
    "highest": 75,
    "lowest": 75,
    "pass_rate": 100.0
}

# 3. Decimal marks
assert analyze_marks([75.5, 80.5, 90.0]) == {
    "average": 82.0,
    "highest": 90.0,
    "lowest": 75.5,
    "pass_rate": 100.0
}

# 4. Custom pass_mark
assert analyze_marks([40, 60, 80], 70) == {
    "average": 60,
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
    assert False, "Expected ValueError"
except ValueError:
    pass

# 5. Text value
try:
    analyze_marks([50, "60", 70])
    assert False, "Expected ValueError"
except ValueError:
    pass

# 6. Mark below 0
try:
    analyze_marks([50, -10, 70])
    assert False, "Expected ValueError"
except ValueError:
    pass

# 8. Mark above 100
try:
    analyze_marks([50, 110, 70])
    assert False, "Expected ValueError"
except ValueError:
    pass

print("All tests passed!")
