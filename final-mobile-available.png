def can_book(start, end, now, blocked, existing):
    """Check a proposed room interval without creating or changing bookings.

    Times are integer minutes after midnight. The candidate interval is
    [start, end), so two intervals that only touch at an endpoint do not
    overlap. `existing` is read-only from this function's point of view.
    """
    # AC1: accept integer minute values only, within one day, with positive
    # duration and a start strictly later than the current time.
    if any(type(value) is not int for value in (start, end, now)):
        return False
    if not (0 <= start < end <= 1440):
        return False
    if start <= now:
        return False

    # AC2: exactly 120 minutes is allowed; anything longer is not.
    if end - start > 120:
        return False

    # AC3: a blocked room cannot be available for any requested interval.
    if blocked:
        return False

    # AC4: half-open intervals overlap only when each starts before the
    # other one ends. Strict inequalities allow endpoint touching.
    for existing_start, existing_end in existing:
        if start < existing_end and existing_start < end:
            return False

    # AC5: return a Boolean only; do not append, sort, or otherwise mutate
    # the caller's existing-bookings collection.
    return True
