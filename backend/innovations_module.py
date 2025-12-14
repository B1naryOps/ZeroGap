# ---- innovations_module.py (patch) ----
import socket
import ssl
import requests
from urllib.parse import urlparse
import ssl, socket
from urllib.parse import urlparse
from datetime import datetime

def scan_basic_ports(target):
    """
    Scanne rapidement les ports les plus courants (HTTP, HTTPS, SSH, FTP, etc.)
    Retourne une liste de ports ouverts.
    """
    common_ports = {
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        110: "POP3",
        143: "IMAP",
        443: "HTTPS",
        3306: "MySQL",
        8080: "HTTP-ALT"
    }

    open_ports = []
    target_clean = target.replace("https://", "").replace("http://", "").split("/")[0]

    print(f"[+] Scan rapide des ports sur {target_clean}...")

    for port, service in common_ports.items():
        try:
            with socket.create_connection((target_clean, port), timeout=3):
                open_ports.append(f"{port} ({service})")
        except (socket.timeout, ConnectionRefusedError, OSError):
            continue

    return open_ports


def check_ssl_tls_configuration(target):
    """
    Vérifie la validité et les informations du certificat SSL/TLS du site.
    Retourne un dictionnaire avec les résultats.
    """
    target_clean = target.replace("https://", "").replace("http://", "").split("/")[0]
    ctx = ssl.create_default_context()

    try:
        with ctx.wrap_socket(socket.socket(), server_hostname=target_clean) as s:
            s.settimeout(5)
            s.connect((target_clean, 443))
            cert = s.getpeercert()

        issuer = dict(x[0] for x in cert.get('issuer', []))
        issued_by = issuer.get('organizationName', 'Inconnu')
        expiry = cert.get('notAfter', 'N/A')

        return {
            "valid": True,
            "issuer": issued_by,
            "expires": expiry
        }
    except ssl.SSLError:
        return {"valid": False, "issuer": "Erreur SSL", "expires": "N/A"}
    except Exception:
        return {"valid": False, "issuer": "Inconnu", "expires": "N/A"}


def check_server_version(target):
    """
    Vérifie la version du serveur HTTP via les en-têtes de réponse.
    """
    try:
        response = requests.head(target, timeout=5)
        server_header = response.headers.get("Server", "Non détecté")
        return server_header
    except Exception:
        return "Non détecté"


def calculate_security_score(vulnerabilities, open_ports=None, ssl_info=None, server_info=None):
    """
    Calcule un score simple sur 100.
    Arguments :
      - vulnerabilities : liste de dicts { 'severity': 'LOW'|'MEDIUM'|'HIGH'|'CRITICAL', ... }
      - open_ports : liste (ou None) des ports ouverts détectés
      - ssl_info : dict (ou None) contenant 'valid' boolean
      - server_info : dict (ou None) informations serveur (optionnel)
    Retour : int score 0..100
    """
    if open_ports is None:
        open_ports = []
    if ssl_info is None:
        ssl_info = {}
    if server_info is None:
        server_info = {}

    score = 100

    # pénalités selon les vulnérabilités
    for v in vulnerabilities or []:
        sev = (v.get('severity') or '').upper()
        if sev == "CRITICAL":
            score -= 40
        elif sev == "HIGH":
            score -= 25
        elif sev == "MEDIUM":
            score -= 10
        elif sev == "LOW":
            score -= 5

    # pénalité pour ports ouverts (faible)
    try:
        score -= len(open_ports) * 2
    except Exception:
        pass

    # pénalité si SSL invalide / absent
    if not ssl_info.get("valid", False):
        score -= 15

    # ajustement selon server_info (optionnel)
    server_str = ""
    try:
        server_str = server_info.get("Server") if isinstance(server_info, dict) else str(server_info)
    except Exception:
        server_str = ""

    # exemples d'ajustement (facultatif)
    if server_str and ("apache/2.2" in server_str.lower() or "apache/2.0" in server_str.lower()):
        score -= 5

    # borne
    if score < 0:
        score = 0
    if score > 100:
        score = 100

    return int(score)




def generate_executive_summary(target_url, vulnerabilities, open_ports, ssl_info, score):
    """
    Crée un résumé texte simple et lisible.
    """
    ports_text = ", ".join([f"{svc} ({prt})" for prt, svc in open_ports]) if open_ports else "Aucun"
    issuer = "N/A"
    expiry = "N/A"
    if isinstance(ssl_info.get("issuer"), dict):
        issuer = ssl_info["issuer"].get("organizationName") or ssl_info["issuer"].get("O") or str(ssl_info["issuer"])
    elif ssl_info.get("issuer"):
        issuer = str(ssl_info.get("issuer"))
    if ssl_info.get("expiry_date"):
        expiry = ssl_info.get("expiry_date")
    vulns_count = len(vulnerabilities) if vulnerabilities else 0

    summary = f"""=== Résumé du Scan de Sécurité ===
Cible : {target_url}
Score global : {score}/100

Ports ouverts détectés :
{ports_text}

SSL/TLS :
- Certificat valide : {ssl_info.get('valid', False)}
- Émetteur : {issuer}
- Expiration : {expiry}

Vulnérabilités détectées :
{vulns_count} problème(s) trouvé(s)
"""
    return summary
# ---- fin du patch ----
