import { useState, useRef, useEffect } from 'react';
import { sendChat } from '../services/api';

const SUGGESTIONS = [
  "What are the best restaurants in Paris?",
  "Is Tokyo expensive to visit?",
  "Tips for traveling on a budget?",
  "Best time to visit Japan?",
];

export default function ChatView() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "✈️ Hello! I'm your AI Travel Copilot. Ask me anything about travel — destinations, budgets, tips, visas, or local culture. I'm here to help plan your perfect trip!",
    },
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const sendMessage = async (text) => {
    const content = (text || input).trim();
    if (!content) return;

    const history = messages.map(m => ({ role: m.role, content: m.content }));
    setMessages(prev => [...prev, { role: 'user', content }]);
    setInput('');
    setIsTyping(true);

    try {
      const reply = await sendChat(content, history);
      setMessages(prev => [...prev, { role: 'assistant', content: reply }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '⚠️ Sorry, I couldn\'t connect to the backend. Please make sure the FastAPI server is running on port 8000.',
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-view">
      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`chat-message ${msg.role === 'user' ? 'user' : 'assistant'}`}>
            <div className={`chat-avatar ${msg.role === 'user' ? 'user' : 'ai'}`}>
              {msg.role === 'user' ? '👤' : '✈️'}
            </div>
            <div className="chat-bubble" style={{ whiteSpace: 'pre-wrap' }}>
              {msg.content}
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="chat-message assistant">
            <div className="chat-avatar ai">✈️</div>
            <div className="chat-bubble">
              <span className="typing-dot" />
              <span className="typing-dot" />
              <span className="typing-dot" />
            </div>
          </div>
        )}

        {messages.length === 1 && (
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '8px' }}>
            {SUGGESTIONS.map((s, i) => (
              <button
                key={i}
                className="btn btn-secondary"
                style={{ fontSize: '0.78rem', padding: '7px 14px' }}
                onClick={() => sendMessage(s)}
              >
                {s}
              </button>
            ))}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="chat-input-area">
        <div className="chat-input-wrapper">
          <textarea
            ref={textareaRef}
            id="chat-input"
            className="chat-textarea"
            placeholder="Ask me anything about travel… (Enter to send)"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
          />
        </div>
        <button
          id="chat-send-btn"
          className="chat-send-btn"
          onClick={() => sendMessage()}
          disabled={isTyping || !input.trim()}
        >
          {isTyping ? <div className="spinner" style={{ width: 18, height: 18 }} /> : '➤'}
        </button>
      </div>
    </div>
  );
}
