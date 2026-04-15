#!/usr/bin/env python3
# app.py - Login con Browserless BQL + chiavi da Supabase + loop + DEBUG

import requests
import json
import time
import os
import pickle
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from supabase import create_client

# ==================== CONFIGURAZIONE ====================
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

EASYHITS_EMAIL = "sandrominori50+uiszuzoqatr@gmail.com"
EASYHITS_PASSWORD = "DDnmVV45!!"
REFERER_URL = "https://www.easyhits4u.com/?ref=nicolacaporale"
BROWSERLESS_URL = "https://production-sfo.browserless.io/chrome/bql"

ACCOUNT_NAME = "main"
REFRESH_INTERVAL = 6 * 3600  # 6 ore

OUTPUT_DIR = "/tmp/easyhits4u"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==================== SERVER HTTP ====================
PORT = int(os.environ.get("PORT", 10000))

class CookieHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/cookies':
            try:
                latest_path = os.path.join(OUTPUT_DIR, "cookies_latest.txt")
                if os.path.exists(latest_path):
                    with open(latest_path, "r") as f:
                        cookie_string = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain")
                    self.end_headers()
                    self.wfile.write(cookie_string.encode())
                else:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b"Cookie file not found yet")
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, format, *args):
        pass

def start_http_server():
    server = HTTPServer(('0.0.0.0', PORT), CookieHandler)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🌐 Server HTTP avviato sulla porta {PORT}")
    server.serve_forever()

threading.Thread(target=start_http_server, daemon=True).start()
time.sleep(1)

# ==================== FUNZIONI ====================
def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def get_working_keys():
    """Recupera le chiavi Browserless con status 'working' dal database"""
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    resp = supabase.table('browserless_keys')\
        .select('api_key')\
        .eq('status', 'working')\
        .execute()
    
    keys = [row['api_key'] for row in resp.data]
    
    # DEBUG: stampa ogni chiave con dettagli
    log(f"📋 DEBUG - Chiavi lette dal database ({len(keys)}):")
    for i, key in enumerate(keys):
        log(f"   [{i+1}] lunghezza={len(key)}, repr={repr(key[:30])}...")
    
    return keys

def get_cf_token(api_key):
    query = """
    mutation {
      goto(url: "https://www.easyhits4u.com/logon/", waitUntil: networkIdle, timeout: 60000) {
        status
      }
      solve(type: cloudflare, timeout: 60000) {
        solved
        token
        time
      }
    }
    """
    url = f"{BROWSERLESS_URL}?token={api_key}"
    try:
        start = time.time()
        response = requests.post(url, json={"query": query}, headers={"Content-Type": "application/json"}, timeout=120)
        if response.status_code != 200:
            return None
        data = response.json()
        if "errors" in data:
            return None
        solve_info = data.get("data", {}).get("solve", {})
        if solve_info.get("solved"):
            token = solve_info.get("token")
            log(f"   ✅ Token ({time.time()-start:.1f}s)")
            return token
        return None
    except Exception as e:
        log(f"   ❌ Errore token: {e}")
        return None

def build_cookie_string(cookies_dict):
    return '; '.join([f"{k}={v}" for k, v in cookies_dict.items()])

def login_and_get_cookies(api_key):
    # DEBUG: mostra la chiave esatta che stiamo usando
    log(f"   🔑 CHIAVE TEST: '{api_key[:20]}...' (len={len(api_key)})")
    
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/148.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    # GET homepage
    session.get("https://www.easyhits4u.com/", headers=headers, verify=False, timeout=15)
    time.sleep(1)
    
    token = get_cf_token(api_key)
    if not token:
        return None
    
    # POST login
    login_headers = headers.copy()
    login_headers['Content-Type'] = 'application/x-www-form-urlencoded'
    login_headers['Referer'] = REFERER_URL
    data = {
        'manual': '1',
        'fb_id': '',
        'fb_token': '',
        'google_code': '',
        'username': EASYHITS_EMAIL,
        'password': EASYHITS_PASSWORD,
        'cf-turnstile-response': token,
    }
    login_resp = session.post("https://www.easyhits4u.com/logon/", data=data, headers=login_headers, allow_redirects=True, timeout=30)
    if login_resp.status_code != 200:
        return None
    time.sleep(2)
    
    # GET /member/
    session.get("https://www.easyhits4u.com/member/", headers=headers, verify=False, timeout=15)
    time.sleep(1)
    
    # GET /surf/
    session.get("https://www.easyhits4u.com/surf/", headers=headers, verify=False, timeout=15)
    time.sleep(1)
    
    # GET referer
    session.get(REFERER_URL, headers=headers, verify=False, timeout=15)
    
    cookies = session.cookies.get_dict()
    if 'user_id' in cookies and 'sesids' in cookies:
        cookies['surftype'] = '2'
        cookie_string = build_cookie_string(cookies)
        return cookie_string, cookies['user_id'], cookies['sesids']
    return None

def save_cookies(cookie_string, user_id, sesids):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Salva su file
    with open(os.path.join(OUTPUT_DIR, f"cookies_{timestamp}.json"), "w") as f:
        json.dump({'user_id': user_id, 'sesids': sesids, 'cookie_string': cookie_string}, f, indent=2)
    with open(os.path.join(OUTPUT_DIR, "cookies_latest.txt"), "w") as f:
        f.write(cookie_string)
    
    log("   💾 Cookie salvati su file")
    
    # Salva anche su Supabase (opzionale, per il bot di autosurf)
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        supabase.table('account_cookies').upsert({
            'account_name': ACCOUNT_NAME,
            'cookie_string': cookie_string,
            'user_id': user_id,
            'sesids': sesids,
            'status': 'active',
            'updated_at': datetime.now().isoformat()
        }, on_conflict='account_name').execute()
        log("   💾 Cookie salvati su Supabase")
    except Exception as e:
        log(f"   ⚠️ Errore Supabase: {e}")

def generate_cookie():
    """Tenta di generare un cookie con le chiavi working dal database"""
    log("🔄 Generazione nuovo cookie...")
    
    keys = get_working_keys()
    if not keys:
        log("❌ Nessuna chiave 'working' trovata nel database")
        return False
    
    log(f"🔑 Trovate {len(keys)} chiavi 'working'")
    
    for i, api_key in enumerate(keys):
        log(f"🔑 [{i+1}/{len(keys)}] Tentativo con chiave: {api_key[:15]}...")
        result = login_and_get_cookies(api_key)
        if result:
            cookie_string, user_id, sesids = result
            log(f"🎉 Cookie generato! user_id={user_id}, sesids={sesids}")
            save_cookies(cookie_string, user_id, sesids)
            return True
        else:
            log(f"   ❌ Fallito")
    
    log("❌ Nessuna chiave funzionante")
    return False

def main():
    log("=" * 50)
    log("🚀 GENERATORE COOKIE DINAMICO (CHIAVI DA SUPABASE) - DEBUG")
    log(f"📅 Intervallo: {REFRESH_INTERVAL // 3600} ore")
    log("=" * 50)
    
    # Verifica connessione a Supabase
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        log("❌ SUPABASE_URL o SUPABASE_SERVICE_KEY non impostate")
        return
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        supabase.table('browserless_keys').select('count').limit(1).execute()
        log("✅ Connessione a Supabase OK")
    except Exception as e:
        log(f"❌ Errore connessione Supabase: {e}")
        return
    
    while True:
        success = generate_cookie()
        if success:
            log(f"✅ Cookie generato. Prossimo tra {REFRESH_INTERVAL // 3600} ore")
        else:
            log("❌ Nessuna chiave funzionante. Riprovo tra 1 ora")
            time.sleep(3600)
            continue
        
        time.sleep(REFRESH_INTERVAL)

if __name__ == "__main__":
    main()
