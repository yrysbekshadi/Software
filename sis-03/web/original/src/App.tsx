import { useMemo, useState, type FormEvent } from 'react';
import { Building2, Clock } from 'lucide-react';
import ToggleSwitch from '@/components/ToggleSwitch';
import {
  CURRENT_TIME_MINUTES,
  MAX_DURATION_MINUTES,
  ROOM_NAME,
  checkAvailability,
  formatMinutes,
  getBookings,
  parseTimeInput,
  type AvailabilityResult,
} from '@/lib/availability';

interface SubmittedTimes {
  start: number | null;
  end: number | null;
}

const resultStyles: Record<AvailabilityResult['status'], string> = {
  available: 'border-emerald-300 bg-emerald-50 text-emerald-900',
  unavailable: 'border-rose-300 bg-rose-50 text-rose-900',
  invalid: 'border-amber-300 bg-amber-50 text-amber-900',
};

const inputClass =
  'mt-2 block min-h-12 w-full rounded-lg border border-slate-300 bg-white px-3 text-base text-slate-900 shadow-sm focus:border-sky-600 focus:outline-none focus:ring-2 focus:ring-sky-600/30';

function App() {
  const [startInput, setStartInput] = useState('');
  const [endInput, setEndInput] = useState('');
  const [submitted, setSubmitted] = useState<SubmittedTimes | null>(null);
  const [simulateBlocked, setSimulateBlocked] = useState(false);
  const [includeSecondBooking, setIncludeSecondBooking] = useState(false);

  const bookings = useMemo(() => getBookings(includeSecondBooking), [includeSecondBooking]);

  const result = submitted
    ? checkAvailability({
        start: submitted.start,
        end: submitted.end,
        roomBlocked: simulateBlocked,
        bookings,
      })
    : null;

  const handleCheck = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitted({
      start: parseTimeInput(startInput),
      end: parseTimeInput(endInput),
    });
  };

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <div className="mx-auto w-full max-w-xl px-4 py-8 sm:py-12">
        <header className="flex items-center gap-3">
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-sky-800 text-white">
            <Building2 className="h-5 w-5" aria-hidden="true" />
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-sky-800">Smart Campus</p>
            <h1 className="text-xl font-semibold leading-tight text-slate-900 sm:text-2xl">
              Room Availability Checker
            </h1>
          </div>
        </header>

        <main className="mt-8 space-y-6">
          <section className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200 sm:p-6">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm text-slate-500">Selected room</p>
                <p className="text-lg font-semibold text-slate-900">{ROOM_NAME}</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-slate-500">Current time</p>
                <p className="flex items-center justify-end gap-1.5 text-lg font-semibold text-slate-900">
                  <Clock className="h-4 w-4 text-sky-800" aria-hidden="true" />
                  {formatMinutes(CURRENT_TIME_MINUTES)}
                </p>
              </div>
            </div>

            <div className="mt-5 border-t border-slate-200 pt-4">
              <p className="text-sm font-medium text-slate-700">Existing bookings</p>
              <ul className="mt-2 space-y-2">
                {bookings.map((booking) => (
                  <li
                    key={`${booking.start}-${booking.end}`}
                    className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 text-sm"
                  >
                    <span className="text-slate-700">{booking.label}</span>
                    <span className="font-medium tabular-nums text-slate-900">
                      {formatMinutes(booking.start)} to {formatMinutes(booking.end)}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </section>

          <section className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200 sm:p-6">
            <h2 className="text-base font-semibold text-slate-900">Check a time window</h2>
            <p className="mt-1 text-sm text-slate-500">
              Choose a start and end time. Requests must start after {formatMinutes(CURRENT_TIME_MINUTES)} and last no
              more than {MAX_DURATION_MINUTES} minutes.
            </p>

            <form onSubmit={handleCheck} noValidate className="mt-5 space-y-5">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label htmlFor="start-time" className="block text-sm font-medium text-slate-700">
                    Start time
                  </label>
                  <input
                    id="start-time"
                    type="time"
                    step={60}
                    value={startInput}
                    onChange={(event) => setStartInput(event.target.value)}
                    className={inputClass}
                  />
                </div>
                <div>
                  <label htmlFor="end-time" className="block text-sm font-medium text-slate-700">
                    End time
                  </label>
                  <input
                    id="end-time"
                    type="time"
                    step={60}
                    value={endInput}
                    onChange={(event) => setEndInput(event.target.value)}
                    className={inputClass}
                  />
                </div>
              </div>

              <p className="text-xs leading-relaxed text-slate-500">
                Note: the time picker cannot enter 24:00 (end of day), so that end point cannot be tested through these
                inputs.
              </p>

              <button
                type="submit"
                className="min-h-12 w-full cursor-pointer rounded-lg bg-sky-800 px-4 py-3 text-base font-semibold text-white shadow-sm transition-colors duration-200 hover:bg-sky-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-600 focus-visible:ring-offset-2 active:bg-sky-950"
              >
                Check availability
              </button>
            </form>

            <div aria-live="polite" className="mt-5">
              {result ? (
                <div
                  role="status"
                  className={`rounded-xl border p-4 transition-colors duration-200 sm:p-5 ${resultStyles[result.status]}`}
                >
                  <p className="text-2xl font-bold leading-tight">{result.title}</p>
                  <p className="mt-2 text-sm leading-relaxed">{result.reason}</p>
                </div>
              ) : (
                <div className="rounded-xl border border-dashed border-slate-300 p-4 text-sm text-slate-500">
                  The result will appear here after you check a time window.
                </div>
              )}
            </div>
          </section>

          <section className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200 sm:p-6">
            <h2 className="text-base font-semibold text-slate-900">Test setup</h2>
            <p className="mt-1 text-sm text-slate-500">
              These switches only reproduce test cases. They do not create or change real bookings.
            </p>
            <div className="mt-2 divide-y divide-slate-200">
              <ToggleSwitch
                id="simulate-blocked"
                label="Simulate room blocked"
                description="Every request returns Unavailable while this is on."
                checked={simulateBlocked}
                onChange={setSimulateBlocked}
              />
              <ToggleSwitch
                id="include-second-booking"
                label="Include second demo booking"
                description="Adds a booking from 11:40 to 12:40 to the list and to the checks."
                checked={includeSecondBooking}
                onChange={setIncludeSecondBooking}
              />
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}

export default App;
