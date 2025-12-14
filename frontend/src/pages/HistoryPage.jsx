import React, { useState } from 'react';
import { Trash2, Eye, RefreshCw, AlertTriangle, ChevronLeft, ChevronRight, FileText, Download } from 'lucide-react';

export default function HistoryPage({ scanHistory, loadHistory, onViewScan, API_URL }) {
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;
  const [isLoading, setIsLoading] = useState(false);

  // --- Logique de Pagination ---
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = scanHistory.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(scanHistory.length / itemsPerPage);

  const nextPage = () => {
    if (currentPage < totalPages) setCurrentPage(currentPage + 1);
  };

  const prevPage = () => {
    if (currentPage > 1) setCurrentPage(currentPage - 1);
  };

  // --- Actions ---

  const handleDelete = async (scanId) => {
    if (!window.confirm("Êtes-vous sûr de vouloir supprimer ce scan ?")) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/history/${scanId}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        await loadHistory(); // Demande à App.js de recharger la liste
      } else {
        alert("Erreur lors de la suppression");
      }
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = async () => {
    if (!window.confirm("ATTENTION : Cela va supprimer TOUS les rapports de scans. Continuer ?")) return;

    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/history`, {
        method: 'DELETE',
      });
      if (response.ok) {
        await loadHistory();
        setCurrentPage(1);
      } else {
        alert("Erreur lors de la réinitialisation");
      }
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const downloadReport = (scanId, format) => {
    const endpoint = format === 'json' ? 'report/json' : 'report';
    window.open(`${API_URL}/scan/${scanId}/${endpoint}`, '_blank');
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 animate-fade-in">
      {/* Header de la page */}
      <div className="flex justify-between items-center mb-6 border-b pb-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Historique Complet</h2>
          <p className="text-sm text-gray-500">Gérez et consultez vos anciens rapports d'audit.</p>
        </div>
        <div className="flex space-x-3">
          <button 
            onClick={loadHistory}
            className="flex items-center px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Actualiser
          </button>
          
          {scanHistory.length > 0 && (
            <button 
              onClick={handleReset}
              className="flex items-center px-3 py-2 bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 rounded-md transition-colors"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Tout Effacer
            </button>
          )}
        </div>
      </div>

      {/* Tableau */}
      {scanHistory.length > 0 ? (
        <>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date & Heure</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cible (URL)</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vulnérabilités</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Statut</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {currentItems.map((scan) => (
                  <tr key={scan.id || scan.scan_id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {scan.date} <span className="text-xs text-gray-400">{scan.time}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      <div className="truncate max-w-xs" title={scan.url}>
                        {scan.url}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        scan.vulnerabilities > 0 ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                      }`}>
                        {scan.vulnerabilities} détectées
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 capitalize">
                      {scan.status}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                      {/* Bouton Télécharger HTML */}
                      <button 
                        onClick={() => downloadReport(scan.id || scan.scan_id, 'html')}
                        title="Télécharger rapport HTML"
                        className="text-gray-400 hover:text-blue-600 transition-colors"
                      >
                        <FileText className="w-5 h-5" />
                      </button>

                      {/* Bouton Télécharger JSON */}
                      <button 
                        onClick={() => downloadReport(scan.id || scan.scan_id, 'json')}
                        title="Télécharger données JSON"
                        className="text-gray-400 hover:text-purple-600 transition-colors"
                      >
                        <Download className="w-5 h-5" />
                      </button>

                      {/* Bouton Charger dans Dashboard */}
                      <button
                        onClick={() => onViewScan(scan.id || scan.scan_id)}
                        title="Charger dans le Dashboard"
                        className="text-blue-600 hover:text-blue-900 transition-colors"
                      >
                        <Eye className="w-5 h-5" />
                      </button>

                      {/* Bouton Supprimer Ligne */}
                      <button
                        onClick={() => handleDelete(scan.id || scan.scan_id)}
                        title="Supprimer ce scan"
                        className="text-red-400 hover:text-red-600 transition-colors"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Contrôles de Pagination */}
          <div className="flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6 mt-4">
            <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700">
                  Affichage de <span className="font-medium">{indexOfFirstItem + 1}</span> à <span className="font-medium">{Math.min(indexOfLastItem, scanHistory.length)}</span> sur <span className="font-medium">{scanHistory.length}</span> résultats
                </p>
              </div>
              <div>
                <nav className="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
                  <button
                    onClick={prevPage}
                    disabled={currentPage === 1}
                    className="relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50"
                  >
                    <ChevronLeft className="h-5 w-5" aria-hidden="true" />
                  </button>
                  <span className="relative inline-flex items-center px-4 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300 focus:outline-offset-0">
                    {currentPage} / {totalPages}
                  </span>
                  <button
                    onClick={nextPage}
                    disabled={currentPage === totalPages}
                    className="relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50"
                  >
                    <ChevronRight className="h-5 w-5" aria-hidden="true" />
                  </button>
                </nav>
              </div>
            </div>
          </div>
        </>
      ) : (
        <div className="text-center py-12">
          <AlertTriangle className="mx-auto h-12 w-12 text-gray-300" />
          <h3 className="mt-2 text-sm font-semibold text-gray-900">Aucun historique</h3>
          <p className="mt-1 text-sm text-gray-500">Lancez un scan pour voir apparaître des résultats ici.</p>
        </div>
      )}
    </div>
  );
}