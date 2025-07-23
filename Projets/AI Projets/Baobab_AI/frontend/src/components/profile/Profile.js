import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import './Profile.css';

export default function Profile() {
  const { user, updateUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    full_name: user?.full_name || '',
    email: user?.email || '',
    country: user?.country || '',
    profession: user?.profession || '',
    experience_level: user?.experience_level || 'beginner',
    interests: user?.interests || []
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleInterestToggle = (interest) => {
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter(i => i !== interest)
        : [...prev.interests, interest]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      await updateUser(formData);
      setIsEditing(false);
      setMessage('Profil mis à jour avec succès !');
    } catch (error) {
      setMessage('Erreur lors de la mise à jour du profil');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      full_name: user?.full_name || '',
      email: user?.email || '',
      country: user?.country || '',
      profession: user?.profession || '',
      experience_level: user?.experience_level || 'beginner',
      interests: user?.interests || []
    });
    setIsEditing(false);
    setMessage('');
  };

  const availableInterests = [
    'Machine Learning',
    'Entrepreneuriat',
    'Fintech',
    'E-commerce',
    'Marketing Digital',
    'Intelligence Artificielle',
    'Blockchain',
    'IoT',
    'Développement Web',
    'Analyse de Données'
  ];

  const getExperienceLabel = (level) => {
    switch (level) {
      case 'beginner': return 'Débutant';
      case 'intermediate': return 'Intermédiaire';
      case 'advanced': return 'Avancé';
      default: return level;
    }
  };

  const getJoinDate = () => {
    if (user?.created_at) {
      return new Date(user.created_at).toLocaleDateString('fr-FR', {
        year: 'numeric',
        month: 'long'
      });
    }
    return 'Date inconnue';
  };

  return (
    <div className="profile-page">
      <div className="page-header">
        <h1 className="page-title">Mon Profil</h1>
        <p className="page-subtitle">
          Gérez vos informations personnelles et préférences
        </p>
      </div>

      <div className="profile-container">
        {/* Profile Header */}
        <div className="profile-header">
          <div className="profile-avatar">
            {user?.full_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
          </div>
          <div className="profile-info">
            <h2 className="profile-name">
              {user?.full_name || user?.username}
            </h2>
            <p className="profile-email">{user?.email}</p>
            <p className="profile-join-date">
              Membre depuis {getJoinDate()}
            </p>
          </div>
          <div className="profile-actions">
            {!isEditing ? (
              <button 
                className="edit-profile-btn"
                onClick={() => setIsEditing(true)}
              >
                ✏️ Modifier le profil
              </button>
            ) : (
              <div className="edit-actions">
                <button 
                  className="save-btn"
                  onClick={handleSubmit}
                  disabled={loading}
                >
                  {loading ? 'Sauvegarde...' : '💾 Sauvegarder'}
                </button>
                <button 
                  className="cancel-btn"
                  onClick={handleCancel}
                  disabled={loading}
                >
                  ❌ Annuler
                </button>
              </div>
            )}
          </div>
        </div>

        {message && (
          <div className={`profile-message ${message.includes('succès') ? 'success' : 'error'}`}>
            {message}
          </div>
        )}

        {/* Profile Form */}
        <div className="profile-form-container">
          <form onSubmit={handleSubmit} className="profile-form">
            <div className="form-section">
              <h3 className="section-title">Informations personnelles</h3>
              
              <div className="form-grid">
                <div className="form-group">
                  <label htmlFor="full_name">Nom complet</label>
                  <input
                    type="text"
                    id="full_name"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                    disabled={!isEditing}
                    className={!isEditing ? 'readonly' : ''}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="email">Email</label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    disabled={!isEditing}
                    className={!isEditing ? 'readonly' : ''}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="country">Pays</label>
                  <input
                    type="text"
                    id="country"
                    name="country"
                    value={formData.country}
                    onChange={handleChange}
                    disabled={!isEditing}
                    className={!isEditing ? 'readonly' : ''}
                    placeholder="Votre pays"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="profession">Profession</label>
                  <input
                    type="text"
                    id="profession"
                    name="profession"
                    value={formData.profession}
                    onChange={handleChange}
                    disabled={!isEditing}
                    className={!isEditing ? 'readonly' : ''}
                    placeholder="Votre profession"
                  />
                </div>
              </div>
            </div>

            <div className="form-section">
              <h3 className="section-title">Niveau d'expérience</h3>
              
              <div className="experience-selector">
                {['beginner', 'intermediate', 'advanced'].map((level) => (
                  <label key={level} className="experience-option">
                    <input
                      type="radio"
                      name="experience_level"
                      value={level}
                      checked={formData.experience_level === level}
                      onChange={handleChange}
                      disabled={!isEditing}
                    />
                    <span className="experience-label">
                      {getExperienceLabel(level)}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            <div className="form-section">
              <h3 className="section-title">Centres d'intérêt</h3>
              
              <div className="interests-grid">
                {availableInterests.map((interest) => (
                  <label key={interest} className="interest-option">
                    <input
                      type="checkbox"
                      checked={formData.interests.includes(interest)}
                      onChange={() => handleInterestToggle(interest)}
                      disabled={!isEditing}
                    />
                    <span className="interest-label">{interest}</span>
                  </label>
                ))}
              </div>
            </div>
          </form>
        </div>

        {/* Profile Stats */}
        <div className="profile-stats">
          <h3 className="section-title">Statistiques</h3>
          
          <div className="stats-grid">
            <div className="stat-item">
              <div className="stat-icon">💬</div>
              <div className="stat-content">
                <div className="stat-number">0</div>
                <div className="stat-label">Conversations</div>
              </div>
            </div>

            <div className="stat-item">
              <div className="stat-icon">📚</div>
              <div className="stat-content">
                <div className="stat-number">0</div>
                <div className="stat-label">Tutoriels terminés</div>
              </div>
            </div>

            <div className="stat-item">
              <div className="stat-icon">⭐</div>
              <div className="stat-content">
                <div className="stat-number">0</div>
                <div className="stat-label">Points d'expérience</div>
              </div>
            </div>

            <div className="stat-item">
              <div className="stat-icon">🏆</div>
              <div className="stat-content">
                <div className="stat-number">0</div>
                <div className="stat-label">Badges obtenus</div>
              </div>
            </div>
          </div>
        </div>

        {/* Account Actions */}
        <div className="account-section">
          <h3 className="section-title">Paramètres du compte</h3>
          
          <div className="account-actions">
            <button className="account-btn secondary">
              🔒 Changer le mot de passe
            </button>
            <button className="account-btn secondary">
              📧 Préférences de notification
            </button>
            <button className="account-btn secondary">
              📊 Exporter mes données
            </button>
            <button className="account-btn danger">
              🗑️ Supprimer le compte
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}