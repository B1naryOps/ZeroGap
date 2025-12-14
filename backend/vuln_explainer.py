import json
import os
import re

# 1. Initialisation de la variable globale (en MAJUSCULES pour l'import)
VULN_DB = {}

# 2. Chargement automatique au démarrage
try:
    # Chemin absolu sûr
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "vuln_db.json")
    
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r", encoding="utf-8") as f:
            VULN_DB = json.load(f)
        print(f"[INFO] VULN_DB chargée : {len(VULN_DB)} entrées.")
        # print("Keys:", list(VULN_DB.keys())) # Décommenter pour debug
    else:
        print(f"[WARN] Fichier introuvable : {DB_PATH}")
        VULN_DB = {}

except Exception as e:
    print(f"[ERREUR] Échec chargement vuln_db.json : {e}")
    VULN_DB = {}


def normalize(text):
    if not text:
        return ""
    text = text.lower()
    # remove punctuation except letters/numbers -> convert to spaces
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return text.strip()

def explain_vulnerability(vuln_name: str):
    """
    Retourne un dict standardisé (title, summary, details, remediation, remediation_short, examples).
    """
    # print("[DEBUG] explain_vulnerability input:", vuln_name)
    name = (vuln_name or "").lower()

    keyword_map = {
        "x-content-type-options": "x_content_type_options_missing",
        "x content type options": "x_content_type_options_missing",
        "strict-transport-security": "strict_transport_security_missing",
        "hsts": "strict_transport_security_missing",
        "x-frame-options": "x_frame_options_missing",
        "x frame options": "x_frame_options_missing",
        "reflected xss": "reflected_xss",
        "sql injection": "sql_injection",
    }

    # 1. Try keywords
    for keyword, db_key in keyword_map.items():
        if keyword in name:
            # print("[MATCH] using keyword:", keyword, "->", db_key)
            item = VULN_DB.get(db_key) # Utilisation de VULN_DB (Majuscules)
            if item:
                return format_response(item, db_key)
            break

    # 2. Loose matching by keys/titles
    # Check title contains
    for key, item in VULN_DB.items():
        title = (item.get("title") or "").lower()
        if title and title in name:
            # print("[MATCH] by title ->", key)
            return format_response(item, key)

    # Check key name contains in input
    for key, item in VULN_DB.items():
        if key.replace("_", " ") in name:
            # print("[MATCH] by key ->", key)
            return format_response(item, key)

    # Fallback (not found)
    # print("[NO MATCH] returning fallback for:", vuln_name)
    return {
        "title": vuln_name or "Inconnue",
        "summary": "Aucune correspondance trouvée dans la base.",
        "details": "Aucune donnée technique disponible.",
        "remediation": "Aucune recommandation disponible.",
        "remediation_short": "Consultez les logs serveur.",
        "examples": {}
    }

def format_response(item, key):
    """Helper pour formater la réponse de manière cohérente"""
    return {
        "title": item.get("title") or key,
        "summary": item.get("for_humans") or item.get("summary") or item.get("description") or "",
        "details": item.get("for_experts") or item.get("technical_description") or "",
        "remediation": item.get("remediation") or item.get("solution") or item.get("remediation_short") or "",
        "remediation_short": item.get("remediation_short") or item.get("remediation") or item.get("quick_fix") or "",
        "examples": item.get("examples") or {}
    }