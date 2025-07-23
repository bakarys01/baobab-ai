import React, { useState, useRef, useEffect } from 'react';
import { chatService } from '../../services/chatService';
import { useAuth } from '../../contexts/AuthContext';
import './ChatInterface.css';

export default function ChatInterface() {
  const [messages, setMessages] = useState([
    { 
      role: 'assistant', 
      content: "Bonjour ! Je suis Baobab AI, votre assistant IA spécialisé dans le contexte africain. Comment puis-je vous aider aujourd'hui ?",
      timestamp: new Date().toISOString()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentSession, setCurrentSession] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [showSessionList, setShowSessionList] = useState(false);
  const chatEndRef = useRef(null);
  const { user } = useAuth();

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    loadChatSessions();
  }, []);

  const loadChatSessions = async () => {
    try {
      const sessionList = await chatService.getChatSessions();
      setSessions(sessionList);
    } catch (error) {
      console.error('Error loading chat sessions:', error);
    }
  };

  const createNewSession = async () => {
    try {
      const newSession = await chatService.createChatSession();
      setCurrentSession(newSession);
      setMessages([
        { 
          role: 'assistant', 
          content: 'Nouvelle conversation démarrée. Comment puis-je vous aider ?',
          timestamp: new Date().toISOString()
        }
      ]);
      await loadChatSessions();
    } catch (error) {
      console.error('Error creating new session:', error);
    }
  };

  const loadSession = async (sessionId) => {
    try {
      const session = await chatService.getChatSession(sessionId);
      setCurrentSession(session);
      setMessages(session.messages || []);
      setShowSessionList(false);
    } catch (error) {
      console.error('Error loading session:', error);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    setError('');

    try {
      // If no current session, create one
      if (!currentSession) {
        await createNewSession();
      }

      // Send message using the enhanced chat service
      const response = await chatService.sendEnhancedMessage(input, currentSession?.id);
      
      // Process the response to extract final answer if needed
      let answer = response.answer || response.message || response;
      if (typeof answer === 'string' && answer.includes('Final Answer:')) {
        answer = answer.split('Final Answer:').pop()
          .replace(/^\\s*[:.-\\s]*/, '')
          .replace(/^I now know the final answer\\.?\\s*/i, '')
          .trim();
      }

      const assistantMessage = {
        role: 'assistant',
        content: answer,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      // Update session list
      await loadChatSessions();
    } catch (err) {
      console.error('Chat error:', err);
      const errorMessage = {
        role: 'assistant',
        content: 'Désolé, je rencontre des difficultés techniques. Veuillez réessayer dans quelques instants.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
      setError("Erreur lors de l'envoi du message");
    } finally {
      setLoading(false);
      setInput('');
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getSuggestions = () => {
    return [
      'Comment créer une startup en Afrique ?',
      "Quelles sont les opportunités d'IA en Afrique ?",
      'Stratégies de financement pour entrepreneurs africains',
      'Technologies émergentes en Afrique',
      'Comment développer un produit pour le marché africain ?'
    ];
  };

  return (
    <div className="chat-interface">
      {/* Chat Header */}
      <div className="chat-header">
        <div className="chat-title">
          <div className="chat-avatar">🤖</div>
          <div>
            <h2>Baobab AI Assistant</h2>
            <p className="chat-subtitle">IA spécialisée pour l'Afrique</p>
          </div>
        </div>
        <div className="chat-actions">
          <button 
            className="session-toggle-btn"
            onClick={() => setShowSessionList(!showSessionList)}
          >
            📋 Historique
          </button>
          <button 
            className="new-session-btn"
            onClick={createNewSession}
          >
            ➕ Nouveau
          </button>
        </div>
      </div>

      {/* Session List */}
      {showSessionList && (
        <div className="session-list">
          <h3>Conversations récentes</h3>
          {sessions.length > 0 ? (
            <div className="session-items">
              {sessions.slice(0, 10).map((session) => (
                <button
                  key={session.id}
                  className={`session-item ${currentSession?.id === session.id ? 'active' : ''}`}
                  onClick={() => loadSession(session.id)}
                >
                  <div className="session-title">
                    {session.title || `Conversation ${session.id}`}
                  </div>
                  <div className="session-date">
                    {new Date(session.updated_at || session.created_at).toLocaleDateString('fr-FR')}
                  </div>
                </button>
              ))}
            </div>
          ) : (
            <p className="no-sessions">Aucune conversation sauvegardée</p>
          )}
        </div>
      )}

      <div className="chat-container">
        {/* Chat Messages */}
        <div className="chat-messages">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.role}`}>
              <div className="message-content">
                <div className="message-text">{msg.content}</div>
                <div className="message-timestamp">
                  {formatTimestamp(msg.timestamp)}
                </div>
              </div>
            </div>
          ))}
          
          {loading && (
            <div className="message assistant">
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={chatEndRef} />
        </div>

        {/* Quick Suggestions */}
        {messages.length === 1 && (
          <div className="suggestions">
            <p className="suggestions-title">Suggestions de questions :</p>
            <div className="suggestions-grid">
              {getSuggestions().map((suggestion, index) => (
                <button
                  key={index}
                  className="suggestion-btn"
                  onClick={() => setInput(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Chat Input */}
        <form className="chat-input-form" onSubmit={sendMessage}>
          <div className="input-container">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Posez votre question sur l'entrepreneuriat, la tech ou l'innovation en Afrique..."
              disabled={loading}
              className="chat-input"
            />
            <button 
              type="submit" 
              disabled={loading || !input.trim()}
              className="send-button"
            >
              {loading ? (
                <div className="send-loading">⏳</div>
              ) : (
                <div className="send-icon">➤</div>
              )}
            </button>
          </div>
        </form>

        {error && (
          <div className="chat-error">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}
      </div>

      {/* Chat Info */}
      <div className="chat-info">
        <p>
          💡 <strong>Conseil :</strong> Baobab AI est optimisé pour répondre aux questions 
          sur l'entrepreneuriat, l'innovation et les technologies en Afrique.
        </p>
      </div>
    </div>
  );
}