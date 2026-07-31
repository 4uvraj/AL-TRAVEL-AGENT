import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import L from 'leaflet';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// Fix Leaflet default marker icons in bundlers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const DAY_COLORS = ['#6366f1', '#06b6d4', '#f59e0b', '#10b981', '#ec4899', '#8b5cf6', '#ef4444'];

function createNumberedIcon(number, color = '#6366f1') {
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="
      background: ${color};
      color: white;
      width: 28px;
      height: 28px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 12px;
      border: 2px solid white;
      box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    ">${number}</div>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
    popupAnchor: [0, -14],
  });
}

export default function MapView({ route }) {
  if (!route || !route.coordinates || !route.sequence || route.sequence.length === 0) {
    return null;
  }

  const coords = route.coordinates;
  const sequence = route.sequence;
  
  // Build position array for polyline
  const positions = sequence
    .filter(loc => coords[loc])
    .map(loc => coords[loc]);

  if (positions.length === 0) return null;

  const center = route.center || positions[0];

  return (
    <div className="map-section animate-fadeInUp">
      <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--color-text)', marginBottom: '12px', display: 'flex', gap: '8px', alignItems: 'center' }}>
        🗺️ Route Map
        <span className="badge badge-cyan" style={{ fontSize: '0.7rem' }}>Interactive</span>
      </h3>
      <div style={{ borderRadius: '12px', overflow: 'hidden', border: '1px solid var(--color-border)' }}>
        <MapContainer
          center={center}
          zoom={12}
          style={{ height: '400px', width: '100%' }}
          scrollWheelZoom={true}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {sequence.map((loc, i) => {
            const pos = coords[loc];
            if (!pos) return null;
            const color = DAY_COLORS[i % DAY_COLORS.length];
            return (
              <Marker key={i} position={pos} icon={createNumberedIcon(i + 1, color)}>
                <Popup>
                  <strong>Stop {i + 1}</strong><br />{loc}
                </Popup>
              </Marker>
            );
          })}
          {positions.length > 1 && (
            <Polyline
              positions={positions}
              pathOptions={{
                color: '#6366f1',
                weight: 3,
                opacity: 0.8,
                dashArray: '8, 4',
              }}
            />
          )}
        </MapContainer>
      </div>
      <div style={{ fontSize: '0.72rem', color: 'var(--color-text-dim)', marginTop: '6px', textAlign: 'right' }}>
        📍 {sequence.length} stops · {route.total_distance_km} km total
      </div>
    </div>
  );
}
