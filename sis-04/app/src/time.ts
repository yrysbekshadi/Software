import type { Interval } from './rooms';

// 'HH:MM' from a time input to minutes after midnight; null when it is empty or malformed.
export function parseTime(value: string): number | null {
  const match = /^(\d{1,2}):(\d{2})$/.exec(value);
  if (!match) return null;
  return Number(match[1]) * 60 + Number(match[2]);
}

// 600 -> '10:00', 1440 -> '24:00'
export function formatTime(minutes: number): string {
  const hours = String(Math.floor(minutes / 60)).padStart(2, '0');
  const rest = String(minutes % 60).padStart(2, '0');
  return `${hours}:${rest}`;
}

export function formatRange({ start, end }: Interval): string {
  return `${formatTime(start)}–${formatTime(end)}`;
}
