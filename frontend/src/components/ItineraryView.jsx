import MapView from './MapView';
import BudgetCharts from './BudgetCharts';
import PdfExport from './PdfExport';

const TYPE_ICONS = {
  attraction: '🏛️', museum: '🖼️', hotel: '🏨', restaurant: '🍽️',
  park: '🌿', beach: '🏖️', shopping: '🛍️', temple: '🛕', market: '🏪', default: '📍',
};

function getIcon(type = '') {
  return TYPE_ICONS[type.toLowerCase()] || TYPE_ICONS.default;
}

function StarRating({ stars = 3 }) {
  return (
    <span style={{ color: '#fcd34d', fontSize: '0.8rem', letterSpacing: '1px' }}>
      {'★'.repeat(Math.min(stars, 5))}{'☆'.repeat(Math.max(0, 5 - stars))}
    </span>
  );
}

function ImageTooltip({ text, image }) {
  if (!image) return <span>{text}</span>;
  return (
    <div className="image-tooltip-container">
      <span className="tooltip-trigger">{text}</span>
      <div className="tooltip-content">
        <img src={image} alt={text} />
      </div>
    </div>
  );
}

function HeroBanner({ destination, summary, image, totalDays, travelStyle, onExport }) {
  return (
    <div className="hero-banner animate-fadeInUp" style={{
      position: 'relative',
      borderRadius: 'var(--radius-lg)',
      overflow: 'hidden',
      minHeight: '240px',
      display: 'flex',
      alignItems: 'flex-end',
    }}>
      <div style={{
        position: 'absolute', inset: 0,
        backgroundImage: image ? `url(${image})` : 'linear-gradient(135deg, #1e1b4b, #0f172a)',
        backgroundSize: 'cover', backgroundPosition: 'center',
        filter: 'brightness(0.45)',
      }} />
      <div style={{
        position: 'absolute', inset: 0,
        background: 'linear-gradient(to top, rgba(8,12,20,0.95) 0%, rgba(8,12,20,0.3) 60%, transparent 100%)',
      }} />
      <div style={{ position: 'relative', padding: '28px 28px 24px', width: '100%' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h1 style={{
              fontSize: '2.2rem', color: '#fff', marginBottom: '6px',
              textShadow: '0 2px 20px rgba(0,0,0,0.5)',
            }}>✈️ {destination}</h1>
            <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.92rem', maxWidth: '600px' }}>{summary}</p>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '12px' }}>
              <span className="badge badge-primary">🗓️ {totalDays} Days</span>
              <span className="badge badge-cyan">🎯 {travelStyle}</span>
            </div>
          </div>
          {onExport}
        </div>
      </div>
    </div>
  );
}

function CountryBanner({ info }) {
  if (!info || !info.name) return null;
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: '14px',
      padding: '14px 18px', borderRadius: 'var(--radius-md)',
      background: 'var(--color-surface)', border: '1px solid var(--color-border)',
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

function ActivityItem({ activity, image }) {
  const icon = getIcon(activity.type);
  return (
    <div className="activity-item" style={{ position: 'relative', overflow: 'hidden' }}>
      {image && (
        <div style={{
          width: '64px', height: '64px', borderRadius: '10px', overflow: 'hidden',
          flexShrink: 0, border: '1px solid var(--color-border)',
        }}>
          <img src={image} alt={activity.name}
            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            onError={e => { e.target.style.display = 'none'; }}
          />
        </div>
      )}
      {!image && (
        <div className={`activity-icon${activity.type === 'hotel' ? ' hotel' : activity.type === 'restaurant' ? ' restaurant' : ''}`}>
          {icon}
        </div>
      )}
      <div className="activity-info">
        <h4><ImageTooltip text={activity.name} image={image} /></h4>
        <p>{activity.description}</p>
        {activity.rating && (
          <span style={{ fontSize: '0.72rem', color: '#fcd34d', marginTop: '2px', display: 'block' }}>
            ⭐ {activity.rating} · {activity.duration_hours}h visit
          </span>
        )}
      </div>
      <div className="activity-cost">
        {activity.cost > 0 ? `₹${activity.cost.toLocaleString()}` : 'Free'}
      </div>
    </div>
  );
}

function DayCard({ day, index, placeImages }) {
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
          <ActivityItem key={i} activity={act} image={placeImages?.[act.name]} />
        ))}
        {(!day.activities || day.activities.length === 0) && (
          <div style={{ padding: '16px', color: 'var(--color-text-muted)', fontSize: '0.85rem', textAlign: 'center' }}>
            Free exploration day 🌍
          </div>
        )}
      </div>

      <div className="day-footer">
        <div className="hotel-info">
          <span>🏨</span>
          <div>
            <ImageTooltip text={day.hotel || 'Hotel TBD'} image={placeImages?.[day.hotel]} />
            {day.hotel_stars > 0 && (
              <span style={{ marginLeft: '8px' }}><StarRating stars={day.hotel_stars} /></span>
            )}
            {day.hotel_price > 0 && (
              <span style={{ fontSize: '0.75rem', color: 'var(--color-accent)', marginLeft: '8px' }}>
                ₹{day.hotel_price.toLocaleString()}/night
              </span>
            )}
          </div>
        </div>
        <div className="day-total">
          {day.transport_mode && (
            <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginRight: '10px' }}>
              🚗 {day.transport_mode}
            </span>
          )}
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
      <h3>🗺️ Optimized Route <span className="badge badge-green" style={{ marginLeft: '8px' }}>Nearest-Neighbor TSP</span></h3>
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
  const budget = itinerary.budget || {};
  const country = itinerary.country_info || null;
  const placeImages = itinerary.place_images || {};

  return (
    <div className="itinerary-view">
      {/* Hero Banner with Destination Image */}
      <HeroBanner
        destination={itinerary.destination}
        summary={itinerary.summary}
        image={itinerary.destination_image}
        totalDays={itinerary.total_days}
        travelStyle={itinerary.travel_style}
        onExport={<PdfExport destination={itinerary.destination} />}
      />

      {/* Country Info Banner */}
      <CountryBanner info={country} />

      {/* Budget Summary */}
      <div className="budget-summary animate-fadeInUp">
        <BudgetCard label="🏨 Accommodation" value={budget.accommodation_total} colorClass="primary" />
        <BudgetCard label="🍽️ Food" value={budget.food_total} colorClass="cyan" />
        <BudgetCard label="🚌 Transport" value={budget.transport_total} colorClass="amber" />
        <BudgetCard label="🎡 Activities" value={budget.activities_total} colorClass="green" />
        <BudgetCard label="💰 Grand Total" value={budget.grand_total} colorClass="grand" />
      </div>

      {/* Budget Charts */}
      <BudgetCharts budget={budget} days={itinerary.days} />

      {/* Route Card */}
      <RouteCard route={itinerary.optimized_route} />

      {/* Interactive Map */}
      <MapView route={itinerary.optimized_route} />

      {/* Day Cards */}
      {(itinerary.days || []).map((day, i) => (
        <DayCard key={day.day} day={day} index={i} placeImages={placeImages} />
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
