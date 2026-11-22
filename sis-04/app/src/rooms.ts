// Fictional room catalog. Times are minutes after midnight.
export type Interval = { start: number; end: number };

export type Room = {
  id: string;
  name: string;
  capacity: number;
  equipment: string[];
  blocked: boolean;
  bookings: Interval[];
};

export const ROOMS: Room[] = [
  { id: 'a101', name: 'Room A-101', capacity: 12, equipment: ['projector', 'whiteboard'], blocked: false, bookings: [{ start: 600, end: 660 }] },
  { id: 'b204', name: 'Room B-204', capacity: 30, equipment: ['projector', 'whiteboard', 'video call'], blocked: false, bookings: [{ start: 780, end: 870 }] },
  { id: 'c310', name: 'Lab C-310', capacity: 8, equipment: ['whiteboard', 'computers'], blocked: false, bookings: [{ start: 540, end: 600 }, { start: 900, end: 960 }] },
  { id: 'd015', name: 'Hall D-015', capacity: 60, equipment: ['projector', 'video call'], blocked: false, bookings: [{ start: 540, end: 630 }, { start: 840, end: 960 }] },
  { id: 'e120', name: 'Room E-120', capacity: 20, equipment: ['projector', 'whiteboard', 'computers'], blocked: true, bookings: [] },
];

export const EQUIPMENT_OPTIONS: string[] = Array.from(new Set(ROOMS.flatMap(room => room.equipment))).sort();
