import unittest
from booking import can_book


class BookingTests(unittest.TestCase):
    # The six required cases from the handout.
    def test_touching_at_existing_end_is_allowed(self):
        self.assertIs(can_book(660, 720, 540, False, [(600, 660)]), True)

    def test_overlap_is_rejected(self):
        self.assertIs(can_book(630, 690, 540, False, [(600, 660)]), False)

    def test_blocked_room_is_rejected(self):
        self.assertIs(can_book(660, 720, 540, True, [(600, 660)]), False)

    def test_exactly_120_minutes_is_allowed(self):
        self.assertIs(can_book(720, 840, 540, False, [(600, 660)]), True)

    def test_121_minutes_is_rejected(self):
        self.assertIs(can_book(720, 841, 540, False, [(600, 660)]), False)

    def test_starting_at_now_is_rejected(self):
        self.assertIs(can_book(540, 570, 540, False, [(600, 660)]), False)

    # AC1: interval order and day boundaries.
    def test_zero_length_is_rejected(self):
        self.assertIs(can_book(700, 700, 540, False, []), False)

    def test_reversed_interval_is_rejected(self):
        self.assertIs(can_book(720, 700, 540, False, []), False)

    def test_end_at_1440_is_allowed(self):
        self.assertIs(can_book(1380, 1440, 540, False, []), True)

    def test_end_after_1440_is_rejected(self):
        self.assertIs(can_book(1380, 1441, 540, False, []), False)

    def test_negative_start_is_rejected(self):
        self.assertIs(can_book(-1, 30, 0, False, []), False)

    def test_start_one_minute_after_now_is_allowed(self):
        self.assertIs(can_book(541, 571, 540, False, []), True)

    # AC4: each overlap relationship and all existing bookings.
    def test_overlap_from_left_is_rejected(self):
        self.assertIs(can_book(570, 630, 540, False, [(600, 660)]), False)

    def test_booking_inside_existing_is_rejected(self):
        self.assertIs(can_book(615, 645, 540, False, [(600, 660)]), False)

    def test_booking_containing_existing_is_rejected(self):
        self.assertIs(can_book(570, 690, 540, False, [(600, 660)]), False)

    def test_identical_interval_is_rejected(self):
        self.assertIs(can_book(600, 660, 540, False, [(600, 660)]), False)

    def test_touching_at_existing_start_is_allowed(self):
        self.assertIs(can_book(570, 600, 540, False, [(600, 660)]), True)

    def test_second_booking_is_checked(self):
        self.assertIs(can_book(720, 780, 540, False, [(600, 660), (700, 760)]), False)

    def test_empty_existing_list_allows_valid_request(self):
        self.assertIs(can_book(600, 660, 540, False, []), True)

    def test_unsorted_existing_list_is_not_modified(self):
        existing = [(900, 960), (600, 660), (700, 760)]
        before = existing.copy()
        result = can_book(780, 840, 540, False, existing)
        self.assertIs(result, True)
        self.assertEqual(existing, before)

    def test_rejected_request_does_not_modify_existing(self):
        existing = [(900, 960), (600, 660), (700, 760)]
        before = existing.copy()
        result = can_book(610, 650, 540, False, existing)
        self.assertIs(result, False)
        self.assertEqual(existing, before)

    def test_result_is_boolean(self):
        result = can_book(660, 720, 540, False, [(600, 660)])
        self.assertIs(type(result), bool)

    # A final one-minute slot is valid when the current time is 1438.
    def test_one_minute_booking_at_day_end_is_allowed(self):
        self.assertIs(can_book(1439, 1440, 1438, False, []), True)

    # The contract leaves non-integer times open; Python does not explicitly reject them.
    def test_non_integer_time_is_outside_contract_and_not_validated(self):
        self.assertIs(can_book(600.5, 660, 540, False, []), True)


if __name__ == "__main__":
    unittest.main()
