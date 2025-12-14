import React, { useState, useEffect, useCallback } from 'react';
// Composants locaux
import Navbar from './components/Navbar';
import QuickScan from './components/QuickScan';
import ResultSummary from './components/ResultSummary';
import SeverityStats from './components/SeverityStats';
import VulnerabilityCards from './components/VulnerabilityCards';
import VulnerabilityTable from './components/VulnerabilityTable';
import HistoryPreview from './components/HistoryPreview';
import StatisticsPanel from './components/StatisticsPanel';
import DebugPanel from './components/DebugPanel';
import Notification from './components/Notification';

// Autres imports existants
import ExplanationModal from "./ExplanationModal";
import HistoryPage from "./pages/HistoryPage";

const API_URL = 'http://localhost:5000/api';

export default function VulnerabilityScanner() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [url, setUrl] = useState('');
  const [threads, setThreads] = useState(5);
  const [currentScan, setCurrentScan] = useState(null);
  const [scanHistory, setScanHistory] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [notification, setNotification] = useState(null);
  const [debugMode, setDebugMode] = useState(false);

  const [modalOpen, setModalOpen] = useState(false);
  const [modalData, setModalData] = useState(null);

  // --- Gestion du Modal et Explications ---
  const askExplain = async (vulnText) => {
    try {
      // Note: Assure-toi que l'URL est correcte (localhost:5000)
      const response = await fetch(`${API_URL}/explain`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ vuln_text: vulnText }),
      });

      const data = await response.json();

      if (data.error) {
        setModalData({
          title: "Erreur",
          summary: data.error,
          remediation_short: "",
        });
        setModalOpen(true);
        return;
      }

      const result = data.result;
      setModalData({
        title: result.title || "Sans titre",
        summary: result.summary || "Aucun résumé disponible",
        remediation_short: result.remediation_short || "Aucune solution fournie",
      });
      setModalOpen(true);

    } catch (err) {
      console.error(err);
      setModalData({
        title: "Erreur connexion",
        summary: "Impossible de contacter le backend.",
        remediation_short: "",
      });
      setModalOpen(true);
    }
  };

  // --- Chargement des Données ---
  const loadHistory = async () => {
    try {
      console.log('[DEBUG] Chargement de l\'historique...');
      const response = await fetch(`${API_URL}/history?limit=10`);
      const data = await response.json();
      console.log('[DEBUG] Historique reçu:', data);
      setScanHistory(data.scans || []);
    } catch (error) {
      console.error('Erreur lors du chargement de l\'historique:', error);
      setNotification({
        type: 'error',
        message: 'Erreur de chargement de l\'historique'
      });
    }
  };

  const loadStatistics = async () => {
    try {
      const response = await fetch(`${API_URL}/stats`);
      const data = await response.json();
      setStatistics(data);
    } catch (error) {
      console.error('Erreur lors du chargement des statistiques:', error);
    }
  };

  // Charger au démarrage
  useEffect(() => {
    loadHistory();
    loadStatistics();
  }, []);

  // --- Gestion du Scan ---
  const fetchScanStatus = useCallback(async (scanId) => {
    try {
      const response = await fetch(`${API_URL}/scan/${scanId}`);
      const data = await response.json();
      
      console.log('Statut du scan:', data);
      
      const wasRunning = currentScan?.status === 'running';
      const isNowCompleted = data.status === 'completed';
      
      setCurrentScan(data);
      
      if (wasRunning && isNowCompleted) {
        setNotification({
          type: 'success',
          message: `Scan terminé ! ${data.total_vulnerabilities} vulnérabilités détectées.`
        });
        setTimeout(() => setNotification(null), 5000);
      }
      
      if (data.status === 'completed' || data.status === 'failed') {
        setTimeout(() => {
          loadHistory();
          loadStatistics();
        }, 500);
      }
    } catch (error) {
      console.error('Erreur lors de la récupération du statut:', error);
    }
  }, [currentScan]);

  // Polling
  useEffect(() => {
    if (currentScan && (currentScan.status === 'running' || currentScan.status === 'starting')) {
      const interval = setInterval(() => {
        fetchScanStatus(currentScan.scan_id);
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [currentScan, fetchScanStatus]);

  const handleScan = async () => {
    if (!url) {
      alert('Veuillez entrer une URL');
      return;
    }

    try {
      const response = await fetch(`${API_URL}/scan/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url, threads: threads })
      });

      const data = await response.json();
      
      if (response.ok) {
        setCurrentScan({
          scan_id: data.scan_id,
          url: data.url,
          status: 'running',
          progress: 0,
          vulnerabilities: [],
          total_vulnerabilities: 0
        });
      } else {
        alert('Erreur: ' + data.error);
      }
    } catch (error) {
      alert('Erreur de connexion à l\'API: ' + error.message);
    }
  };

  const downloadReport = async (scanId, format = 'html') => {
    try {
      const endpoint = format === 'json' ? 'report/json' : 'report';
      window.open(`${API_URL}/scan/${scanId}/${endpoint}`, '_blank');
    } catch (error) {
      alert('Erreur lors du téléchargement du rapport');
    }
  };

  const handleViewScan = (scanId) => {
    fetchScanStatus(scanId);
    setActiveTab('dashboard');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // --- Rendu ---
  return (
    <div className="min-h-screen bg-gray-50">
      
      {/* Notification Toast */}
      <Notification notification={notification} onClose={() => setNotification(null)} />

      {/* Modal Explication (Si ton composant ExplanationModal est compatible avec modalData, utilise-le. 
          Sinon, voici l'implémentation inline conservée pour compatibilité) */}
      {modalOpen && modalData && (
        <div style={{ position: "fixed", top: 0, left: 0, width: "100%", height: "100%", background: "rgba(0,0,0,0.6)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 9999, padding: "20px" }}>
          <div style={{ background: "#fff", borderRadius: "10px", width: "500px", maxWidth: "100%", padding: "25px", boxShadow: "0 10px 30px rgba(0,0,0,0.3)", animation: "fadeIn 0.2s" }}>
            <h2 style={{ marginBottom: "10px", color: "#222" }}>{modalData.title}</h2>
            <p style={{ marginBottom: "15px", color: "#444" }}>{modalData.summary}</p>
            <h3 style={{ marginTop: "20px", marginBottom: "10px", color: "#222" }}>🔧 Correction rapide</h3>
            <p style={{ marginBottom: "20px", color: "#555" }}>{modalData.remediation_short}</p>
            <button onClick={() => setModalOpen(false)} style={{ background: "#d62828", color: "#fff", border: "none", padding: "10px 20px", borderRadius: "8px", cursor: "pointer", fontWeight: "bold" }}>Fermer</button>
          </div>
        </div>
      )}
      
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Affichage conditionnel : Dashboard ou Historique */}
        {activeTab === 'dashboard' ? (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              
              <QuickScan 
                url={url} 
                setUrl={setUrl} 
                threads={threads} 
                setThreads={setThreads} 
                handleScan={handleScan} 
                currentScan={currentScan} 
              />

              <ResultSummary 
                currentScan={currentScan} 
                downloadReport={downloadReport} 
              />

              <SeverityStats 
                currentScan={currentScan} 
              />
            </div>

            <VulnerabilityCards 
              vulnerabilities={currentScan?.vulnerabilities} 
              askExplain={askExplain} 
            />

            <VulnerabilityTable 
              vulnerabilities={currentScan?.vulnerabilities} 
              askExplain={askExplain} 
            />

            <HistoryPreview 
              scanHistory={scanHistory} 
              loadHistory={loadHistory} 
              fetchScanStatus={fetchScanStatus} 
            />

            <StatisticsPanel 
              statistics={statistics} 
            />
            
            <DebugPanel 
              debugMode={debugMode}
              setDebugMode={setDebugMode}
              API_URL={API_URL}
              currentScan={currentScan}
              scanHistory={scanHistory}
              statistics={statistics}
              loadHistory={loadHistory}
              loadStatistics={loadStatistics}
            />
          </>
        ) : (
          /* Page Historique Complète */
          <HistoryPage 
              scanHistory={scanHistory} // Vient du state de App.js
              loadHistory={loadHistory} // Fonction de App.js pour rafraichir
              onViewScan={handleViewScan} // Fonction de App.js pour voir le détail
              API_URL={API_URL} // Constante API
          />
        )}

      </main>
    </div>
  );
}