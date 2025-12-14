import shutil
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import threading
import uuid
import json
import os
from datetime import datetime
import time

# Import des modules locaux (ils sont dans le même dossier backend/)
from scanner_vulnerabilites_v2 import VulnerabilityScannerV2
from vuln_explainer import explain_vulnerability

app = Flask(__name__)
CORS(app)

# --- 1. CONFIGURATION DES CHEMINS ---
# Le fichier actuel est dans /backend/
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
# La racine du projet est un niveau au-dessus
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
# Le dossier scans doit être à la racine
SCANS_DIR = os.path.join(PROJECT_ROOT, "scans")

if not os.path.exists(SCANS_DIR):
    os.makedirs(SCANS_DIR)

# --- 2. VARIABLES GLOBALES (C'est ce qui manquait !) ---
active_scans = {}

# --- 3. FONCTIONS UTILITAIRES ---

def get_directory_for_scan(scan_id):
    """Retourne le chemin du dossier pour un ID donné"""
    return os.path.join(SCANS_DIR, scan_id)

def load_history_from_disk():
    """Lit le disque pour reconstruire l'historique complet"""
    history = []
    
    if not os.path.exists(SCANS_DIR):
        return []
        
    for folder_name in os.listdir(SCANS_DIR):
        folder_path = os.path.join(SCANS_DIR, folder_name)
        
        if os.path.isdir(folder_path):
            json_path = os.path.join(folder_path, "rapport_scan_v2.json")
            
            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        scan_date = data.get('scan_date', '')
                        try:
                            dt = datetime.fromisoformat(scan_date)
                            date_str = dt.strftime('%d/%m/%Y')
                            time_str = dt.strftime('%H:%M:%S')
                        except:
                            date_str = "Inconnu"
                            time_str = ""

                        history.append({
                            'id': folder_name,
                            'scan_id': folder_name, # Important pour le frontend
                            'url': data.get('target', 'Inconnu'),
                            'date': date_str,
                            'time': time_str,
                            'vulnerabilities': data.get('total_vulnerabilities', 0),
                            'status': 'completed'
                        })
                except Exception as e:
                    print(f"[WARN] Erreur lecture historique {folder_name}: {e}")

    # Tri du plus récent au plus ancien
    return sorted(history, key=lambda x: x['date'], reverse=True)

# --- 4. THREAD DE SCAN ---

class ScanThread(threading.Thread):
    def __init__(self, scan_id, target_url, max_workers):
        threading.Thread.__init__(self)
        self.scan_id = scan_id
        self.target_url = target_url
        self.max_workers = max_workers
        self.scanner = None
        self.daemon = True
        
    def run(self):
        try:
            print(f"\n[DEBUG] Démarrage du scan {self.scan_id}")
            
            # Définir le dossier FINAL dès le début
            final_folder = get_directory_for_scan(self.scan_id)
            if not os.path.exists(final_folder):
                os.makedirs(final_folder)

            active_scans[self.scan_id]['status'] = 'running'
            active_scans[self.scan_id]['progress'] = 10
            
            # Création du scanner avec dossier de sortie imposé
            self.scanner = VulnerabilityScannerV2(
                self.target_url, 
                self.max_workers, 
                output_dir=final_folder
            )
            
            # Phase 1: Crawl
            active_scans[self.scan_id]['progress'] = 20
            self.scanner.crawl_website(self.scanner.target_url)
            
            active_scans[self.scan_id].update({
                'progress': 40,
                'crawled_urls': list(self.scanner.crawled_urls),
                'forms_found': self.scanner.forms
            })
            
            # Phase 2: Scan Vuln
            self.scanner.scan_vulnerabilities_parallel()
            
            active_scans[self.scan_id].update({
                'progress': 80,
                'vulnerabilities': self.scanner.vulnerabilities,
                'total_vulnerabilities': len(self.scanner.vulnerabilities)
            })
            
            # Phase 3: Rapport
            if not hasattr(self.scanner, 'start_time') or self.scanner.start_time is None:
                self.scanner.start_time = time.time()
            
            self.scanner.generate_report()

            # Stats Sévérité
            severity_stats = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
            for v in self.scanner.vulnerabilities:
                sev = v.get('severity', 'LOW').upper()
                # Sécurité pour les clés inconnues
                if sev not in severity_stats: sev = 'LOW' 
                severity_stats[sev] += 1
            
            # Fin
            active_scans[self.scan_id].update({
                'status': 'completed',
                'progress': 100,
                'report_dir': final_folder,
                'severity_stats': severity_stats,
                'crawled_urls_count': len(self.scanner.crawled_urls),
                'forms_count': len(self.scanner.forms),
                'completed_at': datetime.now().isoformat()
            })
            
            print(f"[DEBUG] Scan terminé. Rapport : {final_folder}")
            
        except Exception as e:
            import traceback
            print(f"[ERREUR] Scan {self.scan_id}: {e}")
            traceback.print_exc()
            active_scans[self.scan_id].update({
                'status': 'failed',
                'error': str(e),
                'progress': 0
            })

# --- 5. ROUTES API ---

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

@app.route('/api/scan/start', methods=['POST'])
def start_scan():
    data = request.json
    url = data.get('url', '').strip()
    threads = data.get('threads', 5)
    
    if not url: return jsonify({'error': 'URL requise'}), 400
    if not url.startswith(('http://', 'https://')): url = 'http://' + url
    
    scan_id = str(uuid.uuid4())
    
    active_scans[scan_id] = {
        'id': scan_id,
        'scan_id': scan_id, # Redondance pour sécurité frontend
        'url': url,
        'status': 'starting',
        'progress': 0,
        'threads': threads,
        'started_at': datetime.now().isoformat(),
        'vulnerabilities': [],
        'total_vulnerabilities': 0
    }
    
    thread = ScanThread(scan_id, url, threads)
    thread.start()
    
    return jsonify({'scan_id': scan_id, 'url': url}), 201

@app.route('/api/scan/<scan_id>', methods=['GET'])
def get_scan_status(scan_id):
    # 1. Scan Actif
    if scan_id in active_scans:
        data = active_scans[scan_id].copy()
        data['scan_id'] = scan_id 
        return jsonify(data)
    
    # 2. Scan Archivé
    folder_path = get_directory_for_scan(scan_id)
    json_path = os.path.join(folder_path, "rapport_scan_v2.json")
    
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            vulnerabilities = data.get('vulnerabilities', [])
            
            severity_stats = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
            for v in vulnerabilities:
                sev = v.get('severity', 'LOW').upper()
                if sev not in severity_stats: sev = 'LOW'
                severity_stats[sev] += 1

            reconstructed_scan = {
                'scan_id': scan_id,
                'url': data.get('target'),
                'status': 'completed',
                'progress': 100,
                'threads': data.get('performance', {}).get('threads_used', 0),
                'started_at': data.get('scan_date'),
                'completed_at': data.get('scan_date'),
                'total_vulnerabilities': data.get('total_vulnerabilities', 0),
                'vulnerabilities': vulnerabilities,
                'crawled_urls_count': len(data.get('crawled_urls', [])),
                'forms_count': len(data.get('forms_found', [])),
                'severity_stats': severity_stats,
                'report_dir': folder_path
            }
            return jsonify(reconstructed_scan)
        except Exception as e:
            return jsonify({'error': f"Erreur lecture archive: {str(e)}"}), 500

    return jsonify({'error': 'Scan introuvable'}), 404

@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        history = load_history_from_disk()
        return jsonify({'scans': history, 'total': len(history)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/<scan_id>', methods=['DELETE'])
def delete_scan(scan_id):
    if scan_id in active_scans:
        del active_scans[scan_id]
        
    folder_path = get_directory_for_scan(scan_id)
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
            return jsonify({'status': 'success'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Scan introuvable'}), 404

@app.route('/api/history', methods=['DELETE'])
def reset_history():
    global active_scans
    active_scans = {} 
    
    try:
        if os.path.exists(SCANS_DIR):
            for filename in os.listdir(SCANS_DIR):
                file_path = os.path.join(SCANS_DIR, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'Erreur suppression {file_path}: {e}')
                    
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan/<scan_id>/report/<fmt>', methods=['GET'])
@app.route('/api/scan/<scan_id>/report', defaults={'fmt': 'html'}, methods=['GET'])
def download_report(scan_id, fmt):
    folder_path = get_directory_for_scan(scan_id)
    
    if scan_id in active_scans and active_scans[scan_id].get('report_dir'):
        folder_path = active_scans[scan_id]['report_dir']
    
    filename = "rapport_scan_v2.json" if fmt == 'json' else "rapport_scan_v2.html"
    file_path = os.path.join(folder_path, filename)
    
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({'error': 'Fichier manquant'}), 404

@app.route('/api/stats', methods=['GET'])
def get_stats():
    # C'EST ICI QUE L'ERREUR SE PRODUISAIT
    try:
        history = load_history_from_disk()
        total_scans = len(history)
        total_vulns = sum(h['vulnerabilities'] for h in history)
        avg = round(total_vulns / total_scans, 1) if total_scans > 0 else 0
        
        # Maintenant active_scans est bien défini globalement
        running_scans = len([s for s in active_scans.values() if s.get('status') == 'running'])
        
        return jsonify({
            'total_scans': total_scans,
            'total_vulnerabilities': total_vulns,
            'average_vulnerabilities_per_scan': avg,
            'active_scans': running_scans
        })
    except Exception as e:
        print(f"Erreur stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/api/explain", methods=["POST"])
def explain():
    try:
        data = request.get_json() or {}
        vuln_text = data.get("vuln_text") or data.get("text") or ""
        if not vuln_text.strip(): return jsonify({"error": "Vide"}), 400
        
        result = explain_vulnerability(vuln_text)
        
        payload = result
        if "result" in result: payload = result["result"]
            
        return jsonify({"result": payload})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print(f"API Backend démarrée.")
    print(f"Dossier Scans: {SCANS_DIR}")
    app.run(debug=True, host='0.0.0.0', port=5000)