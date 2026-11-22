import { useState } from 'react';
import { checkRoom } from './booking';
import type { BookingWindow } from './booking';
import CheckForm from './components/CheckForm';
import FilterPanel from './components/FilterPanel';
import ResultBanner from './components/ResultBanner';
import RoomList from './components/RoomList';
import { filterRooms } from './filter';
import { EQUIPMENT_OPTIONS, ROOMS } from './rooms';

// App owns presentation state only. Catalog data and decision rules live in their own modules.
export default function App() {
  const [attendees, setAttendees] = useState('1');
  const [equipment, setEquipment] = useState<string[]>([]);
  const [roomId, setRoomId] = useState(ROOMS[0]?.id ?? '');
  const [request, setRequest] = useState<BookingWindow | null>(null);

  const criteria = { attendees: Math.max(1, Number(attendees) || 1), equipment };
  const rooms = filterRooms(ROOMS, criteria);
  // Derive the selected room from the current filtered list. Never retain a stale room object.
  const room = rooms.find(item => item.id === roomId) ?? null;
  // Recalculate for the selected room on every render: this is the F5 refresh behavior.
  const available = room && request ? checkRoom(ROOMS, room.id, request) : null;

  function toggleEquipment(item: string) {
    setEquipment(current =>
      current.includes(item) ? current.filter(value => value !== item) : [...current, item],
    );
    setRequest(null);
  }

  function changeAttendees(value: string) {
    setAttendees(value);
    setRequest(null);
  }

  return (
    <main className="page">
      <header className="page-header">
        <p className="eyebrow">SMART CAMPUS · ROOM FINDER</p>
        <h1>Room availability checker</h1>
        <p className="intro">Find a room that fits your group, then check its time slots.</p>
      </header>

      <FilterPanel
        attendees={attendees}
        onAttendeesChange={changeAttendees}
        options={EQUIPMENT_OPTIONS}
        selected={equipment}
        onToggle={toggleEquipment}
      />

      <RoomList
        rooms={rooms}
        total={ROOMS.length}
        criteria={criteria}
        selectedId={room ? room.id : null}
        onSelect={id => { setRoomId(id); setRequest(null); }}
      />

      <CheckForm roomName={room ? room.name : null} onCheck={setRequest} />

      {room && request && available !== null && (
        <ResultBanner room={room} request={request} available={available} />
      )}
    </main>
  );
}
