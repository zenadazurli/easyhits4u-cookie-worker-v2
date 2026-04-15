#!/usr/bin/env python3
# app.py - Login con Browserless BQL + acquisizione cookie completi + server HTTP per download

import requests
import json
import time
import os
import pickle
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# ==================== CHIAVI VALIDE ====================
VALID_KEYS = [
    "2UL8m6BcAfHYAFxd5ecc52e551f286dbd72cce5fa350a2091",
    "2UL8n777kF6fwCmbfc2300911b1fac61745a7d382e65a9219",
    "2UL8pINenLzFZZxd7139e0a88d9b01b982fa4d19fb80c5322",
    "2UL8qeyKL6Pktwj5f32492aa3ed7aa80ebefb7a44af6ef2e2",
    "2UL8sQdVV06yZkOd5f22643a2f467a87d06d04a2b667a6a86",
    "2UL8ueD9EJSZeXm773e84c545f86f762185487f1b57c06fe7",
    "2UL8wv0wEuEFmEe629ee64554980c6ae710b550e834dcfefd",
    "2UL8xelkv5JaWc3e4faa839aa48102cf37c41ae894b532fcb",
    "2UL8zDUapLqCSBU770f53ccdf1591ce45e6371304b72b0c92",
    "2UL9055xj8Nv4l221a380b4cb0dab7bdc105d95ac2635539c",
]

BROWSERLESS_URL = "https://production-sfo.browserless.io/chrome/bql"

# CREDENZIALI
EASYHITS_EMAIL = "sandrominori50+giorgiofaggiolini@gmail.com"
EASYHITS_PASSWORD = "DDnmVV45!!"
REFERER_URL = "https://www.easyhits4u.com/?ref=nicolacaporale"

# Directory di output
OUTPUT_DIR = "/tmp/easyhits4u"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==================== SERVER HTTP PER DOWNLOAD COOKIE ====================
PORT = int(os.environ.get("PORT", 10000))
server_running = False

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
    global server_running
    try:
        server = HTTPServer(('0.0.0.0', PORT), CookieHandler)
        server_running = True
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🌐 Server HTTP avviato sulla porta {PORT} - GET /cookies per scaricare la stringa cookie")
        server.serve_forever()
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Errore avvio server: {e}")

threading.Thread(target=start_http_server, daemon=True).start()
time.sleep(1)

# ==================== FUNZIONI ====================
def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

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

def login_and_get_complete_cookies(api_key):
    log(f"   🔐 TEST CHIAVE: {api_key[:15]}...")
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
    log("   🌐 GET homepage...")
    try:
        home = session.get("https://www.easyhits4u.com/", headers=headers, verify=False, timeout=15)
        log(f"      Homepage status: {home.status_code}")
        time.sleep(1)
    except Exception as e:
        log(f"      ❌ Errore homepage: {e}")
        return None, None, None
    
    # Token
    token = get_cf_token(api_key)
    if not token:
        log(f"   ❌ Token non ottenuto per chiave {api_key[:15]}...")
        return None, None, None
    
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
        time.sleep(1)
    except Exception as e:
        log(f"      ❌ Errore POST login: {e}")
        return None, None, None
    
    # GET /member/
    log("   🌐 GET /member/...")
    try:
        member = session.get("https://www.easyhits4u.com/member/", headers=headers, verify=False, timeout=15)
        log(f"      Member status: {member.status_code}")
        time.sleep(1)
    except Exception as e:
        log(f"      ❌ Errore member: {e}")
        return None, None, None
    
    # GET /surf/
    log("   🌐 GET /surf/...")
    try:
        surf = session.get("https://www.easyhits4u.com/surf/", headers=headers, verify=False, timeout=15)
        log(f"      Surf page status: {surf.status_code}")
        time.sleep(1)
    except Exception as e:
        log(f"      ❌ Errore surf: {e}")
        return None, None, None
    
    # GET referer
    log("   🌐 GET referer...")
    try:
        ref = session.get(REFERER_URL, headers=headers, verify=False, timeout=15)
        log(f"      Referer status: {ref.status_code}")
    except Exception as e:
        log(f"      ⚠️ Errore referer: {e}")
    
    cookies_dict = session.cookies.get_dict()
    cookie_string = build_cookie_string(cookies_dict)
    log(f"   🍪 Cookie ottenuti: {list(cookies_dict.keys())}")
    
    if 'user_id' in cookies_dict and 'sesids' in cookies_dict:
        log(f"   ✅✅✅ LOGIN COMPLETO! user_id={cookies_dict['user_id']}, sesids={cookies_dict['sesids']}")
        log(f"   🎉 CHIAVE FUNZIONANTE: {api_key[:15]}...")
        return cookies_dict, cookie_string, session
    else:
        log(f"   ❌ Cookie essenziali mancanti: user_id={cookies_dict.get('user_id')}, sesids={cookies_dict.get('sesids')}")
        log(f"   ❌ CHIAVE NON FUNZIONANTE: {api_key[:15]}...")
        return None, None, None

def save_cookies(cookies_dict, cookie_string, session):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    json_path = os.path.join(OUTPUT_DIR, f"cookies_{timestamp}.json")
    with open(json_path, "w") as f:
        json.dump(cookies_dict, f, indent=2)
    log(f"   💾 Cookie JSON: {json_path}")
    
    txt_path = os.path.join(OUTPUT_DIR, f"cookie_string_{timestamp}.txt")
    with open(txt_path, "w") as f:
        f.write(cookie_string)
    log(f"   💾 Cookie stringa: {txt_path}")
    
    latest_path = os.path.join(OUTPUT_DIR, "cookies_latest.txt")
    with open(latest_path, "w") as f:
        f.write(cookie_string)
    log(f"   💾 Ultimo cookie: {latest_path}")
    
    session_path = os.path.join(OUTPUT_DIR, f"session_{timestamp}.pkl")
    with open(session_path, "wb") as f:
        pickle.dump(session, f)
    log(f"   💾 Sessione pickle: {session_path}")
    
    latest_session = os.path.join(OUTPUT_DIR, "session_latest.pkl")
    with open(latest_session, "wb") as f:
        pickle.dump(session, f)

def main():
    log("=" * 50)
    log("🚀 LOGIN BROWSERLESS BQL + ACQUISIZIONE COOKIE COMPLETI")
    log(f"📋 Chiavi da testare: {len(VALID_KEYS)}")
    log("=" * 50)
    
    for i, api_key in enumerate(VALID_KEYS, 1):
        log(f"\n🔑 [{i}/{len(VALID_KEYS)}] Tentativo con chiave: {api_key[:15]}...")
        cookies_dict, cookie_string, session = login_and_get_complete_cookies(api_key)
        if cookies_dict:
            log("🎉 Login e navigazione riusciti! Salvo cookie...")
            save_cookies(cookies_dict, cookie_string, session)
            log("✅ Fatto. Cookie salvati in /tmp/easyhits4u/")
            log(f"   🌐 curl http://localhost:{PORT}/cookies")
            log("   ⚠️ Il servizio rimane in esecuzione per servire il file.")
            while True:
                time.sleep(60)
        else:
            log(f"   ❌ Tentativo fallito con questa chiave")
    
    log("❌ Login fallito con tutte le chiavi. Server rimane attivo per eventuali richieste.")
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
