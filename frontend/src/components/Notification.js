import React, { useEffect } from 'react';
import { CheckCircle, XCircle, X } from 'lucide-react';

export default function Notification({ notification, onClose }) {
  // Optionnel : Fermeture automatique après 5 secondes si pas géré ailleurs
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => {
        onClose();
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [notification, onClose]);

  if (!notification) return null;

  return (
    <div className="fixed top-4 right-4 z-[9999] w-full max-w-sm px-4 sm:px-0 pointer-events-none">
      {/* 
         pointer-events-auto est nécessaire car le parent a pointer-events-none 
         (pour cliquer à travers la zone vide autour de la notif)
      */}
      <div className={`pointer-events-auto rounded-lg shadow-2xl p-4 flex items-start space-x-3 border-l-4 transform transition-all duration-300 ease-out translate-y-0 opacity-100 ${
        notification.type === 'success' 
          ? 'bg-white border-green-500 text-gray-800' 
          : 'bg-white border-red-500 text-gray-800'
      }`}>
        
        {/* Icône */}
        <div className="flex-shrink-0">
          {notification.type === 'success' ? (
            <CheckCircle className="w-6 h-6 text-green-500" />
          ) : (
            <XCircle className="w-6 h-6 text-red-500" />
          )}
        </div>

        {/* Contenu */}
        <div className="flex-1 pt-0.5">
          <p className="font-bold text-sm">
            {notification.type === 'success' ? 'Succès' : 'Erreur'}
          </p>
          <p className="text-sm text-gray-600 mt-1 leading-snug">
            {notification.message}
          </p>
        </div>

        {/* Bouton Fermer */}
        <button 
          onClick={onClose}
          className="flex-shrink-0 ml-4 text-gray-400 hover:text-gray-600 transition-colors focus:outline-none"
        >
          <X className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}