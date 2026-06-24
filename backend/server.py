import os
import sys
import json
import sqlite3
import webbrowser
from http.server import SimpleHTTPRequestHandler, HTTPServer

# Determina la cartella principale (root) in modo blindato
if getattr(sys, 'frozen', False):
    ROOT_DIR = os.path.dirname(sys.executable)
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(current_dir) == 'backend':
        ROOT_DIR = os.path.dirname(current_dir)
    else:
        ROOT_DIR = current_dir

# Forza la directory di lavoro sulla root principale della chiavetta
os.chdir(ROOT_DIR)

# CONFIGURAZIONE PERCORSI (Con la F maiuscola come la tua cartella!)
FRONTEND_DIR = os.path.join(ROOT_DIR, 'Frontend')
BACKEND_DIR = os.path.join(ROOT_DIR, 'backend')
DB_PATH = os.path.join(BACKEND_DIR, 'database.db')

def init_db():
    if not os.path.exists(BACKEND_DIR):
        os.makedirs(BACKEND_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS impostazioni (
            chiave TEXT PRIMARY KEY,
            valore TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class GestoreRichieste(SimpleHTTPRequestHandler):
    def do_GET(self):
        # API Dati
        if self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT valore FROM impostazioni WHERE chiave = 'dati_onoranze'")
            riga = cursor.fetchone()
            conn.close()
            if riga:
                self.wfile.write(riga[0].encode('utf-8'))
            else:
                self.wfile.write(b'{}')
            return

        # Home page: reindirizza alla cartella con la F MAIUSCOLA
        if self.path == '/' or self.path == '/index.html':
            self.path = '/Frontend/Ricerca onoranze.html'

        return super().do_GET()

    def do_POST(self):
        if self.path == '/api/save':
            lunghezza_contenuto = int(self.headers['Content-Length'])
            dati_ricevuti = self.rfile.read(lunghezza_contenuto).decode('utf-8')
            try:
                json.loads(dati_ricevuti)
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO impostazioni (chiave, valore) 
                    VALUES ('dati_onoranze', ?)
                """, (dati_ricevuti,))
                conn.commit()
                conn.close()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "success"}')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f'{"status": "error", "message": "{str(e)}"}'.encode('utf-8'))
            return

def avvia_server():
    porta = 8000
    server = HTTPServer(('localhost', porta), GestoreRichieste)
    print("Server SQL pronto.")
    webbrowser.open(f"http://localhost:{porta}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer spento.")

if __name__ == '__main__':
    avvia_server()