import { describe, expect, test } from 'vitest';
import { canBook } from './booking';

describe('canBook — assistant-generated first suite', () => {
  test('T01 AC4: touching after an existing booking is available', () => {
    expect(canBook({ start: 660, end: 720, now: 540, blocked: false, bookings: [{ start: 600, end: 660 }] })).toBe(true);
  });

  test('T02 AC1: a request starting at the current time is unavailable', () => {
    expect(canBook({ start: 540, end: 570, now: 540, blocked: false, bookings: [{ start: 600, end: 660 }] })).toBe(false);
  });

  test('T03 AC1: a zero-duration request is unavailable', () => {
    expect(canBook({ start: 720, end: 720, now: 540, blocked: false, bookings: [{ start: 600, end: 660 }] })).toBe(false);
  });

  test('T04 AC1: a reversed request is unavailable', () => {
    expect(canBook({ start: 750, end: 720, now: 540, blocked: false, bookings: [{ start: 600, end: 660 }] })).toBe(false);
  });

  test('T05 AC1: a request ending after midnight is unavailable', () => {
    expect(canBook({ start: 1380, end: 1441, now: 540, blocked: false, bookings: [{ start: 600, end: 660 }] })).toBe(false);
  });

  // This first generated expectation is deliberately retained for review; compare it with AC2.
  test('T06 AC2: a request lasting exactly 120 minutes is available', () => {
    expect(canBook({ start: 720, end: 840, now: 540, blocked: false, bookings: [{ start: 600, end: 660 }] })).toBe(true);
  });

  test('T07 AC2: a request lasting 121 minutes is unavailable', () => {
    expect(canBook({ start: 720, end: 841, now: 540, blocked: false, bookings: [{ start: 600, end: 660 }] })).toBe(false);
  });

  test('T08 AC4: touching before an existing booking is available', () => {
    expect(canBook({ start: 570, end: 600, now: 540, blocked: false, bookings: [{ start: 600, end: 660 }] })).toBe(true);
  });

  test('T09 AC4: a partial overlap is unavailable', () => {
    expect(canBook({ start: 630, end: 690, now: 540, blocked: false, bookings: [{ start: 600, end: 660 }] })).toBe(false);
  });

  test('T10 AC4: a request containing an existing booking is unavailable', () => {
    expect(canBook({ start: 570, end: 690, now: 540, blocked: false, bookings: [{ start: 600, end: 660 }] })).toBe(false);
  });

  test('T11 AC4: a request inside an existing booking is unavailable', () => {
    expect(canBook({ start: 615, end: 645, now: 540, blocked: false, bookings: [{ start: 600, end: 660 }] })).toBe(false);
  });

  test('T12 AC4: an identical interval is unavailable', () => {
    expect(canBook({ start: 600, end: 660, now: 540, blocked: false, bookings: [{ start: 600, end: 660 }] })).toBe(false);
  });

  test('T13 AC3: a blocked room is unavailable', () => {
    expect(canBook({ start: 660, end: 720, now: 540, blocked: true, bookings: [{ start: 600, end: 660 }] })).toBe(false);
  });

  test('T14 AC4: a request is available when there are no existing bookings', () => {
    expect(canBook({ start: 630, end: 690, now: 540, blocked: false, bookings: [] })).toBe(true);
  });

  test('AC5: an available check does not change the existing bookings', () => {
    const bookings = [{ start: 600, end: 660 }];
    const before = structuredClone(bookings);
    expect(canBook({ start: 720, end: 780, now: 540, blocked: false, bookings })).toBe(true);
    expect(bookings).toEqual(before);
  });

  test('X1 AC1: a valid 120-minute request ending exactly at 24:00 is available', () => {
    expect(canBook({ start: 1320, end: 1440, now: 540, blocked: false, bookings: [{ start: 600, end: 660 }] })).toBe(true);
  });

  test('X2 AC4: a request between two touching bookings is available', () => {
    expect(canBook({ start: 660, end: 720, now: 540, blocked: false, bookings: [{ start: 600, end: 660 }, { start: 720, end: 780 }] })).toBe(true);
  });

});
