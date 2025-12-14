import React from 'react';
import { History, RefreshCw, Clock } from 'lucide-react';

export default function HistoryPreview({ scanHistory, loadHistory, fetchScanStatus }) {
  return (
    <div className="mt-6 bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-gray-900">Historique des Scans</h2>
        <button 
          onClick={loadHistory}
          className="text-blue-600 hover:text-blue-700 flex items-center space-x-1"
        >
          <RefreshCw className="w-4 h-4" />
          <span className="text-sm">Actualiser</span>
        </button>
      </div>
      
      {scanHistory.length > 0 ? (
        <div className="space-y-3">
          {scanHistory.map((scan, index) => (
            <div key={index} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition-colors border border-gray-100">
              <div className="flex items-center space-x-3">
                <Clock className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-900">{scan.date} à {scan.time}</p>
                  <p className="text-xs text-gray-500">{scan.url}</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-sm text-gray-600">
                  {scan.vulnerabilities} vuln.
                </span>
                <button
                  onClick={() => fetchScanStatus(scan.id)}
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                >
                  Voir
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          <History className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p>Aucun scan dans l'historique</p>
        </div>
      )}
    </div>
  );
}