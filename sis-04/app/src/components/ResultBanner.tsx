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
    <p className={`result ${available ? 'available' : 'unavailable'}`} role="status">
      <strong>{available ? 'Available' : 'Unavailable'}</strong>{' '}
      <span>
        {room.name}, {formatRange(request)}
        {room.blocked && ' (this room is blocked)'}
      </span>
    </p>
  );
}
