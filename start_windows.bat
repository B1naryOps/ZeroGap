@echo off
title ZeroGap Launcher
color 0A
echo ===================================================
echo           LANCEMENT DE ZEROGAP (WINDOWS)
echo ===================================================

:: 1. VERIFICATION PYTHON
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python n'est pas installe.
    pause
    exit /b
)

:: 2. CONFIGURATION BACKEND
echo.
echo [1/3] Configuration du Backend...

if not exist venv (
    echo Creation de l'environnement virtuel...
    python -m venv venv
)

call venv\Scripts\activate

:: Installation des dépendances (cherche dans backend/ ou racine)
if exist "backend\requirements.txt" (
    pip install -r backend\requirements.txt >nul
) else if exist "requirements.txt" (
    pip install -r requirements.txt >nul
) else (
    echo [ATTENTION] requirements.txt introuvable.
)

:: 3. LANCEMENT API (DANS UNE NOUVELLE FENETRE)
echo [2/3] Démarrage du serveur Python Flask...
:: On rentre dans backend avant de lancer pour éviter les erreurs de chemin
start "ZeroGap API" cmd /k "call venv\Scripts\activate && cd backend && python api_flask.py"

:: 4. CONFIGURATION FRONTEND
echo [3/3] Configuration du Frontend...

:: Vérification Node
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] NodeJS/NPM n'est pas installe.
    echo Veuillez installer NodeJS : https://nodejs.org/
    pause
    exit /b
)

if exist "frontend" (
    cd frontend
    if not exist node_modules (
        echo Installation des dependances React...
        call npm install
    )
    echo Lancement de l'interface React...
    npm start
) else (
    echo [ERREUR] Dossier 'frontend' introuvable !
    pause
)