import { useState } from "react";
import "./App.css";
import Markdown from "./Markdown";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  // ---------------------------------------------------------
  // Redis session
  // ---------------------------------------------------------

  const [sessionId, setSessionId] = useState(null);

  // ---------------------------------------------------------
  // Send message
  // ---------------------------------------------------------

  const sendMessage = async () => {
    const userMessage = input.trim();

    if (!userMessage || loading) {
      return;
    }

    // Add user's message to the UI immediately
    setMessages((previousMessages) => [
      ...previousMessages,
      {
        role: "user",
        content: userMessage,
      },
    ]);

    setInput("");
    setLoading(true);

    try {
      // -----------------------------------------------------
      // Build API request
      // -----------------------------------------------------

      const requestBody = {
        message: userMessage,
      };

      // If a Redis session already exists,
      // send it back to the backend.
      if (sessionId) {
        requestBody.session_id = sessionId;
      }

      // -----------------------------------------------------
      // Call AURA backend
      // -----------------------------------------------------

      const response = await fetch(
        `${API_URL}/chat`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify(requestBody),
        }
      );

      // -----------------------------------------------------
      // Handle HTTP errors
      // -----------------------------------------------------

      if (!response.ok) {
        let errorMessage = "Something went wrong.";

        try {
          const errorData = await response.json();

          if (errorData?.detail) {
            errorMessage = errorData.detail;
          }
        } catch {
          // Response was not valid JSON.
        }

        throw new Error(errorMessage);
      }

      // -----------------------------------------------------
      // Parse response
      // -----------------------------------------------------

      const data = await response.json();

      // -----------------------------------------------------
      // Save Redis session ID
      // -----------------------------------------------------

      if (data?.session_id) {
        setSessionId(data.session_id);
      }

      // -----------------------------------------------------
      // Add AURA response
      // -----------------------------------------------------

      setMessages((previousMessages) => [
        ...previousMessages,
        {
          role: "assistant",
          content:
            data?.response ||
            "AURA returned an empty response.",
        },
      ]);
    } catch (error) {
      console.error(
        "AURA request failed:",
        error
      );

      // -----------------------------------------------------
      // Show error inside chat
      // -----------------------------------------------------

      setMessages((previousMessages) => [
        ...previousMessages,
        {
          role: "assistant",
          content:
            error?.message ||
            "Unable to connect to AURA.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // ---------------------------------------------------------
  // Keyboard handling
  // ---------------------------------------------------------

  const handleKeyDown = (event) => {
    // Enter sends message.
    // Shift + Enter creates a new line.
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      sendMessage();
    }
  };

  // ---------------------------------------------------------
  // Clear local conversation
  // ---------------------------------------------------------

  const clearConversation = () => {
    setMessages([]);
    setSessionId(null);
    setInput("");
  };

  // ---------------------------------------------------------
  // Suggestion helper
  // ---------------------------------------------------------

  const useSuggestion = (question) => {
    setInput(question);
  };

  // ---------------------------------------------------------
  // UI
  // ---------------------------------------------------------

  return (
    <div className="app">

      {/* =====================================================
          HEADER
          ===================================================== */}

      <header className="header">

        <div>
          <h1>AURA</h1>

          <p>
            Autonomous Business Intelligence Agent
          </p>
        </div>

        <div className="header-actions">

          {sessionId && (
            <span className="session-status">
              ● Memory Active
            </span>
          )}

          <button
            className="clear-button"
            onClick={clearConversation}
            disabled={loading}
          >
            Clear
          </button>

        </div>

      </header>

      {/* =====================================================
          CHAT AREA
          ===================================================== */}

      <main className="chat-container">

        {/* ---------------------------------------------------
            Welcome screen
            --------------------------------------------------- */}

        {messages.length === 0 ? (

          <div className="welcome">

            <h2>
              Welcome to AURA
            </h2>

            <p>
              Ask questions about your business data,
              research, analytics, or other supported tasks.
            </p>

            <div className="suggestions">

              <button
                onClick={() =>
                  useSuggestion(
                    "What is the total revenue?"
                  )
                }
              >
                Total revenue
              </button>

              <button
                onClick={() =>
                  useSuggestion(
                    "Which region has the highest revenue?"
                  )
                }
              >
                Highest revenue region
              </button>

              <button
                onClick={() =>
                  useSuggestion(
                    "What is the total profit?"
                  )
                }
              >
                Total profit
              </button>

            </div>

          </div>

        ) : (

          /* -------------------------------------------------
             Messages
             ------------------------------------------------- */

          <div className="messages">

            {messages.map(
              (message, index) => (

                <div
                  key={`${message.role}-${index}`}
                  className={`message ${
                    message.role === "user"
                      ? "user-message"
                      : "assistant-message"
                  }`}
                >

                  <div className="message-role">

                    {message.role === "user"
                      ? "You"
                      : "AURA"}

                  </div>

                  <div className="message-content">

                    {message.role === "assistant" ? (

                      <Markdown>
                        {message.content}
                      </Markdown>

                    ) : (

                      message.content

                    )}

                  </div>

                </div>

              )
            )}

            {/* ------------------------------------------------
                Loading indicator
                ------------------------------------------------ */}

            {loading && (

              <div className="message assistant-message">

                <div className="message-role">
                  AURA
                </div>

                <div className="message-content loading">
                  Thinking...
                </div>

              </div>

            )}

          </div>

        )}

      </main>

      {/* =====================================================
          INPUT AREA
          ===================================================== */}

      <footer className="input-area">

        <div className="input-wrapper">

          <textarea
            value={input}
            onChange={(event) =>
              setInput(event.target.value)
            }
            onKeyDown={handleKeyDown}
            placeholder="Ask AURA anything..."
            rows={1}
            disabled={loading}
          />

          <button
            onClick={sendMessage}
            disabled={
              !input.trim() ||
              loading
            }
          >
            {loading ? "..." : "Send"}
          </button>

        </div>

        <div className="footer-info">

          AURA • AI-powered business intelligence

          {sessionId && (
            <span className="memory-indicator">
              {" "}• Redis Memory
            </span>
          )}

        </div>

      </footer>

    </div>
  );
}

export default App;