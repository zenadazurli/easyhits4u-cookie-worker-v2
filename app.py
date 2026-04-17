#!/usr/bin/env python3
# app.py - Login con Browserless BQL + chiavi da Supabase (solo status='working') + loop

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
# Database per le chiavi Browserless
BROWSERLESS_SUPABASE_URL = os.environ.get("BROWSERLESS_SUPABASE_URL", "https://lmtmjfrhzbjtayjwcpsq.supabase.co")
BROWSERLESS_SUPABASE_KEY = os.environ.get("BROWSERLESS_SUPABASE_KEY")

# Database per i cookie degli account
COOKIES_SUPABASE_URL = os.environ.get("COOKIES_SUPABASE_URL", "https://ofijopixtpwahgbwyutc.supabase.co")
COOKIES_SUPABASE_KEY = os.environ.get("COOKIES_SUPABASE_KEY")

# CREDENZIALI - NUOVO ACCOUNT
EASYHITS_EMAIL = "sandrominori50+giovannibarresi@gmail.com"
EASYHITS_PASSWORD = "DDnmVV45!!"
REFERER_URL = "https://www.easyhits4u.com/?ref=nicolacaporale"
BROWSERLESS_URL = "https://production-sfo.browserless.io/chrome/bql"

ACCOUNT_NAME = "giovannibaresi"
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
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🌐 Server HTTP avviato sulla porta {PORT} - GET /cookies")
    server.serve_forever()

threading.Thread(target=start_http_server, daemon=True).start()
time.sleep(1)

# ==================== FUNZIONI ====================
def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def get_working_keys():
    """
    Recupera le chiavi Browserless con status 'working' dal database
    Pulisce i caratteri invisibili con .strip()
    """
    supabase = create_client(BROWSERLESS_SUPABASE_URL, BROWSERLESS_SUPABASE_KEY)
    resp = supabase.table('browserless_keys')\
        .select('api_key')\
        .eq('status', 'working')\
        .execute()
    
    # Pulisci le chiavi da caratteri invisibili (IMPORTANTE!)
    keys = []
    for row in resp.data:
        clean_key = row['api_key'].strip()
        keys.append(clean_key)
    
    log(f"📋 Trovate {len(keys)} chiavi 'working' nel database")
    
    # Mostra le prime 3 chiavi (debug)
    if keys:
        log(f"   Prime 3 chiavi: {keys[0][:15]}..., {keys[1][:15] if len(keys) > 1 else ''}, {keys[2][:15] if len(keys) > 2 else ''}")
    
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
    """Tenta il login con una chiave specifica"""
    # Pulisci la chiave
    api_key = api_key.strip()
    
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.easyhits4u.com/',
        'Origin': 'https://www.easyhits4u.com',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    # GET homepage
    try:
        session.get("https://www.easyhits4u.com/", headers=headers, verify=False, timeout=15)
        time.sleep(1)
    except Exception as e:
        log(f"   ❌ Errore homepage: {e}")
        return None
    
    # Token Cloudflare
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
    
    try:
        login_resp = session.post("https://www.easyhits4u.com/logon/", data=data, headers=login_headers, allow_redirects=True, timeout=30)
        log(f"      Login POST status: {login_resp.status_code}")
        if login_resp.status_code != 200:
            return None
        time.sleep(2)
    except Exception as e:
        log(f"   ❌ Errore POST login: {e}")
        return None
    
    # GET /member/
    try:
        session.get("https://www.easyhits4u.com/member/", headers=headers, verify=False, timeout=15)
        time.sleep(1)
    except Exception as e:
        log(f"   ⚠️ Errore member: {e}")
    
    # GET /surf/
    try:
        session.get("https://www.easyhits4u.com/surf/", headers=headers, verify=False, timeout=15)
        time.sleep(1)
    except Exception as e:
        log(f"   ⚠️ Errore surf: {e}")
    
    # GET referer
    try:
        session.get(REFERER_URL, headers=headers, verify=False, timeout=15)
    except Exception as e:
        log(f"   ⚠️ Errore referer: {e}")
    
    cookies = session.cookies.get_dict()
    log(f"   🍪 Cookie ottenuti: {list(cookies.keys())}")
    
    if 'user_id' in cookies and 'sesids' in cookies:
        cookies['surftype'] = '2'
        cookie_string = build_cookie_string(cookies)
        log(f"   ✅ Login completo! user_id={cookies['user_id']}, sesids={cookies['sesids']}")
        return cookie_string, cookies['user_id'], cookies['sesids']
    else:
        log(f"   ❌ Cookie essenziali mancanti: user_id={cookies.get('user_id')}, sesids={cookies.get('sesids')}")
        return None

def save_cookies(cookie_string, user_id, sesids):
    """Salva i cookie su file e Supabase (database cookies)"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Salva su file
    with open(os.path.join(OUTPUT_DIR, f"cookies_{timestamp}.json"), "w") as f:
        json.dump({'user_id': user_id, 'sesids': sesids, 'cookie_string': cookie_string}, f, indent=2)
    with open(os.path.join(OUTPUT_DIR, "cookies_latest.txt"), "w") as f:
        f.write(cookie_string)
    
    log("   💾 Cookie salvati su file")
    
    # Salva anche su Supabase (database cookies)
    try:
        supabase = create_client(COOKIES_SUPABASE_URL, COOKIES_SUPABASE_KEY)
        
        # Prima controlla se esiste già un record per questo account
        existing = supabase.table('account_cookies')\
            .select('id')\
            .eq('account_name', ACCOUNT_NAME)\
            .execute()
        
        cookie_data = {
            'account_name': ACCOUNT_NAME,
            'email': EASYHITS_EMAIL,
            'password': EASYHITS_PASSWORD,
            'cookies_string': cookie_string,
            'user_id': user_id,
            'sesids': sesids,
            'status': 'active',
            'updated_at': datetime.now().isoformat()
        }
        
        if existing.data:
            # Aggiorna esistente
            supabase.table('account_cookies')\
                .update(cookie_data)\
                .eq('account_name', ACCOUNT_NAME)\
                .execute()
            log("   💾 Cookie aggiornati su Supabase (cookies DB)")
        else:
            # Inserisci nuovo
            cookie_data['created_at'] = datetime.now().isoformat()
            supabase.table('account_cookies').insert(cookie_data).execute()
            log("   💾 Cookie salvati su Supabase (cookies DB - nuovo record)")
            
    except Exception as e:
        log(f"   ⚠️ Errore Supabase (cookies DB): {e}")

def generate_cookie():
    """Tenta di generare un cookie con le chiavi working dal database"""
    log("🔄 Generazione nuovo cookie...")
    
    keys = get_working_keys()
    if not keys:
        log("❌ Nessuna chiave 'working' trovata nel database")
        return False
    
    for i, api_key in enumerate(keys, 1):
        log(f"🔑 [{i}/{len(keys)}] Tentativo con chiave: {api_key[:15]}...")
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
    log("🚀 GENERATORE COOKIE DINAMICO")
    log(f"📧 Account: {EASYHITS_EMAIL}")
    log(f"📅 Intervallo: {REFRESH_INTERVAL // 3600} ore")
    log("=" * 50)
    
    # Verifica connessione al database delle chiavi
    if not BROWSERLESS_SUPABASE_KEY:
        log("❌ BROWSERLESS_SUPABASE_KEY non impostata")
        log("   Imposta le variabili d'ambiente su Render")
        return
    
    if not COOKIES_SUPABASE_KEY:
        log("❌ COOKIES_SUPABASE_KEY non impostata")
        log("   Imposta le variabili d'ambiente su Render")
        return
    
    try:
        supabase = create_client(BROWSERLESS_SUPABASE_URL, BROWSERLESS_SUPABASE_KEY)
        supabase.table('browserless_keys').select('count').limit(1).execute()
        log("✅ Connessione a Browserless DB OK")
    except Exception as e:
        log(f"❌ Errore connessione Browserless DB: {e}")
        return
    
    try:
        supabase = create_client(COOKIES_SUPABASE_URL, COOKIES_SUPABASE_KEY)
        supabase.table('account_cookies').select('count').limit(1).execute()
        log("✅ Connessione a Cookies DB OK")
    except Exception as e:
        log(f"⚠️ Errore connessione Cookies DB: {e}")
        log("   I cookie verranno salvati solo su file")
    
    # Loop principale
    while True:
        success = generate_cookie()
        if success:
            log(f"✅ Cookie generato. Prossimo tra {REFRESH_INTERVAL // 3600} ore")
            time.sleep(REFRESH_INTERVAL)
        else:
            log("❌ Nessuna chiave funzionante. Riprovo tra 1 ora")
            time.sleep(3600)

if __name__ == "__main__":
    main()
