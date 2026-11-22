import type { FilterCriteria } from '../filter';
import type { Room } from '../rooms';
import { formatRange } from '../time';

type RoomListProps = {
  rooms: Room[];
  total: number;
  criteria: FilterCriteria;
  selectedId: string | null;
  onSelect: (id: string) => void;
};

function summarize({ attendees, equipment }: FilterCriteria): string {
  const people = `${attendees} attendee${attendees === 1 ? '' : 's'}`;
  return equipment.length ? `${people} with ${equipment.join(' + ')}` : people;
}

export default function RoomList({ rooms, total, criteria, selectedId, onSelect }: RoomListProps) {
  return (
    <section className="panel" aria-labelledby="rooms-title">
      <h2 id="rooms-title">
        Rooms <span className="count">{rooms.length} of {total} match</span>
      </h2>
      {rooms.length === 0 ? (
        <p className="empty" role="status">
          No rooms match {summarize(criteria)}. Lower the number of attendees or remove an equipment item.
        </p>
      ) : (
        <ul className="rooms">
          {rooms.map(room => (
            <li key={room.id}>
              <label className={`room${room.id === selectedId ? ' selected' : ''}${room.blocked ? ' blocked' : ''}`}>
                <input type="radio" name="room" value={room.id} checked={room.id === selectedId} onChange={() => onSelect(room.id)} />
                <span className="room-body">
                  <span className="room-name">
                    {room.name}
                    {room.blocked && <span className="badge">Blocked</span>}
                  </span>
                  <span className="room-meta">{room.capacity} seats, {room.equipment.join(', ')}</span>
                  <span className="room-meta">
                    {room.bookings.length ? `Booked ${room.bookings.map(formatRange).join(', ')}` : 'No bookings'}
                  </span>
                </span>
              </label>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
