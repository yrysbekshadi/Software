# Acceptance criteria — three selected stories

## Assumptions

- **Overlap:** a booking that ends exactly when another begins is **allowed** under R3, because the two bookings do not share any time.
- **Duration:** a booking of exactly two hours is **allowed** under R2, because R2 says a booking lasts at most two hours.
- **Cancellation ownership:** only the Student who made a reservation can cancel that reservation, because UC-03 releases a reservation the Student made.

## US-02 — Book room

### AC-01
- **Given** a Student selects a free room and a future time slot lasting exactly two hours
- **When** the Student books the room
- **Then** the booking is created for that time slot

### AC-02
- **Given** a Student selects a free room but the requested booking starts in the past
- **When** the Student books the room
- **Then** the booking is rejected and no reservation is created

### AC-03
- **Given** the selected room already has a booking that overlaps the requested time
- **When** the Student books the room
- **Then** the booking is rejected and the existing booking remains unchanged

### AC-04
- **Given** the selected room is blocked
- **When** the Student books the room
- **Then** the booking is rejected because a blocked room cannot be booked

## US-03 — Cancel booking

### AC-05
- **Given** a Student has a reservation for a study room
- **When** the Student cancels that reservation
- **Then** the reservation is released

### AC-06
- **Given** a Student has no reservation that the Student made for the selected booking
- **When** the Student attempts to cancel that booking
- **Then** no reservation is released

### AC-07
- **Given** a Student has a reservation and the cancellation is accepted
- **When** the cancellation is completed
- **Then** the system sends a confirmation of the cancellation

## US-05 — Block or unblock room

### AC-08
- **Given** a study room is available
- **When** the Administrator blocks the room
- **Then** the room is no longer available for booking

### AC-09
- **Given** a study room is blocked
- **When** a Student attempts to book that room
- **Then** the booking is rejected because a blocked room cannot be booked

### AC-10
- **Given** a study room is blocked
- **When** the Administrator unblocks the room
- **Then** the room is returned to the available set for booking
