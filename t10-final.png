import unittest
from booking import can_book


class BookingTests(unittest.TestCase):
    def test_touching_at_existing_end_is_available(self):
        self.assertIs(can_book(660, 720, 540, False, [(600, 660)]), True)

    def test_touching_at_existing_start_is_available(self):
        self.assertIs(can_book(540, 600, 500, False, [(600, 660)]), True)

    def test_partial_overlap_is_unavailable(self):
        self.assertIs(can_book(630, 690, 540, False, [(600, 660)]), False)

    def test_blocked_room_is_unavailable(self):
        self.assertIs(can_book(660, 720, 540, True, [(600, 660)]), False)

    def test_exactly_120_minutes_is_allowed(self):
        self.assertIs(can_book(720, 840, 540, False, [(600, 660)]), True)

    def test_121_minutes_is_rejected(self):
        self.assertIs(can_book(720, 841, 540, False, [(600, 660)]), False)

    def test_start_equal_to_now_is_rejected(self):
        self.assertIs(can_book(540, 570, 540, False, [(600, 660)]), False)

    def test_start_in_the_past_is_rejected(self):
        self.assertIs(can_book(500, 530, 540, False, [(600, 660)]), False)

    def test_reversed_times_are_rejected(self):
        self.assertIs(can_book(720, 660, 540, False, [(600, 660)]), False)

    def test_zero_length_interval_is_rejected(self):
        self.assertIs(can_book(600, 600, 540, False, []), False)

    def test_negative_start_is_rejected(self):
        self.assertIs(can_book(-1, 30, 0, False, []), False)

    def test_end_after_midnight_boundary_is_rejected(self):
        self.assertIs(can_book(1380, 1441, 540, False, []), False)

    def test_ending_exactly_at_midnight_is_allowed(self):
        self.assertIs(can_book(1380, 1440, 540, False, []), True)

    def test_start_at_midnight_must_still_be_after_now(self):
        self.assertIs(can_book(0, 60, 0, False, []), False)

    def test_one_minute_after_now_is_allowed(self):
        self.assertIs(can_book(541, 601, 540, False, []), True)

    def test_second_existing_booking_is_checked(self):
        existing = [(600, 660), (700, 760)]
        self.assertIs(can_book(720, 780, 540, False, existing), False)

    def test_candidate_that_contains_existing_booking_is_rejected(self):
        self.assertIs(can_book(570, 690, 540, False, [(600, 660)]), False)

    def test_empty_existing_list_allows_valid_future_slot(self):
        self.assertIs(can_book(600, 660, 540, False, []), True)

    def test_result_is_a_real_boolean(self):
        result = can_book(660, 720, 540, False, [(600, 660)])
        self.assertIs(type(result), bool)

    def test_existing_list_is_not_mutated_after_available_check(self):
        existing = [(900, 960), (600, 660), (700, 760)]
        before = existing.copy()
        self.assertIs(can_book(780, 840, 540, False, existing), True)
        self.assertEqual(existing, before)

    def test_existing_list_is_not_mutated_after_rejected_check(self):
        existing = [(900, 960), (600, 660), (700, 760)]
        before = existing.copy()
        self.assertIs(can_book(610, 650, 540, False, existing), False)
        self.assertEqual(existing, before)

    def test_non_integer_candidate_values_are_rejected(self):
        self.assertIs(can_book(660.0, 720, 540, False, [(600, 660)]), False)


if __name__ == "__main__":
    unittest.main()
