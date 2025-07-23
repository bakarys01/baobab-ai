import React from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './Layout.css';

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const navigationItems = [
    { path: '/dashboard', label: 'Tableau de bord', icon: '📊' },
    { path: '/chat', label: 'Chat IA', icon: '💬' },
    { path: '/content', label: 'Contenu', icon: '📚' },
    { path: '/community', label: 'Communauté', icon: '👥' },
    { path: '/profile', label: 'Profil', icon: '👤' }
  ];

  return (
    <div className="layout-container">
      <nav className="sidebar">
        <div className="sidebar-header">
          <h1 className="sidebar-title">Baobab AI</h1>
          <div className="user-info">
            <div className="user-avatar">
              {user?.full_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
            </div>
            <div className="user-details">
              <p className="user-name">{user?.full_name || user?.username}</p>
              <p className="user-email">{user?.email}</p>
            </div>
          </div>
        </div>

        <div className="sidebar-nav">
          {navigationItems.map((item) => (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </button>
          ))}
        </div>

        <div className="sidebar-footer">
          <button onClick={handleLogout} className="logout-button">
            <span className="nav-icon">🚪</span>
            <span className="nav-label">Déconnexion</span>
          </button>
        </div>
      </nav>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}