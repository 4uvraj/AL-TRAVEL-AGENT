import { useState } from 'react';
import './index.css';
import './App.css';
import TripForm from './components/TripForm';
import ItineraryView from './components/ItineraryView';
import ChatView from './components/ChatView';

const LOADING_STEPS = [
  '🧠 Planner Agent: Designing your logical day-by-day outline...',
  '🔍 RAG Agent: Fetching verified hotels, restaurants & attractions...',
  '💰 Budget Agent: Calculating realistic city-specific costs...',
  '🗺️ Route Agent: Optimizing route sequence using GPS logic...',
  '🌦️ Weather Agent: Syncing live forecast & country metadata...',
  '✨ Explainer Agent: Assembling your final travel portfolio...'
];

function LoadingState({ statusMsg }) {
  let currentIndex = 0;
  if (statusMsg) {
    const foundIndex = LOADING_STEPS.findIndex(s => s === statusMsg);
    if (foundIndex !== -1) {
      currentIndex = foundIndex + 1;
    }
  }

  return (
    <div className="loading-state">
      <div className="loading-pulse">🌍</div>
      <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>
        AI servers processing your trip in real-time...
      </p>
      
      <div className="progress-bar-container" style={{ width: '100%', height: '6px', background: '#333', borderRadius: '3px', margin: '20px 0', overflow: 'hidden' }}>
        <div style={{ width: `${Math.min((currentIndex / LOADING_STEPS.length) * 100, 100)}%`, height: '100%', background: 'var(--color-primary)', transition: 'width 0.5s ease-out' }} />
      </div>

      <div className="loading-steps">
        {LOADING_STEPS.map((label, i) => (
          <div key={i} className={`loading-step ${i < currentIndex ? 'done' : i === currentIndex ? 'active' : ''}`} style={{ opacity: i > currentIndex ? 0.4 : 1 }}>
            <div className="step-dot" />
            <span style={{ fontSize: '0.9rem' }}>{label}</span>
            {i < currentIndex && <span style={{ marginLeft: 'auto', color: 'var(--color-success)' }}>✓</span>}
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
  const [statusMsg, setStatusMsg] = useState('');
  const [itinerary, setItinerary] = useState(null);

  const handleResult = (result) => {
    setItinerary(result);
    setActiveTab('plan'); // ensure plan tab is visible after generation
  };

  const renderMainContent = () => {
    if (activeTab === 'chat') return <ChatView />;
    if (loading) return <LoadingState statusMsg={statusMsg} />;
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
            <TripForm onResult={handleResult} setLoading={setLoading} setStatusMsg={setStatusMsg} />
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
