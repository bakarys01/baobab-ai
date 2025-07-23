import React from 'react';
import './LoadingScreen.css';

export default function LoadingScreen() {
  return (
    <div className="loading-screen">
      <div className="loading-content">
        <div className="loading-logo">
          <div className="baobab-tree">🌳</div>
          <h1>Baobab AI</h1>
        </div>
        <div className="loading-spinner-container">
          <div className="loading-spinner"></div>
        </div>
        <p className="loading-text">Chargement de votre expérience IA...</p>
      </div>
    </div>
  );
}