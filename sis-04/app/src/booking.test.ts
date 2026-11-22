import { expect, test } from 'vitest';
import { canBook, checkRoom } from './booking';
import type { Room } from './rooms';

const NOW = 480; // 08:00
const noBookings: { start: number; end: number }[] = [];
const booked = [{ start: 600, end: 660 }]; // 10:00-11:00

function deepFreeze<T>(value: T): T {
  if (typeof value === 'object' && value !== null) {
    Object.values(value).forEach(item => deepFreeze(item));
    Object.freeze(value);
  }
  return value;
}

test('T01 AC1: start equal to end is rejected', () => {
  expect(canBook({ start: 720, end: 720, now: NOW, blocked: false, bookings: noBookings })).toBe(false);
});
test('T02 AC1: start after end is rejected', () => {
  expect(canBook({ start: 780, end: 720, now: NOW, blocked: false, bookings: noBookings })).toBe(false);
});
test('T03 AC1: past request is rejected and a future request is accepted', () => {
  expect(canBook({ start: 420, end: 480, now: NOW, blocked: false, bookings: noBookings })).toBe(false);
  expect(canBook({ start: 540, end: 600, now: NOW, blocked: false, bookings: noBookings })).toBe(true);
});
test('T04 AC2 B1: exactly 120 minutes is available', () => {
  expect(canBook({ start: 720, end: 840, now: NOW, blocked: false, bookings: noBookings })).toBe(true);
});
test('T05 AC2 B2: 121 minutes is rejected', () => {
  expect(canBook({ start: 720, end: 841, now: NOW, blocked: false, bookings: noBookings })).toBe(false);
});
test('T06 AC3: a blocked room is rejected even when the interval is free', () => {
  expect(canBook({ start: 720, end: 780, now: NOW, blocked: true, bookings: noBookings })).toBe(false);
  expect(canBook({ start: 720, end: 780, now: NOW, blocked: false, bookings: noBookings })).toBe(true);
});
test('T07 AC4 B3: a request ending when a booking starts is available', () => {
  expect(canBook({ start: 540, end: 600, now: NOW, blocked: false, bookings: booked })).toBe(true);
});
test('T08 AC4 B3: a request starting when a booking ends is available', () => {
  expect(canBook({ start: 660, end: 720, now: NOW, blocked: false, bookings: booked })).toBe(true);
});
test('T09 AC4 B4: a request overlapping the start of a booking is rejected', () => {
  expect(canBook({ start: 570, end: 630, now: NOW, blocked: false, bookings: booked })).toBe(false);
});
test('T10 AC4 B4: a request inside an existing booking is rejected', () => {
  expect(canBook({ start: 615, end: 645, now: NOW, blocked: false, bookings: booked })).toBe(false);
});
test('T11 AC4 B4: a request covering an existing booking is rejected', () => {
  expect(canBook({ start: 570, end: 690, now: NOW, blocked: false, bookings: booked })).toBe(false);
});
test('T12 AC5: canBook leaves the booking data unchanged', () => {
  const input = deepFreeze([{ start: 600, end: 660 }, { start: 780, end: 840 }]);
  const before = JSON.stringify(input);
  expect(canBook({ start: 540, end: 600, now: NOW, blocked: false, bookings: input })).toBe(true);
  expect(canBook({ start: 570, end: 630, now: NOW, blocked: false, bookings: input })).toBe(false);
  expect(JSON.stringify(input)).toBe(before);
});

const rooms: Room[] = [
  { id: 'x1', name: 'Room X-1', capacity: 10, equipment: ['projector'], blocked: false, bookings: [{ start: 600, end: 660 }] },
  { id: 'y2', name: 'Room Y-2', capacity: 10, equipment: ['projector'], blocked: false, bookings: [{ start: 720, end: 780 }] },
  { id: 'z3', name: 'Room Z-3', capacity: 10, equipment: ['projector'], blocked: true, bookings: [] },
];

test('T13 F3: checkRoom never reports a blocked room as available', () => {
  const slot = { start: 840, end: 900, now: NOW };
  expect(checkRoom(rooms, 'z3', slot)).toBe(false);
  expect(checkRoom(rooms, 'x1', slot)).toBe(true);
});
test('T14 F5: the same times use the selected room bookings', () => {
  const slot = { start: 600, end: 660, now: NOW };
  expect(checkRoom(rooms, 'x1', slot)).toBe(false);
  expect(checkRoom(rooms, 'y2', slot)).toBe(true);
});
test('T15 F5: changing the selected room changes the result in the opposite direction', () => {
  const slot = { start: 720, end: 780, now: NOW };
  expect(checkRoom(rooms, 'x1', slot)).toBe(true);
  expect(checkRoom(rooms, 'y2', slot)).toBe(false);
});
test('T16 F5: an unknown room id is unavailable', () => {
  expect(checkRoom(rooms, 'unknown', { start: 840, end: 900, now: NOW })).toBe(false);
});
test('T17 AC5 F5: checkRoom leaves the room catalog unchanged', () => {
  const input = deepFreeze(JSON.parse(JSON.stringify(rooms)) as Room[]);
  const before = JSON.stringify(input);
  checkRoom(input, 'x1', { start: 600, end: 660, now: NOW });
  checkRoom(input, 'z3', { start: 840, end: 900, now: NOW });
  expect(JSON.stringify(input)).toBe(before);
});
