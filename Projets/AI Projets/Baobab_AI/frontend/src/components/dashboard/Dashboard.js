import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { chatService } from '../../services/chatService';
import './Dashboard.css';

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalChats: 0,
    totalTutorials: 12,
    completedTutorials: 3,
    communityPosts: 8
  });
  const [recentChats, setRecentChats] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        // Load recent chat sessions
        const sessions = await chatService.getChatSessions();
        setRecentChats(sessions.slice(0, 5)); // Get last 5 sessions
        setStats(prev => ({
          ...prev,
          totalChats: sessions.length
        }));
      } catch (error) {
        console.error('Error loading dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Bonjour';
    if (hour < 18) return 'Bon après-midi';
    return 'Bonsoir';
  };

  const getProgressPercentage = () => {
    return Math.round((stats.completedTutorials / stats.totalTutorials) * 100);
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Chargement de votre tableau de bord...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="page-header">
        <h1 className="page-title">
          {getGreeting()}, {user?.full_name || user?.username} 👋
        </h1>
        <p className="page-subtitle">
          Voici un aperçu de votre activité sur Baobab AI
        </p>
      </div>

      {/* Stats Cards */}
      <div className="content-grid grid-2">
        <div className="stat-card">
          <h3 className="stat-number">{stats.totalChats}</h3>
          <p className="stat-label">Conversations IA</p>
        </div>
        <div className="stat-card" style={{background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)'}}>
          <h3 className="stat-number">{stats.completedTutorials}/{stats.totalTutorials}</h3>
          <p className="stat-label">Tutoriels complétés</p>
        </div>
      </div>

      <div className="content-grid grid-2" style={{marginTop: '24px'}}>
        {/* Progress Overview */}
        <div className="content-card">
          <h2 className="section-title">Progression d'apprentissage</h2>
          <div className="progress-overview">
            <div className="progress-circle">
              <svg viewBox="0 0 36 36" className="circular-chart">
                <path className="circle-bg"
                  d="M18 2.0845
                    a 15.9155 15.9155 0 0 1 0 31.831
                    a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                <path className="circle"
                  strokeDasharray={`${getProgressPercentage()}, 100`}
                  d="M18 2.0845
                    a 15.9155 15.9155 0 0 1 0 31.831
                    a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                <text x="18" y="20.35" className="percentage">{getProgressPercentage()}%</text>
              </svg>
            </div>
            <div className="progress-details">
              <p className="progress-text">
                Vous avez complété <strong>{stats.completedTutorials}</strong> tutoriels sur <strong>{stats.totalTutorials}</strong>
              </p>
              <button className="continue-learning-btn">
                Continuer l'apprentissage →
              </button>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="content-card">
          <h2 className="section-title">Actions rapides</h2>
          <div className="quick-actions">
            <button className="action-btn primary">
              <span className="action-icon">💬</span>
              <span>Nouvelle conversation</span>
            </button>
            <button className="action-btn secondary">
              <span className="action-icon">📚</span>
              <span>Parcourir les tutoriels</span>
            </button>
            <button className="action-btn secondary">
              <span className="action-icon">👥</span>
              <span>Rejoindre la communauté</span>
            </button>
            <button className="action-btn secondary">
              <span className="action-icon">📊</span>
              <span>Voir les études de cas</span>
            </button>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="content-grid" style={{marginTop: '24px'}}>
        <div className="content-card">
          <h2 className="section-title">Activité récente</h2>
          {recentChats.length > 0 ? (
            <div className="recent-activity">
              {recentChats.map((chat, index) => (
                <div key={chat.id || index} className="activity-item">
                  <div className="activity-icon">💬</div>
                  <div className="activity-content">
                    <h3 className="activity-title">
                      {chat.title || `Conversation ${index + 1}`}
                    </h3>
                    <p className="activity-time">
                      {new Date(chat.created_at || Date.now()).toLocaleDateString('fr-FR', {
                        day: 'numeric',
                        month: 'long',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                  <button className="activity-action">Ouvrir</button>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">💬</div>
              <h3 className="empty-title">Aucune conversation récente</h3>
              <p className="empty-text">
                Commencez votre première conversation avec Baobab AI pour obtenir des conseils personnalisés.
              </p>
              <button className="empty-action-btn">Démarrer une conversation</button>
            </div>
          )}
        </div>
      </div>

      {/* Featured Content */}
      <div className="content-grid" style={{marginTop: '24px'}}>
        <div className="content-card">
          <h2 className="section-title">Contenu recommandé</h2>
          <div className="featured-content">
            <div className="featured-item">
              <div className="featured-image">📈</div>
              <div className="featured-details">
                <h3 className="featured-title">Stratégies de croissance pour startups africaines</h3>
                <p className="featured-description">
                  Découvrez les meilleures pratiques pour développer votre startup en Afrique.
                </p>
                <span className="featured-type">Étude de cas</span>
              </div>
            </div>
            
            <div className="featured-item">
              <div className="featured-image">🤖</div>
              <div className="featured-details">
                <h3 className="featured-title">Introduction au Machine Learning</h3>
                <p className="featured-description">
                  Les bases de l'apprentissage automatique expliquées simplement.
                </p>
                <span className="featured-type">Tutoriel</span>
              </div>
            </div>

            <div className="featured-item">
              <div className="featured-image">💡</div>
              <div className="featured-details">
                <h3 className="featured-title">Innovation technologique au Kenya</h3>
                <p className="featured-description">
                  Comment M-Pesa a révolutionné les paiements mobiles en Afrique.
                </p>
                <span className="featured-type">Étude de cas</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}