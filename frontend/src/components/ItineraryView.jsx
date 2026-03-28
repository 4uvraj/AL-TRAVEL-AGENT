const TYPE_ICONS = {
  attraction: '🏛️',
  museum: '🖼️',
  hotel: '🏨',
  restaurant: '🍽️',
  park: '🌿',
  beach: '🏖️',
  shopping: '🛍️',
  default: '📍',
};

function getIcon(type = '') {
  return TYPE_ICONS[type.toLowerCase()] || TYPE_ICONS.default;
}

function CountryBanner({ info }) {
  if (!info || !info.name) return null;
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: '14px',
      padding: '14px 18px',
      borderRadius: 'var(--radius-md)',
      background: 'var(--color-surface)',
      border: '1px solid var(--color-border)',
      flexWrap: 'wrap',
    }}>
      {info.flag_url && (
        <img src={info.flag_url} alt={info.name + ' flag'}
          style={{ height: '28px', borderRadius: '4px', boxShadow: '0 2px 8px rgba(0,0,0,0.4)' }} />
      )}
      <div>
        <div style={{ fontWeight: 700, fontSize: '1rem' }}>
          {info.flag_emoji} {info.name}
        </div>
        <div style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)', marginTop: '2px', display: 'flex', gap: '14px', flexWrap: 'wrap' }}>
          {info.capital && <span>🏠 {info.capital}</span>}
          {info.currency_symbol && <span>{info.currency_symbol} {info.currency_name} ({info.currency_code})</span>}
          {info.region && <span>🌍 {info.region}</span>}
          {info.languages?.length > 0 && <span>🗣️ {info.languages.join(', ')}</span>}
        </div>
      </div>
    </div>
  );
}

function BudgetCard({ label, value, colorClass }) {
  return (
    <div className="budget-card">
      <div className="budget-card-label">{label}</div>
      <div className={`budget-card-value ${colorClass}`}>
        ₹{parseFloat(value || 0).toLocaleString()}
      </div>
    </div>
  );
}

function ActivityItem({ activity }) {
  const icon = getIcon(activity.type);
  return (
    <div className="activity-item">
      <div className={`activity-icon${activity.type === 'hotel' ? ' hotel' : activity.type === 'restaurant' ? ' restaurant' : ''}`}>
        {icon}
      </div>
      <div className="activity-info">
        <h4>{activity.name}</h4>
        <p>{activity.description}</p>
        {activity.rating && (
          <span style={{ fontSize: '0.72rem', color: '#fcd34d', marginTop: '2px', display: 'block' }}>
            ⭐ {activity.rating} · {activity.duration_hours}h visit
          </span>
        )}
      </div>
      <div className="activity-cost">
        {activity.cost > 0 ? `₹${activity.cost}` : 'Free'}
      </div>
    </div>
  );
}

function DayCard({ day, index }) {
  const w = day.weather;
  return (
    <div className="day-card" style={{ animationDelay: `${index * 0.08}s` }}>
      <div className="day-card-header">
        <div className="day-number">
          <span>Day</span>
          <strong>{day.day}</strong>
        </div>
        <div className="day-card-info">
          <h3>{day.theme || `Day ${day.day} in ${day.location}`}</h3>
          <span>📍 {day.location} · {day.date}</span>
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' }}>
          <span className="badge badge-primary">₹{day.day_total?.toLocaleString()}</span>
          {w && (
            <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
              {w.weather_emoji} {w.temp_max}°C / {w.temp_min}°C
              <span className="badge badge-cyan" style={{ padding: '2px 7px', fontSize: '0.65rem' }}>{w.weather_desc}</span>
            </span>
          )}
        </div>
      </div>

      <div className="day-card-body">
        {(day.activities || []).map((act, i) => (
          <ActivityItem key={i} activity={act} />
        ))}
        {(!day.activities || day.activities.length === 0) && (
          <div style={{ padding: '16px', color: 'var(--color-text-muted)', fontSize: '0.85rem', textAlign: 'center' }}>
            Free exploration day 🌍
          </div>
        )}
      </div>

      <div className="day-footer">
        <div className="hotel-info">
          <span>🏨</span> {day.hotel || 'Hotel TBD'}
        </div>
        <div className="day-total">
          🍽️ ₹{day.meals_cost?.toLocaleString()} · 🚌 ₹{day.transport_cost?.toLocaleString()} · Total: <em>₹{day.day_total?.toLocaleString()}</em>
        </div>
      </div>
    </div>
  );
}

function RouteCard({ route }) {
  if (!route || !route.sequence || route.sequence.length === 0) return null;
  return (
    <div className="route-card">
      <h3>🗺️ Optimized Route <span className="badge badge-green" style={{ marginLeft: '8px' }}>Dijkstra TSP</span></h3>
      <div className="route-stops">
        {route.sequence.map((stop, i) => (
          <div key={i} className="route-stop-pill">
            <span className="route-stop-name">{stop}</span>
            {i < route.sequence.length - 1 && <span className="route-arrow">→</span>}
          </div>
        ))}
      </div>
      <div className="route-meta">
        <div className="route-stat">📏 Total Distance: <strong>{route.total_distance_km} km</strong></div>
        <div className="route-stat">⏱️ Est. Travel Time: <strong>{route.estimated_travel_hours} hrs</strong></div>
        <div className="route-stat">📍 Stops: <strong>{route.sequence.length}</strong></div>
      </div>
    </div>
  );
}

export default function ItineraryView({ itinerary }) {
  if (!itinerary) return null;
  const budget  = itinerary.budget || {};
  const country = itinerary.country_info || null;

  return (
    <div className="itinerary-view">
      {/* Header */}
      <div className="itinerary-header animate-fadeInUp">
        <div className="itinerary-title">
          <h1>✈️ {itinerary.destination}</h1>
          <p>{itinerary.summary}</p>
          <div className="itinerary-meta">
            <span className="badge badge-primary">🗓️ {itinerary.total_days} Days</span>
            <span className="badge badge-cyan">🎯 {itinerary.travel_style}</span>
            {(itinerary.recommendations || []).slice(0, 2).map((r, i) => (
              <span key={i} className="badge badge-amber">📍 {r}</span>
            ))}
          </div>
        </div>
      </div>

      {/* Country Info Banner */}
      <CountryBanner info={country} destination={itinerary.destination} />
      {/* Budget Summary */}
      <div className="budget-summary animate-fadeInUp">
        <BudgetCard label="🏨 Accommodation" value={budget.accommodation_total} colorClass="primary" />
        <BudgetCard label="🍽️ Food" value={budget.food_total} colorClass="cyan" />
        <BudgetCard label="🚌 Transport" value={budget.transport_total} colorClass="amber" />
        <BudgetCard label="🎡 Activities" value={budget.activities_total} colorClass="green" />
        <BudgetCard label="💰 Grand Total" value={budget.grand_total} colorClass="grand" />
      </div>

      {/* Route Card */}
      <RouteCard route={itinerary.optimized_route} />

      {/* Day Cards */}
      {(itinerary.days || []).map((day, i) => (
        <DayCard key={day.day} day={day} index={i} />
      ))}

      {/* Tips */}
      {(itinerary.tips || []).length > 0 && (
        <div className="tips-section animate-fadeInUp">
          <h3>💡 Travel Tips</h3>
          {itinerary.tips.map((tip, i) => (
            <div key={i} className="tip-item">{tip}</div>
          ))}
        </div>
      )}
    </div>
  );
}
