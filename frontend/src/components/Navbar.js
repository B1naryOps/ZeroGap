import React, { useState } from 'react';
import { Menu, X, Globe, History } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab }) {
  // État pour gérer l'ouverture/fermeture du menu mobile
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Fonction pour changer d'onglet et fermer le menu mobile automatiquement
  const handleNavClick = (tab) => {
    setActiveTab(tab);
    setIsMobileMenuOpen(false);
  };

  return (
    <header className="bg-gradient-to-r from-blue-600 to-blue-700 shadow-lg sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          
          {/* LOGO */}
          <div className="flex items-center space-x-3">
            <div className="relative">
              <div className="w-10 h-10 rounded-full border-4 border-white flex items-center justify-center">
                <div className="w-4 h-4 rounded-full bg-white"></div>
              </div>
              <div className="absolute top-0 left-0 w-10 h-10">
                <div className="absolute top-0 left-1/2 w-1 h-2 bg-cyan-400 -translate-x-1/2"></div>
                <div className="absolute bottom-0 left-1/2 w-1 h-2 bg-cyan-400 -translate-x-1/2"></div>
                <div className="absolute left-0 top-1/2 h-1 w-2 bg-cyan-400 -translate-y-1/2"></div>
                <div className="absolute right-0 top-1/2 h-1 w-2 bg-cyan-400 -translate-y-1/2"></div>
              </div>
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">ZeroGap</h1>
          </div>
          
          {/* NAVIGATION DESKTOP (Cachée sur mobile) */}
          <nav className="hidden md:flex space-x-8">
            <button 
              onClick={() => setActiveTab('dashboard')}
              className={`flex items-center space-x-2 px-3 py-2 text-sm font-medium transition-colors ${activeTab === 'dashboard' ? 'text-white bg-blue-800 rounded-lg' : 'text-blue-100 hover:text-white'}`}
            >
              <Globe className="w-4 h-4" />
              <span>Dashboard</span>
            </button>
            <button 
              onClick={() => setActiveTab('history')}
              className={`flex items-center space-x-2 px-3 py-2 text-sm font-medium transition-colors ${
                activeTab === 'history'
                  ? 'text-white bg-blue-800 rounded-lg'
                  : 'text-blue-100 hover:text-white'
              }`}
            >
              <History className="w-4 h-4" />
              <span>Historique</span>
            </button>
          </nav>
          
          {/* BOUTON BURGER MOBILE (Visible uniquement sur mobile) */}
          <button 
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden text-white hover:bg-blue-800 p-2 rounded transition-colors"
          >
            {isMobileMenuOpen ? (
              <X className="w-6 h-6" /> // Icône croix si ouvert
            ) : (
              <Menu className="w-6 h-6" /> // Icône burger si fermé
            )}
          </button>
        </div>
      </div>

      {/* MENU DÉROULANT MOBILE */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-blue-800 border-t border-blue-600 animate-slide-in-top">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            <button
              onClick={() => handleNavClick('dashboard')}
              className={`w-full flex items-center space-x-2 px-3 py-3 rounded-md text-base font-medium ${
                activeTab === 'dashboard' 
                  ? 'bg-blue-900 text-white' 
                  : 'text-blue-100 hover:bg-blue-700 hover:text-white'
              }`}
            >
              <Globe className="w-5 h-5" />
              <span>Dashboard</span>
            </button>

            <button
              onClick={() => handleNavClick('history')}
              className={`w-full flex items-center space-x-2 px-3 py-3 rounded-md text-base font-medium ${
                activeTab === 'history' 
                  ? 'bg-blue-900 text-white' 
                  : 'text-blue-100 hover:bg-blue-700 hover:text-white'
              }`}
            >
              <History className="w-5 h-5" />
              <span>Historique</span>
            </button>
          </div>
        </div>
      )}
    </header>
  );
}