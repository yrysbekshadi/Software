def analyze_marks(marks, pass_mark=50):
    average = sum(marks) / len(marks)
    highest = max(marks)
    lowest = min(marks)
    
    passed = sum(mark >= pass_mark for mark in marks)
    pass_rate = passed / len(marks) * 100

    return {
        "average": average,
        "highest": highest,
        "lowest": lowest,
        "pass_rate": pass_rate
    }


# Example
marks = [75, 60, 45, 90, 50, 30]

result = analyze_marks(marks)

print(result)
