import type { Room } from './rooms';

export type FilterCriteria = { attendees: number; equipment: string[] };

// F1: capacity must meet or exceed attendee count.
// F2: every requested item must be present. Blocked status is checked by booking.ts.
export function filterRooms(rooms: Room[], { attendees, equipment }: FilterCriteria): Room[] {
  return rooms.filter(room =>
    room.capacity >= attendees && equipment.every(item => room.equipment.includes(item)),
  );
}
