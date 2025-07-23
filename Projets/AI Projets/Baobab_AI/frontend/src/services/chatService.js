import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ChatService {
  constructor() {
    this.api = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('baobab_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );
  }

  async sendMessage(question, history = []) {
    const response = await this.api.post('/rag', {
      question,
      history,
    });
    return response.data;
  }

  async sendEnhancedMessage(message, sessionId = null) {
    const response = await this.api.post('/api/chat/message', {
      message,
      session_id: sessionId,
    });
    return response.data;
  }

  async getChatSessions() {
    const response = await this.api.get('/api/chat/sessions');
    return response.data;
  }

  async getChatSession(sessionId) {
    const response = await this.api.get(`/api/chat/sessions/${sessionId}`);
    return response.data;
  }

  async createChatSession(title = null) {
    const response = await this.api.post('/api/chat/sessions', {
      title,
    });
    return response.data;
  }

  async deleteChatSession(sessionId) {
    const response = await this.api.delete(`/api/chat/sessions/${sessionId}`);
    return response.data;
  }
}

export const chatService = new ChatService();