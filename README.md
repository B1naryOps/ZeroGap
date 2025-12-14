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
git clone https://github.com/B1naryOps/ZeroGap.git
cd ZeroGap
```
*(Remplacez l'URL par le lien de votre dépôt si vous l'avez hébergé)*

### 2. Démarrage Automatisé (Recommandé)

Le projet inclut des scripts "tout-en-un" qui installent les dépendances (Python & Node) et lancent l'application.

#### 🖥️ Sous Windows
Double-cliquez simplement sur le fichier :
`start_windows.bat`

#### 🐧 Sous Linux / macOS
Rendez le script exécutable et lancez-le :
```bash
chmod +x start_linux.sh
./start_linux.sh
```

Une fois le lancement terminé, votre navigateur s'ouvrira automatiquement sur : **http://localhost:3000**

---

## 🛠️ Installation Manuelle (Alternative)

Si les scripts automatiques ne fonctionnent pas dans votre environnement, procédez étape par étape :

### A. Configuration du Backend
```bash
cd backend

# Création de l'environnement virtuel
python -m venv venv

# Activation
# Windows :
venv\Scripts\activate
# Linux/Mac :
source venv/bin/activate

# Installation des dépendances
pip install -r requirements.txt

# Lancement du serveur API
python api_flask.py
```
*L'API tournera sur http://localhost:5000*

### B. Configuration du Frontend
Ouvrez un **nouveau terminal** à la racine du projet :

```bash
cd frontend

# Installation des paquets Node
npm install

# Lancement de l'interface
npm start
```
*Le dashboard tournera sur http://localhost:3000*

---

## 📂 Structure du Projet

```text
ZeroGap/
│
├── backend/                   # API Flask & Cœur du scanner
│   ├── api_flask.py           # Point d'entrée de l'API
│   ├── scanner_vulnerabilites_v2.py # Logique de scan & Crawling
│   ├── innovations_module.py  # Modules (Ports, SSL, Score)
│   ├── vuln_explainer.py      # Moteur d'explication pédagogique
│   ├── vuln_db.json           # Base de données des explications
│   └── requirements.txt       # Dépendances Python
│
├── frontend/                  # Interface React
│   ├── src/
│   │   ├── components/        # Composants (Graphiques, Tableaux, Cartes)
│   │   ├── pages/             # Pages (Dashboard, Historique)
│   │   └── App.js             # Logique principale frontend
│   └── package.json           # Dépendances React
│
├── scans/                     # Dossier de stockage des rapports générés
├── start_windows.bat          # Script de lancement Windows
├── start_linux.sh             # Script de lancement Linux
└── README.md                  # Documentation
```

---

## ⚠️ Avertissement Légal

**L'utilisation de ce scanner de vulnérabilités doit se faire uniquement sur des systèmes que vous possédez ou pour lesquels vous avez une autorisation écrite explicite.**

Les auteurs déclinent toute responsabilité en cas de dommages causés ou de mauvaise utilisation de cet outil. L'utilisation de scanners de sécurité sur des cibles non autorisées est illégale et passible de poursuites pénales.

Utilisez **ZeroGap** pour sécuriser vos propres applications ou dans des environnements de test dédiés (ex: DVWA, bWAPP, localhost).

---

## 👥 Équipe Projet

Ce projet a été conçu et réalisé par une équipe d'ingénieurs en cybersécurité en formation :

*   **BARIKI Yendouparou Wilson (CG)** - *Ingénieur Cybersécurité en Formation*
*   **ABAKTA Haana Camille** - *Ingénieur Cybersécurité en Formation*
*   **MALOU Essozimna Wilfried** - *Ingénieur Cybersécurité en Formation*

---

## 🐛 Dépannage Courant

*   **Erreur `utf-8 codec` lors de l'install Python** : Vérifiez que vos fichiers textes ne contiennent pas de caractères spéciaux corrompus.
*   **`npm` non reconnu** : Assurez-vous d'avoir installé Node.js et redémarré votre terminal.
*   **Port 5000 déjà utilisé** : Si le backend ne démarre pas, vérifiez qu'une autre instance de Python ne tourne pas déjà. Vous pouvez changer le port dans `backend/api_flask.py`.
*   **Scan bloqué** : Certains pare-feux (WAF) peuvent bloquer les requêtes du scanner. Testez sur un environnement local ou autorisé.

---

## 🤝 Crédits Techniques

Projet développé avec :
*   [Flask](https://flask.palletsprojects.com/)
*   [React](https://reactjs.org/)
*   [Tailwind CSS](https://tailwindcss.com/)
*   [Lucide React](https://lucide.dev/) (Icônes)
```
