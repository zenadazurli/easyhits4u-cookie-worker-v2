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

# ==================== CHIAVI VALIDE (NUOVE) ====================
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
    "2UL923lRSXQBxpvad7db181c28a9e1ad7ab10946e23661df1",
    "2UL93ESEgtjVWw39dbf70d172eca2bfd7d7f4bd3e317e9ad3",
    "2UL957MdkKXBfvLadd85cb130bcc04546f9523dd9b496c656",
    "2UL96ZLBJhcAsPB821e8afb0bff69605ddddaef825308a28b",
    "2UL98XYztR0QK5H6fb65c651ed1a8be9fa4c212338a202395",
    "2UL99ERKq0hvsNA0019cc3be5e45df475e7d65a5aa882c12f",
    "2UL9BXvp0gEJfB6f9651335bfd2880f2e70d01b4b99277864",
    "2UL9C4Iudc5TsFM7cc019b6577a24694452b634536270da3a",
    "2UL9ER4qe7udtQ5a1b459a556d79524fc8fdfa9e0bcde7a9e",
    "2UL9GhmUe7QmmEgd0b1cb1bf2d3abd76b5bb075a7d78bc183",
    "2UL9vvggUjSawwW45183fffb77c3a4d5743803c7554201c28",
    "2UL9xndXFZgA15x493be499566a49db12759ad80e008df427",
    "2UL9yJsOqwtjSJJ8b3c06e2485607767659737f28fd695222",
    "2ULA0qdhEjkrBLtd80f91007bcd4833d416fdf3f63de22cbd",
    "2ULA197YfpRmYpW1e1f04cdc962a8617b2575eac96d23307d",
    "2ULA3kJCeBH36f4d135b047b16b8dc93241c25d1f25b8a5ee",
    "2ULA5DKmvi23DSOa73fa7e09c773ea49d0f50b6556930cac0",
    "2ULA7KE8xi6DU1n6ed5389e5c7b63709eb77405535336a38d",
    "2ULA8GlckzPAnr4ec611daad92fa6bc27e1b70d145d80e4ef",
    "2ULAA4W0mjXVv2Na1d0612debfa017c166294efcef5df9fe2",
    "2ULABtCAp8CFXLzc374b979e89e97ac7beeda07f81b1776e8",
    "2ULADORGc1XdsRwa2c2f411c5fd45f5b97c761b01955148a2",
    "2ULAEVtLF7ZA58Ed9b9c835c0c3c47026f425d831ae506084",
    "2ULAGSPT8Jaq5H0217bb66fba36f861c1b616c43f2931eec9",
    "2ULAHsChPIXhLJe983885e40bd5a68b98456c3086d9faed20",
    "2ULAJnOFfaIFioSfdf73fc016b513089b2792f4dfc10887f5",
    "2ULAKw2vjHk3QV2343b29113c160112f2b86112f20770f4c1",
    "2ULAM5rOaLqpSrJ81765ba853b0d887e06cc5256efcd29625",
    "2ULAOR1Se25QPA89e02363c2c4e78a42e81c5e6800eba689a",
    "2ULAVE8fDpuYDDt0a75edc48421dfdbc12b927a9a73a195b2",
    "2ULAW3Te59dIYfkcae2f31846f08b069a722da4979741a575",
    "2ULAYZhPD9nMJjt61bf879adbb2a4148710104008b2b39f85",
    "2ULAZhuDe3Nu3lAfbceedd5488286a23be43f7ca652f7dca2",
    "2ULAbrS9RBdXgNI0845fdf02d932b93b0f30da917bd7298db",
    "2UKQAmAKiLpVrFv185d7c617411aca8839d2ca36abb5fd8cb",
    "2ULAf5HPyaLhxiR08835593f6b91d369dc4814a4227760d4f",
    "2ULAg9O1Wg9Ricocad73eade8d3ccdb53793e394b01975d21",
    "2ULAi5pO7dawf1o7d5fea61ea5f1eafe0024e09dfe0be0cc7",
    "2ULAjTXZt2tr7WM150b3b2783c214b26153ebded80f629f9b",
    "2ULAlJ7JDjykK0Ze4df9ca167b10659b5460d96141bb40d72",
    "2ULAmV6cG7adBIGb56b652c1f0b549a7690f21cdb9ee970cf",
    "2UIubwkm21RIi9Yf891666901a176d8776a02480b6b816550",
    "2ULAqznUrnXofpa13c3fa4a351de63f8cf3a62218eea21f6f",
    "2ULArh6SPkKpcene5b0c034acec3572d740d213b4ae5d01a1",
    "2ULAtvkaRDFnryX78971d080b54b643ad6f2e71dbf5731f51",
    "2ULAvw3E10z3hDqe2a999d8e393e1b2653b0d42706fb48435",
    "2ULAw9BWRnPa56Lcc933dfd9a0a4a50d27603b6ee4cb59437",
    "2ULAydVuqfxEuWh5d033164907bd23ee2a5704a42a81376aa",
    "2ULAzz3SNUbcMfh61e1affefaac6b81a7c2fccab140a74f4a",
    "2ULB1MyIUzs9ak2eb4fe3188c9613f6711f535d855808e541",
    "2ULB273YPA5qqbYbff8ee90211f7ee4758ba2724e13d543b9",
    "2ULB4rO15zUb3rwdc8c5f6e9c4a9e39886c1c551837bf7bb7",
    "2ULB61Gzivw8IOvde6cdeb6186c634e6091572f558424de12",
    "2ULB7yCs015Z3Tq13210d0fb8052a93238145830da8fb88ed",
    "2ULBASz93PuLnOY3bb2c3faa1a7e4f47b04be84a239957780",
    "2ULBBLOU9ZrIqAra4397a5936c77f2bca1bcb70fdbdb152b8",
    "2ULBDzX4bkeWITq04c185d1bc6a1fded643ed162f8e31177f",
    "2ULBELffpsjv09ye4eb9b4a1a94ebc4b85478a91e598b7beb",
    "2ULBG6LH8tLpgRaa5956ab663c12650ccf45dc6ac11392fca",
    "2ULBIMsSrGnOzle7117921acb3b74043146ffc2a2e0a1ba80",
    "2ULBKVe4PG9Gfc801e274fbd685e16dc12e044486fd10cf44",
    "2ULBL8L1eNBeOKM23381e75f5203fd779c884f3e9ce5eb6d0",
    "2ULBNxJicoyRN29ee1c40b8267d7f2b368f4154e918e8b365",
    "2ULBOjAsp0UM5xQ7c9a6005a1d707e3034dc01491904fc689",
    "2ULBQixLUKJHoa54956844057eb3a02886bbd3a34e4bdfd84",
    "2ULBR4C8izWvF8989271c7e8540d1e378363d719358c71994",
    "2ULBTOVEHwMXROZ563b8f4f4c3fb89eb80c34e7c1af42ad19",
    "2ULBVxKDgZdpZK8bedf563cb4617559c31a787f218c63336d",
    "2ULBaA5pG5nbE5w1dea4dae862fe605db97a84a644a7135fc",
    "2ULBciv3lATSTbWf9d06766ed91353915c77dffddf40ae726",
    "2ULBeGPbKbkSkByeb67ab69007bdad7e1da21f9ca8b966e8e",
    "2ULBfh8wYgNAZx1ff01810fd5cc1d6f266f922462c1221c07",
    "2ULBhh32F0pfQci87bc420d8ad8da20b64fa67f843ca81be2",
    "2ULBiwJFpzTMJFIdd8f44a7ad373db964dd0aaef1b9fabdba",
    "2ULBkBUQd2XQk04cd5e1944f43ead251f4f560db08cdb60d8",
    "2ULBl4wVzW8ZMene219ea95b1fe98f90b272150fc6962b17b",
    "2ULBn9PdH5mERRPf88c59ef1e78451ad2f046e88066219707",
    "2ULBq41rQWgZNKCb0e088ee18e7cab9589fc8e4e423166572",
    "2ULBrMdEKMSDEyR6b0e4af076b452a08b2d40c591c02f029d",
    "2ULBtJ6GfGOltk23dd447d9518bf779121f1deae657dfdd22",
    "2ULBuJJZzP1gLswde2ca5cb3a569948622289f3613eee4c87",
    "2ULBwLpHDP5JH3a0e37fe701f0739840ef23862877b88c4aa",
    "2ULBxPi4DP0wRsc9fd0668f806ff7ae7075acbbb082533197",
    "2ULBzu7QVbKTMow03b7b6e3245a48105c4e7da4717344e344",
    "2ULC0OCbQMky2Kr2d3e7de84bd8c9b84bdcf9e042ffe739ef",
    "2ULC2kkMp0NLFsKc4b8b9fb2e2d613ca502d445723fef1377",
    "2ULC4zTTD9M4tCl234d9c0fdff662eaa70ab877bcb71b1f32",
    "2ULC5QHKQlhE7yD9cf5b919893d398badda5997ed4a254f6e",
    "2ULC70Y4hrkboKU4013dd5d06bd6900f95cf27a91cc840410",
    "2ULC9Mrd9r2TdGffe441f2073749a5c6b2e53250ecb9c2ae7",
    "2ULCAhYjsLQvdEk1e527aeb73f63d8920ef77a33b5a8bae9c",
    "2ULCDDFJ7ObYnQ2bceefcf66a44e1ad0002f455dcc3ef5563",
    "2ULCQbidTtzDhYmfc1c071b713c684a81a802cda8e0a2f8d0",
    "2ULCTxIDmpvy8wfcbba32128e54dc18a9eb97d4505cf4d743",
    "2ULCViuZPEa4MDXe8dd4a972ec70a200c4ce0bffabe67cffc",
]

BROWSERLESS_URL = "https://production-sfo.browserless.io/chrome/bql"

# CREDENZIALI
EASYHITS_EMAIL = "sandrominori50+uiszuzoqatr@gmail.com"
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

# Avvia il server in un thread separato
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
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/148.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    # 1. GET homepage
    log("   🌐 GET homepage...")
    try:
        home = session.get("https://www.easyhits4u.com/", headers=headers, verify=False, timeout=15)
        log(f"      Homepage status: {home.status_code}")
        time.sleep(1)
    except Exception as e:
        log(f"      ❌ Errore homepage: {e}")
        return None, None, None
    
    # 2. Token
    token = get_cf_token(api_key)
    if not token:
        return None, None, None
    
    # 3. POST login
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
    
    # 4. GET /member/
    log("   🌐 GET /member/...")
    try:
        member = session.get("https://www.easyhits4u.com/member/", headers=headers, verify=False, timeout=15)
        log(f"      Member status: {member.status_code}")
        time.sleep(1)
    except Exception as e:
        log(f"      ❌ Errore member: {e}")
        return None, None, None
    
    # 5. GET /surf/
    log("   🌐 GET /surf/...")
    try:
        surf = session.get("https://www.easyhits4u.com/surf/", headers=headers, verify=False, timeout=15)
        log(f"      Surf page status: {surf.status_code}")
        time.sleep(1)
    except Exception as e:
        log(f"      ❌ Errore surf: {e}")
        return None, None, None
    
    # 6. GET referer (opzionale)
    log("   🌐 GET referer...")
    try:
        ref = session.get(REFERER_URL, headers=headers, verify=False, timeout=15)
        log(f"      Referer status: {ref.status_code}")
    except Exception as e:
        log(f"      ⚠️ Errore referer (non bloccante): {e}")
    
    cookies_dict = session.cookies.get_dict()
    cookie_string = build_cookie_string(cookies_dict)
    log(f"   🍪 Cookie ottenuti: {list(cookies_dict.keys())}")
    
    if 'user_id' in cookies_dict and 'sesids' in cookies_dict:
        log(f"   ✅ Login completo! user_id={cookies_dict['user_id']}, sesids={cookies_dict['sesids']}")
        return cookies_dict, cookie_string, session
    else:
        log(f"   ❌ Cookie essenziali mancanti: user_id={cookies_dict.get('user_id')}, sesids={cookies_dict.get('sesids')}")
        return None, None, None

def save_cookies(cookies_dict, cookie_string, session):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # JSON
    json_path = os.path.join(OUTPUT_DIR, f"cookies_{timestamp}.json")
    with open(json_path, "w") as f:
        json.dump(cookies_dict, f, indent=2)
    log(f"   💾 Cookie JSON: {json_path}")
    
    # Stringa TXT
    txt_path = os.path.join(OUTPUT_DIR, f"cookie_string_{timestamp}.txt")
    with open(txt_path, "w") as f:
        f.write(cookie_string)
    log(f"   💾 Cookie stringa: {txt_path}")
    
    # Ultimo (sovrascrive)
    latest_path = os.path.join(OUTPUT_DIR, "cookies_latest.txt")
    with open(latest_path, "w") as f:
        f.write(cookie_string)
    log(f"   💾 Ultimo cookie: {latest_path}")
    
    # Sessione pickle
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
    log("=" * 50)
    
    for api_key in VALID_KEYS:
        log(f"🔑 Tentativo con chiave: {api_key[:10]}...")
        cookies_dict, cookie_string, session = login_and_get_complete_cookies(api_key)
        if cookies_dict:
            log("🎉 Login e navigazione riusciti! Salvo cookie...")
            save_cookies(cookies_dict, cookie_string, session)
            log("✅ Fatto. Cookie salvati in /tmp/easyhits4u/")
            log(f"   🌐 Per scaricare l'ultima stringa cookie, usa: curl http://localhost:{PORT}/cookies")
            log("   ⚠️ Il servizio rimane in esecuzione per servire il file. Premi Ctrl+C per fermarlo.")
            # Mantieni il processo vivo
            while True:
                time.sleep(60)
        else:
            log(f"   ❌ Tentativo fallito con questa chiave")
    
    log("❌ Login fallito con tutte le chiavi. Server rimane attivo per eventuali richieste.")
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
