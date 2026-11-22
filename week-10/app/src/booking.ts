export type BookingInterval = { start: number; end: number };

export type CanBookInput = {
  start: number;
  end: number;
  now: number;
  blocked: boolean;
  bookings: BookingInterval[];
};

// Returns true when the candidate interval is Available, otherwise false.
// Times are minutes after midnight on the same day.
export function canBook({ start, end, now, blocked, bookings }: CanBookInput): boolean {
  let ok = true;
  if (!(0 <= start && start < end && end <= 1440)) ok = false;
  else if (!(start > now)) ok = false;
  else if (end - start > 120) ok = false;
  else if (blocked) ok = false;
  else {
    for (const booking of bookings) {
      if (start < booking.end && end > booking.start) {
        ok = false;
        break;
      }
    }
  }
  return ok;
}
