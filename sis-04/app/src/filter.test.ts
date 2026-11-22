import { expect, test } from 'vitest';
import { filterRooms } from './filter';
import { checkRoom } from './booking';
import type { Room } from './rooms';

const catalog: Room[] = [
  { id: 'r8', name: 'Lab R-8', capacity: 8, equipment: ['whiteboard'], blocked: false, bookings: [] },
  { id: 'r12', name: 'Room R-12', capacity: 12, equipment: ['projector'], blocked: false, bookings: [] },
  { id: 'r20', name: 'Room R-20', capacity: 20, equipment: ['projector', 'whiteboard'], blocked: false, bookings: [{ start: 600, end: 660 }] },
  { id: 'r25', name: 'Room R-25', capacity: 25, equipment: ['projector', 'whiteboard'], blocked: true, bookings: [] },
  { id: 'r30', name: 'Hall R-30', capacity: 30, equipment: ['projector', 'whiteboard', 'video call'], blocked: false, bookings: [] },
];
const ids = (rooms: Room[]) => rooms.map(room => room.id);
const NOW = 480;

test('T18 F1: rooms smaller than the attendee count are excluded', () => {
  expect(ids(filterRooms(catalog, { attendees: 15, equipment: [] }))).toEqual(['r20', 'r25', 'r30']);
});
test('T19 F2: only some selected equipment is not enough', () => {
  expect(ids(filterRooms(catalog, { attendees: 1, equipment: ['projector', 'whiteboard'] }))).toEqual(['r20', 'r25', 'r30']);
});
test('T20 F2: all three selected items must be present', () => {
  expect(ids(filterRooms(catalog, { attendees: 1, equipment: ['projector', 'whiteboard', 'video call'] }))).toEqual(['r30']);
});
test('T21 F2: no equipment selected does not restrict the equipment list', () => {
  expect(ids(filterRooms(catalog, { attendees: 10, equipment: [] }))).toEqual(['r12', 'r20', 'r25', 'r30']);
});
test('T22 F4: too many attendees returns an empty list', () => {
  expect(filterRooms(catalog, { attendees: 31, equipment: [] })).toEqual([]);
});
test('T23 F4: missing equipment returns an empty list', () => {
  expect(filterRooms(catalog, { attendees: 1, equipment: ['microphone'] })).toEqual([]);
});
test('T24 B5: capacity equal to attendees is included', () => {
  expect(ids(filterRooms(catalog, { attendees: 20, equipment: [] }))).toEqual(['r20', 'r25', 'r30']);
});
test('T25 B6: capacity one below attendees is excluded', () => {
  expect(ids(filterRooms(catalog, { attendees: 21, equipment: [] }))).toEqual(['r25', 'r30']);
});
test('T26 INT: filterRooms result is checked using each returned room booking', () => {
  const listed = filterRooms(catalog, { attendees: 15, equipment: ['projector'] });
  expect(ids(listed)).toEqual(['r20', 'r25', 'r30']);
  const slot = { start: 630, end: 690, now: NOW };
  expect(listed.map(room => checkRoom(catalog, room.id, slot))).toEqual([false, false, true]);
});
test('T27 INT F3: a blocked room may be listed but is never available', () => {
  const listed = filterRooms(catalog, { attendees: 25, equipment: ['projector', 'whiteboard'] });
  expect(ids(listed)).toEqual(['r25', 'r30']);
  const slot = { start: 840, end: 900, now: NOW };
  expect(checkRoom(catalog, 'r25', slot)).toBe(false);
  expect(checkRoom(catalog, 'r30', slot)).toBe(true);
});
