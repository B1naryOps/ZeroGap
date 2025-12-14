import React from 'react';
import { Globe, CheckCircle, Clock, XCircle, AlertTriangle, FileText, Download } from 'lucide-react';

export default function ResultSummary({ currentScan, downloadReport }) {
  const totalVulnerabilities = currentScan?.total_vulnerabilities || 0;

  if (!currentScan) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Résultat Récent</h2>
        <div className="text-center py-8 text-gray-500">
          <AlertTriangle className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p>Aucun scan actif</p>
          <p className="text-sm">Lancez un nouveau scan</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Résultat Actuel</h2>
      
      <div className="space-y-4">
        <div className="flex items-center space-x-2">
          <Globe className="w-5 h-5 text-gray-400" />
          <p className="text-lg font-medium text-gray-900 truncate">{currentScan.url}</p>
        </div>
        
        <div className="flex items-center space-x-2">
          {currentScan.status === 'completed' ? (
            <CheckCircle className="w-5 h-5 text-green-500" />
          ) : currentScan.status === 'running' || currentScan.status === 'starting' ? (
            <Clock className="w-5 h-5 text-blue-500 animate-pulse" />
          ) : currentScan.status === 'failed' ? (
            <XCircle className="w-5 h-5 text-red-500" />
          ) : (
            <AlertTriangle className="w-5 h-5 text-yellow-500" />
          )}
          <p className="text-sm text-gray-600">
            Statut: <span className="font-medium capitalize">{
              currentScan.status === 'running' ? 'En cours' :
              currentScan.status === 'completed' ? 'Terminé' :
              currentScan.status === 'failed' ? 'Échoué' :
              currentScan.status === 'starting' ? 'Démarrage' :
              currentScan.status
            }</span>
          </p>
        </div>
        
        {currentScan.status === 'failed' && currentScan.error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-3 rounded">
            <p className="text-sm font-medium text-red-800">Erreur:</p>
            <p className="text-xs text-red-700 mt-1">{currentScan.error}</p>
          </div>
        )}
        
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
          <p className="text-2xl font-bold text-red-600">{totalVulnerabilities}</p>
          <p className="text-sm text-red-700">vulnérabilités trouvées</p>
        </div>
        
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="bg-gray-50 p-2 rounded">
            <p className="text-gray-500">URLs</p>
            <p className="font-semibold text-gray-900">{currentScan.crawled_urls_count || 0}</p>
          </div>
          <div className="bg-gray-50 p-2 rounded">
            <p className="text-gray-500">Formulaires</p>
            <p className="font-semibold text-gray-900">{currentScan.forms_count || 0}</p>
          </div>
        </div>
        
        {currentScan.status === 'completed' && (
          <div className="flex gap-2">
            <button 
              onClick={() => downloadReport(currentScan.scan_id, 'html')}
              className="flex-1 bg-blue-50 hover:bg-blue-100 text-blue-700 font-medium py-2 px-3 rounded-lg flex items-center justify-center space-x-2 transition-colors text-sm border border-blue-200"
            >
              <FileText className="w-4 h-4" />
              <span>HTML</span>
            </button>
            <button 
              onClick={() => downloadReport(currentScan.scan_id, 'json')}
              className="flex-1 bg-blue-50 hover:bg-blue-100 text-blue-700 font-medium py-2 px-3 rounded-lg flex items-center justify-center space-x-2 transition-colors text-sm border border-blue-200"
            >
              <Download className="w-4 h-4" />
              <span>JSON</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}