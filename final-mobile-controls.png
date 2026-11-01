Build a responsive, single-page web prototype named “Smart Campus Room Availability Checker”.

Purpose and scope:
- A student checks whether one selected campus room is available for a proposed time interval.
- Use one selected room only (label it “Room A-204”) and fictional, hard-coded booking data.
- The page checks availability only. It must never create, reserve, submit, or confirm a booking.
- Do not add login, sign-in, authentication, backend, database, external API, payments, analytics, or unrelated features.
- No network requests and no browser storage. Keep all demo data in memory and do not mutate the existing bookings during a check.

Implement these fixed acceptance criteria without changing their meaning:
AC1: Candidate times represent integer minutes after midnight and must satisfy 0 <= start < end <= 1440. The start must be strictly after the current time. Use a demo current time of 09:00 (540 minutes) so the supplied acceptance cases can be reproduced consistently.
AC2: Duration must be no more than 120 minutes; exactly 120 minutes is valid.
AC3: If Room A-204 is blocked, every request is Unavailable.
AC4: Reject overlap with any existing booking. Treat intervals as [start, end): touching at an endpoint is NOT overlap. Use the demo booking 10:00–11:00 (600–660 minutes).
AC5: Show a clear, unambiguous “Available” or “Unavailable” result, plus a human-readable reason. Checking must not append, remove, sort, or otherwise mutate existing bookings.
AC6: Give understandable validation messages for invalid time order, past/current start, too-long duration, blocked room and overlap. The page must remain usable at a narrow phone width around 375 px, with labels, controls and result visible without horizontal scrolling.

UI requirements:
- Clean campus-style interface, restrained colors, readable typography and clear spacing.
- Show the selected room, demo current time (09:00), existing demo booking(s), start and end time inputs, a “Check availability” button, and a result area.
- Use native time inputs if appropriate; if the browser cannot represent 24:00, state that the page input cannot test the 1440-minute endpoint rather than silently changing the rule.
- Do not include a “Book”, “Confirm”, or “Reserve” button.
- Keep the implementation simple and self-contained. Do not add features outside this specification.

Before finishing, inspect the generated implementation against AC1–AC6 and explain where each rule is enforced. Do not claim tests were run unless you actually run them.

---

## Test-control addendum used with the v1 generation

Add a small "Test setup" section with two controls:

1. A "Simulate room blocked" toggle, OFF by default. When ON, every availability request must return Unavailable.
2. An "Include second demo booking" toggle, OFF by default. When ON, include a second fictional booking from 11:40 to 12:40 alongside the original 10:00–11:00 booking. Use a separate derived array; never mutate the original bookings.

These controls exist only to reproduce AC3 and T10. Do not add real booking creation or any backend functionality.

**Status:** Fresh v1 was generated in Bolt.new and exported to `web/original/`. The later focused UI repair is reflected in `web/final/`.
