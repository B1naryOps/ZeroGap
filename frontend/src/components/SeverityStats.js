import React from 'react';

export default function SeverityStats({ currentScan }) {
  const totalVulnerabilities = currentScan?.total_vulnerabilities || 0;
  // Clé unique pour forcer le rafraichissement du graphique quand les données changent
  const scanId = currentScan?.scan_id || 'no-scan';
  
  const getSeverityCount = (severity) => {
    return currentScan?.severity_stats?.[severity] || 0;
  };

  // 1. Configuration du cercle
  const RADIUS = 80;
  const CIRCUMFERENCE = 2 * Math.PI * RADIUS; // ≈ 502.65
  const CENTER = 96;

  // 2. Définition des segments à dessiner
  // L'ordre est important pour l'empilement (Critique d'abord, etc.)
  // J'utilise ici les codes couleurs HEX qui correspondent aux classes Tailwind de ta légende
  const segments = [
    { key: 'CRITICAL', color: '#b91c1c' }, // Rouge foncé (bg-red-700)
    { key: 'HIGH', color: '#ef4444' },     // Rouge (bg-red-500)
    { key: 'MEDIUM', color: '#eab308' },   // Jaune (bg-yellow-500)
    { key: 'LOW', color: '#22c55e' }       // Vert (bg-green-500)
  ];

  // 3. Calcul dynamique des arcs
  let accumulatedOffset = 0; // Sert à décaler le début de chaque nouveau segment

  const svgSegments = segments.map((seg) => {
    const count = getSeverityCount(seg.key);
    
    // Si ce niveau a 0 vulnérabilité, on ne dessine rien
    if (count === 0 || totalVulnerabilities === 0) return null;

    // Calcul de la longueur de l'arc pour ce segment
    // Exemple : si 2 Faibles sur 2 total -> (2/2)*502 = 502 (cercle complet)
    const strokeLength = (count / totalVulnerabilities) * CIRCUMFERENCE;
    
    // Configuration du tiret SVG : [Longueur du trait, Espace vide]
    const dashArray = `${strokeLength} ${CIRCUMFERENCE}`;
    
    // Le décalage (offset) : on doit tourner le cercle pour commencer après le segment précédent
    // SVG tourne dans le sens anti-horaire pour les offsets négatifs
    const dashOffset = -accumulatedOffset;

    // On ajoute la longueur actuelle à l'offset pour le PROCHAIN segment
    accumulatedOffset += strokeLength;

    return (
      <circle
        key={seg.key}
        cx={CENTER}
        cy={CENTER}
        r={RADIUS}
        fill="none"
        stroke={seg.color}
        strokeWidth="24"
        strokeDasharray={dashArray}
        strokeDashoffset={dashOffset}
        // Transition pour l'effet d'animation fluide
        className="transition-all duration-1000 ease-out"
      />
    );
  });

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Vulnérabilités par Niveau</h2>
      
      <div className="flex justify-center mb-6">
        <div className="relative w-48 h-48">
          {/* SVG Principal */}
          <svg 
            key={`${scanId}-${totalVulnerabilities}`} 
            className="w-full h-full transform -rotate-90"
            viewBox="0 0 192 192"
          >
            {/* Fond gris du cercle (toujours visible si total = 0 ou pour boucher les trous) */}
            <circle cx={CENTER} cy={CENTER} r={RADIUS} fill="none" stroke="#e5e7eb" strokeWidth="24" />
            
            {/* Dessin des segments colorés par dessus */}
            {totalVulnerabilities > 0 && svgSegments}
          </svg>
          
          {/* Texte au centre */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <p className="text-3xl font-bold text-gray-900">{totalVulnerabilities}</p>
              <p className="text-xs text-gray-500">Total</p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Légende */}
      <div className="space-y-2">
        {[
          { label: 'Critique', key: 'CRITICAL', color: 'bg-red-700' },
          { label: 'Élevé', key: 'HIGH', color: 'bg-red-500' },
          { label: 'Moyen', key: 'MEDIUM', color: 'bg-yellow-500' },
          { label: 'Faible', key: 'LOW', color: 'bg-green-500' },
        ].map((item) => (
          <div key={item.key} className="flex items-center justify-between hover:bg-gray-50 p-1 rounded transition-colors">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${item.color}`}></div>
              <span className="text-sm text-gray-700">{item.label}</span>
            </div>
            <span className="text-sm font-medium text-gray-900">{getSeverityCount(item.key)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}