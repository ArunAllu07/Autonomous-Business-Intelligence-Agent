import { useState } from "react";
import "./App.css";
import Markdown from "./Markdown";

const API_URL = "http://127.0.0.1:8000";

function Icon({ children, size = 18 }) {
  return (
    <span
      className="icon"
      style={{ width: size, height: size }}
    >
      {children}
    </span>
  );
}

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);

  const sendMessage = async (messageOverride = null) => {
    const message = (messageOverride ?? input).trim();

    if (!message || loading) return;

    setInput("");

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: message,
      },
    ]);

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message,
          ...(sessionId ? { session_id: sessionId } : {}),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Something went wrong.");
      }

      if (data.session_id) {
        setSessionId(data.session_id);
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.response,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "I couldn't connect to the AURA backend. Please make sure the API server is running.",
          error: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setSessionId(null);
  };

  const suggestions = [
    {
      title: "Business Overview",
      text: "Give me a concise summary of the overall sales performance.",
    },
    {
      title: "Revenue Analysis",
      text: "What is the total revenue and which region generated the most revenue?",
    },
    {
      title: "Profit Analysis",
      text: "Which region is the most profitable and why?",
    },
  ];

  return (
    <div className="app-shell">

      {/* SIDEBAR */}
      <aside className="sidebar">

        <div className="brand">
          <div className="brand-mark">
            A
          </div>

          <div>
            <div className="brand-name">AURA</div>
            <div className="brand-subtitle">
              Intelligence Platform
            </div>
          </div>
        </div>

        <button className="new-chat-btn" onClick={clearChat}>
          <span>+</span>
          New conversation
        </button>

        <div className="sidebar-section">
          <div className="section-label">
            WORKSPACE
          </div>

          <div className="nav-item active">
            <Icon>◉</Icon>
            Business Intelligence
          </div>

          <div className="nav-item">
            <Icon>⌕</Icon>
            Research
          </div>

          <div className="nav-item">
            <Icon>▥</Icon>
            Data Analytics
          </div>
        </div>

        <div className="sidebar-section">
          <div className="section-label">
            AGENTS
          </div>

          <div className="agent-status">
            <span className="status-dot"></span>
            Orchestrator
          </div>

          <div className="agent-status">
            <span className="status-dot"></span>
            Research Agent
          </div>

          <div className="agent-status">
            <span className="status-dot"></span>
            SQL Agent
          </div>

          <div className="agent-status">
            <span className="status-dot"></span>
            Data Analyst
          </div>
        </div>

        <div className="sidebar-bottom">

          <div className="memory-card">
            <div className="memory-icon">✦</div>

            <div>
              <div className="memory-title">
                Memory Active
              </div>

              <div className="memory-text">
                Conversation context enabled
              </div>
            </div>

            <span className="memory-dot"></span>
          </div>

          <div className="sidebar-footer">
            <span>v1.0</span>
            <span>•</span>
            <span>Local Environment</span>
          </div>

        </div>

      </aside>

      {/* MAIN */}
      <main className="main-panel">

        {/* TOP BAR */}
        <header className="topbar">

          <div>
            <div className="page-title">
              Business Intelligence
            </div>

            <div className="page-subtitle">
              Ask AURA to analyze, research and reason over your data.
            </div>
          </div>

          <div className="system-status">
            <span className="online-dot"></span>
            System Online
          </div>

        </header>

        {/* CHAT AREA */}
        <section className="chat-area">

          {messages.length === 0 ? (

            <div className="welcome-container">

              <div className="welcome-badge">
                <span>✦</span>
                Autonomous Business Intelligence
              </div>

              <h1>
                Intelligence that
                <span> works for you.</span>
              </h1>

              <p className="welcome-description">
                Ask questions about business performance, research,
                analytics, databases and more. AURA chooses the
                right agent and tools for the task.
              </p>

              <div className="suggestion-grid">

                {suggestions.map((item, index) => (
                  <button
                    key={index}
                    className="suggestion-card"
                    onClick={() => sendMessage(item.text)}
                  >
                    <div className="suggestion-title">
                      {item.title}
                    </div>

                    <div className="suggestion-text">
                      {item.text}
                    </div>

                    <div className="suggestion-arrow">
                      →
                    </div>
                  </button>
                ))}

              </div>

            </div>

          ) : (

            <div className="messages-container">

              {messages.map((message, index) => (

                <div
                  key={index}
                  className={`message-row ${message.role}`}
                >

                  <div className="message-avatar">
                    {message.role === "user" ? "You" : "A"}
                  </div>

                  <div className="message-content">

                    <div className="message-name">
                      {message.role === "user"
                        ? "You"
                        : "AURA"}
                    </div>

                    <div
                      className={`message-bubble ${
                        message.error ? "error-message" : ""
                      }`}
                    >
                      {message.role === "assistant" ? (
                        <Markdown>
                          {message.content}
                        </Markdown>
                      ) : (
                        message.content
                      )}
                    </div>

                  </div>

                </div>

              ))}

              {loading && (
                <div className="message-row assistant">

                  <div className="message-avatar">
                    A
                  </div>

                  <div className="message-content">

                    <div className="message-name">
                      AURA
                    </div>

                    <div className="message-bubble thinking">
                      <span></span>
                      <span></span>
                      <span></span>
                      <label>Thinking...</label>
                    </div>

                  </div>

                </div>
              )}

            </div>

          )}

        </section>

        {/* INPUT */}
        <div className="input-section">

          <div className="input-wrapper">

            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (
                  e.key === "Enter" &&
                  !e.shiftKey
                ) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
              placeholder="Ask AURA anything..."
              rows="1"
              disabled={loading}
            />

            <button
              className="send-btn"
              onClick={() => sendMessage()}
              disabled={!input.trim() || loading}
            >
              ↑
            </button>

          </div>

          <div className="input-footer">
            <span>
              AURA can make mistakes. Verify important information.
            </span>

            <span>
              Enter to send · Shift + Enter for new line
            </span>
          </div>

        </div>

      </main>

    </div>
  );
}

export default App;