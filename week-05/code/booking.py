def can_book(start, end, now, blocked, existing):
    """Return whether the booking request is allowed."""
    if not (0 <= start < end <= 1440):
        return False
    if start <= now:
        return False
    if end - start > 120:
        return False
    if blocked:
        return False
    for booking_start, booking_end in existing:
        if start < booking_end and end > booking_start:
            return False
    return True
