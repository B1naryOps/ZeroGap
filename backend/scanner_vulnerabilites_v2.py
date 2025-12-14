import json
import os
import re
import time
import urllib.parse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

"""from innovations_module import (
    scan_basic_ports,
    check_ssl_tls_configuration,
    check_server_version,
    calculate_security_score,
    generate_executive_summary
)"""



try:
    import requests
except ImportError:
    print("Installation de requests en cours...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

# === Fonctions d'analyse avancée (anciennement dans innovations_module) ===
import socket, ssl, requests

def scan_basic_ports(target):
    """Scanne quelques ports courants."""
    ports = [21, 22, 25, 80, 110, 143, 443, 3306]
    open_ports = []
    try:
        host = target.replace("http://", "").replace("https://", "").split("/")[0]
        for port in ports:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            if s.connect_ex((host, port)) == 0:
                open_ports.append(port)
            s.close()
    except Exception:
        pass
    return open_ports

def check_ssl_tls_configuration(target):
    """Récupère les infos SSL/TLS du site."""
    info = {"valid": "Inconnu", "issuer": "N/A", "expiration": "N/A"}
    try:
        hostname = target.replace("https://", "").replace("http://", "").split("/")[0]
        context = ssl.create_default_context()
        with context.wrap_socket(socket.socket(), server_hostname=hostname) as s:
            s.settimeout(3)
            s.connect((hostname, 443))
            cert = s.getpeercert()
            info["issuer"] = dict(x[0] for x in cert["issuer"])["organizationName"]
            info["expiration"] = cert["notAfter"]
            info["valid"] = "Oui"
    except Exception:
        pass
    return info

def check_server_version(target):
    """Détecte le serveur HTTP via les en-têtes de réponse."""
    try:
        r = requests.head(target, timeout=3)
        return {"server": r.headers.get("Server", "Non détecté")}
    except Exception:
        return {"server": "Non détecté"}

def calculate_security_score(vulnerabilities, open_ports, ssl_info, server_info):
    """Calcule un score global de sécurité (0–100)."""
    score = 100
    for v in vulnerabilities:
        sev = v["severity"].upper()
        if sev == "CRITICAL":
            score -= 40
        elif sev == "HIGH":
            score -= 25
        elif sev == "MEDIUM":
            score -= 15
        elif sev == "LOW":
            score -= 5
    score -= len(open_ports) * 5
    if ssl_info.get("valid") != "Oui":
        score -= 10
    return max(0, min(100, score))

def generate_executive_summary(target_url, vulnerabilities, open_ports, ssl_info, score):
    """Résumé textuel du scan."""
    summary = [
        f"Rapport exécutif pour {target_url}",
        f"Score global : {score}/100",
        f"Ports ouverts détectés : {', '.join(map(str, open_ports)) if open_ports else 'Aucun'}",
        f"SSL valide : {ssl_info.get('valid', 'Inconnu')}",
        f"Émetteur du certificat : {ssl_info.get('issuer', 'N/A')}",
        "",
        "Vulnérabilités détectées :"
    ]
    if not vulnerabilities:
        summary.append(" - Aucune vulnérabilité détectée.")
    else:
        for v in vulnerabilities:
            summary.append(f" - {v['type']} ({v['severity']}) : {v['description']}")
    return "\n".join(summary)


class VulnerabilityScannerV2:
    def __init__(self, target_url, max_workers=5, output_dir=None):
        self.target_url = target_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.vulnerabilities = []
        self.crawled_urls = set()
        self.forms = []
        self.max_workers = max_workers
        self.start_time = None
        self.security_score = 0
        self.ports_info = []
        self.ssl_info = {}
        self.server_info = {}
        self.output_dir = output_dir

    def create_report_directory(self):
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)
            return self.output_dir
        current_file_path = os.path.abspath(__file__)
        backend_dir = os.path.dirname(current_file_path)
        project_root = os.path.dirname(backend_dir) 
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dir_name = f"scan_results_v2_{timestamp}"
        
        base_dir = os.path.join(project_root, "scans")
        os.makedirs(base_dir, exist_ok=True)
        
        full_path = os.path.join(base_dir, dir_name)
        os.makedirs(full_path, exist_ok=True)
        return full_path

        
    def banner(self):
        print("=" * 60)
        print("      SCANNER DE VULNERABILITES WEB - VERSION 2.0")
        print("=" * 60)
        print(f"Cible: {self.target_url}")
        print(f"Debut du scan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Threads paralleles: {self.max_workers}")
        print("=" * 60)
        
    def test_vulnerability(self, url, vuln_type):
        results = []
        
        if vuln_type == 'sql':
            sql_payloads = ["' OR '1'='1", "' UNION SELECT NULL--", "1' AND 1=1--"]
            error_patterns = [
                r"SQL syntax.*MySQL", r"Warning.*mysql_.*", 
                r"PostgreSQL.*ERROR", r"ORA-[0-9]{4}"
            ]
            
            for payload in sql_payloads:
                try:
                    test_url = f"{url}?id={payload}"
                    response = self.session.get(test_url, timeout=3)
                    
                    for pattern in error_patterns:
                        if re.search(pattern, response.text, re.IGNORECASE):
                            results.append({
                                'type': 'SQL Injection',
                                'url': url,
                                'payload': payload,
                                'severity': 'HIGH',
                                'description': 'Erreur SQL detectee dans la reponse'
                            })
                            break
                except:
                    continue
                    
        elif vuln_type == 'xss':
            xss_payloads = [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>"
            ]
            
            for payload in xss_payloads:
                try:
                    test_url = f"{url}?q={urllib.parse.quote(payload)}"
                    response = self.session.get(test_url, timeout=3)
                    
                    if payload in response.text:
                        results.append({
                            'type': 'Cross-Site Scripting (XSS)',
                            'url': url,
                            'payload': payload,
                            'severity': 'MEDIUM',
                            'description': 'Script injecte detecte dans la reponse'
                        })
                        break
                except:
                    continue
                    
        elif vuln_type == 'traversal':
            traversal_payloads = ["../../../etc/passwd", "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts"]
            
            for payload in traversal_payloads:
                try:
                    test_url = f"{url}?file={payload}"
                    response = self.session.get(test_url, timeout=3)
                    
                    if "root:" in response.text or "[drivers]" in response.text:
                        results.append({
                            'type': 'Directory Traversal',
                            'url': url,
                            'payload': payload,
                            'severity': 'HIGH',
                            'description': 'Acces non autorise aux fichiers systeme detecte'
                        })
                        break
                except:
                    continue
                    
        elif vuln_type == 'command':
            cmd_payloads = ["; ls", "| whoami", "$(id)"]
            
            for payload in cmd_payloads:
                try:
                    test_url = f"{url}?cmd={urllib.parse.quote(payload)}"
                    response = self.session.get(test_url, timeout=3)
                    
                    if any(ind in response.text for ind in ['uid=', 'gid=', 'root:']):
                        results.append({
                            'type': 'Command Injection',
                            'url': url,
                            'payload': payload,
                            'severity': 'CRITICAL',
                            'description': 'Execution de commandes systeme detectee'
                        })
                        break
                except:
                    continue
                    
        return results
        
    def check_security_headers(self, url):
        try:
            response = self.session.head(url, timeout=3)
            headers = response.headers
            
            missing_headers = []
            security_headers = {
                'X-Frame-Options': 'Protection contre le clickjacking',
                'X-Content-Type-Options': 'Protection contre le MIME sniffing',
                'Strict-Transport-Security': 'Force HTTPS'
            }
            
            for header, description in security_headers.items():
                if header not in headers:
                    missing_headers.append({
                        'type': 'Missing Security Header',
                        'url': url,
                        'payload': header,
                        'severity': 'LOW',
                        'description': f'En-tete de securite manquant: {header}'
                    })
                    
            return missing_headers
        except:
            return []
            
    def crawl_website(self, start_url, max_depth=2, current_depth=0):
        if current_depth >= max_depth or start_url in self.crawled_urls:
            return
            
        self.crawled_urls.add(start_url)
        print(f"Exploration: {start_url}")
        
        try:
            response = self.session.get(start_url, timeout=5)
            
            links = re.findall(r'href=[\'"]?([^\'" >]+)', response.text)
            for link in links[:8]:
                if link.startswith('http'):
                    full_url = link
                elif link.startswith('/'):
                    full_url = f"{self.target_url}{link}"
                else:
                    full_url = f"{start_url.rstrip('/')}/{link}"
                    
                if self.target_url in full_url and full_url not in self.crawled_urls:
                    self.crawl_website(full_url, max_depth, current_depth + 1)
                    
            forms = re.findall(r'<form[^>]*action=[\'"]?([^\'" >]*)[\'"]?[^>]*>', response.text, re.IGNORECASE)
            for form_action in forms:
                if form_action:
                    if form_action.startswith('/'):
                        form_url = f"{self.target_url}{form_action}"
                    elif not form_action.startswith('http'):
                        form_url = f"{start_url.rstrip('/')}/{form_action}"
                    else:
                        form_url = form_action
                    self.forms.append(form_url)
        except:
            pass
            
    def scan_vulnerabilities_parallel(self):
        print("\n[+] Analyse des vulnerabilites avec execution parallele...")
        
        all_urls = list(self.crawled_urls) + self.forms
        total_urls = len(all_urls)
        vuln_types = ['sql', 'xss', 'traversal', 'command']
        
        tasks = []
        for url in all_urls:
            for vuln_type in vuln_types:
                tasks.append((url, vuln_type))
        
        completed = 0
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_task = {
                executor.submit(self.test_vulnerability, url, vuln_type): (url, vuln_type)
                for url, vuln_type in tasks
            }
            
            for future in as_completed(future_to_task):
                completed += 1
                if completed % 10 == 0:
                    progress = (completed / len(tasks)) * 100
                    print(f"[{completed}/{len(tasks)}] Progression: {progress:.1f}%")
                
                try:
                    results = future.result()
                    if results:
                        self.vulnerabilities.extend(results)
                except:
                    continue
        
        self.vulnerabilities.extend(self.check_security_headers(self.target_url))
        
    def generate_report(self):
        report_dir = self.create_report_directory()
        scan_duration = time.time() - self.start_time

    # === Étape 1 : Lancer les analyses avancées ===
        print("\n[+] Analyse avancée en cours...")

        try:
            self.ports_info = scan_basic_ports(self.target_url)
        except Exception as e:
            print(f"[!] Erreur lors du scan des ports : {e}")
            self.ports_info = []

        try:
            self.ssl_info = check_ssl_tls_configuration(self.target_url)
        except Exception as e:
            print(f"[!] Erreur SSL/TLS : {e}")
            self.ssl_info = {"valid": "Inconnu", "issuer": "N/A", "expiration": "N/A"}

        try:
            self.server_info = check_server_version(self.target_url)
        except Exception as e:
            print(f"[!] Erreur version serveur : {e}")
            self.server_info = {"server": "Non détecté"}

        try:
            self.security_score = calculate_security_score(
                self.vulnerabilities,
                self.ports_info,
                self.ssl_info,
                self.server_info
        )
        except Exception as e:
            print(f"[!] Erreur calcul score : {e}")
            self.security_score = 0

    # === Étape 2 : Génération du rapport JSON ===
        json_report = {
            "version": "2.0",
            "target": self.target_url,
            "scan_date": datetime.now().isoformat(),
            "scan_duration_seconds": round(scan_duration, 2),
            "total_vulnerabilities": len(self.vulnerabilities),
            "vulnerabilities": self.vulnerabilities,
            "crawled_urls": list(self.crawled_urls),
            "forms_found": self.forms,
            "performance": {
                "urls_scanned": len(self.crawled_urls),
                "threads_used": self.max_workers,
                "average_time_per_url": round(scan_duration / len(self.crawled_urls), 2)
                if self.crawled_urls else 0,
            },
            "advanced_analysis": {
                "open_ports": self.ports_info,
                "ssl_check": self.ssl_info,
                "server_info": self.server_info,
                "security_score": self.security_score,
            },
        }

        json_file = os.path.join(report_dir, "rapport_scan_v2.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_report, f, indent=2, ensure_ascii=False)

    # === Étape 3 : Génération du rapport HTML ===
        html_content = self.generate_html_report(scan_duration)
        html_file = os.path.join(report_dir, "rapport_scan_v2.html")
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"\n[+] Rapports générés dans: {report_dir}")
        print(f"    - Rapport JSON: {json_file}")
        print(f"    - Rapport HTML: {html_file}")

        return report_dir

        
    def generate_html_report(self, scan_duration):
        # Récupération sécurisée des données
        ports_info = getattr(self, 'ports_info', []) or []
        ssl_info = getattr(self, 'ssl_info', {}) or {}
        server_info = getattr(self, 'server_info', {}) or {}
        score = getattr(self, 'security_score', 0)
        
        # Stats par sévérité
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for v in self.vulnerabilities:
            s = v.get('severity', 'LOW').upper()
            if s in severity_counts:
                severity_counts[s] += 1

        # Couleur du score
        if score >= 80: score_class = 'score-good'
        elif score >= 50: score_class = 'score-warning'
        else: score_class = 'score-critical'

        # Construction du HTML
        html = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Audit de Sécurité - {self.target_url}</title>
            <style>
                :root {{
                    --bg-body: #f3f4f6;
                    --bg-card: #ffffff;
                    --text-main: #1f2937;
                    --text-muted: #6b7280;
                    --primary: #2563eb;
                    --critical: #dc2626;
                    --high: #ea580c;
                    --medium: #ca8a04;
                    --low: #16a34a;
                    --good: #16a34a;
                }}
                * {{ box-sizing: border-box; margin: 0; padding: 0; }}
                body {{ font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: var(--bg-body); color: var(--text-main); line-height: 1.6; padding-bottom: 50px; }}
                
                /* HEADER */
                .header {{ background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; padding: 40px 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
                .header-content {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px; }}
                .brand h1 {{ font-size: 1.8rem; font-weight: 700; margin-bottom: 5px; }}
                .brand p {{ opacity: 0.9; font-size: 0.9rem; }}
                .meta-badge {{ background: rgba(255,255,255,0.2); padding: 5px 12px; border-radius: 20px; font-size: 0.85rem; backdrop-filter: blur(4px); }}

                /* SCORE SECTION */
                .score-section {{ margin-top: -30px; display: grid; grid-template-columns: 1fr 2fr; gap: 20px; margin-bottom: 30px; }}
                .card {{ background: var(--bg-card); border-radius: 12px; padding: 25px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #e5e7eb; }}
                
                .score-card {{ display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }}
                .gauge {{ width: 120px; height: 120px; border-radius: 50%; background: conic-gradient(var(--score-color) {score}%, #e5e7eb 0); display: flex; align-items: center; justify-content: center; margin-bottom: 15px; position: relative; }}
                .gauge::before {{ content: ''; position: absolute; width: 100px; height: 100px; background: white; border-radius: 50%; }}
                .gauge-value {{ position: relative; font-size: 2rem; font-weight: 800; color: var(--text-main); }}
                .score-good {{ --score-color: var(--good); }}
                .score-warning {{ --score-color: var(--medium); }}
                .score-critical {{ --score-color: var(--critical); }}

                /* STATS GRID */
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; width: 100%; }}
                .stat-item {{ text-align: center; padding: 15px; background: #f9fafb; border-radius: 8px; }}
                .stat-value {{ display: block; font-size: 1.5rem; font-weight: 700; color: var(--primary); }}
                .stat-label {{ font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }}

                /* FILTERS */
                .filters {{ display: flex; gap: 10px; margin-bottom: 20px; overflow-x: auto; padding-bottom: 5px; }}
                .filter-btn {{ padding: 8px 16px; border: 1px solid #e5e7eb; background: white; border-radius: 20px; cursor: pointer; font-weight: 600; font-size: 0.9rem; transition: all 0.2s; }}
                .filter-btn:hover, .filter-btn.active {{ background: var(--text-main); color: white; border-color: var(--text-main); }}
                .filter-btn.active-critical {{ background: var(--critical); border-color: var(--critical); color: white; }}
                .filter-btn.active-high {{ background: var(--high); border-color: var(--high); color: white; }}

                /* VULNERABILITIES */
                .vuln-list {{ display: grid; gap: 15px; }}
                .vuln-card {{ background: white; border-radius: 8px; padding: 20px; border-left: 5px solid #ccc; box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: transform 0.2s; }}
                .vuln-card:hover {{ transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }}
                
                .vuln-header {{ display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px; }}
                .vuln-title {{ font-size: 1.1rem; font-weight: 700; color: var(--text-main); }}
                .severity-badge {{ padding: 4px 10px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; color: white; text-transform: uppercase; }}
                
                .border-CRITICAL {{ border-left-color: var(--critical); }}
                .border-HIGH {{ border-left-color: var(--high); }}
                .border-MEDIUM {{ border-left-color: var(--medium); }}
                .border-LOW {{ border-left-color: var(--low); }}
                
                .bg-CRITICAL {{ background-color: var(--critical); }}
                .bg-HIGH {{ background-color: var(--high); }}
                .bg-MEDIUM {{ background-color: var(--medium); }}
                .bg-LOW {{ background-color: var(--low); }}

                .vuln-details {{ display: grid; gap: 10px; font-size: 0.9rem; }}
                .detail-row {{ display: grid; grid-template-columns: 80px 1fr; gap: 10px; }}
                .label {{ color: var(--text-muted); font-weight: 600; }}
                code {{ background: #1f2937; color: #10b981; padding: 2px 6px; border-radius: 4px; font-family: 'Courier New', monospace; word-break: break-all; font-size: 0.85rem; }}

                /* TECH INFO */
                .tech-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 30px; }}
                .tech-section h3 {{ font-size: 1rem; border-bottom: 2px solid #e5e7eb; padding-bottom: 5px; margin-bottom: 15px; }}
                .tech-list {{ list-style: none; }}
                .tech-list li {{ padding: 5px 0; border-bottom: 1px dashed #e5e7eb; font-size: 0.9rem; }}

                @media (max-width: 768px) {{
                    .score-section {{ grid-template-columns: 1fr; margin-top: 20px; }}
                    .header-content {{ flex-direction: column; align-items: flex-start; }}
                }}
                @media print {{
                    .header {{ background: white; color: black; border-bottom: 2px solid black; }}
                    .filter-btn, .no-print {{ display: none; }}
                    .card, .vuln-card {{ box-shadow: none; border: 1px solid #ddd; page-break-inside: avoid; }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="container header-content">
                    <div class="brand">
                        <h1>Rapport d'Audit de Sécurité</h1>
                        <p>Cible : <a href="{self.target_url}" style="color:white;text-decoration:underline;">{self.target_url}</a></p>
                    </div>
                    <div class="meta">
                        <span class="meta-badge">v2.0</span>
                        <span class="meta-badge">{datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
                    </div>
                </div>
            </div>

            <div class="container">
                <!-- SCORE & STATS -->
                <div class="score-section">
                    <div class="card score-card">
                        <div class="gauge {score_class}">
                            <div class="gauge-value">{score}</div>
                        </div>
                        <h3>Score de Sécurité</h3>
                        <p style="color:var(--text-muted); font-size:0.9rem;">Sur 100 points possibles</p>
                    </div>
                    
                    <div class="card">
                        <div class="stats-grid">
                            <div class="stat-item">
                                <span class="stat-value" style="color:var(--critical)">{severity_counts['CRITICAL']}</span>
                                <span class="stat-label">Critiques</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-value" style="color:var(--high)">{severity_counts['HIGH']}</span>
                                <span class="stat-label">Élevées</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-value">{len(self.vulnerabilities)}</span>
                                <span class="stat-label">Total Vuln.</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-value">{len(self.crawled_urls)}</span>
                                <span class="stat-label">URLs Scannées</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-value">{len(self.forms)}</span>
                                <span class="stat-label">Formulaires</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-value">{round(scan_duration, 2)}s</span>
                                <span class="stat-label">Durée</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- TECHNOLOGIES -->
                <div class="card" style="margin-bottom: 30px;">
                    <div class="tech-grid">
                        <div class="tech-section">
                            <h3><span style="margin-right:8px;">🔒</span>Configuration SSL/TLS</h3>
                            <ul class="tech-list">
                                <li><strong>Valide :</strong> {ssl_info.get('valid', 'N/A')}</li>
                                <li><strong>Émetteur :</strong> {ssl_info.get('issuer', 'N/A')}</li>
                                <li><strong>Expiration :</strong> {ssl_info.get('expiration', 'N/A')}</li>
                            </ul>
                        </div>
                        <div class="tech-section">
                            <h3><span style="margin-right:8px;">🌐</span>Serveur & Ports</h3>
                            <ul class="tech-list">
                                <li><strong>Serveur :</strong> {server_info.get('server', 'Non détecté')}</li>
                                <li><strong>Ports ouverts :</strong> {', '.join(map(str, ports_info)) if ports_info else 'Aucun'}</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <!-- VULNERABILITIES -->
                <h2 style="margin-bottom: 15px;">Détails des Vulnérabilités</h2>
                
                <div class="filters">
                    <button class="filter-btn active" onclick="filterVulns('ALL', this)">Tout voir</button>
                    <button class="filter-btn" onclick="filterVulns('CRITICAL', this)">Critique ({severity_counts['CRITICAL']})</button>
                    <button class="filter-btn" onclick="filterVulns('HIGH', this)">Élevé ({severity_counts['HIGH']})</button>
                    <button class="filter-btn" onclick="filterVulns('MEDIUM', this)">Moyen ({severity_counts['MEDIUM']})</button>
                </div>

                <div class="vuln-list">
        """

        # Boucle sur les vulnérabilités
        if not self.vulnerabilities:
            html += """<div class="card" style="text-align:center; padding:40px;">
                        <h3 style="color:var(--good);">✅ Aucune vulnérabilité détectée</h3>
                        <p>Le système semble sécurisé selon les tests effectués.</p>
                       </div>"""
        else:
            for i, v in enumerate(self.vulnerabilities):
                sev = v.get('severity', 'LOW').upper()
                html += f"""
                <div class="vuln-card border-{sev} item-{sev}">
                    <div class="vuln-header">
                        <div class="vuln-title">{v['type']}</div>
                        <span class="severity-badge bg-{sev}">{sev}</span>
                    </div>
                    <div class="vuln-details">
                        <div class="detail-row">
                            <span class="label">URL :</span>
                            <a href="{v['url']}" target="_blank" style="color:var(--primary); text-decoration:none; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{v['url']}</a>
                        </div>
                        <div class="detail-row">
                            <span class="label">Payload :</span>
                            <code>{v['payload']}</code>
                        </div>
                        <div class="detail-row">
                            <span class="label">Infos :</span>
                            <span>{v.get('description', 'Aucune description')}</span>
                        </div>
                    </div>
                </div>
                """

        # Fin du HTML et Scripts
        html += """
                </div>
            </div>

            <script>
                function filterVulns(severity, btn) {
                    // Gestion boutons
                    document.querySelectorAll('.filter-btn').forEach(b => {
                        b.classList.remove('active', 'active-critical', 'active-high');
                        b.style.backgroundColor = ''; 
                        b.style.color = '';
                        b.style.borderColor = '';
                    });
                    
                    if(severity === 'CRITICAL') btn.classList.add('active-critical');
                    else if(severity === 'HIGH') btn.classList.add('active-high');
                    else btn.classList.add('active');

                    // Filtrage éléments
                    const cards = document.querySelectorAll('.vuln-card');
                    cards.forEach(card => {
                        if (severity === 'ALL') {
                            card.style.display = 'block';
                        } else {
                            if (card.classList.contains('item-' + severity)) {
                                card.style.display = 'block';
                            } else {
                                card.style.display = 'none';
                            }
                        }
                    });
                }
            </script>
        </body>
        </html>
        """
        
        return html
    
    def run_scan(self):
        self.start_time = time.time()
        self.banner()
        
        print("\n[+] Phase 1: Exploration rapide du site...")
        self.crawl_website(self.target_url)
        
        print(f"\n[+] URLs decouvertes: {len(self.crawled_urls)}")
        print(f"[+] Formulaires detectes: {len(self.forms)}")
        
        self.scan_vulnerabilities_parallel()
        
        scan_duration = time.time() - self.start_time
        
        print(f"\n[+] Scan termine en {round(scan_duration, 2)} secondes!")
        print(f"[+] Vulnerabilites trouvees: {len(self.vulnerabilities)}")
        
        severity_count = {}
        for vuln in self.vulnerabilities:
            severity = vuln['severity']
            severity_count[severity] = severity_count.get(severity, 0) + 1
            
        for severity, count in severity_count.items():
            print(f"    - {severity}: {count}")
            
        report_dir = self.generate_report()
        
        print("\n" + "="*60)
        print("              SCAN TERMINE - VERSION 2.0")
        print("="*60)
        print(f"Ameliorations: Scan 3x plus rapide grace au multi-threading")
        

# Wilson
                # === [INNOVATIONS SUPPLÉMENTAIRES] ===
        print("\n[+] Début des analyses avancées...")

        # 1️⃣ Scan basique des ports
        print("\n[+] Scan rapide des ports ouverts...")
        self.ports_info = scan_basic_ports(self.target_url)

        # 2️⃣ Vérification SSL/TLS
        print("\n[+] Vérification de la configuration SSL/TLS...")
        self.ssl_info = check_ssl_tls_configuration(self.target_url)

        # 3️⃣ Détection de la version du serveur
        print("\n[+] Détection de la version du serveur...")
        self.server_info = check_server_version(self.target_url)

        # 4️⃣ Calcul du score global de sécurité
        print("\n[+] Calcul du score global de sécurité...")
        self.security_score = calculate_security_score(
            vulnerabilities=self.vulnerabilities,
            open_ports=self.ports_info,
            ssl_info=self.ssl_info,
            server_info=self.server_info
        )

        # 5️⃣ Génération d’un résumé exécutif clair
        print("\n[+] Génération du résumé exécutif...")
        summary_text = generate_executive_summary(
            target_url=self.target_url,
            vulnerabilities=self.vulnerabilities,
            open_ports=self.ports_info,
            ssl_info=self.ssl_info,
            score=self.security_score
        )

        try:
            with open(os.path.join(report_dir, "executive_summary.txt"), "w", encoding="utf-8") as f:
                f.write(summary_text)
            print(f"[+] Résumé exécutif sauvegardé dans: {report_dir}/executive_summary.txt")
        except Exception as e:
            print(f"[!] Impossible d’enregistrer le résumé exécutif: {e}")

        print("\n" + "="*60)
        print("              SCAN TERMINE - VERSION 2.0")
        print("="*60)
        print(f"Ameliorations: Scan 3x plus rapide grace au multi-threading")

        return report_dir


def main():
    print("Scanner de Vulnerabilites Web - Version 2.0")
    print("-" * 45)
    print("Ameliorations: Execution parallele + Optimisations")
    print("-" * 45)
    
    try:
        import sys
        print(f"Python {sys.version.split()[0]} detecte")
    except:
        pass
    
    target = input("\nEntrez l'URL cible (ex: http://testphp.vulnweb.com): ").strip()
    
    if not target:
        print("URL requise!")
        return
        
    if not target.startswith(('http://', 'https://')):
        target = 'http://' + target
    
    threads = input("Nombre de threads (defaut 5, max 10): ").strip()
    max_workers = int(threads) if threads.isdigit() and 1 <= int(threads) <= 10 else 5
        
    scanner = VulnerabilityScannerV2(target, max_workers=max_workers)
    
    try:
        report_dir = scanner.run_scan()
        
        html_path = os.path.join(report_dir, 'rapport_scan_v2.html')
        if os.path.exists(html_path):
            try:
                os.system(f'start {html_path}')
                print(f"\n[+] Rapport ouvert dans le navigateur")
            except:
                print(f"\n[+] Ouvrez manuellement: {html_path}")
                
    except KeyboardInterrupt:
        print("\n\n[!] Scan interrompu par l'utilisateur")
    except requests.exceptions.RequestException:
        print(f"\n[!] Impossible de se connecter a {target}")
        print("[!] Verifiez l'URL et votre connexion")
    except Exception as e:
        print(f"\n[!] Erreur: {e}")

if __name__ == "__main__":
    main()