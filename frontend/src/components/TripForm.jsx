import { useState } from 'react';
import { planTrip } from '../services/api';

const BUDGET_OPTIONS = [
  { label: '🎒 Budget', value: 'budget' },
  { label: '🏨 Mid-Range', value: 'mid-range' },
  { label: '💎 Luxury', value: 'luxury' },
];

export default function TripForm({ onResult, setLoading, setStatusMsg }) {
  const [form, setForm] = useState({
    destination: '',
    days: 3,
    budget_range: 'mid-range',
    preferences: '',
    start_date: '',
  });

  const update = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.destination.trim()) return;
    setLoading(true);
    setStatusMsg(''); // Reset the message explicitly
    try {
      const result = await planTrip(form, (msg) => setStatusMsg(msg));
      onResult(result);
    } catch (err) {
      console.error(err);
      alert('Failed to plan trip. Make sure the backend is running and your OpenAI key is set.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div className="sidebar-title">
        <span>✈️</span> Plan Your Trip
      </div>

      <div className="form-group">
        <label htmlFor="destination">Destination</label>
        <input
          id="destination"
          className="input"
          placeholder="e.g. Paris, Tokyo, New York…"
          value={form.destination}
          onChange={e => update('destination', e.target.value)}
          required
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="days">Days</label>
          <input
            id="days"
            type="number"
            className="input"
            min={1} max={30}
            value={form.days}
            onChange={e => update('days', parseInt(e.target.value) || 1)}
          />
        </div>
        <div className="form-group">
          <label htmlFor="start_date">Start Date</label>
          <input
            id="start_date"
            type="date"
            className="input"
            value={form.start_date}
            onChange={e => update('start_date', e.target.value)}
          />
        </div>
      </div>

      <div className="form-group">
        <label>Budget Style</label>
        <div className="budget-chips">
          {BUDGET_OPTIONS.map(opt => (
            <button
              key={opt.value}
              type="button"
              className={`budget-chip${form.budget_range === opt.value ? ' selected' : ''}`}
              onClick={() => update('budget_range', opt.value)}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="preferences">Preferences</label>
        <textarea
          id="preferences"
          className="input"
          style={{ minHeight: '80px', resize: 'vertical' }}
          placeholder="e.g. museums, street food, hiking, art galleries…"
          value={form.preferences}
          onChange={e => update('preferences', e.target.value)}
        />
      </div>

      <div className="divider" />

      <button id="plan-trip-btn" type="submit" className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '13px' }}>
        <span>🗺️</span> Generate Itinerary
      </button>
    </form>
  );
}
