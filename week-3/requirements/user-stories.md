# User stories — Smart Campus study room booking

### US-01
**Story:** As a Student, I want to view available study rooms and time slots, so that I can choose a suitable room for my study session.
**Priority:** High
**Assumption:** Availability reflects the current set of bookings and room blocks.

### US-02
**Story:** As a Student, I want to book an available room for a time slot, so that I can reserve a place to study without conflicting with another booking.
**Priority:** High
**Assumption:** A booking may be made only for a future time slot and may last no longer than two hours.

### US-03
**Story:** As a Student, I want to cancel a booking I made, so that I can release the room when I no longer need it.
**Priority:** Medium
**Assumption:** A Student can cancel only a reservation that the Student made.

### US-04
**Story:** As a Student, I want to receive a confirmation after booking or cancelling a room, so that I know the requested action was recorded.
**Priority:** Medium
**Assumption:** The system confirms a successful booking or cancellation as specified by UC-06.

### US-05
**Story:** As an Administrator, I want to block or unblock a study room, so that I can take a room out of service or return it to service.
**Priority:** High
**Assumption:** A blocked room is not eligible for a new booking.

### US-06
**Story:** As an Administrator, I want to review room usage over a period, so that I can see how the rooms are being used.
**Priority:** Medium
**Assumption:** Usage is represented by the room booking activity covered by the supplied scenario.
