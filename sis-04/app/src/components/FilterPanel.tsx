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
      <div className="section-heading">
        <div>
          <p className="eyebrow">01 · YOUR REQUIREMENTS</p>
          <h2 id="filter-title">Find a room</h2>
        </div>
      </div>
      <div className="row">
        <label className="attendees-field">
          Attendees
          <input
            type="number"
            min="1"
            step="1"
            value={attendees}
            onChange={event => onAttendeesChange(event.target.value)}
          />
        </label>
        <fieldset>
          <legend>Required equipment <span>(room needs all selected items)</span></legend>
          <div className="equipment-options">
            {options.map(item => (
              <label key={item} className="inline">
                <input type="checkbox" checked={selected.includes(item)} onChange={() => onToggle(item)} />
                {item}
              </label>
            ))}
          </div>
        </fieldset>
      </div>
    </section>
  );
}
