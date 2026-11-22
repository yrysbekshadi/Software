type FilterPanelProps = {
  attendees: string;
  onAttendeesChange: (value: string) => void;
  options: string[];
  selected: string[];
  onToggle: (item: string) => void;
};

export default function FilterPanel({ attendees, onAttendeesChange, options, selected, onToggle }: FilterPanelProps) {
  return (
    <section className="panel" aria-labelledby="filter-title">
      <h2 id="filter-title">Find a room</h2>
      <div className="row">
        <label>
          Attendees
          <input type="number" min="1" step="1" value={attendees} onChange={e => onAttendeesChange(e.target.value)} />
        </label>
        <fieldset>
          <legend>Required equipment (the room needs all of it)</legend>
          {options.map(item => (
            <label key={item} className="inline">
              <input type="checkbox" checked={selected.includes(item)} onChange={() => onToggle(item)} /> {item}
            </label>
          ))}
        </fieldset>
      </div>
    </section>
  );
}
