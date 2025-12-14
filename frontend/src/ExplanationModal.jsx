import { useEffect, useState } from "react";

export default function ExplanationModal({ isOpen, onClose, vuln }) {
  const [activeTab, setActiveTab] = useState("summary");

  if (!isOpen || !vuln) return null;

  // Sécurisation des champs pour éviter les undefined
  const title = vuln.title || "Titre non disponible";
  const summary = vuln.summary || "Aucun résumé disponible.";
  const details = vuln.details || "Aucun détail technique fourni.";
  const remediation = vuln.remediation_short || "Aucune solution fournie.";

  // Fonction copier dans le presse-papiers
  const copyToClipboard = () => {
    const text = `🔐 ${title}\n\nRésumé :\n${summary}\n\nDétails techniques :\n${details}\n\nCorrection rapide :\n${remediation}`;
    navigator.clipboard.writeText(text);
    alert("📋 Contenu copié !");
  };

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        background: "rgba(0,0,0,0.55)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 9999,
        backdropFilter: "blur(3px)",
      }}
    >
      <div
        style={{
          background: "#fff",
          borderRadius: "18px",
          width: "900px",
          maxWidth: "95vw",
          maxHeight: "85vh",
          overflowY: "auto",
          padding: "35px",
          boxShadow: "0 15px 45px rgba(0,0,0,0.30)",
          animation: "fadeIn 0.25s",
        }}
      >
        {/* HEADER */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h2 style={{ marginBottom: "10px", color: "#222", fontSize: "22px", fontWeight: "bold" }}>
            {title}
          </h2>

          <button
            onClick={onClose}
            style={{
              background: "transparent",
              border: "none",
              fontSize: "20px",
              cursor: "pointer",
              color: "#555",
            }}
          >
            ✖
          </button>
        </div>

        {/* TABS */}
        <div style={{ display: "flex", borderBottom: "1px solid #ddd", marginBottom: "15px" }}>
          {["summary", "details", "remediation"].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              style={{
                flex: 1,
                padding: "10px 0",
                borderBottom: activeTab === tab ? "3px solid #1d4ed8" : "3px solid transparent",
                background: "none",
                border: "none",
                cursor: "pointer",
                fontWeight: activeTab === tab ? "bold" : "normal",
                color: activeTab === tab ? "#1d4ed8" : "#555",
              }}
            >
              {tab === "summary" && "Résumé"}
              {tab === "details" && "Détails techniques"}
              {tab === "remediation" && "Correction rapide"}
            </button>
          ))}
        </div>

        {/* CONTENT */}
        <div style={{ lineHeight: "1.6", color: "#333", fontSize: "15px" }}>
          {activeTab === "summary" && <p>{summary}</p>}
          {activeTab === "details" && <p>{details}</p>}
          {activeTab === "remediation" && <p>{remediation}</p>}
        </div>

        {/* FOOTER BUTTONS */}
        <div
          style={{
            marginTop: "25px",
            display: "flex",
            justifyContent: "space-between",
          }}
        >
          <button
            onClick={copyToClipboard}
            style={{
              background: "#1d4ed8",
              color: "#fff",
              padding: "10px 20px",
              borderRadius: "8px",
              border: "none",
              cursor: "pointer",
              fontWeight: "bold",
            }}
          >
            📋 Copier
          </button>

          <button
            onClick={onClose}
            style={{
              background: "#d62828",
              color: "#fff",
              padding: "10px 20px",
              borderRadius: "8px",
              border: "none",
              cursor: "pointer",
              fontWeight: "bold",
            }}
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  );
}
