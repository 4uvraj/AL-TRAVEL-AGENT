const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export async function planTrip(payload, onStatus = () => {}) {
  const res = await fetch(`${API_BASE}/plan-trip`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  
  if (!res.ok) throw new Error(`Server error: ${res.status}`);
  
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    
    const lines = buffer.split('\n\n');
    buffer = lines.pop() || ''; 
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6));
          if (data.type === 'progress') {
            onStatus(data.message);
          } else if (data.type === 'complete') {
            return data.result;
          } else if (data.type === 'error') {
            throw new Error(data.message);
          }
        } catch (e) {
          console.error(e);
        }
      }
    }
  }
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
