import type { Interval, Room } from './rooms';

export const MAX_DURATION = 120;
export const DAY_END = 1440;

export type BookingWindow = { start: number; end: number; now: number };
export type BookingRequest = BookingWindow & { blocked: boolean; bookings: readonly Interval[] };

export function isValidRange(start: number, end: number): boolean {
  return 0 <= start && start < end && end <= DAY_END;
}

// AC1-AC5: preserve Week 08 decisions; this function reads but never mutates bookings.
export function canBook({ start, end, now, blocked, bookings }: BookingRequest): boolean {
  if (!isValidRange(start, end)) return false;
  if (start <= now) return false;
  if (end - start > MAX_DURATION) return false;
  if (blocked) return false;
  for (const booking of bookings) {
    if (start < booking.end && end > booking.start) return false;
  }
  return true;
}

// F3/F5: check the selected room's own blocked flag and bookings. Unknown id is unavailable.
export function checkRoom(rooms: Room[], roomId: string, { start, end, now }: BookingWindow): boolean {
  const room = rooms.find(item => item.id === roomId);
  if (!room) return false;
  return canBook({ start, end, now, blocked: room.blocked, bookings: room.bookings });
}
