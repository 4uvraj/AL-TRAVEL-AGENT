const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export async function planTrip(payload) {
  const res = await fetch(`${API_BASE}/plan-trip`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Server error: ${res.status}`);
  const data = await res.json();
  return data.data;
}

export async function sendChat(message, history = []) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history }),
  });
  if (!res.ok) throw new Error(`Server error: ${res.status}`);
  const data = await res.json();
  return data.reply;
}

export async function optimizeRoute(locations, startLocation = null) {
  const res = await fetch(`${API_BASE}/optimize-route`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ locations, start_location: startLocation }),
  });
  if (!res.ok) throw new Error(`Server error: ${res.status}`);
  const data = await res.json();
  return data.data;
}
