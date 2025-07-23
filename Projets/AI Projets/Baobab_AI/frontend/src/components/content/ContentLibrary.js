import React, { useState, useEffect } from 'react';
import './ContentLibrary.css';

export default function ContentLibrary() {
  const [activeTab, setActiveTab] = useState('tutorials');
  const [tutorials, setTutorials] = useState([]);
  const [caseStudies, setCaseStudies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    category: 'all',
    difficulty: 'all',
    country: 'all'
  });

  // Mock data - in real app, this would come from API
  const mockTutorials = [
    {
      id: 1,
      title: 'Introduction à l\'entrepreneuriat en Afrique',
      description: 'Les bases pour créer et développer une entreprise dans le contexte africain.',
      category: 'business',
      difficulty: 'beginner',
      duration: 45,
      author: 'Dr. Amina Kone',
      completed: false,
      progress: 0,
      image: '📈'
    },
    {
      id: 2,
      title: 'Financement des startups africaines',
      description: 'Découvrez les différentes options de financement disponibles pour les entrepreneurs africains.',
      category: 'business',
      difficulty: 'intermediate',
      duration: 60,
      author: 'Michel Owona',
      completed: false,
      progress: 25,
      image: '💰'
    },
    {
      id: 3,
      title: 'Intelligence Artificielle pour les débutants',
      description: 'Une introduction accessible à l\'IA et ses applications en Afrique.',
      category: 'tech',
      difficulty: 'beginner',
      duration: 90,
      author: 'Prof. Sarah Oduya',
      completed: true,
      progress: 100,
      image: '🤖'
    },
    {
      id: 4,
      title: 'Marketing digital en Afrique',
      description: 'Stratégies de marketing adaptées aux marchés africains.',
      category: 'marketing',
      difficulty: 'intermediate',
      duration: 75,
      author: 'Fatou Diallo',
      completed: false,
      progress: 0,
      image: '📱'
    }
  ];

  const mockCaseStudies = [
    {
      id: 1,
      title: 'M-Pesa : Révolution des paiements mobiles au Kenya',
      company: 'Safaricom',
      country: 'Kenya',
      industry: 'Fintech',
      description: 'Comment M-Pesa a transformé les services financiers en Afrique de l\'Est.',
      insights: ['Innovation frugale', 'Adaptation au contexte local', 'Partenariats stratégiques'],
      image: '📱'
    },
    {
      id: 2,
      title: 'Jumia : L\'Amazon africain',
      company: 'Jumia',
      country: 'Nigeria',
      industry: 'E-commerce',
      description: 'L\'histoire de la première licorne technologique africaine.',
      insights: ['Écosystème digital', 'Logistique adaptée', 'Paiement mobile'],
      image: '🛒'
    },
    {
      id: 3,
      title: 'Andela : Former les développeurs africains',
      company: 'Andela',
      country: 'Nigeria',
      industry: 'EdTech',
      description: 'Comment former et connecter les talents tech africains au marché mondial.',
      insights: ['Formation intensive', 'Travail à distance', 'Talents locaux'],
      image: '👨‍💻'
    }
  ];

  useEffect(() => {
    // Simulate API loading
    setTimeout(() => {
      setTutorials(mockTutorials);
      setCaseStudies(mockCaseStudies);
      setLoading(false);
    }, 1000);
  }, []);

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const filteredTutorials = tutorials.filter(tutorial => {
    if (filters.category !== 'all' && tutorial.category !== filters.category) return false;
    if (filters.difficulty !== 'all' && tutorial.difficulty !== filters.difficulty) return false;
    return true;
  });

  const filteredCaseStudies = caseStudies.filter(study => {
    if (filters.country !== 'all' && study.country !== filters.country) return false;
    return true;
  });

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'beginner': return '#10b981';
      case 'intermediate': return '#f59e0b';
      case 'advanced': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getDifficultyLabel = (difficulty) => {
    switch (difficulty) {
      case 'beginner': return 'Débutant';
      case 'intermediate': return 'Intermédiaire';
      case 'advanced': return 'Avancé';
      default: return difficulty;
    }
  };

  if (loading) {
    return (
      <div className="content-loading">
        <div className="loading-spinner"></div>
        <p>Chargement du contenu...</p>
      </div>
    );
  }

  return (
    <div className="content-library">
      <div className="page-header">
        <h1 className="page-title">Bibliothèque de contenu</h1>
        <p className="page-subtitle">
          Explorez nos tutoriels et études de cas pour développer vos compétences
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="content-tabs">
        <button
          className={`tab-button ${activeTab === 'tutorials' ? 'active' : ''}`}
          onClick={() => setActiveTab('tutorials')}
        >
          📚 Tutoriels ({tutorials.length})
        </button>
        <button
          className={`tab-button ${activeTab === 'case-studies' ? 'active' : ''}`}
          onClick={() => setActiveTab('case-studies')}
        >
          📊 Études de cas ({caseStudies.length})
        </button>
      </div>

      {/* Filters */}
      <div className="content-filters">
        {activeTab === 'tutorials' ? (
          <>
            <select
              value={filters.category}
              onChange={(e) => handleFilterChange('category', e.target.value)}
              className="filter-select"
            >
              <option value="all">Toutes les catégories</option>
              <option value="business">Business</option>
              <option value="tech">Technologie</option>
              <option value="marketing">Marketing</option>
            </select>
            <select
              value={filters.difficulty}
              onChange={(e) => handleFilterChange('difficulty', e.target.value)}
              className="filter-select"
            >
              <option value="all">Tous les niveaux</option>
              <option value="beginner">Débutant</option>
              <option value="intermediate">Intermédiaire</option>
              <option value="advanced">Avancé</option>
            </select>
          </>
        ) : (
          <select
            value={filters.country}
            onChange={(e) => handleFilterChange('country', e.target.value)}
            className="filter-select"
          >
            <option value="all">Tous les pays</option>
            <option value="Kenya">Kenya</option>
            <option value="Nigeria">Nigeria</option>
            <option value="Ghana">Ghana</option>
            <option value="South Africa">Afrique du Sud</option>
          </select>
        )}
      </div>

      {/* Content Grid */}
      {activeTab === 'tutorials' ? (
        <div className="content-grid">
          {filteredTutorials.map((tutorial) => (
            <div key={tutorial.id} className="tutorial-card">
              <div className="tutorial-image">
                {tutorial.image}
              </div>
              <div className="tutorial-content">
                <div className="tutorial-header">
                  <h3 className="tutorial-title">{tutorial.title}</h3>
                  <div className="tutorial-meta">
                    <span 
                      className="difficulty-badge"
                      style={{ backgroundColor: getDifficultyColor(tutorial.difficulty) }}
                    >
                      {getDifficultyLabel(tutorial.difficulty)}
                    </span>
                    <span className="duration-badge">
                      ⏱️ {tutorial.duration} min
                    </span>
                  </div>
                </div>
                
                <p className="tutorial-description">{tutorial.description}</p>
                
                <div className="tutorial-progress">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${tutorial.progress}%` }}
                    ></div>
                  </div>
                  <span className="progress-text">
                    {tutorial.progress}% terminé
                  </span>
                </div>

                <div className="tutorial-footer">
                  <span className="tutorial-author">Par {tutorial.author}</span>
                  <button className="start-tutorial-btn">
                    {tutorial.progress > 0 ? 'Continuer' : 'Commencer'}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="content-grid">
          {filteredCaseStudies.map((study) => (
            <div key={study.id} className="case-study-card">
              <div className="case-study-image">
                {study.image}
              </div>
              <div className="case-study-content">
                <div className="case-study-header">
                  <h3 className="case-study-title">{study.title}</h3>
                  <div className="case-study-meta">
                    <span className="company-badge">{study.company}</span>
                    <span className="country-badge">📍 {study.country}</span>
                  </div>
                </div>
                
                <p className="case-study-description">{study.description}</p>
                
                <div className="insights">
                  <h4>Insights clés :</h4>
                  <ul>
                    {study.insights.map((insight, index) => (
                      <li key={index}>{insight}</li>
                    ))}
                  </ul>
                </div>

                <div className="case-study-footer">
                  <span className="industry-tag">{study.industry}</span>
                  <button className="read-case-study-btn">
                    Lire l'étude
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {((activeTab === 'tutorials' && filteredTutorials.length === 0) ||
        (activeTab === 'case-studies' && filteredCaseStudies.length === 0)) && (
        <div className="empty-content">
          <div className="empty-icon">
            {activeTab === 'tutorials' ? '📚' : '📊'}
          </div>
          <h3>Aucun contenu trouvé</h3>
          <p>
            Aucun {activeTab === 'tutorials' ? 'tutoriel' : 'étude de cas'} ne correspond à vos critères de recherche.
          </p>
          <button 
            className="reset-filters-btn"
            onClick={() => setFilters({ category: 'all', difficulty: 'all', country: 'all' })}
          >
            Réinitialiser les filtres
          </button>
        </div>
      )}
    </div>
  );
}