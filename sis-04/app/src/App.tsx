import { useState } from 'react';
import { checkRoom } from './booking';
import type { BookingWindow } from './booking';
import CheckForm from './components/CheckForm';
import FilterPanel from './components/FilterPanel';
import ResultBanner from './components/ResultBanner';
import RoomList from './components/RoomList';
import { filterRooms } from './filter';
import { EQUIPMENT_OPTIONS, ROOMS } from './rooms';

// The page only keeps state and wires the parts together. The rules live in booking.ts and
// filter.ts, the data in rooms.ts, the markup in components/.
export default function App() {
  const [attendees, setAttendees] = useState('1');
  const [equipment, setEquipment] = useState<string[]>([]);
  const [roomId, setRoomId] = useState(ROOMS.length ? ROOMS[0].id : '');
  const [request, setRequest] = useState<BookingWindow | null>(null);

  const criteria = { attendees: Number(attendees) || 0, equipment };
  const rooms = filterRooms(ROOMS, criteria);
  const room = rooms.find(r => r.id === roomId) ?? null;
  const available = room && request ? checkRoom(ROOMS, room.id, request) : null;

  function toggleEquipment(item: string) {
    setEquipment(current => (current.includes(item) ? current.filter(i => i !== item) : [...current, item]));
  }

  return (
    <main className="page">
      <h1>Smart Campus Room Availability</h1>
      <FilterPanel
        attendees={attendees}
        onAttendeesChange={setAttendees}
        options={EQUIPMENT_OPTIONS}
        selected={equipment}
        onToggle={toggleEquipment}
      />
      <RoomList
        rooms={rooms}
        total={ROOMS.length}
        criteria={criteria}
        selectedId={room ? room.id : null}
        onSelect={setRoomId}
      />
      <CheckForm roomName={room ? room.name : null} onCheck={setRequest} />
      {room && request && available !== null && <ResultBanner room={room} request={request} available={available} />}
    </main>
  );
}
