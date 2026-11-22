import type { BookingWindow } from '../booking';
import type { Room } from '../rooms';
import { formatRange } from '../time';

type ResultBannerProps = {
  room: Room;
  request: BookingWindow;
  available: boolean;
};

export default function ResultBanner({ room, request, available }: ResultBannerProps) {
  return (
    <section className={`result ${available ? 'available' : 'unavailable'}`} role="status" aria-live="polite">
      <span className="result-kicker">AVAILABILITY RESULT</span>
      <p><strong>{available ? 'Available' : 'Unavailable'}</strong></p>
      <span>{room.name} · {formatRange(request)}{room.blocked && ' · This room is blocked'}</span>
    </section>
  );
}
