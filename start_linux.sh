#!/bin/bash

# Fonction pour nettoyer les processus en quittant (Ctrl+C)
cleanup() {
    echo ""
    echo "🛑 Arrêt de ZeroGap..."
    # Tue les processus enfants (le backend lancé en background)
    kill $(jobs -p) 2>/dev/null
    exit
}

# Intercepte le signal de sortie
trap cleanup SIGINT SIGTERM EXIT

echo "==================================================="
echo "           LANCEMENT DE ZEROGAP (LINUX/MAC)"
echo "==================================================="

# 1. VÉRIFICATION PYTHON
if ! command -v python3 &> /dev/null; then
    echo "[ERREUR] python3 n'est pas installé."
    exit 1
fi

# 2. CONFIGURATION BACKEND
echo ""
echo "[1/3] Configuration du Backend..."

if [ ! -d "venv" ]; then
    echo "Création du venv..."
    python3 -m venv venv
fi

source venv/bin/activate

# Installation des dépendances
if [ -f "backend/requirements.txt" ]; then
    pip install -r backend/requirements.txt > /dev/null
elif [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > /dev/null
else
    echo "[ATTENTION] requirements.txt introuvable."
fi

# 3. LANCEMENT API (EN ARRIÈRE PLAN)
echo "[2/3] Démarrage du serveur Python Flask..."
# On se déplace dans backend, on lance, et on revient (& pour background)
(cd backend && python3 api_flask.py) &
BACKEND_PID=$!

# Attendre un peu que le serveur démarre
sleep 3

# 4. CONFIGURATION FRONTEND
echo "[3/3] Configuration du Frontend..."

if ! command -v npm &> /dev/null; then
    echo "[ERREUR] npm n'est pas installé. Installez NodeJS."
    kill $BACKEND_PID
    exit 1
fi

if [ -d "frontend" ]; then
    cd frontend
    
    if [ ! -d "node_modules" ]; then
        echo "Installation des dépendances React..."
        npm install
    fi
    
    echo "Lancement de l'interface React..."
    npm start
else
    echo "[ERREUR] Dossier 'frontend' introuvable !"
    kill $BACKEND_PID
    exit 1
fi

# Garder le script actif pour que le trap fonctionne
wait