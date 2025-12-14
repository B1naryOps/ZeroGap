# 🛡️ ZeroGap - Scanner de Vulnérabilités Web (v2.0)

**ZeroGap** est un outil d'audit de sécurité web moderne combinant un backend performant en **Python (Flask)** et une interface utilisateur intuitive en **React.js**. Il permet d'analyser des sites web pour détecter des vulnérabilités critiques, vérifier la configuration serveur et générer des rapports détaillés pour les auditeurs et développeurs.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/backend-Python%20Flask-yellow.svg)
![React](https://img.shields.io/badge/frontend-React-cyan.svg)
![Status](https://img.shields.io/badge/status-stable-green.svg)

---

## 🚀 Fonctionnalités Principales

### 🔍 Moteur d'Analyse
*   **Scan Multi-threadé** : Architecture parallèle pour une exécution rapide.
*   **Détection des failles OWASP** :
    *   SQL Injection (SQLi)
    *   Cross-Site Scripting (Reflected XSS)
    *   Directory Traversal (LFI)
    *   Command Injection (RCE)
*   **Analyse d'Infrastructure** :
    *   Scan des ports ouverts (HTTP, SSH, MySQL, etc.).
    *   Vérification de la configuration SSL/TLS et validité des certificats.
    *   Identification du serveur et des technologies.
*   **Headers de Sécurité** : Vérification de HSTS, X-Frame-Options, CSP, etc.

### 📊 Tableau de Bord (Frontend)
*   **Suivi en temps réel** : Barre de progression et logs d'état.
*   **Score de Sécurité** : Note globale sur 100 calculée dynamiquement.
*   **Visualisation** : Graphiques circulaires par niveau de sévérité (Critique, Élevée, Moyenne, Faible).
*   **Module Éducatif** : Explications détaillées et solutions de remédiation intégrées pour chaque vulnérabilité détectée.
*   **Historique** : Sauvegarde locale des scans passés avec possibilité de relecture.

### 📝 Rapports
*   Exportation des résultats en **JSON** (données brutes) et **HTML** (rapport visuel).
*   Résumé exécutif généré automatiquement.

---

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir installé les outils suivants :

1.  **Git** : [Télécharger Git](https://git-scm.com/)
2.  **Python 3.8+** : [Télécharger Python](https://www.python.org/downloads/) (Cochez "Add to PATH" à l'installation).
3.  **Node.js & npm** : [Télécharger Node.js](https://nodejs.org/) (Version LTS recommandée).

---

## 📥 Installation & Démarrage

### 1. Cloner le projet
Ouvrez un terminal (ou l'invite de commande) et récupérez le code source :

```bash
git clone https://github.com/VOTRE_USERNAME/ZeroGap.git
cd ZeroGap
