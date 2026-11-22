import { useState } from 'react';
import { DAY_END, isValidRange, MAX_DURATION } from '../booking';
import type { BookingWindow } from '../booking';
import { parseTime } from '../time';

type CheckFormProps = {
  roomName: string | null;
  onCheck: (request: BookingWindow | null) => void;
};

export default function CheckForm({ roomName, onCheck }: CheckFormProps) {
  const [now, setNow] = useState('09:00');
  const [start, setStart] = useState('10:30');
  const [end, setEnd] = useState('11:30');
  const [endOfDay, setEndOfDay] = useState(false);
  const [error, setError] = useState('');

  function invalidate() {
    setError('');
    onCheck(null);
  }

  function check() {
    const s = parseTime(start);
    const e = endOfDay ? DAY_END : parseTime(end);
    const n = parseTime(now);
    if (s === null || e === null || n === null) {
      setError('Fill in the current time, start and end.');
      onCheck(null);
      return;
    }
    if (!isValidRange(s, e)) {
      setError('The end time must be after the start time.');
      onCheck(null);
      return;
    }
    setError('');
    onCheck({ start: s, end: e, now: n });
  }

  return (
    <section className="panel" aria-labelledby="check-title">
      <p className="eyebrow">03 · TIME SLOT</p>
      <h2 id="check-title">Check availability <span className="count">{roomName ?? 'No room selected'}</span></h2>
      <div className="row time-fields">
        <label>Current time<input type="time" value={now} onChange={event => { setNow(event.target.value); invalidate(); }} /></label>
        <label>Start<input type="time" value={start} onChange={event => { setStart(event.target.value); invalidate(); }} /></label>
        <label>End<input type="time" value={end} disabled={endOfDay} onChange={event => { setEnd(event.target.value); invalidate(); }} /></label>
        <label className="inline end-of-day">
          <input type="checkbox" checked={endOfDay} onChange={event => { setEndOfDay(event.target.checked); invalidate(); }} />
          Ends at 24:00
        </label>
      </div>
      <p className="hint">
        A booking must start after the current time, last at most {MAX_DURATION} minutes and not overlap an existing booking. Touching another booking is allowed.
      </p>
      <button type="button" onClick={check} disabled={roomName === null}>Check availability</button>
      {!roomName && <p className="hint">Choose a matching room above to check its bookings.</p>}
      {error && <p className="error" role="alert">{error}</p>}
    </section>
  );
}
