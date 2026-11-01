def can_book(start, end, now, blocked, existing):
    """Return whether a room booking request appears to be available."""
    if start < 0 or end > 1440 or start > end:
        return False
    if start < now:
        return False
    if end - start > 120:
        return False
    if blocked:
        return False
    for existing_start, existing_end in existing:
        if start <= existing_end and end >= existing_start:
            return False
    return True
