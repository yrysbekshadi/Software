export type BookingInterval = { start: number; end: number };

export type CanBookInput = {
  start: number;
  end: number;
  now: number;
  blocked: boolean;
  bookings: BookingInterval[];
};

const DAY_MINUTES = 1440;
const MAX_DURATION_MINUTES = 120;

function isValidInterval(interval: BookingInterval): boolean {
  return Number.isFinite(interval.start)
    && Number.isFinite(interval.end)
    && 0 <= interval.start
    && interval.start < interval.end
    && interval.end <= DAY_MINUTES;
}

function overlaps(candidate: BookingInterval, existing: BookingInterval): boolean {
  return candidate.start < existing.end && candidate.end > existing.start;
}

// A pure availability decision: valid inputs keep the original AC1-AC5 behaviour.
export function canBook({ start, end, now, blocked, bookings }: CanBookInput): boolean {
  const candidate = { start, end };

  if (!Number.isFinite(now) || !isValidInterval(candidate)) return false;
  if (start <= now || end - start > MAX_DURATION_MINUTES || blocked) return false;
  if (!Array.isArray(bookings) || !bookings.every(isValidInterval)) return false;

  return !bookings.some((booking) => overlaps(candidate, booking));
}
