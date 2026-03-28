import { useState } from 'react';
import './index.css';
import './App.css';
import TripForm from './components/TripForm';
import ItineraryView from './components/ItineraryView';
import ChatView from './components/ChatView';

const LOADING_STEPS = [
  { key: 'planner',   label: '🧠 Planner Agent: Building real itinerary with actual places…' },
  { key: 'rag',       label: '🔍 RAG Agent: Fetching real hotels, restaurants & attractions…' },
  { key: 'budget',    label: '💰 Budget Agent: Calculating city-specific cost breakdown…' },
  { key: 'route',     label: '🗺️ Route Agent: Optimizing sequence with real GPS coords…' },
  { key: 'weather',   label: '🌦️ Weather Agent: Fetching live forecast & country info…' },
  { key: 'explainer', label: '✨ Explainer Agent: Assembling your complete travel plan…' },
];

function LoadingState() {
  const [step, setStep] = useState(0);
  
  // Animate steps every 1.5s
  useState(() => {
    let current = 0;
    const interval = setInterval(() => {
      current++;
      if (current >= LOADING_STEPS.length) { clearInterval(interval); return; }
      setStep(current);
    }, 1800);
    return () => clearInterval(interval);
  });

  return (
    <div className="loading-state">
      <div className="loading-pulse">🌍</div>
      <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>
        AI agents working on your perfect trip…
      </p>
      <div className="loading-steps">
        {LOADING_STEPS.map((s, i) => (
          <div key={s.key} className={`loading-step ${i < step ? 'done' : i === step ? 'active' : ''}`}>
            <div className="step-dot" />
            <span>{s.label}</span>
            {i < step && <span style={{ marginLeft: 'auto', color: 'var(--color-success)' }}>✓</span>}
          </div>
        ))}
      </div>
    </div>
  );
}

function WelcomeState() {
  return (
    <div className="welcome">
      <div className="welcome-icon">🌍</div>
      <h2>Your AI Travel Copilot</h2>
      <p>
        Powered by multi-agent AI — fill in the form and let our planning agents
        build a personalized, budget-optimized itinerary with route optimization.
      </p>
      <div className="feature-pills">
        <span className="feature-pill">🧠 LangGraph Multi-Agent</span>
        <span className="feature-pill">🔍 RAG-Powered Recommendations</span>
        <span className="feature-pill">🗺️ Dijkstra Route Optimization</span>
        <span className="feature-pill">💰 Smart Budget Planner</span>
        <span className="feature-pill">💬 AI Chat Assistant</span>
      </div>
    </div>
  );
}

export default function App() {
  const [activeTab, setActiveTab] = useState('plan');
  const [loading, setLoading] = useState(false);
  const [itinerary, setItinerary] = useState(null);

  const handleResult = (result) => {
    setItinerary(result);
    setActiveTab('plan'); // ensure plan tab is visible after generation
  };

  const renderMainContent = () => {
    if (activeTab === 'chat') return <ChatView />;
    if (loading) return <LoadingState />;
    if (itinerary) return <ItineraryView itinerary={itinerary} />;
    return <WelcomeState />;
  };

  return (
    <>
      {/* Navbar */}
      <nav className="navbar">
        <a className="navbar-logo" href="/" aria-label="AI Travel Copilot Home">
          <div className="logo-icon">✈️</div>
          AI Travel Copilot
        </a>

        <div className="navbar-tabs" role="tablist">
          <button
            id="tab-plan"
            className={`navbar-tab${activeTab === 'plan' ? ' active' : ''}`}
            role="tab"
            aria-selected={activeTab === 'plan'}
            onClick={() => setActiveTab('plan')}
          >
            🗺️ Trip Planner
          </button>
          <button
            id="tab-chat"
            className={`navbar-tab${activeTab === 'chat' ? ' active' : ''}`}
            role="tab"
            aria-selected={activeTab === 'chat'}
            onClick={() => setActiveTab('chat')}
          >
            💬 AI Chat
          </button>
        </div>
      </nav>

      {/* Main Layout */}
      <div className="app-layout">
        {/* Sidebar — only shown on plan tab */}
        {activeTab === 'plan' && (
          <aside className="sidebar" aria-label="Trip Planning Form">
            <TripForm onResult={handleResult} setLoading={setLoading} />
            {itinerary && (
              <button
                id="clear-itinerary-btn"
                className="btn btn-secondary"
                style={{ width: '100%', justifyContent: 'center' }}
                onClick={() => setItinerary(null)}
              >
                🔄 Plan Another Trip
              </button>
            )}
          </aside>
        )}

        {/* Main content panel */}
        <main className="main-content" role="main">
          {renderMainContent()}
        </main>
      </div>
    </>
  );
}
