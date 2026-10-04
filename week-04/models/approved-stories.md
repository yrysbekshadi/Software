# Approved stories — Smart Campus study room booking

> This lab uses the reference story set from README §3 because the Week 03 stories were not supplied with the Week 04 handout. The IDs below are the approved stories used for all three diagrams.

## Scenario

Students view room availability, book a room, and cancel their own bookings. Administrators block
or unblock rooms and review usage.

- **R1.** Future start, with duration greater than 0 and at most 2 hours.
- **R2.** Active bookings for the same room cannot overlap.
- **R3.** A blocked room cannot accept a new booking.
- **R4.** A successful booking produces a confirmation.

## Reference set

| ID | Story | Rules |
| --- | --- | --- |
| US-01 | As a student, I want to book a free study room for a time slot, so that I have a place to work, and I get a confirmation when the booking succeeds. | R1, R2, R3, R4 |
| US-02 | As a student, I want to see which rooms are free at a given time, so that I can choose one before booking. | — |
| US-03 | As a student, I want to cancel one of my own bookings, so that the room is released for others. | R2 |
| US-04 | As an administrator, I want to block a room, so that no new bookings can be made for it. | R3 |
| US-05 | As an administrator, I want to unblock a room, so that students can book it again. | R3 |
| US-06 | As an administrator, I want to review how rooms are used, so that I can plan capacity. | — |

## Assumptions declared for this lab

- **A1:** Touching bookings are allowed. A booking ending at 12:00 and another starting at 12:00 do not overlap.
- **A2:** Blocking a room does not cancel or modify existing bookings; it prevents new bookings.

**Out of scope:** payments, equipment in rooms, recurring bookings, waiting lists, notifications other than the booking confirmation, and user registration.
