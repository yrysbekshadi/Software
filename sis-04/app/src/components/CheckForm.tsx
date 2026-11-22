import { useState } from 'react';
import { DAY_END, MAX_DURATION, isValidRange } from '../booking';
import type { BookingWindow } from '../booking';
import { parseTime } from '../time';

type CheckFormProps = {
  roomName: string | null;
  onCheck: (request: BookingWindow | null) => void;
};

export default function CheckForm({ roomName, onCheck }: CheckFormProps) {
  const [now, setNow] = useState('09:00');
  const [start, setStart] = useState('11:00');
  const [end, setEnd] = useState('12:00');
  const [endOfDay, setEndOfDay] = useState(false);
  const [error, setError] = useState('');

  function check() {
    const s = parseTime(start);
    const e = endOfDay ? DAY_END : parseTime(end);
    const n = parseTime(now);
    if (s === null || e === null || n === null) {
      setError('Fill in the current time, the start and the end.');
      onCheck(null);
      return;
    }
    setError(isValidRange(s, e) ? '' : 'The end time must be after the start time.');
    onCheck({ start: s, end: e, now: n });
  }

  return (
    <section className="panel" aria-labelledby="check-title">
      <h2 id="check-title">
        Check availability
        {roomName && <span className="count">{roomName}</span>}
      </h2>
      <div className="row">
        <label>Current time<input type="time" value={now} onChange={e => setNow(e.target.value)} /></label>
        <label>Start<input type="time" value={start} onChange={e => setStart(e.target.value)} /></label>
        <label>End<input type="time" value={end} disabled={endOfDay} onChange={e => setEnd(e.target.value)} /></label>
        <label className="inline">
          <input type="checkbox" checked={endOfDay} onChange={e => setEndOfDay(e.target.checked)} /> Ends at 24:00
        </label>
      </div>
      <p className="hint">
        A booking must start after the current time, last at most {MAX_DURATION} minutes and not overlap an existing booking.
        Touching another booking is fine.
      </p>
      <button type="button" onClick={check} disabled={roomName === null}>Check availability</button>
      {roomName === null && <p className="hint">Pick a room from the list to check it.</p>}
      {error && <p className="error" role="alert">{error}</p>}
    </section>
  );
}
