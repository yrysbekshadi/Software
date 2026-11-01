export const ROOM_NAME = 'Room A-204';
export const CURRENT_TIME_MINUTES = 540;
export const MAX_DURATION_MINUTES = 120;
export const DAY_END_MINUTES = 1440;

export interface Booking {
  readonly label: string;
  readonly start: number;
  readonly end: number;
}

const BASE_BOOKINGS: readonly Booking[] = [
  { label: 'Existing booking', start: 600, end: 660 },
];

const SECOND_DEMO_BOOKING: Booking = { label: 'Second demo booking', start: 700, end: 760 };

export function getBookings(includeSecondDemoBooking: boolean): Booking[] {
  return includeSecondDemoBooking
    ? [...BASE_BOOKINGS, SECOND_DEMO_BOOKING]
    : [...BASE_BOOKINGS];
}

export function parseTimeInput(value: string): number | null {
  const match = /^(\d{2}):(\d{2})$/.exec(value);
  if (!match) return null;
  const hours = Number(match[1]);
  const minutes = Number(match[2]);
  if (hours > 23 || minutes > 59) return null;
  return hours * 60 + minutes;
}

export function formatMinutes(totalMinutes: number): string {
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
}

export type AvailabilityResult =
  | { status: 'available'; title: string; reason: string }
  | { status: 'unavailable'; title: string; reason: string }
  | { status: 'invalid'; title: string; reason: string };

interface CheckInput {
  start: number | null;
  end: number | null;
  roomBlocked: boolean;
  bookings: readonly Booking[];
}

export function checkAvailability({
  start,
  end,
  roomBlocked,
  bookings,
}: CheckInput): AvailabilityResult {
  const invalid = (reason: string): AvailabilityResult => ({
    status: 'invalid',
    title: 'Check your times',
    reason,
  });

  if (start === null || end === null) {
    return invalid('Enter both a start time and an end time.');
  }
  if (start < 0 || end > DAY_END_MINUTES || !Number.isInteger(start) || !Number.isInteger(end)) {
    return invalid('Times must be whole minutes within the day, from 00:00 to 24:00.');
  }
  if (start >= end) {
    return invalid('The end time must be later than the start time.');
  }
  if (start <= CURRENT_TIME_MINUTES) {
    return invalid(
      `The start time must be later than the current time of ${formatMinutes(CURRENT_TIME_MINUTES)}.`,
    );
  }

  const duration = end - start;
  if (duration > MAX_DURATION_MINUTES) {
    return invalid(
      `Requests can be at most ${MAX_DURATION_MINUTES} minutes long. This one is ${duration} minutes.`,
    );
  }

  if (roomBlocked) {
    return {
      status: 'unavailable',
      title: 'Unavailable',
      reason: `${ROOM_NAME} is blocked, so it cannot be used at this time.`,
    };
  }

  const overlapping = bookings.find((booking) => start < booking.end && booking.start < end);
  if (overlapping) {
    return {
      status: 'unavailable',
      title: 'Unavailable',
      reason: `This overlaps the existing booking from ${formatMinutes(overlapping.start)} to ${formatMinutes(overlapping.end)}.`,
    };
  }

  return {
    status: 'available',
    title: 'Available',
    reason: `${ROOM_NAME} is free from ${formatMinutes(start)} to ${formatMinutes(end)}.`,
  };
}
