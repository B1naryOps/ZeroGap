import React from 'react';

export default function DebugPanel({ 
    debugMode, 
    setDebugMode, 
    API_URL, 
    currentScan, 
    scanHistory, 
    statistics, 
    loadHistory, 
    loadStatistics 
}) {
  return (
    <div className="mt-6">
      <button
        onClick={() => setDebugMode(!debugMode)}
        className="text-sm text-gray-500 hover:text-gray-700 flex items-center space-x-1"
      >
        <span>{debugMode ? '🔽' : '▶️'}</span>
        <span>Mode Debug</span>
      </button>
      
      {debugMode && (
        <div className="mt-4 bg-gray-900 text-green-400 rounded-lg p-4 font-mono text-xs overflow-auto max-h-96">
          <div className="mb-4">
            <p className="text-yellow-400 font-bold mb-2">🔍 DIAGNOSTIC ZEROGAP</p>
            <p className="mb-1">API URL: {API_URL}</p>
            <p className="mb-1">Scan actif: {currentScan ? 'OUI' : 'NON'}</p>
            {currentScan && (
              <>
                <p className="mb-1">Scan ID: {currentScan.scan_id}</p>
                <p className="mb-1">Status: {currentScan.status}</p>
                <p className="mb-1">Progress: {currentScan.progress}%</p>
                <p className="mb-1">Vulnérabilités: {currentScan.total_vulnerabilities || 0}</p>
              </>
            )}
          </div>
          
          <div className="mb-4">
            <p className="text-yellow-400 font-bold mb-2">📊 HISTORIQUE</p>
            <p className="mb-1">Nombre de scans: {scanHistory.length}</p>
            {scanHistory.length > 0 && (
              <div className="ml-4 mt-2 border-l-2 border-green-600 pl-2">
                {scanHistory.slice(0, 3).map((scan, i) => (
                  <p key={i} className="mb-1">
                    #{i + 1}: {scan.url} - {scan.vulnerabilities} vulns ({scan.status})
                  </p>
                ))}
              </div>
            )}
          </div>
          
          <div className="mb-4">
            <p className="text-yellow-400 font-bold mb-2">📈 STATISTIQUES</p>
            {statistics ? (
              <>
                <p className="mb-1">Total scans: {statistics.total_scans}</p>
                <p className="mb-1">Total vulnérabilités: {statistics.total_vulnerabilities}</p>
                <p className="mb-1">Scans actifs: {statistics.active_scans}</p>
              </>
            ) : (
              <p className="text-red-400">Aucune statistique disponible</p>
            )}
          </div>
          
          <div className="flex gap-2 mt-4">
            <button
              onClick={() => {
                fetch(`${API_URL}/debug`)
                  .then(r => r.json())
                  .then(data => {
                    console.log('DEBUG API:', data);
                    alert('Voir la console (F12) pour les détails');
                  });
              }}
              className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-xs"
            >
              Tester API Debug
            </button>
            <button
              onClick={() => {
                loadHistory();
                loadStatistics();
              }}
              className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-xs"
            >
              Forcer Rafraîchissement
            </button>
          </div>
          
          {currentScan && (
            <div className="mt-4 border-t border-gray-700 pt-4">
              <p className="text-yellow-400 font-bold mb-2">🔬 DÉTAILS SCAN ACTUEL</p>
              <pre className="text-xs overflow-auto max-h-48 bg-gray-800 p-2 rounded">
                {JSON.stringify(currentScan, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}