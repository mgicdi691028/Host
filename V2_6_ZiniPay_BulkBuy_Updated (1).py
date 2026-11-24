import requests
import time
import json
import os
import uuid
import threading
import random
import re
import html
import zipfile
import io
import pyotp
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from collections import Counter 
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from datetime import datetime 
from urllib.parse import urljoin, urlparse, parse_qs

# ==========================================
# Configuration (Token & Owner ID)
# ==========================================
TOKEN = "9107434537:AAHH13WRHOut7CrdpT6gkx9xJG9PoS4QiYM"  # Generate a fresh token with @BotFather
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
FILE_URL = f"https://api.telegram.org/file/bot{TOKEN}/"

OWNER_ID = 6996098541
BOT_USERNAME = ""
DB_FILE = "bot_data.json"

# ZiniPay Sandbox/API configuration.
# Keep this key private. Replace it if it is ever exposed publicly.
ZINIPAY_API_KEY = "a459f66f6d60985d34b6d4d7ba563b9bb9e5bcd4500edf79"
ZINIPAY_API_BASE = "https://api.zinipay.com"
ZINIPAY_TIMEOUT = 25
ZINIPAY_PUBLIC_BASE_URL = "https://host-production-426d5dd3.up.railway.app"
ZINIPAY_REDIRECT_URL = ZINIPAY_PUBLIC_BASE_URL + "/zinipay/success"
ZINIPAY_CANCEL_URL = ZINIPAY_PUBLIC_BASE_URL + "/zinipay/cancel"
ZINIPAY_WEBHOOK_URL = ZINIPAY_PUBLIC_BASE_URL + "/zinipay/webhook"

# ==========================================
# Premium Emoji Database
# ==========================================
PEM = {
    "ok": '<tg-emoji emoji-id="5352694861990501856">✅</tg-emoji>',
    "no": '<tg-emoji emoji-id="5420130255174145507">❌</tg-emoji>',
    "warn": '<tg-emoji emoji-id="5336944168944047463">⚠️</tg-emoji>',
    "admin": '<tg-emoji emoji-id="5353032893096567467">📊</tg-emoji>',
    "user": '<tg-emoji emoji-id="5352861489541714456">👤</tg-emoji>',
    "file": '<tg-emoji emoji-id="5352721946054268944">📁</tg-emoji>',
    "rocket": '<tg-emoji emoji-id="5352597830089347330">🚀</tg-emoji>',
    "graph": '<tg-emoji emoji-id="5352877703043258544">📊</tg-emoji>',
    "money": '<tg-emoji emoji-id="5348469219761626211">💸</tg-emoji>',
    "gift": '<tg-emoji emoji-id="5420396762189831222">🎁</tg-emoji>',
    "msg": '<tg-emoji emoji-id="5337302974806922068">💬</tg-emoji>',
    "gear": '<tg-emoji emoji-id="5420155432272438703">⚙️</tg-emoji>',
    "link": '<tg-emoji emoji-id="5420517437885943844">🔗</tg-emoji>',
    "trash": '<tg-emoji emoji-id="5422557736330106570">🗑</tg-emoji>',
    "upload": '<tg-emoji emoji-id="5353001161878182134">📤</tg-emoji>',
    "world": '<tg-emoji emoji-id="5336972142066047577">🌐</tg-emoji>',
    "lock": '<tg-emoji emoji-id="5353022963132174959">🔐</tg-emoji>',
    "phone": '<tg-emoji emoji-id="5337132498965010628">📱</tg-emoji>',
    "num": '<tg-emoji emoji-id="5352862640592949843">🔢</tg-emoji>',
    "pin": '<tg-emoji emoji-id="5352922460897452503">📍</tg-emoji>',
    "star": '<tg-emoji emoji-id="5352552689983067014">✨</tg-emoji>',
    "hi": '<tg-emoji emoji-id="5353027129250453493">👋</tg-emoji>'
}

GLOBAL_BODY_EMOJIS = {
    "➖": "5870818207383686839", "🚫": "5334807341109908955", "😒": "5334763399299506604",
    "🖥": "5334880948259427772", "🌐": "5334590977837403844", "🌟": "5337102391244263212",
    "🕓": "5336983442125001376", "⌛": "5337172996211648018", "💬": "5337302974806922068",
    "🔐": "5337255927735163754", "🍏": "5337132498965010628", "❔": "5336850036145823599",
    "⚠️": "5336944168944047463", "🔥": "5337267511261960341", "💸": "5348469219761626211",
    "🥚": "5348390922507817684", "👨‍⚖": "5334763399299506604", "🐁": "5348494358205207761",
    "🧻": "5348486915026884464", "⚗": "5346311574221000149", "🛴": "5348075478634766440",
    "📊": "5353032893096567467", "🔢": "5352862640592949843", "👤": "5352861489541714456",
    "📁": "5352721946054268944", "🚀": "5352597830089347330", "💎": "5352838545826420397",
    "📍": "5352922460897452503", "👋": "5353027129250453493", "✅": "5352694861990501856",
    "1️⃣": "5352651766288652742", "2️⃣": "5355186458418257716", "3️⃣": "5352867219028091093",
    "4️⃣": "5352566657216714037", "5️⃣": "5353086880835474989", "6️⃣": "5354859211975071385",
    "7️⃣": "5352859127309707652", "8️⃣": "5352957533600389988", "9️⃣": "5353060913463204207",
    "🔤": "5352727417842606016", "📣": "5352980533150259581", "📤": "5353001161878182134",
    "✨": "5352552689983067014", "🔹": "5352638632278660622", "🎙": "5355102594886833928",
    "💴": "5352985330628730418", "📅": "5352585194295564660", "📴": "5352974971167611327",
    "✏️": "5395444784611480792", "📱": "5337132498965010628", "🔗": "5420517437885943844",
    "❌": "5420130255174145507", "⚙️": "5420155432272438703", "🫂": "5420145051336485498",
    "➕": "5420323438508155202", "🗑": "5422557736330106570", "🎁": "5420396762189831222",
    "➤": "5420618897898381296", "🏢": "5420156334215565595", "💳": "5190899075968441286",
    "📝": "5192739271886282680", "🛡": "5190447043545438788", "🤝": "5192805934073685937",
    "💰": "5190576863226933563", "👀": "5190645917711114179", "🕹": "5193100774988617665",
    "🟢": "5192812028632274956", "🧪": "5190781475468915802", "🎨": "5190751148704833975",
    "📂": "5257969839313526622", "🌍": "5780471598922337683", "📌": "5318986077455795572",
    "📢": "5789428375261023681", "🆔": "5352862640592949843", "📈": "5352877703043258544",
    "🔔": "5352980533150259581", "🏦": "5348469219761626211", "🧾": "5192739271886282680",
    "👨‍⚖️": "5334763399299506604", "🔍": "5463352748751753567",
    "🔑": "5197288647275071607"
}

DEFAULT_CUSTOM_MESSAGES = {
    "start": {"text": "╔═══════════╗\n       📊 NUMBER BOT\n╚═══════════╝\n🚀 Welcome to Number & OTP Service\n━━━━━━━━━━━━\n✅ Choose an option below\nto continue using the bot.\n━━━━━━━━━━━━\n💎 Premium OTP Service", "buttons": []},
    "get_number": {"text": f"{PEM['pin']} Select a service:", "buttons": []},
    "new_number": {"text": "{flag} NEW NUMBER", "buttons": []},
    "select_country": {"text": f"📌 Select a country for {{service}}:", "buttons": []}, 
    "search_number": {"text": "╔═══════════╗\n     🔍 <b>SEARCH NUMBER</b>\n╚═══════════╝\n✅ Enter 3 to 9 digits  \nto search for a number.\n━━━━━━━━━━━━━\n📝 Example:\n➥ 880\n➥ 9227373\n━━━━━━━━━━━━━\n🔍 Fast Number Lookup System", "buttons": []},
    "traffic": {"text": f"{PEM['graph']} <b>Traffic Overview</b>\n\n{PEM['ok']} Available Numbers: {{avail}}\n{PEM['rocket']} Assigned Numbers: {{assigned}}", "buttons": []},
    "refer": {"text": f"➖➖➖➖➖➖➖\n« {PEM['gift']} REFER & EARN »\n➖➖➖➖➖➖➖\n{PEM['link']} YOUR LINK:\n<code>{{ref_link}}</code>\n➖➖➖➖➖➖➖\n{PEM['user']} TOTAL REFERS: <b>{{total_ref}}</b>\n➖➖➖➖➖➖➖\n{PEM['money']} PER REFER: <b>{{ref_reward}} TK</b>\n➖➖➖➖➖➖➖", "buttons": []},
    "withdrawal": {"text": "➖➖➖➖➖➖➖\n《 😒 WITHDRAWAL 》\n➖➖➖➖➖➖➖\n👋 Total Otp: {total_otp}\n➖➖➖➖➖➖➖\n🫂 Total Reffer :{total_ref}\n➖➖➖➖➖➖➖\n📅 BALANCE: {bal}৳\n➖➖➖➖➖➖➖\n🔐 MINIMUM: {min_w} ৳\n➖➖➖➖➖➖➖\nSELECT METHOD:", "buttons": []},
    "support": {"text": f"{PEM['msg']} Contact us for any help:", "buttons": []}
}

# ==========================================
# Local Persistent Database (No Firebase Required)
# ==========================================
# This replaces the old Firebase/local database dependency with a small
# JSON-backed local database. It works on Railway and other hosts
# without Firebase credentials or the firebase-admin package.

LOCAL_DB_FILE = "local_db.json"

class Increment:
    def __init__(self, amount):
        self.amount = amount

SERVER_TIMESTAMP = object()

class LocalDocumentSnapshot:
    def __init__(self, doc_id, data):
        self.id = str(doc_id)
        self._data = dict(data) if isinstance(data, dict) else {}
        self.exists = bool(data is not None)

    def to_dict(self):
        return dict(self._data)

class LocalDocumentReference:
    def __init__(self, store, collection_name, doc_id):
        self.store = store
        self.collection_name = str(collection_name)
        self.doc_id = str(doc_id)

    def get(self):
        with self.store.lock:
            data = self.store.data.setdefault("collections", {}).setdefault(
                self.collection_name, {}
            ).get(self.doc_id)
            return LocalDocumentSnapshot(self.doc_id, data)

    def set(self, values, merge=False):
        with self.store.lock:
            collection = self.store.data.setdefault("collections", {}).setdefault(
                self.collection_name, {}
            )
            old = dict(collection.get(self.doc_id, {})) if merge else {}
            collection[self.doc_id] = self.store._resolve_values(old, values)
            self.store._save_unlocked()
        return self

    def update(self, values):
        with self.store.lock:
            collection = self.store.data.setdefault("collections", {}).setdefault(
                self.collection_name, {}
            )
            if self.doc_id not in collection:
                raise KeyError(self.doc_id)
            old = dict(collection[self.doc_id])
            collection[self.doc_id] = self.store._resolve_values(old, values)
            self.store._save_unlocked()
        return self

class LocalQuery:
    def __init__(self, store, collection_name, selected_fields=None,
                 order_field=None, descending=False, limit_count=None):
        self.store = store
        self.collection_name = str(collection_name)
        self.selected_fields = selected_fields
        self.order_field = order_field
        self.descending = descending
        self.limit_count = limit_count

    def select(self, fields):
        return LocalQuery(
            self.store, self.collection_name, fields,
            self.order_field, self.descending, self.limit_count
        )

    def order_by(self, field, direction="ASCENDING"):
        return LocalQuery(
            self.store, self.collection_name, self.selected_fields,
            field, str(direction).upper() == "DESCENDING", self.limit_count
        )

    def limit(self, count):
        return LocalQuery(
            self.store, self.collection_name, self.selected_fields,
            self.order_field, self.descending, int(count)
        )

    def stream(self):
        with self.store.lock:
            collection = dict(
                self.store.data.setdefault("collections", {}).setdefault(
                    self.collection_name, {}
                )
            )

        items = list(collection.items())
        if self.order_field:
            def sort_key(item):
                value = item[1].get(self.order_field)
                if value is None:
                    return (0, "")
                return (1, value)
            try:
                items.sort(key=sort_key, reverse=self.descending)
            except TypeError:
                items.sort(key=lambda item: str(item[1].get(self.order_field, "")),
                           reverse=self.descending)

        if self.limit_count is not None:
            items = items[:self.limit_count]

        for doc_id, data in items:
            if self.selected_fields:
                selected = {k: data[k] for k in self.selected_fields if k in data}
            else:
                selected = data
            yield LocalDocumentSnapshot(doc_id, selected)

class LocalCollection:
    def __init__(self, store, collection_name):
        self.store = store
        self.collection_name = str(collection_name)

    def document(self, doc_id):
        return LocalDocumentReference(self.store, self.collection_name, doc_id)

    def select(self, fields):
        return LocalQuery(self.store, self.collection_name, selected_fields=fields)

    def order_by(self, field, direction="ASCENDING"):
        return LocalQuery(
            self.store, self.collection_name,
            order_field=field,
            descending=str(direction).upper() == "DESCENDING"
        )

class LocalStore:
    def __init__(self, filename=LOCAL_DB_FILE):
        self.filename = filename
        self.lock = threading.RLock()
        self.data = {"collections": {}}
        self._load()

    def _load(self):
        try:
            if os.path.exists(self.filename):
                with open(self.filename, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    self.data = loaded
            self.data.setdefault("collections", {})
        except Exception as e:
            print(f"⚠️ Local DB load warning: {e}")
            self.data = {"collections": {}}

    def _resolve_values(self, old, values):
        result = dict(old)
        for key, value in values.items():
            if isinstance(value, Increment):
                try:
                    current = float(result.get(key, 0) or 0)
                    new_value = current + float(value.amount)
                    if new_value.is_integer():
                        new_value = int(new_value)
                    result[key] = new_value
                except (TypeError, ValueError):
                    result[key] = value.amount
            elif value is SERVER_TIMESTAMP:
                result[key] = time.time()
            else:
                result[key] = value
        return result

    def _save_unlocked(self):
        tmp = self.filename + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.filename)

    def collection(self, collection_name):
        return LocalCollection(self, collection_name)

db = LocalStore()
print("✅ Local JSON database enabled (Firebase removed).")

bot_settings = {
    "admins": [OWNER_ID],
    "special_users": [],
    "panels": [], 
    "fw_groups": [], 
    "otp_link": "https://t.me/your_otp_group",
    "withdraw_on": True,
    "min_withdraw": 30.0,
    "otp_reward": 0.1,
    "refer_reward": 0.2,
    "cooldown": 10,
    "num_req": 1,
    "num_share": 1, 
    "support_link": "https://t.me/your_support",
    "support_button_name": "Support",
    "w_methods": ["bKash", "Nagad"],
    "w_group": "",
    "traffic_window_minutes": 30,
    "paid_expiry_minutes": 720,
    "cancel_cooldown_minutes": 5,
    "console_traffic_mode": "on",
    "console_traffic": True, 
    "console_otp": False, 
    
    "fj_on": False,
    "fj_channels": [], 
    "stex_keys": [], 
    "voltx_keys": [],
    "zenex_keys": [],
    "search_countries": [],
    "stex_services": {},
    "voltx_services": {},
    "zenex_services": {},
    "premium_flags": {
        "1": {"char": "🇺🇸", "iso": "US", "name": "United States", "id": "5913463998522592692"},
        "880": {"char": "🇧🇩", "iso": "BD", "name": "Bangladesh", "id": "5911365056594973179"},
        "91": {"char": "🇮🇳", "iso": "IN", "name": "India", "id": "5913754823643107921"},
        "92": {"char": "🇵🇰", "iso": "PK", "name": "Pakistan", "id": "5913705895375672082"},
        "44": {"char": "🇬🇧", "iso": "GB", "name": "United Kingdom", "id": "5913443365499703513"}
    },
    "premium_apps": {
        "FACEBOOK": {"char": "🚫", "id": "5334807341109908955", "name": "Facebook"},
        "WHATSAPP": {"char": "🚫", "id": "5334759662677957452", "name": "WhatsApp"}
    },
    "custom_messages": DEFAULT_CUSTOM_MESSAGES.copy(),
    "reply_keyboard_emojis": {
        "Get Number": "5337132498965010628",
        "Refer": "5420396762189831222",
        "My Profile": "5352861489541714456",
        "Deposit": "5190899075968441286",
        "Support": "5420145051336485498",
        "Admin Panel": "5420155432272438703"
    }
}

FS_KEYS = [
    "admins", "special_users", "panels", "fw_groups", "otp_link", "withdraw_on", 
    "min_withdraw", "otp_reward", "refer_reward", "cooldown", 
    "num_req", "num_share", "support_link", "support_button_name", "w_methods", "stex_keys", "voltx_keys", "search_countries", "stex_services", "voltx_services",
    "fj_on", "fj_channels", "console_otp", "voltx_auto", "stex_auto", "zenex_auto", "zenex_keys", "zenex_services", "zenex_search_countries"
]

number_batches = {}
bulk_sales = {}  # completed store-style bulk purchases; no OTP polling
bulk_contexts = {}
used_numbers_list = []
rejected_numbers_list = []
stex_assigned_numbers = {} 
voltx_assigned_numbers = {}
zenex_assigned_numbers = {}
purchase_lock = threading.RLock()   # protects stock / balance / paid sessions
callback_guard_lock = threading.RLock()
callback_seen_ids = set()
callback_action_times = {}
callback_answered_ids = set()
paid_sessions = {}                  # number -> paid number session (persisted)
paid_user_current = {}              # user_id -> currently active paid number
STEX_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tness/@public/api"
VOLTX_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api"
ZENEX_BASE_URL = "https://api.zenexnetwork.com"
total_uploaded_stats = 0
total_assigned_stats = 0
processed_otps = set() 
recent_traffic = []
user_banned_cache = {}

# Active HTTP sessions for Auto Captcha Panels
panel_sessions = {}

# 🌟 sAjaxSource (AJAX/DataTable) এবং Fallback HTML Parser Helper Function
def fetch_cpt_panel_cdrs(p, session, check_url):
    res = session.get(check_url, timeout=15)
    html_text = res.text
    
    # সেশন শেষ হয়েছে বা লগইন পেজে রিডাইরেক্ট করেছে কি না তা চেক করা
    if "login" in html_text.lower() or "signin" in html_text.lower() or any(x in html_text for x in ["Sign in to your account", "Please sign in", "Welcome back!"]):
        raise Exception("Session expired")
        
    soup = BeautifulSoup(html_text, 'html.parser')
    s_ajax_source = ""
    for script in soup.find_all("script"):
        script_text = script.string or ""
        match = re.search(r'sAjaxSource":\s*"([^"]+)"', script_text)
        if match:
            s_ajax_source = match.group(1)
            break
            
    results = []
    
    n_col_name = p.get("num_col_name", "number").lower()
    m_col_name = p.get("msg_col_name", "message").lower()
    n_idx = int(p.get("num_col_idx", 1)) - 1 if p.get("num_col_idx") else 1
    m_idx = int(p.get("msg_col_idx", 2)) - 1 if p.get("msg_col_idx") else 2

    # ৫.১ যদি sAjaxSource AJAX লিংক পাওয়া যায়
    if s_ajax_source:
        baseUrl = p.get("login_url", "").split("/client")[0].split("/login")[0].strip()
        if not baseUrl.startswith("http"):
            baseUrl = "http://" + baseUrl
            
        full_ajax_url = ""
        if s_ajax_source.startswith("http"):
            full_ajax_url = s_ajax_source
        elif s_ajax_source.startswith("/"):
            full_ajax_url = f"{baseUrl}{s_ajax_source}"
        else:
            last_slash_idx = check_url.rfind("/")
            current_dir = check_url[:last_slash_idx]
            full_ajax_url = f"{current_dir}/{s_ajax_source}"

        if "iDisplayLength" not in full_ajax_url:
            # 250 এর জায়গায় 10000 করে দেওয়া হলো যাতে সব মেসেজ ফেচ করতে পারে
            query_params = "sEcho=1&iColumns=7&iDisplayStart=0&iDisplayLength=10000&sSearch=&iSortingCols=1&iSortCol_0=0&sSortDir_0=desc"
            divider = "&" if "?" in full_ajax_url else "?"
            full_ajax_url += f"{divider}{query_params}"

        ajax_headers = {
            "Referer": check_url,
            "X-Requested-With": "XMLHttpRequest"
        }
        
        ajax_res = session.get(full_ajax_url, headers=ajax_headers, timeout=15)
        data_dict = ajax_res.json()
        rows = data_dict.get("aaData", [])
        for row_val in rows:
            if not isinstance(row_val, list):
                continue
                
            if len(row_val) < max(n_idx, m_idx) + 1:
                continue
                
            num_val = row_val[n_idx] if (0 <= n_idx < len(row_val)) else row_val[2]
            msg_val = row_val[m_idx] if (0 <= m_idx < len(row_val)) else row_val[4]
            
            clean_num = re.sub(r'\D', '', str(num_val))
            if clean_num and 5 <= len(clean_num) <= 18:
                otp = extract_otp_code(msg_val)
                if otp and len(msg_val) > 4:
                    results.append({"number": clean_num, "message": msg_val, "otp": otp})
                    
    else:
        # ৫.২ ডাইরেক্ট HTML টেবিল থেকে রিড করার ব্যাকআপ লজিক
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            if not rows: continue
            
            final_n_idx = n_idx
            final_m_idx = m_idx
            
            header_cells = rows[0].find_all(['th', 'td'])
            for i, cell in enumerate(header_cells):
                c_text = cell.get_text(strip=True).lower()
                if n_col_name in c_text: final_n_idx = i
                if m_col_name in c_text: final_m_idx = i

            for row in rows:
                cols = row.find_all(['td', 'th'])
                if all(c.name == 'th' for c in cols): continue
                
                if len(cols) > max(final_n_idx, final_m_idx):
                    num_text = cols[final_n_idx].get_text(separator=" ", strip=True)
                    msg_text = cols[final_m_idx].get_text(separator=" ", strip=True)
                    
                    clean_num = re.sub(r'\D', '', num_text)
                    if clean_num and 5 <= len(clean_num) <= 18:
                        otp = extract_otp_code(msg_text)
                        if otp and len(msg_text) > 4:
                            results.append({"number": clean_num, "message": msg_text, "otp": otp})
                            
    return results, html_text

# Track active number sessions to expire them automatically
user_active_sessions = {}

assigned_number_rates = {}

def is_special_user(user_id):
    try:
        uid = int(user_id)
    except (TypeError, ValueError):
        uid = user_id
    return uid in set(bot_settings.get("special_users", [])) or str(uid) in {str(x) for x in bot_settings.get("special_users", [])}

def get_otp_reward_for_user(number, user_id):
    """Return the reward configured for this uploaded number and user type."""
    info = assigned_number_rates.get(number)
    if info is None:
        # Backward compatibility with old stock files and API numbers.
        return float(bot_settings.get("otp_reward", 0.0))
    if isinstance(info, dict):
        key = "special" if is_special_user(user_id) else "normal"
        try:
            return float(info.get(key, info.get("normal", bot_settings.get("otp_reward", 0.0))))
        except (TypeError, ValueError):
            return 0.0
    try:
        return float(info)
    except (TypeError, ValueError):
        return 0.0

def special_user_management_text():
    users = bot_settings.get("special_users", [])
    lines = "\n".join(f"• <code>{html.escape(str(uid))}</code>" for uid in users) if users else "<i>No special users set.</i>"
    return render_body_text(
        f"<b>SPECIAL USER MANAGEMENT</b>\n\n"
        f"<b>Special User IDs:</b>\n{lines}\n\n"
        f"Special users will receive the Special User OTP earning rate configured during number upload."
    )

def load_db():
    global bot_settings, number_batches, bulk_sales, used_numbers_list, rejected_numbers_list, total_uploaded_stats, total_assigned_stats, recent_traffic, stex_assigned_numbers, voltx_assigned_numbers, processed_otps, assigned_number_rates, paid_sessions
    
    loaded_from_local = False
    
    # ১. প্রথমে Local DB লোড করবে (এটি সবচেয়ে আপডেট থাকে, তাই Key হারাবে না)
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding='utf-8') as f:
                data = json.load(f)
                saved_settings = data.get("bot_settings", {})
                for key, val in saved_settings.items():
                    if key == "custom_messages":
                        for m_key, m_val in val.items():
                            bot_settings["custom_messages"][m_key] = m_val
                    else:
                        bot_settings[key] = val
                        
                for m_key, m_val in DEFAULT_CUSTOM_MESSAGES.items():
                    if m_key not in bot_settings["custom_messages"]:
                        bot_settings["custom_messages"][m_key] = m_val
                        
                number_batches = data.get("number_batches", {})
                bulk_sales = data.get("bulk_sales", {})
                used_numbers_list = data.get("used_numbers_list", [])
                rejected_numbers_list = data.get("rejected_numbers_list", [])
                total_uploaded_stats = data.get("total_uploaded_stats", 0)
                total_assigned_stats = data.get("total_assigned_stats", 0)
                recent_traffic = data.get("recent_traffic", [])
                stex_assigned_numbers = data.get("stex_assigned_numbers", {})
                voltx_assigned_numbers = data.get("voltx_assigned_numbers", {})
                zenex_assigned_numbers = data.get("zenex_assigned_numbers", {})
                processed_otps = set(data.get("processed_otps", []))
                assigned_number_rates = data.get("assigned_number_rates", {})
                paid_sessions = data.get("paid_sessions", {})
                loaded_from_local = True
            print("✅ Local Stock/UI DB Loaded Successfully!")
        except Exception as e:
            print(f"❌ Error loading local DB: {e}")

    # All persistent configuration is stored locally; no external database is required.

def save_local_db():
    with purchase_lock:
        _save_local_db_inner()

def _save_local_db_inner():
    local_data = {
        "bot_settings": bot_settings,
        "number_batches": number_batches,
        "bulk_sales": bulk_sales,
        "used_numbers_list": used_numbers_list,
        "rejected_numbers_list": rejected_numbers_list,
        "total_uploaded_stats": total_uploaded_stats,
        "total_assigned_stats": total_assigned_stats,
        "recent_traffic": recent_traffic,
        "stex_assigned_numbers": stex_assigned_numbers,
        "voltx_assigned_numbers": voltx_assigned_numbers,
        "zenex_assigned_numbers": zenex_assigned_numbers,
        "processed_otps": list(processed_otps),
        "assigned_number_rates": assigned_number_rates,
        "paid_sessions": paid_sessions,
        "pending_withdrawals": globals().get("pending_withdrawals", {})
    }
    try:
        with open(DB_FILE, "w", encoding='utf-8') as f:
            json.dump(local_data, f, indent=4)
    except Exception as e:
        pass

def save_db():
    # bot_data.json stores stock/settings state; user/withdrawal data is
    # persisted by LocalStore in local_db.json.
    save_local_db()


load_db()
# Migrate the previous 20-minute default to the requested 12-hour no-OTP refund window.
if int(bot_settings.get("paid_expiry_minutes", 720) or 720) == 20:
    bot_settings["paid_expiry_minutes"] = 720
bot_settings.setdefault("cancel_cooldown_minutes", 5)
# Remove legacy deposit configuration left by older database versions.
for _obsolete_key in ("deposit_on", "min_deposit", "deposit_methods"):
    bot_settings.pop(_obsolete_key, None)

user_states = {}
temp_data = {}
user_cooldowns = {}
pending_withdrawals = {}

def restore_pending_withdrawals():
    global pending_withdrawals
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            saved = data.get("pending_withdrawals", {})
            if isinstance(saved, dict):
                pending_withdrawals.clear()
                pending_withdrawals.update(saved)
    except Exception as e:
        print(f"Pending withdrawal restore warning: {e}")

restore_pending_withdrawals()

# ==========================================
# Universal Number File Parser
# ==========================================
def _normalize_uploaded_number(value):
    if value is None: return None
    digits = re.sub(r"\D", "", str(value).strip())
    if not (5 <= len(digits) <= 18): return None
    return "+" + digits

def _extract_numbers_from_text(text):
    if not text: return []
    text = str(text).replace("\x00", " ")
    found = []
    pattern = re.compile(r"(?<!\d)(?:\+\d[\d\s().-]{4,24}\d|\d[\d\s().-]{4,24}\d)(?!\d)")
    for m in pattern.finditer(text):
        n = _normalize_uploaded_number(m.group(0))
        if n: found.append(n)
    for m in re.finditer(r"(?<!\d)\d{5,18}(?!\d)", text):
        n = _normalize_uploaded_number(m.group(0))
        if n: found.append(n)
    return found

def _xlsx_text_values(raw):
    import xml.etree.ElementTree as ET
    values=[]
    with zipfile.ZipFile(io.BytesIO(raw),'r') as z:
        names=z.namelist(); shared=[]
        if 'xl/sharedStrings.xml' in names:
            root=ET.fromstring(z.read('xl/sharedStrings.xml')); ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            for si in root.findall('.//m:si',ns): shared.append(''.join(x.text or '' for x in si.findall('.//m:t',ns)))
        ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        for name in names:
            if not (name.startswith('xl/worksheets/') and name.endswith('.xml')): continue
            root=ET.fromstring(z.read(name))
            for cell in root.findall('.//m:c',ns):
                v=cell.find('m:v',ns)
                if v is None or v.text is None: continue
                val=v.text
                if cell.get('t')=='s':
                    try: val=shared[int(val)]
                    except: pass
                values.append(val)
            for inline in root.findall('.//m:is',ns):
                val=''.join(x.text or '' for x in inline.findall('.//m:t',ns))
                if val: values.append(val)
    return values

def _docx_text_values(raw):
    import xml.etree.ElementTree as ET
    values=[]
    with zipfile.ZipFile(io.BytesIO(raw),'r') as z:
        for name in z.namelist():
            if name.startswith('word/') and name.endswith('.xml'):
                try: root=ET.fromstring(z.read(name))
                except: continue
                vals=[e.text for e in root.iter() if e.tag.endswith('}t') and e.text]
                if vals: values.append(' '.join(vals))
    return values

def extract_numbers_from_uploaded_file(filename, raw):
    """Accept any Telegram document; parse common formats and scan unknown ones."""
    ext=os.path.splitext(str(filename).lower())[1]; texts=[]
    if ext in {'.xlsx','.xlsm','.xltx','.xltm'}:
        try: texts.extend(_xlsx_text_values(raw))
        except Exception as e: print(f'XLSX parser warning: {e}')
    elif ext=='.docx':
        try: texts.extend(_docx_text_values(raw))
        except Exception as e: print(f'DOCX parser warning: {e}')
    elif ext=='.pdf':
        for mod in ('pypdf','PyPDF2'):
            try:
                m=__import__(mod); reader=m.PdfReader(io.BytesIO(raw))
                for page in reader.pages: texts.append(page.extract_text() or '')
                break
            except: pass
    if not texts or ext not in {'.xlsx','.xlsm','.xltx','.xltm','.docx','.pdf'}:
        for enc in ('utf-8-sig','utf-8','utf-16','latin-1'):
            try: texts.append(raw.decode(enc)); break
            except: pass
    if not texts: texts.append(''.join(chr(b) if 32<=b<127 else ' ' for b in raw))
    nums=[]
    for value in texts: nums.extend(_extract_numbers_from_text(value))
    return list(dict.fromkeys(nums))

# ==========================================
# Telegram API & Helpers
# ==========================================
tg_session = requests.Session() # 🌟 Keep-Alive Connection (Makes bot 10x faster)

def api_call(method, payload=None):
    url = f"{BASE_URL}/{method}"
    try:
        # 🌟 Added timeout to prevent hanging!
        res = tg_session.post(url, json=payload, timeout=15)
        return res.json()
    except Exception as e:
        return {}

def send_message(chat_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if reply_markup: payload["reply_markup"] = reply_markup
    return api_call("sendMessage", payload)

def send_photo(chat_id, photo_url_or_file_id, caption="", reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "photo": photo_url_or_file_id, "caption": caption, "parse_mode": parse_mode}
    if reply_markup: payload["reply_markup"] = reply_markup
    return api_call("sendPhoto", payload)

def edit_message(chat_id, message_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if reply_markup: payload["reply_markup"] = reply_markup
    return api_call("editMessageText", payload)

def delete_message(chat_id, message_id):
    return api_call("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

def answer_callback(callback_id, text="", show_alert=False):
    callback_key = str(callback_id or "")
    if callback_key:
        with callback_guard_lock:
            if callback_key in callback_answered_ids:
                return
            callback_answered_ids.add(callback_key)
            if len(callback_answered_ids) > 5000:
                callback_answered_ids.clear()
                callback_answered_ids.add(callback_key)
    api_call("answerCallbackQuery", {"callback_query_id": callback_id, "text": text, "show_alert": show_alert})

def send_document(chat_id, filename, text_content, caption=None):
    """Send a generated text file to Telegram."""
    url = f"{BASE_URL}/sendDocument"
    if isinstance(text_content, str):
        text_content = text_content.encode("utf-8")
    files = {"document": (str(filename), text_content, "text/plain")}
    data = {"chat_id": chat_id}
    if caption:
        data["caption"] = str(caption)
    try:
        response = tg_session.post(url, data=data, files=files, timeout=30)
        return response.json()
    except Exception as exc:
        print(f"sendDocument error: {exc}")
        return {}

# 🌟 Local User List
all_known_users = set()

def sync_users_list():
    global all_known_users
    try:
        if os.path.exists("users_list.json"):
            with open("users_list.json", "r") as f:
                all_known_users = set(json.load(f))
        if not all_known_users and db:
            for doc in db.collection('users').select([]).stream():
                all_known_users.add(doc.id)
            with open("users_list.json", "w") as f:
                json.dump(list(all_known_users), f)
    except: pass

threading.Thread(target=sync_users_list, daemon=True).start()

def _save_users_list():
    try:
        with open("users_list.json", "w") as f:
            json.dump(list(all_known_users), f)
    except: pass

def register_user_local(uid):
    uid_str = str(uid)
    if uid_str not in all_known_users:
        all_known_users.add(uid_str)
        # 🌟 Non-blocking background save (Prevents lag)
        threading.Thread(target=_save_users_list, daemon=True).start()

def broadcast_copymessage(from_chat_id, msg_id, status_msg_id=None):
    success = 0
    failed = 0
    users = list(all_known_users)
    
    # 🌟 Dedicated Connection Pool for Broadcast (Fixes Port Exhaustion & Network Lag)
    b_session = requests.Session()
    url = f"{BASE_URL}/copyMessage"
    
    for user_id in users:
        payload = {"chat_id": user_id, "from_chat_id": from_chat_id, "message_id": msg_id}
        try:
            res = b_session.post(url, json=payload, timeout=5).json()
            if res.get("ok"): success += 1
            else: failed += 1
        except:
            failed += 1
        time.sleep(0.035) # Safe speed (28 msgs/sec) to prevent Telegram Ban

    if status_msg_id:
        try:
            delete_message(from_chat_id, status_msg_id)
        except Exception:
            pass
        

def render_body_text(text):
    if not text: return str(text)
    parts = re.split(r'(<tg-emoji.*?</tg-emoji>)', str(text))
    for i in range(len(parts)):
        if not parts[i].startswith('<tg-emoji'):
            for normal_emj, prem_id in GLOBAL_BODY_EMOJIS.items():
                if normal_emj in parts[i]:
                    parts[i] = parts[i].replace(normal_emj, f'<tg-emoji emoji-id="{prem_id}">{normal_emj}</tg-emoji>')
    return "".join(parts)

def extract_premium_html(msg):
    text = msg.get("text", msg.get("caption", ""))
    entities = msg.get("entities", msg.get("caption_entities", []))
    if not entities: return text
    try:
        b_text = text.encode('utf-16-le')
        c_entities = [e for e in entities if e.get("type") == "custom_emoji"]
        c_entities.sort(key=lambda x: x["offset"], reverse=True)
        for ent in c_entities:
            offset = ent["offset"] * 2
            length = ent["length"] * 2
            eid = ent["custom_emoji_id"]
            emoji_char = b_text[offset:offset+length].decode('utf-16-le')
            html_tag = f'<tg-emoji emoji-id="{eid}">{emoji_char}</tg-emoji>'
            replacement = html_tag.encode('utf-16-le')
            b_text = b_text[:offset] + replacement + b_text[offset+length:]
        return b_text.decode('utf-16-le')
    except Exception as e:
        return text 

def get_flag_info_from_num(num):
    clean = num.replace("+", "").replace(" ", "")
    sorted_codes = sorted(bot_settings.get("premium_flags", {}).keys(), key=len, reverse=True)
    for code in sorted_codes:
        if clean.startswith(code):
            data = bot_settings["premium_flags"][code]
            return data["char"], data.get("iso", "XX"), data.get("id")
    return "🌍", "XX", None

def get_flag_and_code(num):
    char, iso, _ = get_flag_info_from_num(num)
    return char, iso

def get_premium_flag_html_by_iso(iso):
    """Return the configured Telegram custom-emoji flag for a country ISO."""
    iso = str(iso or "").upper().strip()
    for _calling_code, data in bot_settings.get("premium_flags", {}).items():
        if str(data.get("iso", "")).upper() == iso:
            char = str(data.get("char", "") or "")
            emoji_id = str(data.get("id", "") or "")
            if char and emoji_id.isdigit():
                return f'<tg-emoji emoji-id="{emoji_id}">{char}</tg-emoji>'
            if char:
                return char
    if len(iso) == 2 and iso.isalpha():
        return chr(0x1F1E6 + ord(iso[0]) - ord("A")) + chr(0x1F1E6 + ord(iso[1]) - ord("A"))
    return "🌍"

def get_flag_info_html(num_or_iso, return_full_name=False):
    if len(num_or_iso) == 2:
        for code, data in bot_settings.get("premium_flags", {}).items():
            if data.get("iso") == num_or_iso:
                eid = data.get("id")
                char = data.get("char")
                name = data.get("name", num_or_iso)
                if return_full_name: return name
                if eid: return f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
                return char
        if return_full_name: return num_or_iso
        return "🌍"
        
    char, _, eid = get_flag_info_from_num(num_or_iso)
    if return_full_name:
        for code, data in bot_settings.get("premium_flags", {}).items():
            clean = num_or_iso.replace("+", "").replace(" ", "")
            if clean.startswith(code): return data.get("name", num_or_iso)
        return num_or_iso
        
    if eid:
        return f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
    return char

def get_uploaded_country_iso(country_name):
    """Resolve the manually-entered uploaded-stock country to its ISO code.
    Match configured premium flag names first; never infer from the phone prefix.
    """
    wanted = re.sub(r"[^a-z0-9]", "", str(country_name or "").lower())
    aliases = {
        "unitedstates": "US", "unitedstatesofamerica": "US", "usa": "US", "us": "US",
        "america": "US", "uk": "GB", "unitedkingdom": "GB", "greatbritain": "GB",
        "southkorea": "KR", "republicofkorea": "KR", "northkorea": "KP",
        "russia": "RU", "russianfederation": "RU",
    }
    if wanted in aliases:
        return aliases[wanted]
    for _prefix, info in bot_settings.get("premium_flags", {}).items():
        name = re.sub(r"[^a-z0-9]", "", str(info.get("name", "")).lower())
        iso = str(info.get("iso", "")).upper()
        if wanted and (wanted == name or (name and wanted in (name,))):
            return iso
    return "XX"


def get_uploaded_country_flag_html(country_name):
    """Return the configured premium flag for the manually-entered country."""
    iso = get_uploaded_country_iso(country_name)
    if iso != "XX":
        for _calling_code, data in bot_settings.get("premium_flags", {}).items():
            if str(data.get("iso", "")).upper() == iso:
                char = str(data.get("char", "") or "")
                emoji_id = str(data.get("id", "") or "")
                if char and emoji_id.isdigit():
                    return f'<tg-emoji emoji-id="{emoji_id}">{char}</tg-emoji>'
                if char:
                    return char
        if len(iso) == 2 and iso.isalpha():
            return chr(0x1F1E6 + ord(iso[0]) - ord("A")) + chr(0x1F1E6 + ord(iso[1]) - ord("A"))
    return "🌍"


def _upsert_number_record(records, number, api_url):
    """Store number and its API URL, upgrading old number-only entries in place."""
    number = str(number)
    entry = {"num": number, "url": str(api_url or "")}
    for index, old in enumerate(records):
        old_num = str(old.get("num", "")) if isinstance(old, dict) else str(old)
        if old_num == number:
            records[index] = entry
            return
    records.append(entry)

def mask_number(num):
    clean = num.replace("+", "").replace(" ", "")
    mask = bot_settings.get("mask_emoji", {}) if "bot_settings" in globals() else {}
    mask_id = str(mask.get("id", "") or "")
    mask_char = str(mask.get("char", "") or "")
    if mask_id and mask_char:
        mask = f'<tg-emoji emoji-id="{mask_id}">{mask_char}</tg-emoji>'
    else:
        mask = mask_char or "DXA"
    if len(clean) > 7: return f"{clean[:3]}{mask}{clean[-4:]}"
    elif len(clean) > 4: return f"{clean[:1]}{mask}{clean[-4:]}"
    return clean


def mask_activity_number(num):
    """Mask activity-group purchase notices while preserving country prefix and last digits."""
    raw = str(num or "").strip()
    has_plus = raw.startswith("+")
    digits = "".join(ch for ch in raw if ch.isdigit())
    if len(digits) <= 8:
        return ("+" if has_plus else "") + digits
    # Keep the first five and last three digits, as in +88017***789.
    masked = f"{digits[:5]}***{digits[-3:]}"
    return ("+" if has_plus else "") + masked


def mask_activity_user_id(user_id):
    """Show only the first four and last two digits of a user ID in group notices."""
    digits = "".join(ch for ch in str(user_id or "") if ch.isdigit())
    if len(digits) <= 6:
        return digits
    return f"{digits[:4]}****{digits[-2:]}"

LANG_MAP = {
    "#EN": "English", "#BN": "Bengali", "#AR": "Arabic", "#HI": "Hindi", 
    "#PA": "Punjabi", "#GU": "Gujarati", "#OR": "Odia", "#TA": "Tamil", 
    "#TE": "Telugu", "#KN": "Kannada", "#ML": "Malayalam", "#SI": "Sinhala", 
    "#TH": "Thai", "#LO": "Lao", "#BO": "Tibetan", "#MY": "Burmese", 
    "#AM": "Amharic", "#KM": "Khmer", "#KA": "Georgian", "#HY": "Armenian", 
    "#HE": "Hebrew", "#EL": "Greek", "#RU": "Russian", "#ZH": "Chinese", 
    "#JA": "Japanese", "#KO": "Korean", "#ID": "Indonesian", "#MS": "Malay", 
    "#VN": "Vietnamese", "#TL": "Filipino", "#ES": "Spanish", "#PT": "Portuguese", 
    "#FR": "French", "#DE": "German", "#IT": "Italian", "#PL": "Polish", 
    "#TR": "Turkish", "#NL": "Dutch", "#SV": "Swedish", "#DA": "Danish", 
    "#NO": "Norwegian", "#FI": "Finnish", "#CS": "Czech", "#SK": "Slovak", 
    "#HU": "Hungarian", "#RO": "Romanian", "#HR": "Croatian", "#BG": "Bulgarian", 
    "#UK": "Ukrainian", "#SW": "Swahili", "#AF": "Afrikaans"
}

# ==========================================
# 🌟 ADVANCED SERVICE & LANGUAGE DETECTION
# ==========================================

SERVICE_SMS_KEYWORDS = {
    # 🟢 Social Media & Chat (Added Arabic Keywords)
    "whatsapp": ["whatsapp", "whatsa", "whatsap", "whats", "whatsapp business", "whatsapp me", "whatsapp code", "whatsap", "واتساب", "واتساپ", "واٹس ایپ", "व्हाट्सएप", "वाट्सएप", "वॉट्सऐप", "व्हाट्सप्प", "হোয়াটসঅ্যাপ", "হোটসঅ্যাপ", "ватсап", "уотсап", "вотсап", "ватс апп", "వాట్సాప్", "വാട്‌സ്ആപ്പ്", "வாட்ஸ்அப்", "ವಾಟ್ಸಾಪ್", "વોટ્સએપ", "ਵਟਸਐਪ", "ହ୍ଵାଟସ୍ ଆପ୍", "වට්ස්ඇප්", "วอตส์แอปป์", "วอทส์แอพ", "ဝက်စ်အက်ပ်", "វ៉តសាប់", "ວອດແອັບ", "ワッツアップ", "왓츠앱", "whatsapp的", "whatsapp验证码", "וואטסאפ", "γουάτσαπ", "ዋትስአፕ", "ვოთსאფი", "վոթսափ"],
    "facebook": ["facebook", "fb", "meta", "fbook", "fb code", "facebook code", "فيسبوك", "فيس بوك"],
    "instagram": ["instagram", "insta", "ig", "ig code", "instagram code", "انستغرام", "انستقرام"],
    "telegram": ["telegram", "tg", "tele", "telegram code", "tg code", "t.me", "تيليجرام", "تليجرام"],
    "tiktok": ["tiktok", "tik tok", "tikvideo", "tiktok code", "tik code", "تيك توك"],
    "snapchat": ["snapchat", "snap", "snap code", "سناب شات"],
    "twitter": ["twitter", "x.com", "x code", "twitter code", "تويتر"],
    "discord": ["discord", "discord code", "ديسكورد"],
    "viber": ["viber", "viber code", "فايبر"],
    "line": ["line", "line code", "line verification", "لاين"],
    "wechat": ["wechat", "we chat", "wechat code", "وي تشات"],
    "signal": ["signal", "signal code", "سيجنال"],
    "linkedin": ["linkedin", "linked in", "لينكد إن"],
    "imo": ["imo", "imo code", "imo verification", "ايمو"],
    "kakaotalk": ["kakao", "kakaotalk", "كاكاو"],
    "qq": ["qq", "tencent qq"],
    "vk": ["vk", "vkontakte"],

    # 🔵 Tech & Mail
    "google": ["google", "gmail", "youtube", "g-", "google voice", "جوجل", "غوغل"],
    "microsoft": ["microsoft", "ms", "outlook", "live.com", "hotmail"],
    "apple": ["apple", "icloud", "itunes", "apple id"],
    "yahoo": ["yahoo", "yahoo code", "ymail"],
    "protonmail": ["proton", "protonmail"],
    
    # 💰 Crypto & Trading
    "binance": ["binance", "bnb", "binances"],
    "coinbase": ["coinbase"],
    "okx": ["okx", "okex"],
    "kucoin": ["kucoin"],
    "bybit": ["bybit"],
    "huobi": ["huobi", "htx"],
    "mexc": ["mexc"],
    "trustwallet": ["trust wallet", "trustwallet"],

    # 💳 Finance & Wallets
    "bkash": ["bkash", "b-kash", "bkash code"],
    "nagad": ["nagad", "nagad code"],
    "rocket": ["rocket", "dutch bangla"],
    "upay": ["upay", "upay code"],
    "paypal": ["paypal", "pay pal"],
    "paytm": ["paytm"],
    "cashapp": ["cash app", "cashapp"],
    "wise": ["wise", "transferwise"],

    # 🛒 E-commerce & Delivery
    "amazon": ["amazon", "amzn", "amazon code"],
    "ebay": ["ebay"],
    "aliexpress": ["aliexpress", "ali express"],
    "alibaba": ["alibaba"],
    "daraz": ["daraz", "daraz code"],
    "foodpanda": ["foodpanda", "food panda"],
    "uber": ["uber", "uber code", "uber verification", "uber eats"],
    "pathao": ["pathao", "pathao ride"],

    # 🎮 Gaming & Entertainment
    "netflix": ["netflix", "netflix code"],
    "spotify": ["spotify", "spotify code"],
    "steam": ["steam", "steam guard"],
    "epicgames": ["epic games", "epicgames"],
    "roblox": ["roblox", "roblox code"],
    "riotgames": ["riot", "riot games", "valorant", "league of legends"],
    "garena": ["garena", "free fire", "freefire"],
    "playstation": ["playstation", "psn"],

    # 🎲 Betting & Casino
    "1xbet": ["1xbet", "1x bet"],
    "melbet": ["melbet", "melbet code"],
    "linebet": ["linebet"],
    "bet365": ["bet365"],
    "megapari": ["megapari"],

    # ❤️ Dating
    "tinder": ["tinder", "tinder code"],
    "bumble": ["bumble"],
    "badoo": ["badoo"]
}

def detect_service(text):
    text_lower = str(text).lower()
    for service_key, keywords in SERVICE_SMS_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return service_key.upper()
    return None

def get_service_info_html(service_text, msg_text=""):
    s = str(service_text).upper().strip()
    m = str(msg_text).lower().strip()
    apps = bot_settings.get("premium_apps", {})
    
    detected_service = s
    if m:
        for service_key, keywords in SERVICE_SMS_KEYWORDS.items():
            for kw in keywords:
                if kw in m:
                    detected_service = service_key.upper()
                    break
            if detected_service != s: break

    clean_s = re.sub(r'[^\w\s]', '', detected_service).strip()
    
    for app_name, data in apps.items():
        if app_name == detected_service or app_name == clean_s or app_name in detected_service or detected_service in app_name:
            full_name = data.get("name", app_name.title())
            char = data.get("char", "📱")
            eid = data.get("id")
            if eid: return full_name, f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
            return full_name, char
            
    if len(detected_service) > 20:
        return "Message", "💬"
        
    return detected_service.title(), "📱"

def detect_language(text):
    if not text: return "#EN"
    text_str = str(text)

    # ১. Unicode Block দিয়ে নিখুঁত বর্ণমালা শনাক্তকরণ (100% Accurate for scripts)
    if any('\u0600' <= c <= '\u06ff' for c in text_str): return "#AR" # Arabic / Persian / Urdu
    if any('\u0980' <= c <= '\u09ff' for c in text_str): return "#BN" # Bengali
    if any('\u0900' <= c <= '\u097f' for c in text_str): return "#HI" # Hindi / Marathi / Nepali
    if any('\u0a00' <= c <= '\u0a7f' for c in text_str): return "#PA" # Punjabi (Gurmukhi)
    if any('\u0a80' <= c <= '\u0aff' for c in text_str): return "#GU" # Gujarati
    if any('\u0b00' <= c <= '\u0b7f' for c in text_str): return "#OR" # Odia
    if any('\u0b80' <= c <= '\u0bff' for c in text_str): return "#TA" # Tamil
    if any('\u0c00' <= c <= '\u0c7f' for c in text_str): return "#TE" # Telugu
    if any('\u0c80' <= c <= '\u0cff' for c in text_str): return "#KN" # Kannada
    if any('\u0d00' <= c <= '\u0d7f' for c in text_str): return "#ML" # Malayalam
    if any('\u0d80' <= c <= '\u0dff' for c in text_str): return "#SI" # Sinhala
    if any('\u0e00' <= c <= '\u0e7f' for c in text_str): return "#TH" # Thai
    if any('\u0e80' <= c <= '\u0eff' for c in text_str): return "#LO" # Lao
    if any('\u0f00' <= c <= '\u0fff' for c in text_str): return "#BO" # Tibetan
    if any('\u1000' <= c <= '\u109f' for c in text_str): return "#MY" # Burmese (Myanmar)
    if any('\u1200' <= c <= '\u137f' for c in text_str): return "#AM" # Amharic (Ethiopic)
    if any('\u1780' <= c <= '\u17ff' for c in text_str): return "#KM" # Khmer
    if any('\u10a0' <= c <= '\u10ff' for c in text_str): return "#KA" # Georgian
    if any('\u0530' <= c <= '\u058f' for c in text_str): return "#HY" # Armenian
    if any('\u0590' <= c <= '\u05ff' for c in text_str): return "#HE" # Hebrew
    if any('\u0370' <= c <= '\u03ff' for c in text_str): return "#EL" # Greek
    if any('\u0400' <= c <= '\u04ff' for c in text_str): return "#RU" # Russian / Ukrainian (Cyrillic)
    if any('\u4e00' <= c <= '\u9fff' for c in text_str): return "#ZH" # Chinese
    if any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in text_str): return "#JA" # Japanese
    if any('\uac00' <= c <= '\ud7af' for c in text_str): return "#KO" # Korean

    # ২. OTP Keyword দিয়ে ভাষা শনাক্তকরণ (Latin script languages)
    text_lower = text_str.lower()
    
    # Asian / Pacific
    if any(w in text_lower for w in ["kode verifikasi", "jangan bagikan", "rahasia"]): return "#ID" # Indonesian
    if any(w in text_lower for w in ["kod pengesahan", "jangan kongsi"]): return "#MS" # Malay
    if any(w in text_lower for w in ["mã của bạn", "không chia sẻ", "mã xác minh"]): return "#VN" # Vietnamese
    if any(w in text_lower for w in ["ang iyong code", "huwag ibahagi"]): return "#TL" # Tagalog / Filipino
    
    # European / Americas
    if any(w in text_lower for w in ["código", "tu código", "verificación", "no compartas"]): return "#ES" # Spanish
    if any(w in text_lower for w in ["seu código", "código de verificação", "não compartilhe"]): return "#PT" # Portuguese
    if any(w in text_lower for w in ["code secret", "ne partagez pas", "votre code"]): return "#FR" # French
    if any(w in text_lower for w in ["dein code", "bestätigungscode", "nicht teilen"]): return "#DE" # German
    if any(w in text_lower for w in ["il tuo codice", "codice di verifica", "non condividere"]): return "#IT" # Italian
    if any(w in text_lower for w in ["twój kod", "nie udostępniaj", "kod weryfikacyjny"]): return "#PL" # Polish
    if any(w in text_lower for w in ["doğrulama kodu", "paylaşmayın", "onay kodu"]): return "#TR" # Turkish
    if any(w in text_lower for w in ["jouw code", "verificatiecode", "niet delen"]): return "#NL" # Dutch
    if any(w in text_lower for w in ["din kod", "verifieringskod", "dela inte"]): return "#SV" # Swedish
    if any(w in text_lower for w in ["bekræftelseskode", "del ikke"]): return "#DA" # Danish
    if any(w in text_lower for w in ["bekreftelseskode", "ikke del"]): return "#NO" # Norwegian
    if any(w in text_lower for w in ["vahvistuskoodi", "älä jaa"]): return "#FI" # Finnish
    if any(w in text_lower for w in ["váš kód", "ověřovací kód", "nesdílejte"]): return "#CS" # Czech
    if any(w in text_lower for w in ["overovací kód", "nezdieľajte"]): return "#SK" # Slovak
    if any(w in text_lower for w in ["ellenőrző kód", "ne oszd meg"]): return "#HU" # Hungarian
    if any(w in text_lower for w in ["codul tău", "codul de verificare", "nu partaja"]): return "#RO" # Romanian
    if any(w in text_lower for w in ["kontrolni kod", "kod za potvrdu", "ne delite"]): return "#HR" # Croatian/Serbian
    if any(w in text_lower for w in ["код за потвърждение", "не споделяйте"]): return "#BG" # Bulgarian
    if any(w in text_lower for w in ["ваш код", "код підтвердження"]): return "#UK" # Ukrainian
    
    # African
    if any(w in text_lower for w in ["msimbo wako", "usishiriki"]): return "#SW" # Swahili
    if any(w in text_lower for w in ["verifikasiekode", "moenie deel nie"]): return "#AF" # Afrikaans
    
    # ৩. উপরের কোনোটি না মিললে ডিফল্ট
    return "#EN"

def parse_chat_id(text):
    text = text.strip()
    if text.startswith("-100") or (text.startswith("-") and text[1:].isdigit()):
        return text
    if "t.me/" in text:
        parts = text.split("/")
        username = parts[-1]
        if username: return "@" + username if not username.startswith("@") else username
    if text.startswith("@"):
        return text
    return "@" + text

def is_admin(user_id):
    return user_id in bot_settings["admins"] or user_id == OWNER_ID

def check_force_join(user_id):
    if not bot_settings["fj_on"] or not bot_settings["fj_channels"]: return True
    if is_admin(user_id): return True
    for ch in bot_settings["fj_channels"]:
        res = api_call("getChatMember", {"chat_id": ch, "user_id": user_id})
        if res.get("ok") and res["result"]["status"] not in ["left", "kicked"]: continue
        else: return False
    return True

def send_force_join_msg(chat_id):
    kb = []
    for ch in bot_settings["fj_channels"]:
        url = f"https://t.me/{ch.replace('@', '')}" if ch.startswith("@") else ch
        kb.append([{"text": f"Join Channel", "icon_custom_emoji_id": "5789428375261023681", "url": url, "style": "primary"}])
    kb.append([{"text": "Check Joined", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "check_fj", "style": "success"}])
    send_message(chat_id, render_body_text(f"{PEM['warn']} <b>Please join our channels to use the bot!</b>"), reply_markup={"inline_keyboard": kb})

def is_user_banned(user_id):
    if is_admin(user_id): return False
    if user_id in user_banned_cache and time.time() - user_banned_cache[user_id]['time'] < 60:
        return user_banned_cache[user_id]['banned']
    banned = False
    if db:
        try:
            doc = db.collection('users').document(str(user_id)).get()
            banned = doc.exists and doc.to_dict().get("banned", False)
        except: pass
    user_banned_cache[user_id] = {'banned': banned, 'time': time.time()}
    return banned

# ==========================================
# Captcha Auto Login & Parsing Core
# ==========================================
def extract_otp_code(text):
    clean_text = re.sub(r'[\u200B-\u200D\uFEFF]', '', str(text))

    # 1. Multi-part OTPs (e.g. 123-456 or 809-761)
    multi_part = re.search(r'(\d{3}[-\s]+\d{3})|(\d{2}[-\s]+\d{2}[-\s]+\d{2})', clean_text)
    if multi_part:
        # হাইফেন (-) থাকলে সেটা রেখে দিবে, কিন্তু স্পেস থাকলে মুছে একসাথে করে দিবে
        return multi_part.group(0).replace(" ", "")

    # 2. Keyword-based extraction
    otp_keywords = ['code', 'is', 'otp', 'pin', 'verification', 'auth', 'কোড', 'رمز', 'your code']
    keywords_pattern = '|'.join(otp_keywords)
    keyword_match = re.search(rf'(?:{keywords_pattern})\s*(?:is|:|-|=)?\s*([a-z0-9]{{4,10}})', clean_text, re.I)
    if keyword_match and keyword_match.group(1).isdigit():
        return keyword_match.group(1)
        
    keyword_match_rev = re.search(rf'([a-z0-9]{{4,10}})\s*(?:is your|is the|কোড)', clean_text, re.I)
    if keyword_match_rev and keyword_match_rev.group(1).isdigit():
        return keyword_match_rev.group(1)

    # 3. Google OTP
    g_match = re.search(r'G-(\d{6})', clean_text, re.IGNORECASE)
    if g_match: return g_match.group(1)

    # 4. Digit sequences fallback
    digit_matches = re.findall(r'(?<!\d)\d{4,8}(?!\d)', clean_text)
    if digit_matches: return digit_matches[0]

    return None

def parse_panel_response(response_text, p_config=None):
    results = []
    p_type = p_config.get("type", "API Panel") if p_config else "API Panel"
    
    n_col_name = p_config.get("num_col_name", "number").lower() if p_config else "number"
    m_col_name = p_config.get("msg_col_name", "message").lower() if p_config else "message"
    n_idx = int(p_config.get("num_col_idx", 1)) - 1 if p_config and p_config.get("num_col_idx") else 1
    m_idx = int(p_config.get("msg_col_idx", 2)) - 1 if p_config and p_config.get("msg_col_idx") else 2

    if p_type == "Auto Captcha Panel":
        try:
            soup = BeautifulSoup(response_text, 'html.parser')
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                if not rows: continue
                
                # 🌟 Option 1 + Smart HTML Detection: কলামের নাম ও ব্যবহারকারীর দেওয়া সিরিয়াল দিয়ে সঠিক পজিশন বের করা
                final_n_idx = n_idx
                final_m_idx = m_idx
                
                # প্রথম রো (Header) চেক করে কলামের আসল সিরিয়াল মিলিয়ে নেওয়া
                header_cells = rows[0].find_all(['th', 'td'])
                for i, cell in enumerate(header_cells):
                    c_text = cell.get_text(strip=True).lower()
                    if n_col_name in c_text: final_n_idx = i
                    if m_col_name in c_text: final_m_idx = i

                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    
                    # হেডার রো (যেখানে সব th থাকে) সেগুলো থেকে ডাটা নিবে না
                    if all(c.name == 'th' for c in cols): continue
                    
                    if len(cols) > max(final_n_idx, final_m_idx):
                        # HTML টেবিল থেকে টেক্সট বের করা
                        num_text = cols[final_n_idx].get_text(separator=" ", strip=True)
                        msg_text = cols[final_m_idx].get_text(separator=" ", strip=True)
                        
                        clean_num = re.sub(r'\D', '', num_text)
                        
                        # নাম্বারটা আসলেই ৫-১৮ ডিজিটের কিনা তা নিশ্চিত করা (যাতে উল্টাপাল্টা টেক্সট না আসে)
                        if clean_num and 5 <= len(clean_num) <= 18:
                            otp = extract_otp_code(msg_text)
                            if otp and len(msg_text) > 4:
                                results.append({"number": clean_num, "message": msg_text, "otp": otp})
        except Exception as e:
            pass
    else:
        try:
            data = json.loads(response_text)
            temp_results = []
            
            def process_item(item):
                pot_nums_list = []
                pot_msg = None
                values = []
                
                if isinstance(item, dict):
                    # ১. প্রথমে পরিচিত JSON Key (যেমন: num, phone, sms) দিয়ে খোঁজার চেষ্টা
                    lower_keys = {str(k).lower(): v for k, v in item.items()}
                    for k in ["number", "num", "phone", "msisdn", "sender"]:
                        if k in lower_keys:
                            clean_val = re.sub(r'\D', '', str(lower_keys[k]))
                            if 5 <= len(clean_val) <= 18:
                                if clean_val not in pot_nums_list: pot_nums_list.append(clean_val)
                    for k in ["message", "msg", "sms", "content", "text"]:
                        if k in lower_keys:
                            val = str(lower_keys[k])
                            if len(val) > 4:
                                pot_msg = val
                                break
                    values = list(item.values())
                elif isinstance(item, list):
                    values = item

                # ২. যদি Key দিয়ে না পাওয়া যায়, তবে Smart Blind Scan (সব ভ্যালু চেক করবে)
                for v in values:
                    if isinstance(v, (dict, list)) or v is None: continue
                    v_str = str(v).strip()
                    
                    # Number Detection: 7 থেকে 18 ডিজিট
                    clean_v = re.sub(r'\D', '', v_str)
                    if 7 <= len(clean_v) <= 18 and not re.search(r'[a-zA-Z]', v_str):
                        # Date/Time/IP এড়ানোর লজিক
                        if not re.search(r'\d{4}[-/]\d{2}[-/]\d{2}', v_str) and not re.search(r'\d{2}:\d{2}:\d{2}', v_str) and "." not in v_str:
                            if clean_v not in pot_nums_list:
                                pot_nums_list.append(clean_v)
                    
                    # Message Detection: 5 অক্ষরের বেশি এবং শুধু সংখ্যা নয়
                    if len(v_str) > 4 and not v_str.isdigit():
                        if extract_otp_code(v_str):
                            if pot_msg is None or len(v_str) > len(pot_msg):
                                pot_msg = v_str
                                
                # 🌟 ৩. Multiple Numbers Logic (User Priority > Second Number > First Number)
                pot_num = None
                if pot_nums_list:
                    matched_user_num = None
                    for n in pot_nums_list:
                        # চেক করবে ইউজারের অ্যাসাইন করা নাম্বারের তালিকায় এই নাম্বারটি আছে কি না
                        if n in stex_assigned_numbers or any(n in str(key) for key in stex_assigned_numbers.keys()):
                            matched_user_num = n
                            break
                    
                    if matched_user_num:
                        pot_num = matched_user_num
                    elif len(pot_nums_list) >= 2:
                        pot_num = pot_nums_list[1] # ইউজারের কাছে না থাকলে সরাসরি দ্বিতীয় নাম্বারটি নেবে
                    else:
                        pot_num = pot_nums_list[0]
                            
                if pot_num and pot_msg:
                    otp = extract_otp_code(pot_msg)
                    if otp:
                        temp_results.append({"number": pot_num, "message": pot_msg, "otp": otp})
                        
            def traverse_json(node):
                if isinstance(node, list):
                    if len(node) > 0 and not isinstance(node[0], (dict, list)):
                        # It's a flat list representing one record
                        process_item(node)
                    for child in node:
                        if isinstance(child, (dict, list)):
                            traverse_json(child)
                elif isinstance(node, dict):
                    process_item(node)
                    for val in node.values():
                        if isinstance(val, (dict, list)):
                            traverse_json(val)

            traverse_json(data)
            
            # Remove duplicates
            seen = set()
            for r in temp_results:
                uid = f"{r['number']}_{r['otp']}"
                if uid not in seen:
                    seen.add(uid)
                    results.append(r)
        except: pass
        
    return results

# 🌟 Advanced Automated Background Captcha Solver 🌟
def attempt_auto_login(p, idx):
    login_url = p.get("login_url", "").strip()
    if not login_url.startswith("http"):
        login_url = "http://" + login_url
        
    if not login_url.lower().endswith('/login') and not login_url.lower().endswith('.php'):
        login_url = f"{login_url.rstrip('/')}/login"
        
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    })
    
    try:
        res = session.get(login_url, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        all_text = res.text
        
        # 1. SOLVE CAPTCHA (Exact bot 3.py logic)
        captcha_match = re.search(r'(\d+\s*[\+\-\*]\s*\d+)\s*[=\?:]', all_text)
        if not captcha_match:
            captcha_match = re.search(r'what is\s*(\d+\s*[\+\-\*]\s*\d+)', all_text, re.I)
        if not captcha_match:
            elements = soup.find_all(["label", "div", "span", "p", "strong"])
            for el in elements:
                txt = el.get_text(separator=" ", strip=True)
                if any(op in txt for op in ["+", "-", "*"]):
                    m = re.search(r'(\d+\s*[\+\-\*]\s*\d+)', txt)
                    if m:
                        captcha_match = m
                        break
                        
        captcha_text = captcha_match.group(1) if captcha_match else "0 + 0"
        answer = "0"
        m2 = re.search(r'(\d+)\s*([\+\-\*])\s*(\d+)', captcha_text)
        if m2:
            a, op, b = int(m2.group(1)), m2.group(2), int(m2.group(3))
            if op == '+': answer = str(a + b)
            elif op == '-': answer = str(a - b)
            elif op == '*': answer = str(a * b)

        # 2. FIND FORM
        form = soup.find("form")
        if not form:
            p["login_status"] = "❌ No login form found"
            return False
            
        action = form.get("action")
        from urllib.parse import urljoin, urlparse, parse_qs
        post_url = urljoin(login_url, action) if action else login_url

        form_data = {}
        for hidden in form.find_all("input", type="hidden"):
            name = hidden.get("name")
            if name: form_data[name] = hidden.get("value") or ""
        
        user_input = form.find("input", {"name": re.compile(r"user|email|id", re.I)}) or \
                     form.find("input", {"type": "text", "placeholder": re.compile(r"user|email", re.I)}) or \
                     form.find("input", {"type": "text"})
                     
        pass_input = form.find("input", {"name": re.compile(r"pass", re.I)}) or \
                     form.find("input", {"type": "password"})
                     
        captcha_input = form.find("input", {"placeholder": re.compile(r"answer|ans|code|verification|value|captcha", re.I)}) or \
                        form.find("input", {"name": re.compile(r"ans|captcha|ver|code", re.I)})
        
        user_field = user_input.get("name") if user_input else "username"
        pass_field = pass_input.get("name") if pass_input else "password"
        captcha_field = captcha_input.get("name") if captcha_input else "answer"

        form_data[user_field] = p.get("username", "")
        form_data[pass_field] = p.get("password", "")
        if captcha_field:
            form_data[captcha_field] = answer

        # 3. SUBMIT
        login_req = session.post(post_url, data=form_data, allow_redirects=True, timeout=15)
        
        # 4. VERIFY (Exact bot 3.py check logic)
        msg_link = p.get("msg_link", "").strip()
        if not msg_link.startswith("http") and msg_link != "":
            msg_link = "http://" + msg_link
            
        check_url = msg_link if msg_link else f"{login_url.split('/login')[0]}/client/SMSCDRStats"
        
        check_res = session.get(check_url, timeout=10)
        
        if 'logout' in login_req.text.lower() or 'logout' in check_res.text.lower() or 'sms reports' in check_res.text.lower() or 'dashboard' in check_res.text.lower() or 'cdrs' in check_res.text.lower():
            panel_sessions[idx] = session
            p["login_status"] = "✅ Active & Fetching"
            return True
        else:
            # এখানে ফেইল হলে অংক কী পেয়েছিল তা দেখা যাবে
            p["login_status"] = f"❌ Login Failed (Math: {captcha_text} = {answer})"
            return False
            
    except Exception as e:
        p["login_status"] = f"❌ Error: {str(e)[:20]}"
        
    return False

def panel_monitor_thread():
    global processed_otps, recent_traffic, panel_sessions
    while True:
        try:
            for idx, p in enumerate(bot_settings.get("panels", [])):
                if p.get("status") == "ON":
                    
                    if p.get("type") == "Auto Captcha Panel":
                        sess = panel_sessions.get(idx)
                        
                        if not sess:
                            now = time.time()
                            if now - p.get("last_login_attempt", 0) < 30: 
                                continue 
                            p["last_login_attempt"] = now
                            
                            success = attempt_auto_login(p, idx)
                            save_db() # Save login status text to show in settings
                            if not success:
                                continue 
                            sess = panel_sessions.get(idx)
                            
                        try:
                            # 🌟 auto sessions with sAjaxSource and Fallback HTML Parser
                            parsed_data, res_text = fetch_cpt_panel_cdrs(p, sess, p["msg_link"])
                            p["login_status"] = "✅ Active & Fetching"
                        except Exception as e:
                            p["login_status"] = "❌ Session Expired (Retrying...)"
                            del panel_sessions[idx]
                            save_db()
                            continue

                    elif p.get("api_url") or p.get("full_api_url"): 
                        full_url = p.get("full_api_url", "").strip()
                        url = p.get("api_url", "").strip()
                        token = p.get("token", "").strip()
                        if not full_url and not url: continue
                        
                        urls_to_try = []
                        if full_url:
                            urls_to_try.append(full_url)
                        else:
                            if "{token}" in url or "{key}" in url:
                                urls_to_try.append(url.replace("{token}", token).replace("{key}", token))
                            elif "token=" in url or "key=" in url:
                                urls_to_try.append(url)
                            else:
                                sep = '&' if '?' in url else '?'
                                urls_to_try.append(f"{url}{sep}token={token}")
                                urls_to_try.append(f"{url}{sep}key={token}&start=0")
                                urls_to_try.append(f"{url}{sep}key={token}")
                            
                        parsed_data = []
                        # 🌟 Browser Bypass (403 Forbidden Fix)
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                        for try_url in urls_to_try:
                            try:
                                res = requests.get(try_url, headers=headers, timeout=10)
                                parsed_data = parse_panel_response(res.text, p)
                                if parsed_data:
                                    if not full_url and try_url != url and token:
                                        p["api_url"] = try_url.replace(token, "{token}")
                                        save_db()
                                    break
                            except: continue
                        if not parsed_data: continue
                    else:
                        continue
                    
                    if p.get("type") != "Auto Captcha Panel":
                        limit = p.get("records", 0)
                        if limit > 0: parsed_data = parsed_data[:limit]
                        
                    for item in parsed_data:
                        num = item["number"]
                        otp = item["otp"]
                        msg_text = item["message"]
                        unique_id = f"{num}_{otp}"
                        
                        if unique_id not in processed_otps:
                            processed_otps.add(unique_id)
                            if len(processed_otps) > 5000: processed_otps.clear()
                                 
                            char, iso = get_flag_and_code(num)
                            app_full_name, prem_app_html = get_service_info_html(p.get("name", "Panel"), msg_text)
                            current_time = time.time()
                            
                            recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                            recent_traffic.append({
                                "service": app_full_name,
                                "iso": iso,
                                "flag": char,
                                "number": num,
                                "time": current_time,
                                "source": "bot"
                            })
                            # 🌟 শুধু লোকাল ফাইলে সেভ করবে, local database এ অহেতুক Write করবে না!
                            save_local_db()
                                 
                            display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                            masked = mask_number(display_num)
                            lang = detect_language(msg_text)
                            
                            lang_name = lang
                            display_msg = render_body_text(f"{get_premium_flag_html_by_iso(iso)} {iso} | {prem_app_html} {masked} | 💬 {lang}")
                            
                            for fw in bot_settings.get("fw_groups", []):
                                kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5296369303661067030", "copy_text": {"text": otp}, "style": "primary"}]]
                                temp_row = []
                                styles = ["danger", "success", "primary"]
                                for i, btn in enumerate(fw.get("buttons", [])):
                                    b_obj = {"text": btn["text"], "url": btn["url"], "style": styles[i % 3]}
                                    if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                                    temp_row.append(b_obj)
                                    if len(temp_row) == 2:
                                        kb.append(temp_row)
                                        temp_row = []
                                if temp_row: kb.append(temp_row)
                                send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                            
                            owners = []
                            clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                            
                            # 🌟 ALGORITHM FIX: সরাসরি Active Sessions থেকে মালিক খোঁজা 
                            # (কারণ Local Stock থেকে নাম্বার Assign হওয়ার সাথে সাথে ডিলিট হয়ে যায়)
                            for uid, session_data in user_active_sessions.items():
                                for act_num in session_data.get("nums", []):
                                    act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                    if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                        owners.append(uid)
                                        break
                                        
                            # ব্যাকআপ হিসেবে StexSMS-তে চেক করা 
                            if not owners:
                                for stex_n, n_owner in stex_assigned_numbers.items():
                                    clean_stex = str(stex_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                    if clean_stex == clean_api_num or (len(clean_stex) >= 8 and clean_stex.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_stex[-8:])):
                                        owners.append(n_owner)
                                        
                            owners = list(set(owners)) 
                            for owner_id in owners:
                                lang_name = lang
                                inbox_msg = render_body_text(f"{get_premium_flag_html_by_iso(iso)} {iso} | {prem_app_html} {display_num} | 💬 {lang}")
                                inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "primary"}]]
                                
                                # রিওয়ার্ড যোগ করার লজিক
                                reward = float(bot_settings.get("otp_reward", 0.0))
                                if reward > 0:
                                    update_balance(owner_id, reward)
                                    inbox_kb.append([{"text": f"Added {reward} tk", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "ignore", "style": "primary"}])
                                
                                send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                if db:
                                    try: 
                                        db.collection('users').document(str(owner_id)).update({"total_otps": Increment(1)})
                                        if owner_id in user_cache:
                                            user_cache[owner_id]["total_otps"] = user_cache[owner_id].get("total_otps", 0) + 1
                                    except: pass
        except Exception as e:
            pass
        time.sleep(5) 

# ==========================================
# Local User Management
# ==========================================
# 🌟 Local User Cache: avoid repeated local-database reads
user_cache = {}

def get_user(user_id):
    if user_id in user_cache: return user_cache[user_id]
    if not db: return {"user_id": user_id, "balance": 0.0, "total_refers": 0, "total_otps": 0}
    
    doc_ref = db.collection('users').document(str(user_id))
    doc = doc_ref.get()
    if doc.exists: 
        data = doc.to_dict()
        if "total_otps" not in data: data["total_otps"] = 0
        if "banned" not in data: data["banned"] = False
        if "verified" not in data: data["verified"] = False
        if "ref_income" not in data: data["ref_income"] = float(data.get("total_refers", 0) or 0) * float(bot_settings.get("refer_reward", 0.0))
        user_cache[user_id] = data
        return data
    else:
        new_user = {"user_id": user_id, "balance": 0.0, "total_refers": 0, "total_otps": 0, "ref_income": 0.0, "banned": False, "verified": False}
        doc_ref.set(new_user)
        user_cache[user_id] = new_user
        return new_user

def update_balance(user_id, amount):
    if user_id in user_cache:
        user_cache[user_id]["balance"] = user_cache[user_id].get("balance", 0.0) + float(amount)
    if not db: return
    try:
        doc_ref = db.collection('users').document(str(user_id))
        # 🌟 No more .get() before update! Saves 1 Read Cost instantly!
        doc_ref.set({"user_id": user_id, "balance": Increment(float(amount))}, merge=True)
    except: pass

def add_referral(inviter_id, new_user_id):
    if not db.collection('users').document(str(new_user_id)).get().exists:
        get_user(new_user_id) 
        reward = bot_settings.get("refer_reward", 0.2)
        update_balance(inviter_id, reward)
        db.collection('users').document(str(inviter_id)).update({"total_refers": Increment(1), "ref_income": Increment(float(reward))})
        if inviter_id in user_cache:
            user_cache[inviter_id]["total_refers"] = user_cache[inviter_id].get("total_refers", 0) + 1
        
        # আপনার দেওয়া নতুন ডিজাইন
        ref_msg = (
            f"{PEM['gift']} <b>New Referral !</b>\n"
            f"------------------\n"
            f"🔥 <b>You Received {format_money(reward)}</b>\n"
            f"------------------\n"
            f"{PEM['user']} <b>From User ID:</b> <code>{new_user_id}</code>"
        )
        send_message(inviter_id, render_body_text(ref_msg))

# ==========================================
# UI Keyboards & Menu Builders
# ==========================================
def get_cancel_kb():
    return {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]]}



# ==========================================
# COMPLETE DEPOSIT SYSTEM (ported from V8_3 reference)
# ==========================================
def _zinipay_api_request(endpoint, payload):
    """Call the official ZiniPay API. Never log or expose the API key."""
    api_key = str(ZINIPAY_API_KEY or os.getenv("ZINIPAY_API_KEY", "")).strip()
    if not api_key:
        raise RuntimeError("ZiniPay API key is not configured.")
    response = requests.post(
        ZINIPAY_API_BASE + endpoint,
        headers={"Content-Type": "application/json", "zini-api-key": api_key},
        json=payload, timeout=ZINIPAY_TIMEOUT
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise RuntimeError("Invalid response received from ZiniPay.")
    return data


def _zinipay_create_invoice(chat_id, amount_bdt):
    """Create a hosted ZiniPay invoice and persist the pending order."""
    if not str(ZINIPAY_API_KEY or os.getenv("ZINIPAY_API_KEY", "")).strip():
        return send_message(chat_id, render_body_text(
            f"{PEM['warn']} ZiniPay API key configure করা হয়নি।"
        ))
    try:
        amount = round(float(amount_bdt), 2)
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        val_id = "ZP-" + uuid.uuid4().hex[:20].upper()
        user = get_user(chat_id) or {}
        customer_name = str(user.get("profile_name") or "Telegram User")[:80]
        payload = {
            "cus_name": customer_name,
            "cus_email": f"user{int(chat_id)}@telegram.local",
            "amount": amount,
            "metadata": {"order_id": val_id, "customer_id": str(chat_id)},
            "val_id": val_id
        }
        # redirect_url is required by ZiniPay and must match the Brand Website domain.
        redirect_url = os.getenv("ZINIPAY_REDIRECT_URL", "").strip() or ZINIPAY_REDIRECT_URL
        cancel_url = os.getenv("ZINIPAY_CANCEL_URL", "").strip() or ZINIPAY_CANCEL_URL
        webhook_url = os.getenv("ZINIPAY_WEBHOOK_URL", "").strip() or ZINIPAY_WEBHOOK_URL
        payload["redirect_url"] = redirect_url
        payload["cancel_url"] = cancel_url
        payload["webhook_url"] = webhook_url
        result = _zinipay_api_request("/v1/payment/create", payload)
        payment_url = str(result.get("payment_url", "")).strip()
        if result.get("status") is not True or not payment_url.startswith("https://"):
            raise RuntimeError(str(result.get("message") or "ZiniPay invoice creation failed."))
        parsed = urlparse(payment_url)
        invoice_id = parsed.path.rstrip("/").split("/")[-1]
        if not invoice_id:
            raise RuntimeError("ZiniPay did not return a valid invoice URL.")
        _deposit_defaults()
        with purchase_lock:
            next_id = max([int(x.get("id", 0)) for x in bot_settings["deposit_requests"]
                           if isinstance(x, dict)] + [0]) + 1
            record = {
                "id": next_id, "user_id": int(chat_id), "amount": amount,
                "paid_amount": amount, "method": "ZiniPay", "gateway_id": 0,
                "reference": val_id, "val_id": val_id, "invoice_id": invoice_id,
                "payment_url": payment_url, "status": "payment_pending",
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "reviewed_at": "", "provider": "zinipay"
            }
            bot_settings["deposit_requests"].append(record)
            _deposit_save()
        user_states.pop(chat_id, None)
        temp_data.pop(chat_id, None)
        return send_message(chat_id, render_body_text(
            f"{PEM['money']} <b>ZINIPAY PAYMENT INVOICE</b>\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"🧾 Invoice: <code>{html.escape(invoice_id)}</code>\n"
            f"💰 Amount: <b>BDT {_deposit_money(amount)}</b>\n"
            "পেমেন্ট সম্পন্ন করার পর নিচের Verify Payment বাটনে চাপ দিন।\n"
            "পেমেন্ট নিশ্চিত না হওয়া পর্যন্ত Balance যোগ হবে না।"
        ), reply_markup={"inline_keyboard": [
            [{"text": "Pay Now", "url": payment_url, "style": "success"}],
            [{"text": "Verify Payment", "callback_data": f"dep:zverify:{next_id}", "style": "primary"}],
            [{"text": "Cancel", "callback_data": "dep:cancel", "style": "danger"}]
        ]})
    except requests.RequestException as exc:
        print(f"ZiniPay invoice request failed: {type(exc).__name__}: {exc}")
        return send_message(chat_id, render_body_text(
            f"{PEM['no']} ZiniPay-এর সাথে সংযোগ করা যায়নি। কিছুক্ষণ পর আবার চেষ্টা করুন।"
        ))
    except Exception as exc:
        print(f"ZiniPay invoice creation error: {type(exc).__name__}: {exc}")
        return send_message(chat_id, render_body_text(
            f"{PEM['no']} Invoice তৈরি করা যায়নি: {html.escape(str(exc)[:250])}"
        ))


def _zinipay_credit_once(request):
    """Atomically persist wallet balance and provider ledger in LocalStore."""
    uid = str(int(request.get("user_id", 0)))
    val_id = str(request.get("val_id") or request.get("reference") or "")
    amount = round(float(request.get("amount", 0) or 0), 2)
    if not uid or not val_id or amount <= 0:
        raise ValueError("Invalid ZiniPay credit data.")
    with purchase_lock, db.lock:
        collections = db.data.setdefault("collections", {})
        ledger = collections.setdefault("zinipay_transactions", {})
        if val_id in ledger and ledger[val_id].get("credited"):
            return False
        users = collections.setdefault("users", {})
        old_user = dict(users.get(uid, {}))
        old_balance = float(old_user.get("balance", 0) or 0)
        new_balance = round(old_balance + amount, 2)
        old_user.update({"user_id": int(uid), "balance": new_balance})
        users[uid] = old_user
        ledger[val_id] = {
            "credited": True, "user_id": int(uid), "amount": amount,
            "invoice_id": str(request.get("invoice_id", "")),
            "credited_at": datetime.now().isoformat(timespec="seconds")
        }
        db._save_unlocked()
        if int(uid) in user_cache:
            user_cache[int(uid)].update(old_user)
        return True


def _zinipay_verify_deposit(chat_id, deposit_id):
    _deposit_defaults()
    try:
        rid = int(deposit_id)
    except (TypeError, ValueError):
        return send_message(chat_id, "Invalid ZiniPay invoice reference.")
    with purchase_lock:
        request = next((x for x in bot_settings["deposit_requests"]
                        if int(x.get("id", 0)) == rid and x.get("provider") == "zinipay"), None)
        if not request or int(request.get("user_id", 0)) != int(chat_id):
            return send_message(chat_id, "এই Invoice আপনার অ্যাকাউন্টে পাওয়া যায়নি।")
        if request.get("status") == "completed":
            return send_message(chat_id, render_body_text(
                f"{PEM['ok']} এই পেমেন্টের Balance আগেই যোগ করা হয়েছে।"
            ))
        invoice_id = str(request.get("invoice_id", ""))
    try:
        result = _zinipay_api_request("/v1/payment/verify", {"invoice_id": invoice_id})
        status = str(result.get("status", "")).upper()
        if status == "COMPLETED":
            # Cross-check provider's merchant reference and amount before crediting.
            if str(result.get("val_id", "")) != str(request.get("val_id", "")):
                raise RuntimeError("Payment reference mismatch. Please contact support.")
            try:
                paid_amount = round(float(result.get("amount", 0)), 2)
            except (TypeError, ValueError):
                paid_amount = 0
            if paid_amount != round(float(request.get("amount", 0)), 2):
                raise RuntimeError("Paid amount mismatch. Please contact support.")
            credited = _zinipay_credit_once(request)
            with purchase_lock:
                request["status"] = "completed"
                request["payment_method"] = str(result.get("payment_method", ""))[:40]
                request["transaction_id"] = str(result.get("transaction_id", ""))[:100]
                request["reviewed_at"] = datetime.now().isoformat(timespec="seconds")
                request["credit_applied"] = True
                _deposit_save()
            balance = get_user(chat_id).get("balance", 0)
            send_message(chat_id, render_body_text(
                f"{PEM['ok']} <b>PAYMENT SUCCESSFUL</b>\n"
                f"Amount: <b>BDT {_deposit_money(request['amount'])}</b>\n"
                f"Payment Method: <b>{html.escape(str(result.get('payment_method', 'N/A')))}</b>\n"
                f"Transaction: <code>{html.escape(str(result.get('transaction_id', 'N/A')))}</code>\n"
                f"New Balance: <b>BDT {_deposit_money(balance)}</b>"
            ))
            return credited
        if status == "PENDING":
            return send_message(chat_id, "⏳ পেমেন্ট এখনো Pending। কিছুক্ষণ পর আবার Verify করুন।")
        if status == "FAILED":
            with purchase_lock:
                request["status"] = "failed"
                request["reviewed_at"] = datetime.now().isoformat(timespec="seconds")
                _deposit_save()
            return send_message(chat_id, "❌ ZiniPay পেমেন্ট Failed দেখাচ্ছে। নতুন Deposit তৈরি করুন।")
        raise RuntimeError("ZiniPay returned an unknown payment status.")
    except requests.RequestException as exc:
        print(f"ZiniPay verify request failed: {type(exc).__name__}: {exc}")
        return send_message(chat_id, "ZiniPay verification server-এ সংযোগ করা যায়নি। পরে আবার চেষ্টা করুন।")
    except Exception as exc:
        print(f"ZiniPay verification error: {type(exc).__name__}: {exc}")
        return send_message(chat_id, f"Payment verify করা যায়নি: {html.escape(str(exc)[:200])}")


class _ZiniPayWebhookHandler(BaseHTTPRequestHandler):
    def _send_page(self, code, title, message):
        body = (
            "<!doctype html><html><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{html.escape(title)}</title></head>"
            "<body style='font-family:Arial,sans-serif;background:#f5f7fb;padding:32px'>"
            "<main style='max-width:520px;margin:8vh auto;background:white;padding:28px;"
            "border-radius:14px;box-shadow:0 4px 24px #0001'>"
            f"<h2>{html.escape(title)}</h2><p>{html.escape(message)}</p>"
            "<p>You can return to Telegram and use Verify Payment if needed.</p>"
            "</main></body></html>"
        ).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _process_callback(self, payload, query):
        invoice_id = str(payload.get("invoice_id") or (query.get("invoice_id") or [""])[0]).strip()
        val_id = str(payload.get("val_id") or (query.get("val_id") or [""])[0]).strip()
        if not invoice_id and not val_id:
            return 400, b"missing invoice_id/val_id"

        _deposit_defaults()
        with purchase_lock:
            request = next((x for x in bot_settings.get("deposit_requests", [])
                            if x.get("provider") == "zinipay"
                            and ((invoice_id and str(x.get("invoice_id", "")) == invoice_id)
                                 or (val_id and str(x.get("val_id", "")) == val_id))), None)
            if not request:
                return 404, b"invoice not found"
            user_id = int(request.get("user_id", 0))
            deposit_id = int(request.get("id", 0))

        # Callback is only a notification. Always verify directly with ZiniPay
        # before changing a wallet balance.
        _zinipay_verify_deposit(user_id, deposit_id)
        return 200, b"callback received; verification requested"

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/zinipay/webhook":
            self.send_response(404); self.end_headers(); return
        try:
            length = min(int(self.headers.get("Content-Length", "0") or 0), 16384)
            raw = self.rfile.read(length).decode("utf-8", "replace") if length else "{}"
            payload = json.loads(raw) if raw.strip().startswith("{") else {}
            query = parse_qs(urlparse(self.path).query)
            code, body = self._process_callback(payload, query)
            self.send_response(code)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
        except Exception as exc:
            print(f"ZiniPay webhook processing error: {type(exc).__name__}: {exc}")
            self.send_response(500); self.end_headers(); self.wfile.write(b"error")

    def do_GET(self):
        path = urlparse(self.path).path
        query = parse_qs(urlparse(self.path).query)
        if path == "/zinipay/webhook":
            try:
                code, body = self._process_callback({}, query)
                self.send_response(code)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(body)
            except Exception as exc:
                print(f"ZiniPay GET webhook processing error: {type(exc).__name__}: {exc}")
                self.send_response(500); self.end_headers(); self.wfile.write(b"error")
        elif path == "/zinipay/success":
            self._send_page(200, "Payment received", "ZiniPay has redirected you back. Your balance is updated only after server verification.")
        elif path == "/zinipay/cancel":
            self._send_page(200, "Payment cancelled", "The payment page was cancelled or closed. No balance was added.")
        else:
            self.send_response(404); self.end_headers()

    def log_message(self, fmt, *args):
        return


def _start_zinipay_webhook_server():
    port = os.getenv("PORT", "").strip()
    if not port:
        return
    try:
        server = ThreadingHTTPServer(("0.0.0.0", int(port)), _ZiniPayWebhookHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        print(f"ZiniPay webhook listener started on port {port}")
    except Exception as exc:
        print(f"ZiniPay webhook listener could not start: {type(exc).__name__}: {exc}")


def _deposit_defaults():
    bot_settings.setdefault("deposit_gateways", [])
    bot_settings.setdefault("deposit_requests", [])
    bot_settings.setdefault("usd_to_bdt_rate", 125.0)
    bot_settings.setdefault("currency_mode", "BDT")
    bot_settings.setdefault("maintenance_mode", False)
    bot_settings.setdefault("maintenance_description", "The bot is currently under maintenance. Please try again later.")
    bot_settings.setdefault("deposit_referral_percent", 5.0)
    bot_settings.setdefault("activity_group_id", "")
    # Normalize malformed legacy values without discarding valid saved records.
    if not isinstance(bot_settings.get("deposit_gateways"), list):
        bot_settings["deposit_gateways"] = []
    if not isinstance(bot_settings.get("deposit_requests"), list):
        bot_settings["deposit_requests"] = []


def _deposit_save():
    _deposit_defaults()
    save_db()


def get_currency_mode():
    mode = str(bot_settings.get("currency_mode", "BDT")).upper()
    return mode if mode in ("BDT", "USD") else "BDT"

def currency_rate():
    try:
        return max(0.000001, float(bot_settings.get("usd_to_bdt_rate", 125.0) or 125.0))
    except (TypeError, ValueError):
        return 125.0

def amount_to_bdt(value):
    """Convert an amount entered in the currently selected display currency to canonical BDT."""
    amount = float(value)
    return amount * currency_rate() if get_currency_mode() == "USD" else amount

def format_money(value, suffix=True):
    """Format a canonical BDT amount in the admin-selected global currency."""
    try:
        amount = float(value or 0)
    except (TypeError, ValueError):
        amount = 0.0
    if get_currency_mode() == "USD":
        amount /= currency_rate()
        return f"${amount:,.2f}" if suffix else f"{amount:,.2f}"
    return f"BDT {amount:,.2f}" if suffix else f"{amount:,.2f}"

def _deposit_money(value):
    try:
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return "0.00"


def _deposit_admin_ids():
    ids = []
    for value in list(bot_settings.get("admins", [])) + [OWNER_ID]:
        try:
            uid = int(value)
            if uid not in ids:
                ids.append(uid)
        except (TypeError, ValueError):
            continue
    return ids


def _deposit_gateway(gateway_id):
    _deposit_defaults()
    try:
        gid = int(gateway_id)
    except (TypeError, ValueError):
        return None
    return next((g for g in bot_settings["deposit_gateways"]
                 if isinstance(g, dict) and int(g.get("id", -1)) == gid), None)


def _deposit_gateway_list_keyboard(enabled_only=False):
    _deposit_defaults()
    rows = []
    gateways = sorted(bot_settings["deposit_gateways"], key=lambda x: int(x.get("id", 0)))
    for g in gateways:
        if enabled_only and not g.get("enabled", True):
            continue
        rows.append([{
            "text": f"{'ENABLED' if g.get('enabled', True) else 'DISABLED'} · {str(g.get('name', 'Gateway'))[:28]}",
            "icon_custom_emoji_id": "5190899075968441286",
            "callback_data": f"dep:gateway:{int(g.get('id', 0))}",
            "style": "success" if g.get("enabled", True) else "danger"
        }])
    if not enabled_only:
        rows.append([{"text": "➕ Add New Gateway", "icon_custom_emoji_id": "5420323438508155202",
                      "callback_data": "dep:gateway_add", "style": "success"}])
        rows.append([{"text": "⬅️ Back", "icon_custom_emoji_id": "5267490665117275176",
                      "callback_data": "dep:admin", "style": "primary"}])
    return {"inline_keyboard": rows}


def show_deposit(chat_id, user_id):
    _deposit_defaults()
    gateways = [g for g in bot_settings["deposit_gateways"]
                if isinstance(g, dict) and g.get("enabled", True)]
    if not gateways and not os.getenv("ZINIPAY_API_KEY", "").strip():
        return send_message(chat_id, render_body_text(
            f"{PEM['warn']} <b>DEPOSIT TEMPORARILY UNAVAILABLE</b>\n\n"
            "এই মুহূর্তে কোনো Payment Gateway চালু নেই। অনুগ্রহ করে Support-এ যোগাযোগ করুন।"
        ), reply_markup={"inline_keyboard": [
            [{"text": "Support", "icon_custom_emoji_id": "5337302974806922068",
              "url": bot_settings.get("support_link", "https://t.me/your_support"), "style": "success"}],
            [{"text": "Main Menu", "icon_custom_emoji_id": "5267490665117275176",
              "callback_data": "close_msg", "style": "danger"}]
        ]})
    temp_data[user_id] = {"deposit_rate": float(bot_settings.get("usd_to_bdt_rate", 125) or 125)}
    user_states[user_id] = "deposit_wait_amount"
    result = send_message(chat_id, render_body_text(
        f"{PEM['money']} <b>DEPOSIT REQUEST</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "প্রথমে কত টাকা Deposit করতে চান তা লিখুন।\n"
        "<b>Amount (BDT ৳):</b>"
    ), reply_markup={"inline_keyboard": [[
        {"text": "Cancel", "icon_custom_emoji_id": "5420130255174145507",
         "callback_data": "dep:cancel", "style": "danger"}
    ]]})
    if isinstance(result, dict) and result.get("ok") and result.get("result", {}).get("message_id"):
        temp_data[user_id]["deposit_prompt_message_id"] = result["result"]["message_id"]
    return result

def _deposit_start_gateway(chat_id, user_id, gateway_id, message_id=None):
    gateway = _deposit_gateway(gateway_id)
    if not gateway or not gateway.get("enabled", True):
        if message_id:
            delete_message(chat_id, message_id)
        return send_message(chat_id, render_body_text(
            f"{PEM['warn']} এই Payment Gateway বর্তমানে চালু নেই। আবার Gateway নির্বাচন করুন।"
        ), reply_markup=_deposit_gateway_choice_keyboard())
    data = temp_data.setdefault(user_id, {})
    try:
        amount = float(data.get("requested_amount", 0))
        minimum = float(gateway.get("min_limit", 1))
        maximum = float(gateway.get("max_limit", 1000000000))
    except (TypeError, ValueError):
        amount, minimum, maximum = 0, 1, 0
    if amount < minimum or amount > maximum:
        if message_id:
            delete_message(chat_id, message_id)
        return send_message(chat_id, render_body_text(
            f"{PEM['warn']} এই Gateway-তে Deposit limit হলো BDT {_deposit_money(minimum)} থেকে {_deposit_money(maximum)}।\n"
            "অন্য Gateway নির্বাচন করুন অথবা নতুন Amount দিয়ে আবার শুরু করুন।"
        ), reply_markup={"inline_keyboard": [
            [{"text": "Choose Another Gateway", "icon_custom_emoji_id": "5190899075968441286", "callback_data": "dep:choose_gateway", "style": "primary"}],
            [{"text": "Start Again", "icon_custom_emoji_id": "5420155432272438703", "callback_data": "deposit_open", "style": "success"}]
        ]})
    if message_id:
        delete_message(chat_id, message_id)
    data.update({
        "deposit_gateway_id": int(gateway["id"]),
        "deposit_method": str(gateway.get("name", "")),
        "deposit_rate": float(bot_settings.get("usd_to_bdt_rate", 125) or 125),
        "deposit_min": minimum, "deposit_max": maximum
    })
    user_states[user_id] = "deposit_wait_reference"
    description = html.escape(str(gateway.get("description", "")))
    account = html.escape(str(gateway.get("account_number", "")))
    message = (
        f"{PEM['money']} <b>{html.escape(str(gateway.get('name', '')).upper())} PAYMENT</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"{PEM['gift']} <b>Deposit Amount:</b> {format_money(amount)} (BDT {_deposit_money(amount)})\n"
        f"{PEM['phone']} <b>Send Money Number:</b> <code>{account}</code>\n"
        f"{PEM['file']} <b>Payment Instructions:</b> {description or 'Send money to the number above.'}\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"{PEM['msg']} <b>Payment সম্পন্ন হলে Transaction ID পাঠান:</b>"
    )
    result = send_message(chat_id, render_body_text(message), reply_markup={
        "inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5420130255174145507",
                              "callback_data": "dep:cancel", "style": "danger"}]]
    })
    if isinstance(result, dict) and result.get("ok") and result.get("result", {}).get("message_id"):
        data["deposit_prompt_message_id"] = result["result"]["message_id"]
    return result


def _deposit_gateway_choice_keyboard():
    rows = []
    for g in bot_settings.get("deposit_gateways", []):
        if isinstance(g, dict) and g.get("enabled", True):
            rows.append([{"text": str(g.get("name", "Payment"))[:40],
                          "icon_custom_emoji_id": "5190899075968441286",
                          "callback_data": f"dep:select:{int(g.get('id', 0))}", "style": "primary"}])
    if os.getenv("ZINIPAY_API_KEY", "").strip():
        rows.append([{"text": "ZiniPay (Auto Payment)", "icon_custom_emoji_id": "5190899075968441286",
                      "callback_data": "dep:zini_create", "style": "success"}])
    rows.append([{"text": "Cancel", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "dep:cancel", "style": "danger"}])
    return {"inline_keyboard": rows}

def _deposit_submit(chat_id, user_id, reference, paid_bdt, state_data):
    _deposit_defaults()
    gateway_id = int(state_data.get("deposit_gateway_id", 0))
    gateway = _deposit_gateway(gateway_id)
    if not gateway or not gateway.get("enabled", True):
        user_states.pop(user_id, None)
        temp_data.pop(user_id, None)
        return send_message(chat_id, render_body_text(
            f"{PEM['warn']} এই Payment Gateway আর active নেই। আবার Deposit করুন।"
        ), reply_markup=main_menu(user_id))
    reference = str(reference).strip()
    if not reference or len(reference) > 180:
        return send_message(chat_id, "একটি valid Transaction ID পাঠান (সর্বোচ্চ 180 characters)।")
    try:
        paid_bdt = float(paid_bdt)
        minimum = float(gateway.get("min_limit", 1))
        maximum = float(gateway.get("max_limit", 1000000000))
        rate = float(state_data.get("deposit_rate", bot_settings.get("usd_to_bdt_rate", 125)))
        if paid_bdt <= 0 or paid_bdt < minimum or paid_bdt > maximum or rate <= 0:
            raise ValueError()
    except (TypeError, ValueError):
        return send_message(chat_id, f"সঠিক {get_currency_mode()} Amount দিন।")
    # A transaction reference must never be credited twice, even across gateways.
    with purchase_lock:
        for old in bot_settings["deposit_requests"]:
            if str(old.get("reference", "")).strip().casefold() == reference.casefold():
                user_states[user_id] = "deposit_wait_reference"
                temp_data.get(user_id, {}).pop("deposit_reference", None)
                return send_message(chat_id, render_body_text(
                    f"{PEM['no']} এই Transaction ID দিয়ে আগেই একটি Deposit Request করা হয়েছে। নতুন Trx ID দিন।"
                ))
        usd_equivalent = round(paid_bdt / rate, 2)
        # This bot's existing wallet, OTP prices and withdrawals are all in BDT.
        # Keep the credited amount in BDT; retain the USD equivalent for reference only.
        credit_bdt = round(paid_bdt, 2)
        next_id = max([int(x.get("id", 0)) for x in bot_settings["deposit_requests"]
                       if isinstance(x, dict)] + [0]) + 1
        request = {
            "id": next_id, "user_id": int(user_id), "amount": credit_bdt,
            "paid_amount": round(paid_bdt, 2), "usd_equivalent": usd_equivalent, "exchange_rate": rate,
            "method": str(state_data.get("deposit_method", gateway.get("name", ""))),
            "gateway_id": gateway_id, "reference": reference[:180],
            "status": "pending", "created_at": datetime.now().isoformat(timespec="seconds"),
            "reviewed_at": ""
        }
        bot_settings["deposit_requests"].append(request)
        _deposit_save()
    user_states.pop(user_id, None)
    temp_data.pop(user_id, None)
    send_message(chat_id, render_body_text(
        f"{PEM['ok']} <b>DEPOSIT REQUEST SUBMITTED</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"🆔 Request ID: <code>DEP_{next_id:04d}</code>\n"
        f"💳 Gateway: <b>{html.escape(request['method'])}</b>\n"
        f"💰 Balance Credit: <b>BDT {_deposit_money(credit_bdt)}</b>\n"
        f"💵 Sent Amount: <b>BDT {_deposit_money(paid_bdt)}</b>\n"
        f"💱 USD Equivalent: <b>${_deposit_money(usd_equivalent)}</b> at 1 USD = BDT {_deposit_money(rate)}\n"
        f"🧾 Trx ID: <code>{html.escape(reference[:180])}</code>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Admin verification সম্পন্ন হলে আপনার balance update হবে।"
    ), reply_markup=main_menu(user_id))
    admin_text = (
        f"📥 <b>NEW DEPOSIT REQUEST #{next_id}</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"👤 User: <code>{user_id}</code>\n"
        f"💰 Balance Credit: <b>BDT {_deposit_money(credit_bdt)}</b>\n"
        f"💵 Sent Money: <b>BDT {_deposit_money(paid_bdt)}</b>\n"
        f"💱 USD Equivalent: <b>${_deposit_money(usd_equivalent)}</b>\n"
        f"💳 Gateway: <b>{html.escape(request['method'])}</b>\n"
        f"🧾 Trx ID: <code>{html.escape(reference[:180])}</code>"
    )
    keyboard = {"inline_keyboard": [[
        {"text": "Approve", "icon_custom_emoji_id": "5352694861990501856",
         "callback_data": f"dep:approve:{next_id}", "style": "success"},
        {"text": "Reject", "icon_custom_emoji_id": "5420130255174145507",
         "callback_data": f"dep:reject:{next_id}", "style": "danger"}
    ]]}
    for admin_id in _deposit_admin_ids():
        try:
            send_message(admin_id, render_body_text(admin_text), reply_markup=keyboard)
        except Exception as exc:
            print(f"Deposit admin notification failed for {admin_id}: {exc}")


def _deposit_history(chat_id, user_id):
    _deposit_defaults()
    rows = [x for x in bot_settings["deposit_requests"] if int(x.get("user_id", 0)) == int(user_id)]
    rows = sorted(rows, key=lambda x: int(x.get("id", 0)), reverse=True)[:10]
    if not rows:
        return send_message(chat_id, render_body_text(
            f"{PEM['file']} <b>MY DEPOSIT HISTORY</b>\n\nকোনো Deposit Request পাওয়া যায়নি।"
        ), reply_markup={"inline_keyboard": [[
            {"text": "Back to Deposit", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "deposit_open", "style": "primary"}
        ]]})
    lines = [f"{PEM['file']} <b>MY DEPOSIT HISTORY</b>", "━━━━━━━━━━━━━━━━━━"]
    for r in rows:
        status = str(r.get("status", "pending")).upper()
        lines.append(
            f"<b>#{int(r.get('id', 0))} · {html.escape(status)}</b>\n"
            f"💰 Credited: BDT {_deposit_money(r.get('amount', 0))} | Paid: BDT {_deposit_money(r.get('paid_amount', 0))}\n"
            f"💳 {html.escape(str(r.get('method', '')))} | 🧾 <code>{html.escape(str(r.get('reference', '')))}</code>"
        )
    return send_message(chat_id, render_body_text("\n\n".join(lines)), reply_markup={
        "inline_keyboard": [[{"text": "Back to Deposit", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "deposit_open", "style": "primary"}]]
    })


def _deposit_admin_menu(chat_id, message_id=None):
    _deposit_defaults()
    pending = sum(1 for x in bot_settings["deposit_requests"] if x.get("status") == "pending")
    gateways = len(bot_settings["deposit_gateways"])
    rate = float(bot_settings.get("usd_to_bdt_rate", 125) or 125)
    text = render_body_text(
        f"{PEM['money']} <b>DEPOSIT MANAGEMENT</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"💳 Payment Gateways: <b>{gateways}</b>\n"
        f"📥 Pending Deposits: <b>{pending}</b>\n"
        f"💱 Exchange Rate: <b>1 USD = BDT {_deposit_money(rate)}</b>\n"
        f"🤝 Deposit Referral Commission: <b>{float(bot_settings.get('deposit_referral_percent', 0) or 0):g}%</b>"
    )
    kb = {"inline_keyboard": [
        [{"text": "Gateway Management", "icon_custom_emoji_id": "5190899075968441286",
          "callback_data": "dep:gateways", "style": "primary"}],
        [{"text": "Pending Deposits", "icon_custom_emoji_id": "5789428375261023681",
          "callback_data": "dep:pending:0", "style": "success"}],
        [{"text": "Set USD/BDT Rate", "icon_custom_emoji_id": "5420155432272438703",
          "callback_data": "dep:set_rate", "style": "primary"}],
        [{"text": "Set Referral Commission", "icon_custom_emoji_id": "5420396762189831222",
          "callback_data": "dep:set_commission", "style": "primary"}],
        [{"text": "Back to System", "icon_custom_emoji_id": "5267490665117275176",
          "callback_data": "system_settings", "style": "danger"}]
    ]}
    if message_id:
        return edit_message(chat_id, message_id, text, reply_markup=kb)
    return send_message(chat_id, text, reply_markup=kb)


def _deposit_gateway_detail(chat_id, message_id, gateway_id):
    g = _deposit_gateway(gateway_id)
    if not g:
        return edit_message(chat_id, message_id, "Gateway not found.",
                            reply_markup=_deposit_gateway_list_keyboard())
    status = "ENABLED" if g.get("enabled", True) else "DISABLED"
    txt = render_body_text(
        f"💳 <b>{html.escape(str(g.get('name', 'Gateway')))}</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"📱 Account: <code>{html.escape(str(g.get('account_number', '')))}</code>\n"
        f"📝 Description: {html.escape(str(g.get('description', '')))}\n"
        f"➖ Minimum: BDT {_deposit_money(g.get('min_limit', 1))}\n"
        f"➕ Maximum: BDT {_deposit_money(g.get('max_limit', 1000000000))}\n"
        f"⚙️ Status: <b>{status}</b>"
    )
    kb = {"inline_keyboard": [
        [{"text": "Edit Gateway", "callback_data": f"dep:gateway_edit_menu:{gateway_id}", "style": "primary"}],
        [{"text": "Enable Gateway" if not g.get("enabled", True) else "Disable Gateway",
          "callback_data": f"dep:gateway_toggle:{gateway_id}",
          "style": "success" if not g.get("enabled", True) else "danger"}],
        [{"text": "Remove Gateway", "callback_data": f"dep:gateway_remove_confirm:{gateway_id}", "style": "danger"}],
        [{"text": "Back to Gateways", "callback_data": "dep:gateways", "style": "primary"}]
    ]}
    return edit_message(chat_id, message_id, txt, reply_markup=kb)


def _deposit_pending_page(chat_id, message_id, page=0):
    _deposit_defaults()
    pending = sorted([x for x in bot_settings["deposit_requests"] if x.get("status") == "pending"],
                     key=lambda x: int(x.get("id", 0)))
    page_size = 5
    pages = max(1, (len(pending) + page_size - 1) // page_size)
    page = max(0, min(int(page), pages - 1))
    current = pending[page * page_size:(page + 1) * page_size]
    if not current:
        txt = render_body_text(f"{PEM['ok']} <b>NO PENDING DEPOSITS</b>")
        kb = {"inline_keyboard": [[{"text": "Back", "callback_data": "dep:admin", "style": "primary"}]]}
        return edit_message(chat_id, message_id, txt, reply_markup=kb)
    txt_parts = [f"{PEM['file']} <b>PENDING DEPOSITS</b> · Page {page+1}/{pages}",
                 "━━━━━━━━━━━━━━━━━━"]
    kb_rows = []
    for r in current:
        rid = int(r.get("id", 0))
        txt_parts.append(
            f"<b>DEPOSIT #{rid}</b>\n"
            f"👤 User: <code>{int(r.get('user_id', 0))}</code>\n"
            f"💰 Balance Credit: <b>BDT {_deposit_money(r.get('amount', 0))}</b>\n"
            f"💵 Paid: BDT {_deposit_money(r.get('paid_amount', 0))}\n"
            f"💳 Gateway: {html.escape(str(r.get('method', '')))}\n"
            f"🧾 Trx ID: <code>{html.escape(str(r.get('reference', '')))}</code>"
        )
        kb_rows.append([
            {"text": f"Approve #{rid}", "icon_custom_emoji_id": "5352694861990501856",
             "callback_data": f"dep:approve:{rid}", "style": "success"},
            {"text": f"Reject #{rid}", "icon_custom_emoji_id": "5420130255174145507",
             "callback_data": f"dep:reject:{rid}", "style": "danger"}
        ])
    nav = []
    if page > 0:
        nav.append({"text": "Previous", "callback_data": f"dep:pending:{page-1}", "style": "primary"})
    if page + 1 < pages:
        nav.append({"text": "Next", "callback_data": f"dep:pending:{page+1}", "style": "primary"})
    if nav:
        kb_rows.append(nav)
    kb_rows.append([{"text": "Back to Deposit Management", "callback_data": "dep:admin", "style": "danger"}])
    return edit_message(chat_id, message_id, render_body_text("\n\n".join(txt_parts)),
                        reply_markup={"inline_keyboard": kb_rows})


def _deposit_review(chat_id, message_id, deposit_id, approve):
    if not is_admin(chat_id):
        return
    _deposit_defaults()
    try:
        rid = int(deposit_id)
    except (TypeError, ValueError):
        return edit_message(chat_id, message_id, "Invalid deposit ID.")
    with purchase_lock:
        request = next((x for x in bot_settings["deposit_requests"]
                        if int(x.get("id", 0)) == rid), None)
        if not request or request.get("status") != "pending":
            request = None
        else:
            # Save status before balance credit so repeated callbacks cannot credit twice.
            request["status"] = "approved" if approve else "rejected"
            request["reviewed_at"] = datetime.now().isoformat(timespec="seconds")
            _deposit_save()
    if not request:
        return edit_message(chat_id, message_id, "This deposit request is already reviewed or missing.",
                            reply_markup={"inline_keyboard": [[
                                {"text": "Pending Deposits", "callback_data": "dep:pending:0", "style": "primary"}
                            ]]})
    uid = int(request.get("user_id", 0))
    if approve:
        update_balance(uid, float(request.get("amount", 0) or 0))
        pct = max(0.0, min(100.0, float(bot_settings.get("deposit_referral_percent", 0) or 0)))
        try:
            invited = get_user(uid)
            inviter = int(invited.get("referred_by", 0) or 0)
        except Exception:
            inviter = 0
        if inviter and inviter != uid and pct > 0:
            commission = round(float(request.get("amount", 0) or 0) * pct / 100.0, 2)
            if commission > 0:
                update_balance(inviter, commission)
                try:
                    ref_user = get_user(inviter)
                    ref_user["ref_income"] = float(ref_user.get("ref_income", 0) or 0) + commission
                    user_cache[inviter] = ref_user
                    if db:
                        db.collection("users").document(str(inviter)).set(
                            {"ref_income": ref_user["ref_income"]}, merge=True)
                except Exception:
                    pass
                send_message(inviter, render_body_text(
                    f"{PEM['gift']} <b>DEPOSIT REFERRAL COMMISSION</b>\n"
                    f"Commission: <b>{_deposit_money(commission)} ৳</b>\n"
                    f"New Balance: <b>{_deposit_money(get_user(inviter).get('balance', 0))} ৳</b>"
                ))
    if approve:
        _activity_group_notify(
            f"{PEM['money']} <b>DEPOSIT APPROVED</b>\n━━━━━━━━━━━━━━━━━━\n"
            f"{PEM['user']} <b>User:</b> {_activity_user_label(uid)}\n"
            f"{PEM['pin']} <b>User ID:</b> <code>{uid}</code>\n"
            f"{PEM['gift']} <b>Amount:</b> <b>{_deposit_money(request.get('amount', 0))} BDT</b>\n"
            f"{PEM['file']} <b>Gateway:</b> {html.escape(str(request.get('method', '')))}\n"
            f"{PEM['msg']} <b>Trx ID:</b> <code>{html.escape(str(request.get('reference', '')))}</code>\n"
            f"{PEM['ok']} <b>Request:</b> <code>DEP_{rid:04d}</code>"
        )
    status = "APPROVED" if approve else "REJECTED"
    balance = float(get_user(uid).get("balance", 0) or 0)
    send_message(uid, render_body_text(
        f"{PEM['ok'] if approve else PEM['no']} <b>DEPOSIT {status}</b>\n"
        f"Request ID: <code>DEP_{rid:04d}</code>\n"
        f"Amount: <b>BDT {_deposit_money(request.get('amount', 0))}</b>\n"
        f"Current Balance: <b>{_deposit_money(balance)} ৳</b>"
    ))
    return edit_message(chat_id, message_id, render_body_text(
        f"{PEM['ok'] if approve else PEM['no']} <b>DEPOSIT #{rid} {status}</b>\n"
        f"User: <code>{uid}</code>\n"
        f"Credit: <b>BDT {_deposit_money(request.get('amount', 0))}</b>"
    ), reply_markup={"inline_keyboard": [[
        {"text": "Pending Deposits", "callback_data": "dep:pending:0", "style": "primary"},
        {"text": "Deposit Management", "callback_data": "dep:admin", "style": "success"}
    ]]})


def _deposit_handle_text(chat_id, state, text, incoming_message_id=None):
    if state == "deposit_wait_amount":
        try:
            # Deposit gateway limits and wallet ledger are denominated in BDT.
            # The selected currency changes display only; BDT 100 should display as USD 100/rate.
            amount = float(str(text).replace(",", "").replace("৳", "").replace("$", "").strip())
            if amount <= 0:
                raise ValueError()
        except (TypeError, ValueError):
            send_message(chat_id, "সঠিক Deposit Amount দিন (BDT)।")
            return True
        if incoming_message_id:
            delete_message(chat_id, incoming_message_id)
        data = temp_data.setdefault(chat_id, {})
        prompt_id = data.pop("deposit_prompt_message_id", None)
        if prompt_id:
            delete_message(chat_id, prompt_id)
        data["requested_amount"] = round(amount, 2)
        user_states[chat_id] = "deposit_wait_gateway"
        result = send_message(chat_id, render_body_text(
            f"{PEM['money']} <b>SELECT PAYMENT GATEWAY</b>\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"আপনার Deposit Amount: <b>{format_money(amount)}</b>\n"
            f"<i>Gateway-তে পাঠাতে হবে: BDT {_deposit_money(amount)}</i>\n"
            "এখন bKash অথবা Nagad Gateway নির্বাচন করুন।"
        ), reply_markup=_deposit_gateway_choice_keyboard())
        if isinstance(result, dict) and result.get("ok") and result.get("result", {}).get("message_id"):
            data["deposit_prompt_message_id"] = result["result"]["message_id"]
        return True
    if state == "deposit_wait_gateway":
        send_message(chat_id, "নিচের inline button থেকে একটি active Payment Gateway নির্বাচন করুন।")
        return True
    if state == "deposit_wait_reference":
        reference = str(text).strip()
        if not reference or len(reference) > 180:
            send_message(chat_id, "Valid Transaction ID দিন (সর্বোচ্চ 180 characters)।")
            return True
        if incoming_message_id:
            delete_message(chat_id, incoming_message_id)
        data = dict(temp_data.get(chat_id, {}))
        prompt_id = data.get("deposit_prompt_message_id")
        if prompt_id:
            delete_message(chat_id, prompt_id)
        amount = data.get("requested_amount", 0)
        _deposit_submit(chat_id, chat_id, reference, amount, data)
        return True

    if state == "dep_admin_gateway_name":
        value = str(text).strip()
        if not value or len(value) > 40:
            send_message(chat_id, "Gateway name 1–40 characters দিন।")
            return True
        if any(str(g.get("name", "")).casefold() == value.casefold()
               for g in bot_settings.get("deposit_gateways", [])):
            send_message(chat_id, "এই নামে Gateway আগে থেকেই আছে। অন্য নাম দিন।")
            return True
        temp_data.setdefault(chat_id, {})["new_deposit_gateway"] = {"name": value}
        user_states[chat_id] = "dep_admin_gateway_account"
        send_message(chat_id, "Gateway Account Number পাঠান:", reply_markup=get_cancel_kb())
        return True
    if state == "dep_admin_gateway_account":
        value = str(text).strip()
        if not value or len(value) > 80:
            send_message(chat_id, "Valid account number দিন (সর্বোচ্চ 80 characters)।")
            return True
        temp_data.setdefault(chat_id, {}).setdefault("new_deposit_gateway", {})["account_number"] = value
        user_states[chat_id] = "dep_admin_gateway_description"
        send_message(chat_id, "Gateway Instructions/Description পাঠান:", reply_markup=get_cancel_kb())
        return True
    if state == "dep_admin_gateway_description":
        value = str(text).strip()
        if len(value) > 300:
            send_message(chat_id, "Description সর্বোচ্চ 300 characters হবে।")
            return True
        temp_data.setdefault(chat_id, {}).setdefault("new_deposit_gateway", {})["description"] = value
        user_states[chat_id] = "dep_admin_gateway_min"
        send_message(chat_id, "Minimum Deposit Limit (BDT) পাঠান:", reply_markup=get_cancel_kb())
        return True
    if state in ("dep_admin_gateway_min", "dep_admin_gateway_max"):
        try:
            amount = float(str(text).replace(",", "").strip())
            if amount < 0:
                raise ValueError()
        except (TypeError, ValueError):
            send_message(chat_id, "একটি valid positive amount দিন।")
            return True
        data = temp_data.setdefault(chat_id, {}).setdefault("new_deposit_gateway", {})
        if state == "dep_admin_gateway_min":
            data["min_limit"] = amount
            user_states[chat_id] = "dep_admin_gateway_max"
            send_message(chat_id, "Maximum Deposit Limit (BDT) পাঠান:", reply_markup=get_cancel_kb())
            return True
        if amount <= float(data.get("min_limit", 0)):
            send_message(chat_id, "Maximum limit অবশ্যই Minimum limit-এর চেয়ে বেশি হতে হবে। আবার দিন:")
            return True
        data["max_limit"] = amount
        user_states[chat_id] = "dep_admin_gateway_confirm"
        send_message(chat_id, render_body_text(
            f"<b>CONFIRM NEW PAYMENT GATEWAY</b>\n"
            f"Name: {html.escape(data['name'])}\n"
            f"Account: <code>{html.escape(data['account_number'])}</code>\n"
            f"Description: {html.escape(data.get('description', ''))}\n"
            f"Minimum: BDT {_deposit_money(data['min_limit'])}\n"
            f"Maximum: BDT {_deposit_money(data['max_limit'])}"
        ), reply_markup={"inline_keyboard": [
            [{"text": "Confirm & Add", "callback_data": "dep:gateway_add_confirm", "style": "success"}],
            [{"text": "Cancel", "callback_data": "dep:gateway_add_cancel", "style": "danger"}]
        ]})
        return True
    if state == "dep_admin_gateway_confirm":
        send_message(chat_id, "Gateway details are ready. Tap Confirm & Add or Cancel.")
        return True
    if state == "dep_admin_gateway_edit":
        data = temp_data.get(chat_id, {})
        gid, field = int(data.get("edit_gateway_id", 0)), str(data.get("edit_gateway_field", ""))
        gateway = _deposit_gateway(gid)
        value = str(text).strip()
        if not gateway or field not in ("name", "account_number", "description", "min_limit", "max_limit") or not value:
            send_message(chat_id, "Valid value দিন।")
            return True
        if field in ("min_limit", "max_limit"):
            try:
                num = float(value.replace(",", ""))
                other = float(gateway.get("max_limit", 0) if field == "min_limit" else gateway.get("min_limit", 0))
                if num < 0 or (field == "min_limit" and num >= other) or (field == "max_limit" and num <= other):
                    raise ValueError()
                value = num
            except ValueError:
                send_message(chat_id, "Minimum/Maximum limit সঠিকভাবে দিন।")
                return True
        elif field == "name":
            if len(value) > 40 or any(int(g.get("id", -1)) != gid and str(g.get("name", "")).casefold() == value.casefold()
                                      for g in bot_settings.get("deposit_gateways", [])):
                send_message(chat_id, "Gateway name invalid বা আগে থেকেই আছে।")
                return True
        elif field == "account_number" and len(value) > 80:
            send_message(chat_id, "Account number সর্বোচ্চ 80 characters হবে।")
            return True
        elif field == "description" and len(value) > 300:
            send_message(chat_id, "Description সর্বোচ্চ 300 characters হবে।")
            return True
        gateway[field] = value
        _deposit_save()
        user_states.pop(chat_id, None)
        temp_data.pop(chat_id, None)
        send_message(chat_id, render_body_text(f"{PEM['ok']} Gateway updated."))
        return True
    if state in ("dep_admin_rate", "dep_admin_commission"):
        try:
            amount = float(str(text).replace(",", "").strip())
            if amount <= 0 and state == "dep_admin_rate":
                raise ValueError()
            if amount < 0 or (state == "dep_admin_commission" and amount > 100):
                raise ValueError()
        except (TypeError, ValueError):
            send_message(chat_id, "Valid number দিন।")
            return True
        if state == "dep_admin_rate":
            bot_settings["usd_to_bdt_rate"] = amount
            label = f"Exchange rate set: 1 USD = BDT {_deposit_money(amount)}"
        else:
            bot_settings["deposit_referral_percent"] = amount
            label = f"Deposit referral commission set: {amount:g}%"
        _deposit_save()
        user_states.pop(chat_id, None)
        send_message(chat_id, render_body_text(f"{PEM['ok']} {label}"), reply_markup=main_menu(chat_id))
        return True
    return False

_deposit_defaults()


def main_menu(user_id):
    rk = bot_settings.get("reply_keyboard_emojis", {})
    default_ids = {
        "Get Number": "5337132498965010628",
        "My Profile": "5352861489541714456",
        "Refer": "5420396762189831222",
        "Deposit": "5190899075968441286",
        "Support": "5420145051336485498",
        "Admin Panel": "5420155432272438703",
    }
    def rb(text, style):
        b = {"text": text, "style": style}
        emoji_id = rk.get(text) or default_ids.get(text)
        if emoji_id and str(emoji_id).isdigit():
            b["icon_custom_emoji_id"] = str(emoji_id)
        return b
    kb = [
        [rb("Get Number", "primary"), rb("My Profile", "primary")],
        [rb("Refer", "success"), rb("Deposit", "success")],
        [rb("Support", "danger")]
    ]
    if is_admin(user_id):
        kb.append([rb("Admin Panel", "danger")])
    return {"keyboard": kb, "resize_keyboard": True}

def user_profile_keyboard():
    return {"inline_keyboard": [
        [{"text": "My Order", "icon_custom_emoji_id": "5352597830089347330", "callback_data": "my_orders_0", "style": "primary"},
         {"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]
    ]}

def my_orders_page(user_id, page=0):
    orders = [r for r in paid_sessions.values() if str(r.get("user")) == str(user_id)]
    orders.sort(key=lambda r: float(r.get("time", 0) or 0), reverse=True)
    page_size = 10
    total_pages = max(1, (len(orders) + page_size - 1) // page_size)
    page = max(0, min(int(page), total_pages - 1))
    chunk = orders[page * page_size:(page + 1) * page_size]
    lines = [f"{PEM['user']} <b>MY ORDERS</b>", "━━━━━━━━━━━━━━━━━━"]
    if not chunk:
        lines.append("No orders found.")
    for i, rec in enumerate(chunk, page * page_size + 1):
        num = str(rec.get("num", ""))
        if not num.startswith("+"):
            num = "+" + num
        otp = str(rec.get("otp") or "").strip() or "Empty"
        lines.append(
            f"<b>{i}. {html.escape(str(rec.get('service') or 'Unknown'))} - {html.escape(str(rec.get('country') or 'Unknown'))}</b>\n"
            f"Number: <code>{html.escape(num)}</code>\n"
            f"Price: <b>{format_money(rec.get('price', 0))}</b> | OTP: <code>{html.escape(otp)}</code>\n"
            f"Status: {html.escape(str(rec.get('status', 'unknown')).title())}"
        )
    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append(f"Page {page + 1}/{total_pages} • Total orders: {len(orders)}")
    kb, nav = [], []
    if page > 0:
        nav.append({"text": "Previous", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"my_orders_{page-1}", "style": "primary"})
    if page + 1 < total_pages:
        nav.append({"text": "Next", "icon_custom_emoji_id": "5337132498965010628", "callback_data": f"my_orders_{page+1}", "style": "success"})
    if nav:
        kb.append(nav)
    kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
    return render_body_text("\n\n".join(lines)), {"inline_keyboard": kb}

def get_user_profile_text(user_id):
    u = get_user(user_id)
    name = u.get("profile_name") or "User"
    username = u.get("username") or "Not set"
    balance = float(u.get("balance", 0) or 0)
    total_otp = int(u.get("total_otps", 0) or 0)
    total_ref = int(u.get("total_refers", 0) or 0)
    ref_income = float(u.get("ref_income", total_ref * float(bot_settings.get("refer_reward", 0.0))) or 0)
    username_value = f"@{html.escape(str(username).lstrip('@'))}" if username != 'Not set' else 'Not set'
    return render_body_text(
        f"{PEM['user']} <b>MY PROFILE</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"{PEM['user']} <b>Name:</b> {html.escape(str(name))}\n"
        f"{PEM['msg']} <b>Username:</b> {username_value}\n"
        f"{PEM['num']} <b>User ID:</b> <code>{user_id}</code>\n"
        f"{PEM['money']} <b>Balance:</b> {format_money(balance)}\n"
        f"{PEM['phone']} <b>Total OTP:</b> {total_otp}\n"
        f"{PEM['gift']} <b>Total Referred:</b> {total_ref}\n"
        f"{PEM['money']} <b>Referral Income:</b> {format_money(ref_income)}\n"
        f"━━━━━━━━━━━━━━"
    )

def get_admin_text():
    users_count = len(all_known_users) # 🌟 Zero Cost User Count!
    total_files = len(number_batches)
    available_nums = sum(len(b["numbers"]) for b in number_batches.values())

    txt = f"""
{PEM['admin']} <b>ADMIN CONTROL PANEL</b> {PEM['admin']}
━━━━━━━━━━━━━━━━━━

{PEM['graph']} <b>DATABASE OVERVIEW</b>
— — — — — — — — — —
{PEM['user']} Users      » {users_count}
{PEM['file']} Files      » {total_files}
{PEM['num']} Numbers    » {total_uploaded_stats}
{PEM['ok']} Assigned   » {total_assigned_stats}
{PEM['rocket']} Available  » {available_nums}

{PEM['graph']} <b>STOCK LEVEL</b>
— — — — — — — — — —
[██████░░░░░░░░░] {available_nums} free
"""
    return render_body_text(txt)

def send_file_document(chat_id, filename, file_bytes):
    url = f"{BASE_URL}/sendDocument"
    try:
        requests.post(url, data={"chat_id": chat_id},
                      files={"document": (filename, file_bytes, "application/zip")},
                      timeout=30)
        return True
    except:
        return False

def create_database_backup():
    # Save the latest stock/settings snapshot before packaging both databases.
    save_db()
    mem = io.BytesIO()
    with db.lock:
        with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as z:
            for filename in ["bot_data.json", "local_db.json", "users_list.json"]:
                if os.path.exists(filename):
                    z.write(filename, arcname=filename)
    mem.seek(0)
    return mem.getvalue()

def database_keyboard():
    return {"inline_keyboard": [
        [{"text": "Download Database", "icon_custom_emoji_id": "5352721946054268944", "callback_data": "db_download", "style": "success"}],
        [{"text": "Upload Database", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "db_upload", "style": "primary"}],
        [{"text": "Clear All Data", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "db_clear_confirm", "style": "danger"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "primary"}]
    ]}

def reset_all_database_data():
    global db, bot_settings, number_batches, used_numbers_list
    global total_uploaded_stats, total_assigned_stats, recent_traffic
    global stex_assigned_numbers, voltx_assigned_numbers, zenex_assigned_numbers
    global processed_otps, assigned_number_rates, all_known_users
    try:
        for filename in ["bot_data.json", "local_db.json", "users_list.json"]:
            if os.path.exists(filename):
                os.remove(filename)
    except:
        pass
    number_batches = {}
    used_numbers_list = []
    total_uploaded_stats = 0
    total_assigned_stats = 0
    recent_traffic = []
    stex_assigned_numbers = {}
    voltx_assigned_numbers = {}
    zenex_assigned_numbers = {}
    processed_otps = set()
    assigned_number_rates = {}
    all_known_users = set()
    user_cache.clear()
    pending_withdrawals.clear()
    paid_sessions.clear()
    paid_user_current.clear()
    # Recreate the local store and restore default settings.
    db = LocalStore()
    bot_settings.clear()
    bot_settings.update({
        "admins": [OWNER_ID], "special_users": [], "panels": [], "fw_groups": [],
        "otp_link": "https://t.me/your_otp_group", "withdraw_on": True,
        "min_withdraw": 30.0, "otp_reward": 0.1, "refer_reward": 0.2,
        "cooldown": 10, "num_req": 1, "num_share": 1,
        "support_link": "https://t.me/your_support", "support_button_name": "Support", "w_methods": ["bKash", "Nagad"],
        "fj_on": False, "fj_channels": [], "console_otp": False, "stex_keys": [], "voltx_keys": [], "zenex_keys": [],
        "search_countries": [], "stex_services": {}, "voltx_services": {}, "zenex_services": {},
        "deposit_gateways": [], "deposit_requests": [], "usd_to_bdt_rate": 125.0,
        "currency_mode": "BDT", "maintenance_mode": False,
        "maintenance_description": "The bot is currently under maintenance. Please try again later.",
        "deposit_referral_percent": 5.0,
        "premium_flags": DEFAULT_PREMIUM_FLAGS.copy() if "DEFAULT_PREMIUM_FLAGS" in globals() else {},
        "premium_apps": DEFAULT_PREMIUM_APPS.copy() if "DEFAULT_PREMIUM_APPS" in globals() else {},
        "mask_emoji": {"id": "", "char": "DXA"},
        "custom_messages": DEFAULT_CUSTOM_MESSAGES.copy()
    })
    save_db()

def support_management_keyboard():
    return {"inline_keyboard": [
        [{"text": "EDIT SUPPORT LINK", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "support_edit_link", "style": "primary"}],
        [{"text": "EDIT SUPPORT BUTTON NAME", "icon_custom_emoji_id": "5395444784611480792", "callback_data": "support_edit_name", "style": "success"}],
        [{"text": "BACK", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
    ]}

def support_management_text():
    link = bot_settings.get("support_link", "") or "Not set"
    name = bot_settings.get("support_button_name", "Support")
    return render_body_text(
        f"{PEM['msg']} <b>SUPPORT MANAGEMENT</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>Button Name:</b> {html.escape(str(name))}\n"
        f"<b>Support Link:</b> <code>{html.escape(str(link))}</code>\n\n"
        f"<i>Manage only the Support Center contact button name and its support link.</i>"
    )

def support_user_keyboard():
    kb = []
    link = bot_settings.get("support_link", "") or ""
    if link:
        kb.append([{"text": str(bot_settings.get("support_button_name", "CONTACT SUPPORT"))[:64], "icon_custom_emoji_id": "5337302974806922068", "url": link, "style": "success"}])
    kb.append([{"text": "SEND MESSAGE", "icon_custom_emoji_id": "5395444784611480792", "callback_data": "support_start", "style": "primary"}])
    kb.append([{"text": "CLOSE", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
    return {"inline_keyboard": kb}

def support_ticket_keyboard(user_id):
    return {"inline_keyboard": [
        [{"text": "REPLY", "icon_custom_emoji_id": "5395444784611480792", "callback_data": f"support_reply_{user_id}", "style": "success"},
         {"text": "CLOSE", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"support_close_{user_id}", "style": "danger"}]
    ]}

def _activity_group_menu(chat_id, message_id=None):
    group_id = str(bot_settings.get("activity_group_id", "") or "").strip()
    status = f"<code>{html.escape(group_id)}</code>" if group_id else "<i>Not configured</i>"
    body = render_body_text(
        f"{PEM['graph']} <b>ACTIVITY GROUP</b>\n━━━━━━━━━━━━━━━━━━\n"
        f"{PEM['msg']} <b>Group ID:</b> {status}\n\n"
        "Deposit approve এবং Number purchase activity এই গ্রুপে পাঠানো হবে।"
    )
    kb = {"inline_keyboard": [
        [{"text": "Set / Change Group", "icon_custom_emoji_id": "5395444784611480792", "callback_data": "activity_group_set", "style": "success"}],
        [{"text": "Remove Group", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "activity_group_remove", "style": "danger"}],
        [{"text": "Back to System", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}
    if message_id:
        return edit_message(chat_id, message_id, body, reply_markup=kb)
    return send_message(chat_id, body, reply_markup=kb)


def _activity_group_notify(text):
    group_id = str(bot_settings.get("activity_group_id", "") or "").strip()
    if not group_id:
        return
    try:
        target = int(group_id)
    except (TypeError, ValueError):
        return
    # Do not hold purchase/deposit locks while waiting for Telegram's network.
    def _send():
        try:
            send_message(target, render_body_text(text))
        except Exception as exc:
            print(f"Activity group notification failed: {exc}")
    threading.Thread(target=_send, daemon=True).start()


def _activity_user_label(user_id):
    try:
        user = get_user(int(user_id))
        username = str(user.get("username", "") or "").strip().lstrip("@")
        name = str(user.get("profile_name", "") or "User").strip()
        if username:
            return f"{html.escape(name)} (@{html.escape(username)})"
        return html.escape(name)
    except Exception:
        return "User"


def admin_panel_keyboard():
    return {"inline_keyboard": [
        [{"text": "LEADER BOARD SYSTEM", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "lb_main", "style": "success"}],
        [{"text": "Upload Number", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "upload_num", "style": "primary"},
         {"text": "Delete files", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "delete_files", "style": "danger"}],
        [{"text": "Broadcast", "icon_custom_emoji_id": "5789428375261023681", "callback_data": "broadcast_msg", "style": "success"}],
        [{"text": "System", "icon_custom_emoji_id": "5420155432272438703", "callback_data": "system_settings", "style": "primary"}],
        [{"text": "Database", "icon_custom_emoji_id": "5352721946054268944", "callback_data": "database_menu", "style": "danger"}],
        [{"text": "Used number", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "show_used", "style": "success"},
         {"text": "Canceled Number", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "show_rejected", "style": "danger"}],
        [{"text": "Unused number", "icon_custom_emoji_id": "5352597830089347330", "callback_data": "show_unused", "style": "success"}],
        [{"text": "Bulk Selled", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "bulk_selled", "style": "primary"}],
        [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]
    ]}

def system_settings_keyboard():
    return {"inline_keyboard": [
        [{"text": "Force Join System", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "manage_fj", "style": "primary"},
         {"text": "Admin Management", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "manage_admins", "style": "danger"}],
        [{"text": "Support Management", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "support_management", "style": "success"}],
        [{"text": "Price Manager", "icon_custom_emoji_id": "5352985330628730418", "callback_data": "price_manager", "style": "success"}],
        [{"text": f"No-OTP Refund ({int(bot_settings.get('paid_expiry_minutes', 720))}m)", "icon_custom_emoji_id": "5337172996211648018", "callback_data": "paid_expiry_set", "style": "primary"}],
        [{"text": f"Cancel Cooldown ({int(bot_settings.get('cancel_cooldown_minutes', 5))}m)", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "cancel_cooldown_set", "style": "danger"}],
        [{"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "callback_data": "manage_otp_groups", "style": "danger"},
         {"text": "User Management", "icon_custom_emoji_id": "5193063022226086560", "callback_data": "user_management", "style": "primary"}],
        [{"text": "Deposit Management", "icon_custom_emoji_id": "5190899075968441286", "callback_data": "dep:admin", "style": "success"}],
        [{"text": f"Currency: {get_currency_mode()}", "icon_custom_emoji_id": "5352985330628730418", "callback_data": "currency_settings", "style": "primary"},
         {"text": f"Maintenance: {'ON' if bot_settings.get('maintenance_mode') else 'OFF'}", "icon_custom_emoji_id": "5420155432272438703", "callback_data": "maintenance_toggle", "style": "danger"}],
        [{"text": "Activity Group", "icon_custom_emoji_id": "5192805934073685937", "callback_data": "activity_group", "style": "primary"}],
        [{"text": "DXA Control", "icon_custom_emoji_id": "5193100774988617665", "callback_data": "dxa_control", "style": "primary"},
         {"text": "Premium Emoji", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "manage_emojis", "style": "success"}],
        [{"text": "Menu Design", "icon_custom_emoji_id": "5190751148704833975", "callback_data": "menu_design_list", "style": "primary"},
         {"text": "Test", "icon_custom_emoji_id": "5190781475468915802", "callback_data": "test_message_flow", "style": "primary"}], 
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
    ]}

def get_user_management_text():
    # 🌟 Fast & Free User Management Stats!
    total = len(all_known_users)
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    txt = f"""➖➖➖➖➖➖➖➖
《 👋 USER VIEW 》
➖➖➖➖➖➖➖➖
📊 LIVE STATISTICS:
➖➖➖➖➖➖➖➖
🫂 TOTAL USERS: {total}
✅ VERIFIED USERS: (Hidden to save DB Cost)
🚫 BANNED USERS: (Hidden to save DB Cost)
➖➖➖➖➖➖➖➖
⌛ UPDATED: {now_str}"""
    return render_body_text(txt)

def user_management_keyboard():
    return {"inline_keyboard": [
        [{"text": "Manage Balance", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "um_manage_balance", "style": "primary"},
         {"text": "Ban/Unban User", "icon_custom_emoji_id": "5334807341109908955", "callback_data": "um_ban_unban", "style": "danger"}],
        [{"text": "User Profile", "icon_custom_emoji_id": "5352861489541714456", "callback_data": "um_user_profile", "style": "success"}],
        [{"text": f"All Users ({len(all_known_users)})", "callback_data": "um_all_users", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def reply_keyboard_emoji_settings_keyboard():
    buttons = [
        ("Get Number", "primary"),
        ("My Profile", "primary"),
        ("Refer", "success"),
        ("Deposit", "success"),
        ("Support", "danger"),
        ("Admin Panel", "danger")
    ]
    rk = bot_settings.get("reply_keyboard_emojis", {})
    rows = []
    for text, style in buttons:
        defaults = {"Get Number": "5337132498965010628", "My Profile": "5352861489541714456",
                    "Refer": "5420396762189831222", "Deposit": "5190899075968441286",
                    "Support": "5420145051336485498", "Admin Panel": "5420155432272438703"}
        eid = rk.get(text) or defaults.get(text, "Not set")
        label = f"{text} • {eid}"
        rows.append([{"text": label, "icon_custom_emoji_id": str(eid) if str(eid).isdigit() else "5420130255174145507", "callback_data": "rkemoji_set:" + text, "style": style}])
    rows.append([{"text": "Back to Menu Design", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "menu_design_list", "style": "primary"}])
    return {"inline_keyboard": rows}

def menu_design_list_keyboard():
    return {"inline_keyboard": [
        [{"text": "Edit /start Menu", "icon_custom_emoji_id": "5395444784611480792", "callback_data": "md_edit_start", "style": "primary"}],
        [{"text": "Edit GET NUMBER", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "md_edit_get_number", "style": "success"},
         {"text": "Edit NEW NUMBER", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "md_edit_new_number", "style": "success"}],
        [{"text": "Edit Select Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "md_edit_select_country", "style": "primary"}],
        [{"text": "Edit Refer", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "md_edit_refer", "style": "primary"}],
        [{"text": "Reply Keyboard Emoji", "icon_custom_emoji_id": "6298790803414189709", "callback_data": "reply_keyboard_emoji_settings", "style": "success"}],
        [{"text": "Reset Defaults", "icon_custom_emoji_id": "5192812028632274956", "callback_data": "md_reset_defaults", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def menu_edit_options_keyboard(menu_key):
    return {"inline_keyboard": [
        [{"text": "Edit Body (Text)", "icon_custom_emoji_id": "5395444784611480792", "callback_data": f"md_text_{menu_key}", "style": "primary"}],
        [{"text": "Edit Inline Buttons", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"md_btns_{menu_key}", "style": "success"}],
        [{"text": "Back to Menus", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "menu_design_list", "style": "danger"}]
    ]}

def menu_buttons_list_keyboard(menu_key):
    kb = []
    btns = bot_settings["custom_messages"].get(menu_key, {}).get("buttons", [])
    for idx, btn in enumerate(btns):
        kb.append([{"text": f"Del: {btn['text']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"md_delbtn_{menu_key}_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Inline Button", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"md_addbtn_{menu_key}", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_edit_{menu_key}", "style": "primary"}])
    return {"inline_keyboard": kb}

def emoji_settings_keyboard():
    return {"inline_keyboard": [
        [{"text": "Upload Flags (TXT)", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "up_flags_txt", "style": "primary"},
         {"text": "Download Flags", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_flags_txt", "style": "success"}],
        [{"text": "Upload Services (TXT)", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "up_apps_txt", "style": "primary"},
         {"text": "Download Services", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_apps_txt", "style": "success"}],
        [{"text": "Delete All Flags", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "del_all_flags", "style": "danger"},
         {"text": "Add Single Emoji", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_single_emoji", "style": "success"}],
        [{"text": "Set Number Mask Emoji", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "set_mask_emoji", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}

def fj_settings_keyboard():
    status_text = 'ON' if bot_settings['fj_on'] else 'OFF'
    status_icon = "5352694861990501856" if bot_settings['fj_on'] else "5318840353510408444"
    kb = [[{"text": f"STATUS: {status_text}", "icon_custom_emoji_id": status_icon, "callback_data": "toggle_fj", "style": "primary"}]]
    for idx, ch in enumerate(bot_settings["fj_channels"]):
        kb.append([{"text": f"Delete: {ch}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_fj_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Channel", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_fj", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
    return {"inline_keyboard": kb}

def admin_settings_keyboard():
    kb = []
    for idx, adm in enumerate(bot_settings["admins"]):
        text_btn = f"Owner: {adm}" if adm == OWNER_ID else f"Delete: {adm}"
        icon_id = "5353032893096567467" if adm == OWNER_ID else "5420130255174145507"
        cb_data = "ignore" if adm == OWNER_ID else f"del_adm_{idx}"
        kb.append([{"text": text_btn, "icon_custom_emoji_id": icon_id, "callback_data": cb_data, "style": "danger" if adm != OWNER_ID else "primary"}])
    kb.append([{"text": "Add Admin", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_adm", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
    return {"inline_keyboard": kb}

def otp_groups_list_keyboard():
    kb = [[{"text": "Edit OTP Button Link", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "edit_otp_link", "style": "primary"}]]
    for idx, fg in enumerate(bot_settings["fw_groups"]):
        kb.append([{"text": f"Group: {fg['chat_id']}", "icon_custom_emoji_id": "5193063022226086560", "callback_data": f"manage_fw_{idx}", "style": "primary"}])
    kb.append([{"text": "Add Forward Group", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_fw", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}])
    return {"inline_keyboard": kb}

def stex_control_keyboard():
    auto_status = "ON" if bot_settings.get("stex_auto", False) else "OFF"
    auto_emoji = "5352694861990501856" if auto_status == "ON" else "5420130255174145507"
    return {"inline_keyboard": [
        [{"text": "Add StexSMS Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_stex_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_stex_keys", "style": "danger"}],
        [{"text": "Manage StexSMS Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_stex_srv", "style": "success"}],
        [{"text": f"Auto Range: {auto_status}", "icon_custom_emoji_id": auto_emoji, "callback_data": "toggle_stex_auto", "style": "primary"},
         {"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "stex_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def zenex_control_keyboard():
    auto_status = "ON" if bot_settings.get("zenex_auto", False) else "OFF"
    auto_emoji = "5352694861990501856" if auto_status == "ON" else "5420130255174145507"
    return {"inline_keyboard": [
        [{"text": "Add Zenex Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_zenex_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_zenex_keys", "style": "danger"}],
        [{"text": "Manage Zenex Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_zenex_srv", "style": "success"}],
        [{"text": f"Auto Range: {auto_status}", "icon_custom_emoji_id": auto_emoji, "callback_data": "toggle_zenex_auto", "style": "primary"},
         {"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "zenex_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def voltx_control_keyboard():
    auto_status = "ON" if bot_settings.get("voltx_auto", False) else "OFF"
    auto_emoji = "5352694861990501856" if auto_status == "ON" else "5420130255174145507"
    return {"inline_keyboard": [
        [{"text": "Add Voltx Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_voltx_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_voltx_keys", "style": "danger"}],
        [{"text": "Manage Voltx Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_voltx_srv", "style": "success"}],
        [{"text": f"Auto Range: {auto_status}", "icon_custom_emoji_id": auto_emoji, "callback_data": "toggle_voltx_auto", "style": "primary"},
         {"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "voltx_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def specific_fw_group_keyboard(idx):
    group = bot_settings["fw_groups"][idx]
    kb = []
    for b_idx, btn in enumerate(group.get("buttons", [])):
        kb.append([{"text": f"Del: {btn['text']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_fwbtn_{idx}_{b_idx}", "style": "danger"}])
    
    kb.append([{"text": "Add Inline Button", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"add_fwbtn_{idx}", "style": "success"}])
    kb.append([{"text": "Delete Entire Group", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"del_fw_{idx}", "style": "danger"}])
    kb.append([{"text": "Back to Groups", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "primary"}])
    return {"inline_keyboard": kb}

def dxa_control_keyboard():
    bot_settings["num_req"] = 1
    w_status = "ON" if bot_settings["withdraw_on"] else "OFF"
    pending_count = len(pending_withdrawals)
    return {"inline_keyboard": [
        [{"text": f"OTP REWARD: {bot_settings['otp_reward']}", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "dxa_otp_r", "style": "primary"}],
        [{"text": f"REFER REWARD: {bot_settings['refer_reward']}", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "dxa_ref_r", "style": "success"},
         {"text": f"COOLDOWN: {bot_settings['cooldown']}s", "icon_custom_emoji_id": "5337172996211648018", "callback_data": "dxa_cool", "style": "primary"}],
        [{"text": f"NUM/SHARE: {bot_settings['num_share']}", "icon_custom_emoji_id": "5352862640592949843", "callback_data": "dxa_num_share", "style": "primary"}],
        [{"text": "BACK", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}

def withdrawal_request_keyboard(req_id):
    # Keep the action keyboard Telegram-Bot-API compatible: callback buttons
    # must not depend on optional button icon/style fields.
    return {"inline_keyboard": [[
        {"text": "APPROVE", "icon_custom_emoji_id": "5352694861990501856", "callback_data": f"wapp_{req_id}", "style": "success"},
        {"text": "REJECT", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"wrej_{req_id}", "style": "danger"}
    ]]}

def withdrawal_request_text(req_id, req_data):
    uid = req_data.get("user_id")
    return render_body_text(
        f"{PEM['money']} <b>NEW WITHDRAWAL REQUEST</b>\n\n"
        f"{PEM['user']} <b>USER:</b> <a href='tg://user?id={uid}'>{html.escape(str(req_data.get('full_name', uid)))}</a>\n"
        f"{PEM['money']} <b>AMOUNT:</b> {format_money(req_data.get('amount', 0))}\n"
        f"{PEM['phone']} <b>NUMBER:</b> <code>{html.escape(str(req_data.get('number', '')))}</code>\n"
        f"{PEM['admin']} <b>METHOD:</b> {html.escape(str(req_data.get('method', '')))}\n"
        f"{PEM['lock']} <b>STATUS:</b> PENDING\n"
        f"<b>REQUEST:</b> <code>{html.escape(str(req_id))}</code>"
    )

def w_methods_keyboard():
    kb = []
    for idx, m in enumerate(bot_settings["w_methods"]):
        kb.append([{"text": f"Delete: {m}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_wm_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Method", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_wm", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "dxa_control", "style": "primary"}])
    return {"inline_keyboard": kb}

def typed_panels_list_keyboard(p_type):
    kb = []
    for idx, p in enumerate(bot_settings["panels"]):
        if p.get("type", "API Panel") != p_type: continue
        action_text = f"Turn OFF {p['name']}" if p['status'] == 'ON' else f"Turn ON {p['name']}"
        action_icon = "5318840353510408444" if p['status'] == 'ON' else "5192812028632274956"
        icon_id = "5420155432272438703" 
        kb.append([
            {"text": action_text, "icon_custom_emoji_id": action_icon, "callback_data": f"tog_pnl_{idx}", "style": "danger" if p['status'] == 'ON' else "success"},
            {"text": f"{p['name']}", "icon_custom_emoji_id": icon_id, "callback_data": f"conf_pnl_{idx}", "style": "primary"}
        ])
    add_cb = "add_api_panel" if p_type == "API Panel" else "add_cpt_panel"
    kb.append([{"text": "Add New Provider", "icon_custom_emoji_id": "5420323438508155202", "callback_data": add_cb, "style": "success"}])
    kb.append([{"text": "Delete Provider", "icon_custom_emoji_id": "5336944168944047463", "callback_data": f"list_del_{'api' if p_type=='API Panel' else 'cpt'}", "style": "danger"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_panels", "style": "primary"}])
    return {"inline_keyboard": kb}

def panel_config_keyboard(idx):
    p = bot_settings["panels"][idx]
    
    kb = []
    action_text = "Turn OFF" if p['status'] == 'ON' else "Turn ON"
    action_icon = "5318840353510408444" if p['status'] == 'ON' else "5192812028632274956"
    kb.append([{"text": action_text, "icon_custom_emoji_id": action_icon, "callback_data": f"tog_pnl_{idx}", "style": "danger" if p['status'] == 'ON' else "success"}])
    
    if p["type"] != "Auto Captcha Panel":
        rec_count_text = "All (Unlimited)" if p.get('records', 0) == 0 else str(p.get('records'))
        kb.append([{"text": "Set API URL", "icon_custom_emoji_id": "5420517437885943844", "callback_data": f"set_p_api_{idx}", "style": "primary"}])
        kb.append([{"text": "Set Token", "icon_custom_emoji_id": "5353022963132174959", "callback_data": f"set_p_tok_{idx}", "style": "primary"}])
        kb.append([{"text": "🌐 Full API (URL+Token)", "icon_custom_emoji_id": "5420517437885943844", "callback_data": f"set_p_fapi_{idx}", "style": "primary"}])
        kb.append([{"text": f"Set Records Count: {rec_count_text}", "icon_custom_emoji_id": "5192739271886282680", "callback_data": f"set_p_rec_{idx}", "style": "primary"}])
        
    kb.append([{"text": "Test Connection", "icon_custom_emoji_id": "5352694861990501856", "callback_data": f"test_p_conn_{idx}", "style": "success"}])
        
    back_data = "manage_api_panels" if p.get("type", "API Panel") == "API Panel" else "manage_cpt_panels"
    kb.append([{"text": "Back to Providers", "icon_custom_emoji_id": "5267490665117275176", "callback_data": back_data, "style": "danger"}])
    return {"inline_keyboard": kb}

def build_traffic_ui():
    """Show OTP traffic grouped by service/country using the compact premium layout."""
    global recent_traffic
    current_time = time.time()
    try:
        window_minutes = max(1, int(bot_settings.get("traffic_window_minutes", 30)))
    except Exception:
        window_minutes = 30
    window = window_minutes * 60

    recent_traffic = [
        t for t in recent_traffic
        if current_time - t.get("time", 0) <= window
    ]

    # Traffic source modes:
    # off  = only bot-originated OTP traffic
    # on   = only Console/Auto traffic
    # all  = both sources
    mode = str(bot_settings.get("console_traffic_mode", "on")).lower()
    if mode not in ("off", "on", "all"):
        # Backward compatibility with the old boolean setting.
        mode = "on" if bot_settings.get("console_traffic", True) else "off"
    if mode == "off":
        recent_traffic = [t for t in recent_traffic if t.get("source", "bot") != "console"]
    elif mode == "on":
        recent_traffic = [t for t in recent_traffic if t.get("source", "bot") == "console"]
    # mode == all: keep both sources

    stats = {}
    for t in recent_traffic:
        srv = t.get("service", "Unknown") or "Unknown"
        iso = t.get("iso", "XX") or "XX"
        flag = t.get("flag", "🌍")
        stats.setdefault(srv, {})
        stats[srv].setdefault(iso, {"count": 0, "flag": flag})
        stats[srv][iso]["count"] += 1

    traffic_emoji = '<tg-emoji emoji-id="5203993413346680064">📊</tg-emoji>'
    txt = f"{traffic_emoji} <b>TRAFFIC</b>\n\n"

    if not stats:
        txt += f"<i>No OTP received in the last {window_minutes} minutes.</i>\n"
        return render_body_text(txt), None

    srv_totals = []
    for srv, countries in stats.items():
        total = sum(c["count"] for c in countries.values())
        srv_totals.append((srv, total, countries))
    srv_totals.sort(key=lambda x: x[1], reverse=True)

    for index, (srv, total, countries) in enumerate(srv_totals):
        app_full_name, prem_app_html = get_service_info_html(srv)
        txt += f"{prem_app_html} <b>{html.escape(app_full_name.upper())}</b>\n"

        c_list = sorted(countries.items(), key=lambda x: x[1]["count"], reverse=True)
        max_count = c_list[0][1]["count"] if c_list else 0

        for iso, c_data in c_list:
            count = c_data["count"]
            prem_flag_html = get_flag_info_html(iso)
            c_name = iso
            for code, fdata in bot_settings.get("premium_flags", {}).items():
                if fdata.get("iso") == iso:
                    c_name = fdata.get("name", iso)
                    break

            ratio = (count / max_count) if max_count else 0
            if ratio >= 0.60:
                status_emoji = '<tg-emoji emoji-id="6113685078825505075">🟢</tg-emoji>'
            elif ratio >= 0.30:
                status_emoji = '<tg-emoji emoji-id="5350512473143273043">🟡</tg-emoji>'
            else:
                status_emoji = '<tg-emoji emoji-id="5215313353706057331">🔴</tg-emoji>'

            txt += (
                f"│ {prem_flag_html} <b>{html.escape(str(c_name).upper())}</b>"
                f"    <b>{count}</b> {status_emoji}\n"
            )

        # Premium-looking separator after every service.
        txt += "└────────────────────\n"
        if index < len(srv_totals) - 1:
            txt += "\n"

    now = datetime.now().strftime("%I:%M %p")
    txt += f'\n<tg-emoji emoji-id="5336983442125001376">🕒</tg-emoji> <i>Updated {now} • Last {window_minutes} minutes</i>\n'

    # Traffic is intentionally display-only: no inline buttons.
    return render_body_text(txt), None

# ==========================================
# 💰 PAID NUMBER SYSTEM (number + API URL OTP)
# ==========================================
OTP_API_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
paid_busy = set()
_OTP_API_RE = re.compile(r'^\s*(yes|no)\b\s*[|:：]?\s*(.*)$', re.I | re.S)
_URL_RE = re.compile(r'https?://\S+', re.I)
_PHONE_RE = re.compile(r'\+?\d[\d\s().\-]{3,20}\d')


def parse_number_url_lines(text):
    """Parse lines like:  +13438839116 http://host/api/sms/record?key=...
    Returns (pairs, skipped_count, duplicate_count)."""
    existing = set()
    with purchase_lock:
        for b in number_batches.values():
            for n in b.get("numbers", []):
                existing.add(re.sub(r"\D", "", str(n.get("num", ""))))
    pairs, seen = [], set()
    skipped = dupes = 0
    for line in str(text).replace("\x00", " ").splitlines():
        line = line.strip()
        if not line:
            continue
        m = _URL_RE.search(line)
        if not m:
            skipped += 1
            continue
        url = m.group(0).rstrip(",;")
        rest = line[:m.start()] + " " + line[m.end():]
        pm = _PHONE_RE.search(rest)
        num = _normalize_uploaded_number(pm.group(0)) if pm else None
        if not num:
            skipped += 1
            continue
        digits = num[1:]
        if digits in seen or digits in existing:
            dupes += 1
            continue
        seen.add(digits)
        pairs.append((num, url))
    return pairs, skipped, dupes


def parse_otp_api_response(text):
    """Returns (has_otp, display_text, message_body).
    'NO|暂无短信验证码(...)'            -> (False, raw text, '')
    'YES|Your code: 525-589 ...'        -> (True, 'yes Your code: 525-589 ...', 'Your code: 525-589 ...')"""
    t = (text or "").strip().lstrip("\ufeff")
    if not t:
        return False, "", ""
    if t[:1] in "{[":
        try:
            data = json.loads(t)
            cands = []

            def walk(x):
                if isinstance(x, dict):
                    for v in x.values():
                        walk(v)
                elif isinstance(x, list):
                    for v in x:
                        walk(v)
                elif isinstance(x, str):
                    cands.append(x.strip())
            walk(data)
            for c in cands:
                if _OTP_API_RE.match(c):
                    t = c
                    break
        except Exception:
            pass
    m = _OTP_API_RE.match(t)
    if not m:
        return False, t[:500], ""
    flag, body = m.group(1).lower(), m.group(2).strip()
    if flag == "yes" and body:
        body = body[:1000]
        return True, f"yes {body}", body
    return False, t[:500], ""


def fetch_paid_otp(url):
    try:
        r = requests.get(url, headers=OTP_API_HEADERS, timeout=10)
        raw = r.content or b""
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("gb18030", errors="replace")
        return parse_otp_api_response(text)
    except Exception:
        return False, "", ""


def paid_min_price(service, country):
    prices = [get_effective_batch_price(b) for b in number_batches.values()
              if b.get("service") == service and b.get("country") == country
              and any(n.get("url") for n in b.get("numbers", []))]
    return min(prices) if prices else None


def _price_pair_key(service, country):
    return f"{str(service or '').strip().casefold()}::{str(country or '').strip().casefold()}"

def get_effective_batch_price(batch):
    overrides = bot_settings.setdefault("service_country_prices", {})
    key = _price_pair_key(batch.get("service"), batch.get("country"))
    try:
        if key in overrides:
            return float(overrides[key])
    except Exception:
        pass
    return float(batch.get("price", 0) or 0)

def _price_manager_pairs():
    pairs = {}
    for batch in number_batches.values():
        service = str(batch.get("service") or "").strip()
        country = str(batch.get("country") or "").strip()
        if not service or not country:
            continue
        key = _price_pair_key(service, country)
        current_price = get_effective_batch_price(batch)
        if key not in pairs:
            pairs[key] = {"service": service, "country": country, "price": current_price}
        else:
            pairs[key]["price"] = min(float(pairs[key]["price"]), current_price)
    return sorted(pairs.values(), key=lambda x: (x["service"].casefold(), x["country"].casefold()))

def price_manager_keyboard():
    kb = []
    for i, item in enumerate(_price_manager_pairs()):
        kb.append([{"text": f"{item['service']} - {item['country']}", "icon_custom_emoji_id": "5337302974806922068", "callback_data": f"pm_sel_{i}", "style": "primary"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}])
    return {"inline_keyboard": kb}

def _price_manager_show(chat_id, msg_id):
    pairs = _price_manager_pairs()
    body = f"{PEM['money']} <b>PRICE MANAGER</b>\n━━━━━━━━━━━━━━━━━━\nSelect a service and country to update its number price."
    if not pairs:
        body += "\n\nNo uploaded service/country stock found."
    edit_message(chat_id, msg_id, render_body_text(body), reply_markup=price_manager_keyboard())

def try_buy_local(chat_id, service=None, country=None, prefix=None, kind="service", change_cb="", country_cb=""):
    """Pick the cheapest matching uploaded number, charge the user and register it for OTP polling.
    Returns ("ok", rec) | ("no_balance", {"price","balance"}) | ("empty", None)."""
    global total_assigned_stats
    with purchase_lock:
        cands = []
        for b_id, b in number_batches.items():
            if service is not None and b.get("service") != service:
                continue
            if country is not None and b.get("country") != country:
                continue
            price = get_effective_batch_price(b)
            for n in b.get("numbers", []):
                if not n.get("url"):
                    continue
                if chat_id in n.get("used_by", []):
                    continue
                if prefix and not str(n["num"]).replace("+", "").startswith(prefix):
                    continue
                cands.append((price, random.random(), b_id, n))
        if not cands:
            return "empty", None
        cands.sort(key=lambda x: (x[0], x[1]))
        price, _, b_id, n = cands[0]
        balance = float(get_user(chat_id).get("balance", 0) or 0)
        if balance + 1e-9 < price:
            return "no_balance", {"price": price, "balance": balance}
        update_balance(chat_id, -price)
        b = number_batches[b_id]
        b["numbers"] = [x for x in b["numbers"] if x["num"] != n["num"]]
        # A paid API number is NOT used merely because it was assigned.
        # It becomes used only after an OTP is actually received.
        total_assigned_stats += 1
        if kind == "search":
            change_cb = f"paid_new:{b.get('service', '')}:{b.get('country', '')}"
        rec = {
            "num": n["num"], "url": n["url"], "user": chat_id, "price": price,
            "service": b.get("service", ""), "country": b.get("country", ""),
            "msg_id": None, "time": time.time(), "status": "waiting",
            "last_text": "", "otp": "", "otp_count": 0, "seen": [],
            "kind": kind, "change_cb": change_cb, "country_cb": country_cb
        }
        paid_sessions[n["num"]] = rec
        paid_user_current[chat_id] = n["num"]
        save_db()
        display_number = str(n["num"])
        if not display_number.startswith("+"):
            display_number = "+" + display_number
        _activity_group_notify(
            f"{PEM['phone']} <b>NUMBER PURCHASED</b>\n━━━━━━━━━━━━━━━━━━\n"
            f"{PEM['pin']} <b>User ID:</b> <code>{mask_activity_user_id(chat_id)}</code>\n"
            f"{PEM['world']} <b>Country:</b> {html.escape(str(b.get('country', '')))}\n"
            f"{PEM['msg']} <b>Service:</b> {html.escape(str(b.get('service', '')))}\n"
            f"{PEM['phone']} <b>Number:</b> <code>{mask_activity_number(display_number)}</code>\n"
            f"{PEM['money']} <b>Price:</b> <b>{format_money(price)}</b>"
        )
        return "ok", rec


def _premium_user_inline_button(button_data):
    """Normalize user-facing inline buttons: strip ordinary emoji glyphs and ensure a premium icon."""
    item = dict(button_data or {})
    raw_text = str(item.get("text", "Button"))
    item["text"] = re.sub(r"[\U0001F000-\U0001FAFF\u2600-\u27BF]\uFE0F?|\u200D", "", raw_text).strip() or "Open"
    if not str(item.get("icon_custom_emoji_id", "")).isdigit():
        item["icon_custom_emoji_id"] = "5420155432272438703"
    item.setdefault("style", "primary")
    return item


def build_paid_number_view(rec, final=False):
    num = str(rec.get("num", ""))
    display_num = num if num.startswith("+") else f"+{num}"
    service = str(rec.get("service", ""))
    country = str(rec.get("country", ""))
    # Uploaded stock country is authoritative. Phone prefix +1 is ambiguous and
    # must not override the country explicitly selected by the admin.
    iso = get_uploaded_country_iso(country)
    flag_emoji_id = "5780471598922337683"
    for _code, fdata in bot_settings.get("premium_flags", {}).items():
        if iso != "XX" and iso == fdata.get("iso") and fdata.get("id"):
            flag_emoji_id = fdata["id"]
            break
    flag_html = get_uploaded_country_flag_html(country)
    app_full_name, _ = get_service_info_html(service)
    app_emoji_id = "5337302974806922068"
    for app_key, app_data in bot_settings.get("premium_apps", {}).items():
        if service and (service.upper() == app_key or service.upper() in app_key or app_key in service.upper()):
            if app_data.get("id"):
                app_emoji_id = app_data["id"]
                break

    kb = [[{"text": f"{app_full_name}", "icon_custom_emoji_id": app_emoji_id, "callback_data": "ignore", "style": "primary"}]]
    kb.append([{"text": display_num, "icon_custom_emoji_id": flag_emoji_id, "copy_text": {"text": display_num}, "style": "success"}])
    otp = rec.get("otp")
    if otp:
        kb.append([{"text": str(otp), "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": str(otp)}, "style": "primary"}])

    text_numbers, extra_kb = render_new_number_message(flag_html, country, app_full_name)
    status = rec.get("last_text") or "⏳ Waiting for OTP..."
    price = float(rec.get("price", 0) or 0)
    text = text_numbers + f"\n\n💰 <b>Price:</b> {format_money(price)}\n<code>{html.escape(str(status))}</code>"
    if rec.get("status") == "refunded":
        text += f"\n\n↩️ <b>Refunded:</b> {format_money(price)}"

    if final:
        kb.append([{"text": "Number Expired", "icon_custom_emoji_id": "5336997731481193790", "callback_data": "ignore", "style": "danger"}])
        return text, kb

    if rec.get("status") == "waiting":
        kb.append([{"text": "Cancel Number", "icon_custom_emoji_id": "5422557736330106570",
                    "callback_data": f"reject_num_{num}", "style": "danger"}])
    row = []
    if rec.get("change_cb") and rec.get("status") == "waiting":
        row.append({"text": "New Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": rec["change_cb"], "style": "success"})
    if rec.get("country_cb"):
        row.append({"text": "Change Country", "icon_custom_emoji_id": "5305517382138112561", "callback_data": rec["country_cb"], "style": "danger"})
    if row:
        kb.append(row)
    menu_key = "search_number" if rec.get("kind") == "search" else "get_number"
    c_btns = []
    for c_b in bot_settings.get("custom_messages", {}).get(menu_key, {}).get("buttons", []):
        b_copy = _premium_user_inline_button(c_b)
        c_btns.append(b_copy)
    for i in range(0, len(c_btns), 2):
        kb.append(c_btns[i:i + 2])
    kb.append([{"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings.get("otp_link", ""), "style": "primary"}])
    kb.extend(extra_kb)
    return text, kb


def show_paid_number(chat_id, msg_id, rec):
    text, kb = build_paid_number_view(rec)
    res = edit_message(chat_id, msg_id, text, reply_markup={"inline_keyboard": kb}) if msg_id else {}
    new_id = msg_id
    if not (res and res.get("ok")):
        r2 = send_message(chat_id, text, reply_markup={"inline_keyboard": kb})
        new_id = (r2 or {}).get("result", {}).get("message_id")
    with purchase_lock:
        rec["msg_id"] = new_id
        save_db()


def notify_no_balance(chat_id, payload, msg_id=None):
    txt = render_body_text(
        f"{PEM['no']} <b>Insufficient balance!</b>\n\n"
        f"💰 <b>Price:</b> {format_money(payload['price'])}\n"
        f"💳 <b>Your balance:</b> {format_money(payload['balance'])}\n\n"
        f"Please contact an admin to add balance."
    )
    kb = {"inline_keyboard": [
        [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]
    ]}
    send_message(chat_id, txt, reply_markup=kb)


def finalize_paid_session(num, reason="timeout"):
    refunded = False
    with purchase_lock:
        rec = paid_sessions.get(num)
        if not rec or rec.get("status") not in ("waiting", "done", "cancel_pending"):
            return
        if (rec.get("status") == "cancel_pending" or (rec["status"] == "waiting" and not rec.get("otp_count"))):
            update_balance(rec["user"], float(rec.get("price", 0) or 0))
            rec["status"] = "refunded"
            _upsert_number_record(rejected_numbers_list, num, rec.get("url", ""))
            # Rejected numbers must never be counted as used.
            used_numbers_list[:] = [x for x in used_numbers_list if (x.get("num") if isinstance(x, dict) else str(x)) != str(num)]
            refunded = True
        else:
            rec["status"] = "closed"
        rec["closed_at"] = time.time()
        if paid_user_current.get(rec["user"]) == num:
            paid_user_current.pop(rec["user"], None)
        save_db()
    try:
        if rec.get("msg_id"):
            text, kb = build_paid_number_view(rec, final=True)
            edit_message(rec["user"], rec["msg_id"], text, reply_markup={"inline_keyboard": kb})
        if refunded:
            if reason == "timeout":
                refund_title = f"{PEM['warn']} <b>Number expired without OTP.</b>"
            elif reason == "user_reject":
                refund_title = f"{PEM['no']} <b>Number canceled successfully.</b>"
            else:
                refund_title = f"{PEM['ok']} <b>Number canceled.</b>"
            balance_now = float(get_user(rec["user"]).get("balance", 0) or 0)
            display_refund_num = str(rec.get("num", ""))
            if not display_refund_num.startswith("+"):
                display_refund_num = "+" + display_refund_num
            refund_message = (
                f"{refund_title}\n\n"
                f"🎊 <b>Number:</b> <code>{html.escape(display_refund_num)}</code>\n"
                f"{PEM['money']} <b>Refund:</b> {format_money(rec.get('price', 0))}\n"
                f"🩴 <b>Balance:</b> {format_money(balance_now)}\n"
                f"{PEM['ok']} Amount has been returned to your balance."
            )
            send_message(rec["user"], render_body_text(refund_message))
    except Exception as e:
        print(f"finalize_paid_session UI warning: {e}")


def _paid_otp_context(rec, body):
    num = str(rec["num"])
    display_num = num if num.startswith("+") else f"+{num}"
    iso = get_uploaded_country_iso(rec.get("country", ""))
    _, prem_app_html = get_service_info_html(rec.get("service", ""), body)
    return display_num, iso, get_uploaded_country_flag_html(rec.get("country", "")), prem_app_html, detect_language(body)


def notify_paid_otp(rec, body):
    try:
        otp = rec.get("otp") or ""
        display_num, iso, flag_html, prem_app_html, lang = _paid_otp_context(rec, body)
        txt = render_body_text(f"{flag_html} {iso} | {prem_app_html} {display_num} | 💬 {lang}") + f"\n\n<code>{html.escape(body)}</code>"
        kb = {"inline_keyboard": [[{"text": str(otp), "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": str(otp)}, "style": "primary"}]]} if otp else None
        send_message(rec["user"], txt, reply_markup=kb)
    except Exception as e:
        print(f"notify_paid_otp warning: {e}")


def forward_paid_otp_to_groups(rec, body):
    otp = rec.get("otp") or ""
    if not otp:
        return
    try:
        display_num, iso, flag_html, prem_app_html, lang = _paid_otp_context(rec, body)
        masked = mask_number(display_num)
        msg_text = render_body_text(f"{flag_html} {iso} | {prem_app_html} {masked} | 💬 {lang}")
        for fw in bot_settings.get("fw_groups", []):
            kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5296369303661067030", "copy_text": {"text": otp}, "style": "primary"}]]
            temp_row = []
            styles = ["danger", "success", "primary"]
            for i, btn in enumerate(fw.get("buttons", [])):
                b_obj = {"text": btn["text"], "url": btn["url"], "style": styles[i % 3]}
                if "icon_custom_emoji_id" in btn:
                    b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                temp_row.append(b_obj)
                if len(temp_row) == 2:
                    kb.append(temp_row)
                    temp_row = []
            if temp_row:
                kb.append(temp_row)
            send_message(fw["chat_id"], msg_text, reply_markup={"inline_keyboard": kb})
    except Exception as e:
        print(f"forward_paid_otp_to_groups warning: {e}")


def process_paid_record(rec):
    num = rec["num"]
    # A user-canceled number enters a pending-refund state. The configured
    # no-OTP refund window starts when the user requests cancellation.
    if rec.get("status") == "cancel_pending":
        refund_window = int(bot_settings.get("paid_expiry_minutes", 720) or 720) * 60
        cancel_at = float(rec.get("cancel_requested_at", rec.get("time", 0)) or 0)
        if time.time() - cancel_at >= refund_window:
            finalize_paid_session(num, "user_cancel_refund")
        return

    # Keep polling even if its original message was replaced by a newer order.
    # The configured no-OTP expiry controls the backend timer.
    expiry_seconds = int(bot_settings.get("paid_expiry_minutes", 720) or 720) * 60
    if time.time() - float(rec.get("time", 0)) >= expiry_seconds:
        finalize_paid_session(num, "timeout")
        return
    has_otp, disp, body = fetch_paid_otp(rec["url"])
    if not disp:
        return
    if rec.get("status") == "done" and not has_otp:
        return  # keep showing the OTP we already delivered
    new_otp = bool(has_otp and body and body not in rec.get("seen", []))
    if disp == rec.get("last_text") and not new_otp:
        return
    with purchase_lock:
        if rec.get("status") not in ("waiting", "done"):
            return
        rec["last_text"] = disp
        if new_otp:
            _upsert_number_record(used_numbers_list, num, rec.get("url", ""))
            # If a prior record exists in rejected due to legacy data, keep lists exclusive.
            rejected_numbers_list[:] = [x for x in rejected_numbers_list if (x.get("num") if isinstance(x, dict) else str(x)) != str(num)]
            rec.setdefault("seen", []).append(body)
            rec["seen"] = rec["seen"][-20:]
            rec["otp"] = extract_otp_code(body) or ""
            rec["otp_count"] = int(rec.get("otp_count", 0)) + 1
            rec["status"] = "done"
        save_db()
    if rec.get("msg_id"):
        text, kb = build_paid_number_view(rec)
        edit_message(rec["user"], rec["msg_id"], text, reply_markup={"inline_keyboard": kb})
    if new_otp:
        notify_paid_otp(rec, body)
        forward_paid_otp_to_groups(rec, body)
        uid = rec["user"]
        try:
            if db:
                db.collection('users').document(str(uid)).update({"total_otps": Increment(1)})
                if uid in user_cache:
                    user_cache[uid]["total_otps"] = user_cache[uid].get("total_otps", 0) + 1
        except Exception:
            pass


def _run_paid_record(rec):
    try:
        process_paid_record(rec)
    except Exception as e:
        print(f"Paid OTP poll error: {e}")
    finally:
        with purchase_lock:
            paid_busy.discard(rec.get("num"))


def paid_otp_poller():
    pool = ThreadPoolExecutor(max_workers=30)
    last_prune = 0
    while True:
        try:
            with purchase_lock:
                active = [r for r in paid_sessions.values()
                          if r.get("status") in ("waiting", "done", "cancel_pending") and r.get("num") not in paid_busy]
                for r in active:
                    paid_busy.add(r["num"])
            for r in active:
                pool.submit(_run_paid_record, r)
        except Exception as e:
            print(f"Paid OTP poller warning: {e}")
        time.sleep(4)


# ==========================================
# Message Handler
# ==========================================
def handle_message(msg):
    global total_uploaded_stats
    chat_id = msg["chat"]["id"]
    chat_type = msg["chat"].get("type", "private")
    
    if chat_type != "private":
        return
        
    text = msg.get("text", "")
    register_user_local(chat_id) # 🌟 Save User locally for Free Broadcasts!
    try:
        frm = msg.get("from", {})
        profile_name = " ".join([x for x in [frm.get("first_name", ""), frm.get("last_name", "")] if x]).strip() or "User"
        username = frm.get("username", "")
        u = get_user(chat_id)
        if db and (u.get("profile_name") != profile_name or u.get("username", "") != username):
            db.collection("users").document(str(chat_id)).set({"profile_name": profile_name, "username": username}, merge=True)
            u.update({"profile_name": profile_name, "username": username})
            user_cache[chat_id] = u
    except:
        pass

    if is_user_banned(chat_id):
        send_message(chat_id, render_body_text("🚫 <b>You are banned from using this bot!</b>\nIf you think this is a mistake, please contact support."))
        return
    if bot_settings.get("maintenance_mode", False) and not is_admin(chat_id):
        maintenance_text = str(bot_settings.get("maintenance_description") or "The bot is currently under maintenance. Please try again later.")
        send_message(chat_id, render_body_text(f"🛠️ <b>MAINTENANCE MODE</b>\n\n{html.escape(maintenance_text)}"))
        return
    
    # --- REFERRAL FIX: Save inviter BEFORE Force Join ---
    if text.startswith("/start"):
        parts = text.split()
        if len(parts) > 1 and parts[1].isdigit():
            inviter = int(parts[1])
            if inviter != chat_id:
                if db:
                    doc = db.collection('users').document(str(chat_id)).get()
                    if not doc.exists:
                        get_user(chat_id)
                        db.collection('users').document(str(chat_id)).update({"referred_by": inviter, "ref_paid": False})
                        
    if not check_force_join(chat_id):
        send_force_join_msg(chat_id)
        return
        
    MAIN_MENU_CMDS = ["Get Number", "Deposit", "Refer", "My profile", "My Profile", "Support", "Admin panel", "Admin Panel", "GET NUMBER", "SUPPORT", "Search Number", "2FA ONLINE"]
    
    is_main_cmd = False
    if text in MAIN_MENU_CMDS or text.startswith("/start"):
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        bulk_contexts.pop(chat_id, None)
        is_main_cmd = True
    
    if chat_id in user_states and not is_main_cmd:
        state = user_states[chat_id]

        # ================= STORE-STYLE BULK BUY QUANTITY =================
        if state == "wait_for_bulk_qty" and text:
            try:
                qty = int(text.strip())
                if qty < 1 or qty > 1000:
                    raise ValueError
            except ValueError:
                send_message(chat_id, render_body_text("❌ Enter a valid quantity from 1 to 1000."), reply_markup=get_cancel_kb())
                return
            ctx = bulk_contexts.get(chat_id) or {}
            service, country = ctx.get("service"), ctx.get("country")
            if not service or not country:
                user_states.pop(chat_id, None)
                send_message(chat_id, render_body_text("❌ Bulk purchase session expired. Please select the service and country again."))
                return
            with purchase_lock:
                stock = [(get_effective_batch_price(b), b_id, n) for b_id, b in number_batches.items()
                         if b.get("service") == service and b.get("country") == country
                         for n in b.get("numbers", []) if n.get("url") and not n.get("used_by") and not n.get("shares")]
                stock.sort(key=lambda x: x[0])
                _unique_stock, _seen_stock = [], set()
                for _entry in stock:
                    _number_key = str(_entry[2].get("num", "")).strip()
                    if _number_key and _number_key not in _seen_stock:
                        _seen_stock.add(_number_key)
                        _unique_stock.append(_entry)
                stock = _unique_stock
            if len(stock) < qty:
                send_message(chat_id, render_body_text(f"❌ Not enough unused stock. Available: <b>{len(stock)}</b>."), reply_markup=get_cancel_kb())
                return
            total = sum(float(x[0]) for x in stock[:qty])
            max_unit_price = max(float(x[0]) for x in stock[:qty])
            min_unit_price = min(float(x[0]) for x in stock[:qty])
            temp_data[chat_id] = {"bulk_qty": qty, "bulk_total": total, "bulk_min_unit_price": min_unit_price, "bulk_max_unit_price": max_unit_price, "bulk_service": service, "bulk_country": country}
            user_states[chat_id] = "confirm_bulk_buy"
            kb = {"inline_keyboard": [
                [{"text": "Confirm Purchase", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "bulk_confirm", "style": "success"}],
                [{"text": "Cancel", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "bulk_cancel", "style": "danger"}]
            ]}
            send_message(chat_id, render_body_text(
                f"<b>CONFIRM BULK BUY</b>\n━━━━━━━━━━━━━━━━━━\n"
                f"Service: <b>{html.escape(service)}</b>\nCountry: <b>{html.escape(country)}</b>\n"
                f"Quantity: <b>{qty}</b>\nUnit price: <b>{format_money(min_unit_price)}</b> – <b>{format_money(max_unit_price)}</b>\n"
                f"Total: <b>{format_money(total)}</b>"), reply_markup=kb)
            return

        # ================= DEPOSIT INPUT STATES =================
        if state == "activity_group_wait_id":
            if not is_admin(chat_id):
                user_states.pop(chat_id, None)
                return
            candidate = text.strip()
            if not re.fullmatch(r"-100\d{5,15}", candidate):
                send_message(chat_id, "সঠিক Telegram Supergroup ID দিন। উদাহরণ: <code>-1001234567890</code>")
                return
            bot_settings["activity_group_id"] = candidate
            save_db()
            user_states.pop(chat_id, None)
            send_message(chat_id, render_body_text(f"{PEM['ok']} Activity Group successfully set: <code>{html.escape(candidate)}</code>"), reply_markup=main_menu(chat_id))
            return

        if state in {
            "deposit_wait_reference", "deposit_wait_amount", "deposit_wait_gateway",
            "dep_admin_gateway_name", "dep_admin_gateway_account",
            "dep_admin_gateway_description", "dep_admin_gateway_min",
            "dep_admin_gateway_max", "dep_admin_gateway_edit", "dep_admin_gateway_confirm",
            "dep_admin_rate", "dep_admin_commission"
        }:
            if text.lower() in ("/cancel", "cancel"):
                user_states.pop(chat_id, None)
                temp_data.pop(chat_id, None)
                send_message(chat_id, "Deposit operation cancelled.", reply_markup=main_menu(chat_id))
                return
            if state.startswith("dep_admin_") and not is_admin(chat_id):
                user_states.pop(chat_id, None)
                temp_data.pop(chat_id, None)
                return
            if _deposit_handle_text(chat_id, state, text, msg.get("message_id")): 
                return

        # ================= SUPPORT USER MESSAGE =================
        if state == "support_wait_message" and (text or msg.get("caption")):
            support_text = text or msg.get("caption", "")
            u = get_user(chat_id)
            uname = u.get("username") or msg.get("from", {}).get("username") or "Not set"
            full_name = u.get("profile_name") or msg.get("from", {}).get("first_name") or "User"
            ticket = render_body_text(
                f"{PEM['msg']} <b>NEW SUPPORT MESSAGE</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"<b>User:</b> <a href='tg://user?id={chat_id}'>{html.escape(str(full_name))}</a>\n"
                f"<b>Username:</b> @{html.escape(str(uname).lstrip('@'))}\n"
                f"<b>User ID:</b> <code>{chat_id}</code>\n\n"
                f"<b>Message:</b>\n{html.escape(str(support_text))}"
            )
            delivered = 0
            for admin_id in bot_settings.get("admins", [OWNER_ID]):
                try:
                    r = send_message(admin_id, ticket, reply_markup=support_ticket_keyboard(chat_id))
                    if r and r.get("ok"): delivered += 1
                except Exception as e:
                    print(f"Support delivery error: {e}")
            if delivered:
                send_message(chat_id, render_body_text(f"{PEM['ok']} <b>Message sent to Support.</b>\n\nPlease wait for an admin reply."), reply_markup=main_menu(chat_id))
            else:
                send_message(chat_id, render_body_text(f"{PEM['warn']} <b>Support is temporarily unavailable.</b>\nPlease try again later."), reply_markup=main_menu(chat_id))
            user_states.pop(chat_id, None)
            temp_data.pop(chat_id, None)
            return

        # ================= SUPPORT ADMIN SETTINGS / REPLY =================
        if state == "support_admin_link" and text:
            link = text.strip()
            if not (link.startswith("https://t.me/") or link.startswith("http://t.me/") or link.startswith("https://telegram.me/") or link.startswith("http://telegram.me/")):
                send_message(chat_id, render_body_text(f"{PEM['warn']} <b>Invalid support link.</b>\nPlease send a valid Telegram link."))
                return
            bot_settings["support_link"] = link
            save_db()
            user_states.pop(chat_id, None); temp_data.pop(chat_id, None)
            send_message(chat_id, support_management_text(), reply_markup=support_management_keyboard())
            return

        if state == "support_admin_name" and text:
            name = text.strip()[:40]
            if not name:
                return
            bot_settings["support_button_name"] = name
            save_db()
            user_states.pop(chat_id, None); temp_data.pop(chat_id, None)
            send_message(chat_id, support_management_text(), reply_markup=support_management_keyboard())
            return

        if state == "support_admin_reply" and (text or msg.get("caption")):
            target = str(temp_data.get(chat_id, {}).get("target_user", ""))
            reply_text = text or msg.get("caption", "")
            if target and str(target).isdigit():
                target_id = int(target)
                r = send_message(target_id, render_body_text(f"{PEM['msg']} <b>SUPPORT REPLY</b>\n━━━━━━━━━━━━━━━━━━\n{html.escape(str(reply_text))}"), reply_markup=main_menu(target_id))
                if r and r.get("ok"):
                    old_msg = temp_data.get(chat_id, {}).get("msg_id")
                    if old_msg:
                        edit_message(chat_id, old_msg, render_body_text(f"{PEM['ok']} <b>SUPPORT REPLIED</b>\n\n<b>User ID:</b> <code>{html.escape(target)}</code>\n<b>Reply:</b> {html.escape(str(reply_text))}"), reply_markup=None)
                else:
                    send_message(chat_id, render_body_text(f"{PEM['warn']} <b>Could not deliver the reply.</b>"))
            user_states.pop(chat_id, None); temp_data.pop(chat_id, None)
            return

        # 🌟 Auto Captcha Panel Setup Flow 
        if state == "wait_for_cpanel_url" and text:
            temp_data[chat_id]["p_data"]["login_url"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_user"
            send_message(chat_id, render_body_text("2️⃣ <b>Username</b>\n➡️ Panel এর Username দিন:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_user" and text:
            temp_data[chat_id]["p_data"]["username"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_pass"
            send_message(chat_id, render_body_text("3️⃣ <b>Password</b>\n➡️ Panel এর Password দিন:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_pass" and text:
            temp_data[chat_id]["p_data"]["password"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_msg_link"
            send_message(chat_id, render_body_text("4️⃣ <b>Message Link</b>\n➡️ যেখান থেকে SMS/OTP ডাটা (JSON) আসবে সেই Link দিন:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_link" and text:
            temp_data[chat_id]["p_data"]["msg_link"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_num_col_name"
            send_message(chat_id, render_body_text("5️⃣ <b>Number Column Name</b>\n➡️ Data তে Number column এর নাম কী? (যেমন: number, phone):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_num_col_name" and text:
            temp_data[chat_id]["p_data"]["num_col_name"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_num_col_idx"
            send_message(chat_id, render_body_text("6️⃣ <b>Number Column Serial</b>\n➡️ Number Column এর Serial Number কত? (যেমন: 3, 5):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_num_col_idx" and text:
            if text.isdigit():
                temp_data[chat_id]["p_data"]["num_col_idx"] = int(text)
                user_states[chat_id] = "wait_for_cpanel_msg_col_name"
                send_message(chat_id, render_body_text("7️⃣ <b>Message Column Name</b>\n➡️ Message/OTP column এর নাম কী? (যেমন: message, sms):"), reply_markup=get_cancel_kb())
            else:
                 send_message(chat_id, render_body_text("❌ Please enter a valid number serial!"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_col_name" and text:
            temp_data[chat_id]["p_data"]["msg_col_name"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_msg_col_idx"
            send_message(chat_id, render_body_text("8️⃣ <b>Message Column Serial</b>\n➡️ Message Column এর Serial Number কত? (যেমন: 5, 7):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_col_idx" and text:
            if text.isdigit():
                temp_data[chat_id]["p_data"]["msg_col_idx"] = int(text)
                temp_data[chat_id]["p_data"]["login_status"] = "⏳ Pending Auto-Login..."
                
                # Save the panel configuration
                bot_settings["panels"].append(temp_data[chat_id]["p_data"])
                save_db()
                
                send_message(chat_id, render_body_text(f"{PEM['ok']} <b>Auto Captcha Panel Added Successfully!</b>\nবট এখন থেকে নিজেই ব্যাকগ্রাউন্ডে ক্যাপচা সলভ করে লগিন করে নিবে।"), reply_markup=main_menu(chat_id))
                
                msg_id = temp_data[chat_id]["msg_id"]
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_cpt_panels", "id": "internal"})
                
                del user_states[chat_id]
                del temp_data[chat_id]
            else:
                 send_message(chat_id, render_body_text("❌ Please enter a valid number serial!"), reply_markup=get_cancel_kb())
            return

        # --- Admin configuration flows ---
        elif state == "maintenance_wait_description" and text:
            if not is_admin(chat_id):
                user_states.pop(chat_id, None)
                return
            description = text.strip()
            if not description:
                send_message(chat_id, "Please send a non-empty maintenance description.", reply_markup=get_cancel_kb())
                return
            bot_settings["maintenance_description"] = description[:3500]
            bot_settings["maintenance_mode"] = True
            save_db()
            user_states.pop(chat_id, None)
            send_message(chat_id, render_body_text(f"{PEM['ok']} Maintenance mode enabled.\n\nUser notice:\n{html.escape(description[:3500])}"), reply_markup=main_menu(chat_id))
            return

        elif state == "currency_wait_rate" and text:
            if not is_admin(chat_id):
                user_states.pop(chat_id, None)
                return
            try:
                rate = float(text.replace(",", "").strip())
                if rate <= 0 or rate > 1000000:
                    raise ValueError
            except ValueError:
                send_message(chat_id, "Send a valid exchange rate greater than zero (1 USD = how many BDT?).", reply_markup=get_cancel_kb())
                return
            bot_settings["usd_to_bdt_rate"] = rate
            save_db()
            user_states.pop(chat_id, None)
            send_message(chat_id, render_body_text(f"{PEM['ok']} Exchange rate saved: 1 USD = BDT {rate:,.4f}. Current currency: {get_currency_mode()}"), reply_markup=main_menu(chat_id))
            return

        # --- User Management Flows ---
        elif state == "wait_for_um_bal_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID! Please send a numeric User ID."), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            if db:
                doc = db.collection('users').document(str(target_uid)).get()
                if not doc.exists:
                    send_message(chat_id, render_body_text("❌ User not found in database!"), reply_markup=get_cancel_kb())
                    return
                current_bal = doc.to_dict().get('balance', 0.0)
                temp_data[chat_id]["target_uid"] = target_uid
                user_states[chat_id] = "wait_for_um_bal_amt"
                send_message(chat_id, render_body_text(f"✅ User found!\n💰 Current Balance: {format_money(current_bal)}\n\n📝 Send the amount to ADD (e.g. 50) or REMOVE (e.g. -50) in {get_currency_mode()}:"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_um_bal_amt" and text:
            try:
                amt = amount_to_bdt(float(text.replace(",", "").strip()))
                target_uid = temp_data[chat_id]["target_uid"]
                update_balance(target_uid, amt)
                send_message(chat_id, render_body_text(f"{PEM['ok']} Balance updated successfully for {target_uid}!"), reply_markup=main_menu(chat_id))
                send_message(target_uid, render_body_text(f"🔔 Your balance has been adjusted by <b>{format_money(amt)}</b> by an Admin."))
                del user_states[chat_id]
                del temp_data[chat_id]
            except ValueError:
                send_message(chat_id, render_body_text("❌ Invalid amount! Please send a number."), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_um_ban_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID!"), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            if db:
                doc_ref = db.collection('users').document(str(target_uid))
                doc = doc_ref.get()
                if not doc.exists:
                    send_message(chat_id, render_body_text("❌ User not found in database!"), reply_markup=get_cancel_kb())
                    return
                current_status = doc.to_dict().get("banned", False)
                new_status = not current_status
                doc_ref.update({"banned": new_status})
                
                user_banned_cache[target_uid] = {'banned': new_status, 'time': time.time()}
                
                status_text = "BANNED 🚫" if new_status else "UNBANNED ✅"
                send_message(chat_id, render_body_text(f"✅ User {target_uid} has been {status_text}!"), reply_markup=main_menu(chat_id))
                del user_states[chat_id]
                del temp_data[chat_id]
            return

        elif state == "wait_for_um_prof_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID!"), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            if db:
                doc = db.collection('users').document(str(target_uid)).get()
                if not doc.exists:
                    send_message(chat_id, render_body_text("❌ User not found in database!"), reply_markup=get_cancel_kb())
                    return
                data = doc.to_dict()
                is_verified = True if data.get('total_otps', 0) > 0 else data.get('verified', False)
                prof_text = f"""➖➖➖➖➖➖➖➖
👤 <b>USER PROFILE</b>
➖➖➖➖➖➖➖➖
🆔 ID: <code>{target_uid}</code>
💰 Balance: {format_money(data.get('balance', 0.0))}
🤝 Total Refers: {data.get('total_refers', 0)}
🔐 Total OTPs: {data.get('total_otps', 0)}
✅ Verified: {is_verified}
🚫 Banned: {data.get('banned', False)}
➖➖➖➖➖➖➖➖"""
                kb = {"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "user_management", "style": "primary"}]]}
                send_message(chat_id, render_body_text(prof_text), reply_markup=kb)
                del user_states[chat_id]
                del temp_data[chat_id]
            return

        elif state == "wait_for_traffic_time" and text:
            try:
                minutes = int(text.strip())
                if minutes < 1 or minutes > 1440:
                    raise ValueError
                bot_settings["traffic_window_minutes"] = minutes
                save_db()
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"📊 <b>Traffic time updated</b>\n\nLast <b>{minutes} minutes</b> of OTP traffic will now be counted."), reply_markup={"inline_keyboard": [[{"text": "Back to Traffic Settings", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "md_edit_traffic", "style": "primary"}], [{"text": "Back to Menus", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "menu_design_list", "style": "danger"}]]})
            except Exception:
                send_message(chat_id, render_body_text("❌ Invalid time. Send a whole number from 1 to 1440."))
            finally:
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return

        # --- Reply Keyboard Emoji Settings ---
        elif state == "wait_for_reply_keyboard_emoji" and text:
            try:
                button_name = temp_data[chat_id]["reply_button"]
                emoji_id = None
                for ent in msg.get("entities", []):
                    if ent.get("type") == "custom_emoji" and ent.get("custom_emoji_id"):
                        emoji_id = str(ent.get("custom_emoji_id"))
                        break
                raw = text.strip()
                if emoji_id is None and raw.isdigit():
                    emoji_id = raw
                if not emoji_id:
                    send_message(chat_id, render_body_text("<b>Invalid Premium Emoji</b>\n\nSend a Premium Custom Emoji, or send its Custom Emoji ID."), reply_markup=get_cancel_kb())
                    return
                bot_settings.setdefault("reply_keyboard_emojis", {})[button_name] = emoji_id
                save_db()
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"{PEM['ok']} <b>Reply Keyboard Emoji Updated</b>\n\n<b>Button:</b> {html.escape(button_name)}\n<b>Emoji ID:</b> <code>{emoji_id}</code>"), reply_markup=reply_keyboard_emoji_settings_keyboard())
            except Exception as e:
                send_message(chat_id, render_body_text(f"{PEM['no']} Error: {html.escape(str(e))}"), reply_markup=get_cancel_kb())
            finally:
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return

        # --- Menu Design Flow ---
        elif state == "wait_for_menu_text" and text:
            try:
                menu_key = temp_data[chat_id]["menu_key"]
                formatted_html_text = extract_premium_html(msg)
                
                bot_settings["custom_messages"][menu_key]["text"] = formatted_html_text
                save_db()
                
                delete_message(chat_id, msg["message_id"])
                
                preview_text = render_body_text(formatted_html_text)
                success_text = f"{PEM['ok']} <b>Message Body Updated successfully!</b>\n\n🎨 <b>Editing: {menu_key.upper()}</b>\n\nPreview of current Text:\n{preview_text}"
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(success_text), reply_markup=menu_edit_options_keyboard(menu_key))
            except Exception as e:
                send_message(chat_id, f"❌ Error saving text: {e}")
            finally:
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return
            
        elif state == "wait_for_menu_btn" and text:
            try:
                menu_key = temp_data[chat_id]["menu_key"]
                if "-" in text:
                    parts = text.split("-", 1)
                    btn_text = parts[0].strip()
                    btn_url = parts[1].strip()
                    
                    emoji_id = None
                    emoji_char = ""
                    for ent in msg.get("entities", []):
                        if ent.get("type") == "custom_emoji":
                            emoji_id = ent.get("custom_emoji_id")
                            offset = ent.get("offset", 0)
                            length = ent.get("length", 0)
                            b_text = text.encode('utf-16-le')
                            emoji_char = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                            break
                            
                    if emoji_char:
                        btn_text = btn_text.replace(emoji_char, "").strip()
                        
                    btn_data = {"text": btn_text, "url": btn_url, "style": "primary"}
                    if emoji_id:
                        btn_data["icon_custom_emoji_id"] = emoji_id
                        
                    bot_settings["custom_messages"][menu_key]["buttons"].append(btn_data)
                    save_db()
                    delete_message(chat_id, msg["message_id"])
                    edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"{PEM['gear']} <b>Edit Inline Buttons: {menu_key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(menu_key))
                else:
                    send_message(chat_id, render_body_text(f"{PEM['no']} Invalid format. Use <code>Button Text - https://link.com</code>"))
            except Exception as e:
                 pass
            finally:
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return

        elif state == "wait_for_test_service" and text:
            temp_data[chat_id]["service"] = text.strip()
            user_states[chat_id] = "wait_for_test_number"
            send_message(chat_id, render_body_text("📝 Send the Number (e.g. +8801712345678):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_number" and text:
            temp_data[chat_id]["number"] = text.strip()
            user_states[chat_id] = "wait_for_test_otp"
            send_message(chat_id, render_body_text("📝 Send the OTP (e.g. 556677):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_otp" and text:
            temp_data[chat_id]["otp"] = text.strip()
            user_states[chat_id] = "wait_for_test_lang"
            send_message(chat_id, render_body_text("📝 Send the Language (e.g. EN, AR):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_lang" and text:
            lang = text.strip().upper()
            if not lang.startswith("#"):
                lang = "#" + lang
                
            srv = temp_data[chat_id]["service"]
            num = temp_data[chat_id]["number"]
            otp = temp_data[chat_id]["otp"]
            
            masked = mask_number(num)
            prem_flag_html = get_flag_info_html(num)
            char, iso = get_flag_and_code(num)
            app_full_name, prem_app_html = get_service_info_html(srv)
            
            lang_name = lang
            msg_text = render_body_text(f"{prem_flag_html} {iso} | {prem_app_html} {masked} | 💬 {lang}")
            
            for fw in bot_settings.get("fw_groups", []):
                kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5296369303661067030", "copy_text": {"text": otp}, "style": "primary"}]]
                temp_row = []
                styles = ["danger", "success", "primary"]
                for i, btn in enumerate(fw.get("buttons", [])):
                    b_obj = {"text": btn["text"], "url": btn["url"], "style": styles[i % 3]}
                    if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                    temp_row.append(b_obj)
                    if len(temp_row) == 2:
                        kb.append(temp_row)
                        temp_row = []
                if temp_row: kb.append(temp_row)
                send_message(fw["chat_id"], msg_text, reply_markup={"inline_keyboard": kb})
                
            send_message(chat_id, render_body_text(f"{PEM['ok']} Test message formatted and sent to all Forward Groups!"), reply_markup=main_menu(chat_id))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_mask_emoji":
            entities = msg.get("entities", [])
            custom_emoji_id = None
            emoji_text = ""
            for ent in entities:
                if ent.get("type") == "custom_emoji":
                    custom_emoji_id = ent.get("custom_emoji_id")
                    offset = ent.get("offset", 0)
                    length = ent.get("length", 0)
                    b_text = msg.get("text", "").encode("utf-16-le")
                    emoji_text = b_text[offset*2:(offset+length)*2].decode("utf-16-le")
                    break
            if custom_emoji_id:
                bot_settings["mask_emoji"] = {"id": custom_emoji_id, "char": emoji_text}
            else:
                literal_mask = str(msg.get("text", "")).strip()
                if not literal_mask or len(literal_mask) > 16 or "\n" in literal_mask:
                    send_message(chat_id, render_body_text(f"{PEM['no']} Send one Premium Emoji or a short text mask such as <code>ABC12</code> or <code>DXA</code>."), reply_markup=emoji_settings_keyboard())
                    return
                bot_settings["mask_emoji"] = {"id": "", "char": literal_mask}
            save_db()
            edit_id = temp_data.get(chat_id, {}).get("msg_id")
            if edit_id:
                edit_message(chat_id, edit_id, render_body_text(f"{PEM['ok']} Number mask updated successfully: <code>{html.escape(str(bot_settings['mask_emoji'].get('char', '')))}</code>"), reply_markup=emoji_settings_keyboard())
            else:
                send_message(chat_id, render_body_text(f"{PEM['ok']} Number mask updated successfully."), reply_markup=emoji_settings_keyboard())
            delete_message(chat_id, msg.get("message_id"))
            user_states.pop(chat_id, None)
            temp_data.pop(chat_id, None)
            return

        elif state == "wait_for_emoji_extract":
            entities = msg.get("entities", [])
            custom_emoji_id = None
            emoji_text = ""
            for ent in entities:
                if ent.get("type") == "custom_emoji":
                    custom_emoji_id = ent.get("custom_emoji_id")
                    offset = ent.get("offset", 0)
                    length = ent.get("length", 0)
                    b_text = msg.get("text", "").encode('utf-16-le')
                    emoji_text = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                    break
            
            if custom_emoji_id:
                temp_data[chat_id] = {"id": custom_emoji_id, "char": emoji_text}
                user_states[chat_id] = "wait_for_emoji_details"
                send_message(chat_id, render_body_text(f"{PEM['ok']} Emoji ID পাওয়া গেছে: <code>{custom_emoji_id}</code>\n\n📌 এখন এটি সেভ করার জন্য টাইপ এবং নাম লিখুন।\n\n<b>ফরমেট:</b>\n`FLAG | 880 | BD | Bangladesh`\nঅথবা\n`APP | WhatsApp`"), reply_markup=get_cancel_kb())
            else:
                send_message(chat_id, render_body_text(f"{PEM['no']} কোনো Premium Emoji পাওয়া যায়নি! দয়া করে Custom Emoji সেন্ড করুন।"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_emoji_details" and text:
            parts = [p.strip() for p in text.split("|")]
            mode = parts[0].upper()
            eid = temp_data[chat_id]["id"]
            char = temp_data[chat_id]["char"]
            
            if mode == "FLAG" and len(parts) == 4:
                code, iso, name = parts[1], parts[2], parts[3]
                bot_settings["premium_flags"][code] = {"char": char, "iso": iso.upper(), "name": name, "id": eid}
                save_db()
                send_message(chat_id, render_body_text(f"{PEM['ok']} Flag Emoji সেভ হয়েছে!\nCode: {code} | Name: {name}"), reply_markup=emoji_settings_keyboard())
            elif mode == "APP" and len(parts) == 2:
                name = parts[1]
                bot_settings["premium_apps"][name.upper()] = {"char": char, "id": eid, "name": name.title()}
                save_db()
                send_message(chat_id, render_body_text(f"{PEM['ok']} App Emoji সেভ হয়েছে!\nName: {name}"), reply_markup=emoji_settings_keyboard())
            else:
                send_message(chat_id, render_body_text(f"{PEM['no']} ফরম্যাট ভুল!\n\nসঠিক ফরম্যাট:\n`FLAG | 880 | BD | Bangladesh`\n`APP | WhatsApp`"))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state in ["wait_for_flag_txt", "wait_for_app_txt"] and "document" in msg:
            doc = msg["document"]
            if not doc["file_name"].endswith(".txt"):
                send_message(chat_id, render_body_text(f"{PEM['no']} Please upload a .txt file only."))
                return
            file_id = doc["file_id"]
            file_info = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
            file_path = file_info["result"]["file_path"]
            content = requests.get(f"{FILE_URL}{file_path}").text
            
            mode = "flags" if state == "wait_for_flag_txt" else "apps"
            count = 0
            
            if mode == "flags":
                for line in content.splitlines():
                    json_match = re.search(r'(\{.*\})', line)
                    if json_match:
                        try:
                            data = json.loads(json_match.group(1))
                            char = data.get("emoji")
                            eid = data.get("id")
                            
                            prefix_str = line[:json_match.start()].strip()
                            code_match = re.search(r'\((\d+)\)', prefix_str)
                            iso_match = re.search(r'\(([A-Za-z]+)\)', prefix_str)
                            
                            if code_match and iso_match and char and eid:
                                code = code_match.group(1)
                                iso = iso_match.group(1).upper()
                                name = prefix_str.replace(f"({code})", "").replace(f"({iso_match.group(1)})", "").replace(char, "").strip()
                                bot_settings["premium_flags"][code] = {"char": char, "iso": iso, "name": name, "id": eid}
                                count += 1
                        except: pass
            else:
                for line in content.splitlines():
                    json_match = re.search(r'(\{.*\})', line)
                    if json_match:
                        try:
                            data = json.loads(json_match.group(1))
                            char = data.get("emoji")
                            eid = data.get("id")
                            
                            name_part = line[:json_match.start()].strip()
                            name = name_part.replace(char, '').strip() if char else name_part
                            
                            if char and eid and name:
                                bot_settings["premium_apps"][name.upper()] = {"char": char, "id": eid, "name": name}
                                count += 1
                        except: pass
            
            save_db()
            send_message(chat_id, render_body_text(f"{PEM['ok']} Successfully loaded {count} Emojis!"), reply_markup=emoji_settings_keyboard())
            del user_states[chat_id]
            return

        elif state == "wait_for_broadcast":
            msg_id = msg["message_id"]
            status_res = send_message(chat_id, render_body_text(f"{PEM['ok']} Broadcast started..."))
            status_msg_id = None
            try:
                if status_res and status_res.get("ok") and status_res.get("result"):
                    status_msg_id = status_res["result"].get("message_id")
            except Exception:
                pass
            threading.Thread(target=broadcast_copymessage, args=(chat_id, msg_id, status_msg_id), daemon=True).start()
            del user_states[chat_id]
            return

        elif state == "wait_for_database_upload" and "document" in msg:
            doc = msg["document"]
            filename = doc.get("file_name", "")
            if not filename.lower().endswith(".zip"):
                send_message(chat_id, render_body_text(f"{PEM['no']} Please upload a <b>.zip</b> database backup."))
                return
            try:
                file_id = doc["file_id"]
                file_info_res = requests.get(f"{BASE_URL}/getFile?file_id={file_id}", timeout=15).json()
                if not file_info_res.get("ok"):
                    raise ValueError("Telegram could not locate the uploaded backup")
                file_path = file_info_res["result"]["file_path"]
                download_res = requests.get(f"{FILE_URL}{file_path}", timeout=60)
                download_res.raise_for_status()
                raw = download_res.content

                # Validate the complete backup BEFORE replacing any live database files.
                with zipfile.ZipFile(io.BytesIO(raw), "r") as z:
                    names = set(z.namelist())
                    required = {"bot_data.json", "local_db.json"}
                    if not required.issubset(names):
                        raise ValueError("Backup must contain bot_data.json and local_db.json")
                    restored_files = {}
                    for name in ("bot_data.json", "local_db.json", "users_list.json"):
                        if name in names:
                            payload = z.read(name)
                            if name.endswith(".json"):
                                parsed = json.loads(payload.decode("utf-8"))
                                if not isinstance(parsed, dict if name != "users_list.json" else list):
                                    raise ValueError(f"Invalid structure in {name}")
                            restored_files[name] = payload

                # Atomically replace each file, then reload BOTH data stores.
                for name, payload in restored_files.items():
                    tmp_name = name + ".restore.tmp"
                    with open(tmp_name, "wb") as out:
                        out.write(payload)
                        out.flush()
                        os.fsync(out.fileno())
                    os.replace(tmp_name, name)

                # Critical fix: LocalStore was initialized before upload. Reload its
                # in-memory collections so restored user balances/history are visible.
                with db.lock:
                    db._load()
                load_db()  # reload stock, sessions, settings and other bot_data.json state
                user_cache.clear()  # discard stale zero-balance user cache
                restore_pending_withdrawals()

                # Rebuild the broadcast/user index from the restored user collection.
                restored_user_ids = set()
                for user_doc in db.collection("users").select([]).stream():
                    restored_user_ids.add(str(user_doc.id))
                if "users_list.json" in restored_files:
                    try:
                        restored_user_ids.update(str(x) for x in json.loads(restored_files["users_list.json"].decode("utf-8")))
                    except Exception:
                        pass
                all_known_users.clear()
                all_known_users.update(restored_user_ids)
                _save_users_list()

                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
                send_message(chat_id, render_body_text(
                    f"{PEM['ok']} <b>Database restored successfully.</b>\n\n"
                    f"👤 Users restored: <b>{len(restored_user_ids)}</b>\n"
                    f"💰 User balances and histories reloaded from local_db.json."
                ), reply_markup=main_menu(chat_id))
            except Exception as e:
                print(f"Database restore error: {e}")
                send_message(chat_id, render_body_text(
                    f"{PEM['no']} <b>Database restore failed.</b>\n"
                    "The backup is invalid or corrupted. Existing database files were not intentionally cleared."
                ), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_special_users" and text:
            if not is_admin(chat_id):
                user_states.pop(chat_id, None)
                return
            ids = []
            for token in re.split(r"[,\s]+", text.strip()):
                if token.isdigit():
                    try:
                        uid = int(token)
                        if uid > 0 and uid not in ids:
                            ids.append(uid)
                    except ValueError:
                        pass
            if not ids:
                send_message(chat_id, render_body_text("<b>Invalid User ID.</b>\nPlease send one or more numeric Telegram user IDs."), reply_markup=get_cancel_kb())
                return
            bot_settings["special_users"] = ids
            save_db()
            user_states.pop(chat_id, None)
            send_message(chat_id, special_user_management_text(), reply_markup={"inline_keyboard": [
                [{"text": "Set Special User", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "special_users", "style": "success"}],
                [{"text": "Back to Admin", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "primary"}]
            ]})
            return

        elif state == "wait_for_paid_expiry" and text:
            if not is_admin(chat_id):
                user_states.pop(chat_id, None)
                temp_data.pop(chat_id, None)
                return
            try:
                val = int(text.strip())
                if not (1 <= val <= 43200):
                    raise ValueError
                bot_settings["paid_expiry_minutes"] = val
                save_db()
            except ValueError:
                send_message(chat_id, render_body_text("Invalid value. Enter 1–43200 minutes."), reply_markup=get_cancel_kb())
                return
            user_states.pop(chat_id, None)
            temp_data.pop(chat_id, None)
            send_message(chat_id, render_body_text(f"No-OTP refund time updated to {val} minutes."), reply_markup=system_settings_keyboard())
            return

        elif state == "wait_for_cancel_cooldown" and text:
            if not is_admin(chat_id):
                user_states.pop(chat_id, None)
                return
            try:
                val = int(text.strip())
                if not (1 <= val <= 1440):
                    raise ValueError
                bot_settings["cancel_cooldown_minutes"] = val
                save_db()
            except ValueError:
                send_message(chat_id, render_body_text("Invalid value. Enter 1–1440 minutes."), reply_markup=get_cancel_kb())
                return
            user_states.pop(chat_id, None)
            send_message(chat_id, render_body_text(f"Cancel cooldown updated to {val} minutes."), reply_markup=system_settings_keyboard())
            return

        elif state == "wait_for_service_country_price" and text:
            if not is_admin(chat_id):
                user_states.pop(chat_id, None)
                temp_data.pop(chat_id, None)
                return
            info = temp_data.get(chat_id, {})
            service, country = info.get("price_service"), info.get("price_country")
            if not service or not country:
                user_states.pop(chat_id, None)
                temp_data.pop(chat_id, None)
                send_message(chat_id, render_body_text("Service/country selection expired. Open Price Manager again."))
                return
            try:
                entered = float(text.replace(",", "").strip())
                if not (0 <= entered <= 100000000):
                    raise ValueError
                new_price = amount_to_bdt(entered)
            except ValueError:
                send_message(chat_id, render_body_text("Invalid price. Enter a number 0 or greater."), reply_markup=get_cancel_kb())
                return
            bot_settings.setdefault("service_country_prices", {})[_price_pair_key(service, country)] = new_price
            save_db()
            user_states.pop(chat_id, None)
            temp_data.pop(chat_id, None)
            send_message(chat_id, render_body_text(f"Price updated successfully.\n<b>{html.escape(service)} - {html.escape(country)}</b>\nNew price: <b>{format_money(new_price)}</b>"), reply_markup=system_settings_keyboard())
            return

        # ================= NUMBER UPLOAD (number + API URL, with price) =================
        elif state == "wait_for_txt" and "document" in msg:
            doc = msg["document"]
            filename = doc.get("file_name", "numbers.txt")
            file_id = doc["file_id"]
            try:
                file_info = requests.get(f"{BASE_URL}/getFile", params={"file_id": file_id}, timeout=15).json()
                if not file_info.get("ok"): raise ValueError("Telegram could not prepare the file")
                file_path = file_info["result"]["file_path"]
                raw_file = requests.get(f"{FILE_URL}{file_path}", timeout=60).content
                file_text = None
                for enc in ("utf-8-sig", "utf-16", "gb18030", "latin-1"):
                    try:
                        file_text = raw_file.decode(enc)
                        break
                    except Exception:
                        continue
                pairs, skipped, dupes = parse_number_url_lines(file_text or "")
                if not pairs:
                    send_message(chat_id, render_body_text(
                        f"{PEM['no']} <b>No valid lines found.</b>\n\nEach line must be:\n"
                        f"<code>+13438839116 http://www.smstx.top/api/sms/record?key=XXXX</code>"), reply_markup=get_cancel_kb())
                    return
                temp_data[chat_id] = {"pairs": pairs, "numbers": [p[0] for p in pairs], "filename": filename}
                user_states[chat_id] = "wait_for_service"
                extra = ""
                if skipped or dupes:
                    extra = f"\n⚠️ Skipped invalid lines: <b>{skipped}</b> | Duplicates: <b>{dupes}</b>"
                send_message(chat_id, render_body_text(
                    f"{PEM['ok']} <b>File received successfully.</b>\n\n📁 File: <code>{html.escape(filename)}</code>\n"
                    f"🔢 Numbers found: <b>{len(pairs)}</b>{extra}\n\n📌 Enter the service name (e.g., WHATSAPP):"), reply_markup=get_cancel_kb())
            except Exception as e:
                print(f"Number file parse error ({filename}): {e}")
                send_message(chat_id, render_body_text(f"{PEM['no']} <b>Could not read this file.</b>\nPlease upload a .txt file."), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_service" and text:
            temp_data[chat_id]["service"] = text.strip().upper()
            user_states[chat_id] = "wait_for_file_country"
            send_message(chat_id, render_body_text(
                f"{PEM['ok']} Service saved: <b>{html.escape(temp_data[chat_id]['service'])}</b>\n\n"
                f"🌍 Now enter the <b>country name</b> for these numbers (example: United States, Bangladesh, Canada).\n"
                f"Country will no longer be detected automatically."), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_file_country" and text:
            country = text.strip()
            if len(country) < 2 or len(country) > 60:
                send_message(chat_id, "Please enter a valid country name (2–60 characters).", reply_markup=get_cancel_kb())
                return
            temp_data[chat_id]["country"] = country.upper()
            user_states[chat_id] = "wait_for_file_rate"
            send_message(chat_id, render_body_text(
                f"{PEM['ok']} Country saved: <b>{html.escape(country.upper())}</b>\n\n"
                f"💰 Enter the <b>price ({get_currency_mode()})</b> a user must pay to buy <b>one number</b> from this file.\n"
                f"You can use <code>0</code> for free numbers."), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_file_rate" and text:
            try:
                entered_price = float(text.replace(",", "").strip())
                if not (0 <= entered_price <= 100000000): raise ValueError
                price = amount_to_bdt(entered_price)
            except ValueError:
                send_message(chat_id, render_body_text("❌ Invalid price! Please enter a number 0 or greater."), reply_markup=get_cancel_kb())
                return
            country = temp_data[chat_id]["country"]
            service = temp_data[chat_id]["service"]
            pairs = temp_data[chat_id]["pairs"]
            batch_id = str(uuid.uuid4())[:8]
            with purchase_lock:
                number_batches[batch_id] = {
                    "filename": temp_data[chat_id]["filename"],
                    "service": service,
                    "country": country,
                    "price": price,
                    "numbers": [{"num": n, "url": u, "shares": 0, "used_by": []} for n, u in pairs]
                }
                total_uploaded_stats += len(pairs)
                save_db()

            app_full_name, prem_app_html = get_service_info_html(service)
            prem_flag_html = get_uploaded_country_flag_html(country)
            notice = render_body_text(
                f"━━━━━━━━━━━━━━━━━━\n<b>《 NEW NUMBERS 》</b>\n━━━━━━━━━━━━━━━━━━\n"
                f"{prem_flag_html} <b>{html.escape(country)}</b>  {prem_app_html} <b>{html.escape(service)}</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"{PEM['upload']} <b>Total Added:</b> <b>{len(pairs)}</b>\n"
                f"{PEM['money']} <b>Price:</b> <b>{format_money(price)}</b> per number\n"
                f"━━━━━━━━━━━━━━━━━━\n{PEM['rocket']} Use /start to get your numbers!"
            )
            status_res = send_message(chat_id, render_body_text(
                f"{PEM['ok']} Numbers added to stock.\nPrice: <b>{format_money(price)}</b> per number\n\nStarting broadcast..."))
            status_msg_id = None
            try:
                if status_res and status_res.get("ok") and status_res.get("result"):
                    status_msg_id = status_res["result"].get("message_id")
            except Exception:
                status_msg_id = None

            def simple_broadcast():
                b_session = requests.Session()
                url = f"{BASE_URL}/sendMessage"
                for u_id in list(all_known_users):
                    try:
                        b_session.post(url, json={"chat_id": u_id, "text": notice, "parse_mode": "HTML", "disable_web_page_preview": True}, timeout=5)
                    except Exception as e:
                        print(f"New number broadcast failed for {u_id}: {e}")
                    time.sleep(0.035)
                if status_msg_id:
                    try:
                        delete_message(chat_id, status_msg_id)
                    except Exception:
                        pass
            threading.Thread(target=simple_broadcast, daemon=True).start()

            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_stex_key" and text:
            bot_settings["stex_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ StexSMS API Key Added! Total Keys: {len(bot_settings.get('stex_keys', []))}"), reply_markup=stex_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_voltx_key" and text:
            bot_settings["voltx_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ Voltx API Key Added! Total Keys: {len(bot_settings.get('voltx_keys', []))}"), reply_markup=voltx_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_sc" and text:
            code = text.strip().replace("+", "")
            if "search_countries" not in bot_settings: bot_settings["search_countries"] = []
            bot_settings["search_countries"].append(code)
            save_db()
            delete_message(chat_id, msg["message_id"])
            kb = []
            for idx, c in enumerate(bot_settings.get("search_countries", [])):
                kb.append([{"text": f"❌ Delete {c}", "callback_data": f"del_sc_{idx}", "style": "danger"}])
            kb.append([{"text": "➕ Add Country Code", "callback_data": "add_search_country", "style": "success"}])
            kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🌍 <b>Allowed Search Countries:</b>\nOnly these country codes will be allowed in Search Number."), reply_markup={"inline_keyboard": kb})
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_vsc" and text:
            code = text.strip().replace("+", "")
            if "voltx_search_countries" not in bot_settings: bot_settings["voltx_search_countries"] = []
            bot_settings["voltx_search_countries"].append(code)
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "voltx_search_country", "id": "internal"})
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_nx_srv_name" and text:
            srv = text.strip().upper()
            if "stex_services" not in bot_settings: bot_settings["stex_services"] = {}
            if srv not in bot_settings["stex_services"]: bot_settings["stex_services"][srv] = {}
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_stex_srv", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_nx_cnt_name" and text:
            cnt = text.strip()
            srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["stex_services"][srv]: bot_settings["stex_services"][srv][cnt] = []
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"nx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_nx_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            
            if new_range not in bot_settings["stex_services"][srv][cnt]:
                bot_settings["stex_services"][srv][cnt].append(new_range)
                
                if "search_countries" not in bot_settings:
                    bot_settings["search_countries"] = []
                if new_range not in bot_settings["search_countries"]:
                    bot_settings["search_countries"].append(new_range)
                    
                save_db()
                
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"nx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_vx_srv_name" and text:
            srv = text.strip().upper()
            if "voltx_services" not in bot_settings: bot_settings["voltx_services"] = {}
            if srv not in bot_settings["voltx_services"]: bot_settings["voltx_services"][srv] = {}
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_voltx_srv", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_vx_cnt_name" and text:
            cnt = text.strip()
            srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["voltx_services"][srv]: bot_settings["voltx_services"][srv][cnt] = []
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"vx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_vx_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            
            if new_range not in bot_settings["voltx_services"][srv][cnt]:
                bot_settings["voltx_services"][srv][cnt].append(new_range)
                
                if "voltx_search_countries" not in bot_settings:
                    bot_settings["voltx_search_countries"] = []
                if new_range not in bot_settings["voltx_search_countries"]:
                    bot_settings["voltx_search_countries"].append(new_range)
                    
                save_db()
                
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"vx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_for_add_zenex_key" and text:
            bot_settings["zenex_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ Zenex API Key Added! Total Keys: {len(bot_settings.get('zenex_keys', []))}"), reply_markup=zenex_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_zsc" and text:
            code = text.strip().replace("+", "")
            if "zenex_search_countries" not in bot_settings: bot_settings["zenex_search_countries"] = []
            bot_settings["zenex_search_countries"].append(code)
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "zenex_search_country", "id": "internal"})
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_zx_srv_name" and text:
            srv = text.strip().upper()
            if "zenex_services" not in bot_settings: bot_settings["zenex_services"] = {}
            if srv not in bot_settings["zenex_services"]: bot_settings["zenex_services"][srv] = {}
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_zenex_srv", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_zx_cnt_name" and text:
            cnt = text.strip()
            srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["zenex_services"][srv]: bot_settings["zenex_services"][srv][cnt] = []
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"zx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_zx_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            if new_range not in bot_settings["zenex_services"][srv][cnt]:
                bot_settings["zenex_services"][srv][cnt].append(new_range)
                if "zenex_search_countries" not in bot_settings: bot_settings["zenex_search_countries"] = []
                if new_range not in bot_settings["zenex_search_countries"]: bot_settings["zenex_search_countries"].append(new_range)
                save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"zx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_for_add_wm" and text:
            bot_settings["w_methods"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_fj" and text:
            bot_settings["fj_channels"].append(parse_chat_id(text))
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🔗 <b>FORCE JOIN SYSTEM</b>\nManage channels below:\n<i>(Note: For private links, use numeric IDs like -100...)</i>"), reply_markup=fj_settings_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return
            
        elif state == "wait_for_add_adm" and text:
            if text.isdigit():
                bot_settings["admins"].append(int(text))
                save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("👥 <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_fw_id" and text:
            bot_settings["fw_groups"].append({"chat_id": text.strip(), "buttons": []})
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return
            
        elif state == "wait_for_add_fw_btn" and text:
            fw_idx = temp_data[chat_id]["fw_idx"]
            if "-" in text:
                parts = text.split("-", 1)
                btn_text = parts[0].strip()
                btn_url = parts[1].strip()
                
                emoji_id = None
                emoji_char = ""
                for ent in msg.get("entities", []):
                    if ent.get("type") == "custom_emoji":
                        emoji_id = ent.get("custom_emoji_id")
                        offset = ent.get("offset", 0)
                        length = ent.get("length", 0)
                        b_text = text.encode('utf-16-le')
                        emoji_char = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                        break
                
                if emoji_char:
                    btn_text = btn_text.replace(emoji_char, "").strip()
                    
                btn_data = {"text": btn_text, "url": btn_url}
                if emoji_id:
                    btn_data["icon_custom_emoji_id"] = emoji_id
                    
                bot_settings["fw_groups"][fw_idx]["buttons"].append(btn_data)
                save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"🛡 <b>Manage Group:</b> {bot_settings['fw_groups'][fw_idx]['chat_id']}"), reply_markup=specific_fw_group_keyboard(fw_idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return
            
        elif state == "wait_for_otp_link" and text:
            bot_settings["otp_link"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_panel_name" and text:
            p_name = text.strip()
            t_key = temp_data[chat_id].get("add_type", "api")
            msg_id = temp_data[chat_id]["msg_id"]
            delete_message(chat_id, msg["message_id"])
            
            if t_key == "logc":
                user_states[chat_id] = "wait_for_cpanel_url"
                temp_data[chat_id] = {"msg_id": msg_id, "p_data": {
                    "name": p_name, "type": "Auto Captcha Panel", "status": "ON", "records": 0, "login_status": "⏳ Pending First Login"
                }}
                edit_message(chat_id, msg_id, render_body_text("1️⃣ <b>Login URL</b>\n➡️ Panel এর Login Link দিন:"), reply_markup=get_cancel_kb())
                return
            else:
                bot_settings["panels"].append({
                    "name": p_name, "type": "API Panel", "status": "OFF", "api_url": "", "token": "", "records": 0
                })
                save_db()
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_api_panels", "id": "internal"})
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
                return

        elif state == "wait_for_p_api" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["api_url"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_p_tok" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["token"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_p_fapi" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["full_api_url"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Full API URL:</b> <code>{p.get('full_api_url', 'None')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_p_rec" and text:
            if text.isdigit():
                idx = temp_data[chat_id]["p_idx"]
                bot_settings["panels"][idx]["records"] = int(text)
                save_db()
                delete_message(chat_id, msg["message_id"])
                p = bot_settings["panels"][idx]
                
                ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            else:
                send_message(chat_id, render_body_text("❌ Please enter a valid number! Try again."), reply_markup=get_cancel_kb())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "set_dxa":
            msg_id = temp_data[chat_id]["msg_id"]
            key = temp_data[chat_id]["key"]
            try:
                if key in ["min_withdraw", "otp_reward", "refer_reward"]: bot_settings[key] = float(text)
                elif key in ["cooldown", "num_req", "num_share"]: bot_settings[key] = int(text)
                else: bot_settings[key] = text
                save_db()
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())
            except:
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>\n\n❌ Invalid value!"), reply_markup=dxa_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_search" and text:
            query = text.strip().replace("+", "")
            if not query.isdigit() or len(query) < 3 or len(query) > 9:
                send_message(chat_id, render_body_text("❌ Please enter a valid 3 to 9 digit number!"))
                return
                
            wait_msg = send_message(chat_id, render_body_text("⌛ <i>Processing... Finding Number...</i>"))
            wait_msg_id = wait_msg.get("result", {}).get("message_id")
            
            # 💰 Paid uploaded numbers (number + API URL): charge balance, then poll API for OTP
            _st, _payload = try_buy_local(chat_id, prefix=query, kind="search", change_cb=f"c_n_s_{query}")
            if _st == "ok":
                show_paid_number(chat_id, wait_msg_id, _payload)
                return
            elif _st == "no_balance":
                if wait_msg_id: delete_message(chat_id, wait_msg_id)
                notify_no_balance(chat_id, _payload)
                return

            # 🌟 ১. প্রথমে Local থেকে নাম্বার খুঁজবে (যে কোনো দেশের জন্য)
            found_indices = []
            for b_id, b_data in number_batches.items():
                for idx, n_obj in enumerate(b_data["numbers"]):
                    if n_obj["num"].replace("+", "").startswith(query) and chat_id not in n_obj.get("used_by", []):
                        found_indices.append((b_id, idx))
            
            fetched_nums = []
            if not found_indices:
                # 🌟 ২. যদি Local এ না পায়, তখন চেক করবে Voltx বা StexSMS থেকে আনা যাবে কি না
                stex_allowed = bot_settings.get("search_countries", [])
                voltx_allowed = bot_settings.get("voltx_search_countries", [])
                
                # ফিক্স: অ্যাডমিন প্যানেলে দেশ এড না থাকলে অটোমেটিক Block করে দেবে
                is_stex_allowed = any(query.startswith(c) for c in stex_allowed) if stex_allowed else False
                is_voltx_allowed = any(query.startswith(c) for c in voltx_allowed) if voltx_allowed else False
                
                if not is_stex_allowed and not is_voltx_allowed:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ This country code is not allowed!"), reply_markup=main_menu(chat_id))
                    del user_states[chat_id]
                    return
                    
                if wait_msg_id: edit_message(chat_id, wait_msg_id, render_body_text("⌛ <i>Processing... Finding Number via API...</i>"))
                
                is_voltx_used = False
                req_count = bot_settings.get("num_req", 1)
                
                # 🌟 প্রথমে Voltx চেক করবে
                if is_voltx_allowed:
                    voltx_keys = bot_settings.get("voltx_keys", [])
                    for _ in range(req_count):
                        if len(fetched_nums) >= req_count: break
                        for api_key in voltx_keys:
                            try:
                                headers = {"mauthapi": api_key}
                                res = requests.post(f"{VOLTX_BASE_URL}/getnum", json={"rid": query}, headers=headers, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(resp_data["data"].get("national_number", ""))
                                    fetched_nums.append(num_str)
                                    voltx_assigned_numbers[num_str] = chat_id 
                                    is_voltx_used = True
                                    global total_assigned_stats
                                    total_assigned_stats += 1
                                    break # শুধু api_key লুপ ব্রেক করবে, যাতে পরের নাম্বার আনতে পারে
                            except: continue

                # 🌟 Voltx এ না পেলে বা আরও নাম্বার লাগলে StexSMS তে চেক করবে
                if len(fetched_nums) < req_count and is_stex_allowed:
                    stex_keys = bot_settings.get("stex_keys", [])
                    
                    for _ in range(req_count - len(fetched_nums)): 
                        for api_key in stex_keys:
                            try:
                                headers = {"mauthapi": api_key}
                                res = requests.post(f"{STEX_BASE_URL}/getnum", json={"rid": query}, headers=headers, timeout=10)
                                data = res.json()
                                if data.get("meta", {}).get("code") == 200 and data.get("data"):
                                    num_str = str(data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(data["data"].get("national_number", ""))
                                    fetched_nums.append(num_str)
                                    stex_assigned_numbers[num_str] = chat_id 
                                    total_assigned_stats += 1
                                    break 
                            except: continue
                        
                if not fetched_nums:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ Number out of stock!"), reply_markup=main_menu(chat_id))
                    del user_states[chat_id]
                    return
                save_db()
            else:
                random.shuffle(found_indices)
                for b_id, idx in found_indices:
                    if len(fetched_nums) >= bot_settings.get("num_req", 1): break
                    n_obj = number_batches[b_id]["numbers"][idx]
                    num_str = n_obj["num"]
                    
                    fetched_nums.append(num_str)
                    
                    n_obj["shares"] += 1
                    n_obj["used_by"].append(chat_id)
                    total_assigned_stats += 1
                    
                    if n_obj["shares"] >= bot_settings.get("num_share", 1):
                        n_obj["to_remove"] = True
                        used_numbers_list.append(num_str)
                
                for b_id in number_batches:
                    number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]
                save_db()
                
            kb = []
            flags_db = bot_settings.get("premium_flags", {})
            country_emoji_html = ""
            for num in fetched_nums:
                char_flag, iso = get_flag_and_code(num)
                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                flag_emoji_id = "5780471598922337683"
                for flag_code, flag_data in flags_db.items():
                    if iso == flag_data.get("iso"):
                        if "id" in flag_data: 
                            flag_emoji_id = flag_data["id"]
                            country_emoji_html = f'<tg-emoji emoji-id="{flag_emoji_id}">{flag_data["char"]}</tg-emoji>'
                        break
                if not country_emoji_html: country_emoji_html = char_flag
                kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": flag_emoji_id, "copy_text": {"text": display_num}, "style": "success"}])
            
            vtx_ext = "_vtx" if 'is_voltx_used' in locals() and is_voltx_used else ""
            kb.append([{"text": "Buy New", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"c_n_s_{query}{vtx_ext}", "style": "danger"}])
            
            c_btns = bot_settings["custom_messages"].get("search_number", {}).get("buttons", [])
            for c_b in c_btns: 
                b_copy = _premium_user_inline_button(c_b)
                kb.append([b_copy])
                
            kb.append([{"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
            
            text_numbers, new_number_custom_kb = render_new_number_message(country_emoji_html)
            kb.extend(new_number_custom_kb)
            
            if wait_msg_id:
                edit_message(chat_id, wait_msg_id, text_numbers, reply_markup={"inline_keyboard": kb})
                user_active_sessions[chat_id] = {"msg_id": wait_msg_id, "nums": fetched_nums}
            else:
                msg_res = send_message(chat_id, text_numbers, reply_markup={"inline_keyboard": kb})
                if msg_res and "result" in msg_res:
                    user_active_sessions[chat_id] = {"msg_id": msg_res["result"]["message_id"], "nums": fetched_nums}
            return
            
        elif state == "wait_for_withdraw_amount" and text:
            msg_id_to_edit = temp_data[chat_id].get("msg_id")
            try:
                amount = amount_to_bdt(float(text.replace(",", "").strip()))
                bal = float(temp_data[chat_id]["balance"] or 0)
                min_w = float(bot_settings['min_withdraw'])
                
                if amount < min_w:
                    if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text(f"❌ Minimum withdrawal is {format_money(min_w)}!\n💰 Balance: {format_money(bal)}\n\n📝 Enter again:"), reply_markup=get_cancel_kb())
                    return
                if amount > bal:
                    if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text(f"❌ You don't have enough balance!\n💰 Balance: {format_money(bal)}\n\n📝 Enter again:"), reply_markup=get_cancel_kb())
                    return
                    
                temp_data[chat_id]["amount"] = amount
                user_states[chat_id] = "wait_for_withdraw_number"
                if msg_id_to_edit:
                    edit_message(chat_id, msg_id_to_edit, render_body_text(f"✅ Amount: {format_money(amount)}\n\n📱 Now send your <b>{temp_data[chat_id]['method']}</b> account number:"), reply_markup=get_cancel_kb())
            except ValueError:
                if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text("❌ Invalid amount!\n\n📝 Please send a valid number:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_2fa_key" and text:
            msg_id_to_edit = temp_data.get(chat_id, {}).get("msg_id")
            delete_message(chat_id, msg.get("message_id")) # ইউজারের মেসেজ ডিলিট

            if not msg_id_to_edit:
                send_message(chat_id, render_body_text("❌ Error: Message not found. Try again."))
                del user_states[chat_id]
                return

            try:
                secret = text.strip().replace(" ", "")
                totp = pyotp.TOTP(secret)
                code = totp.now()
                remaining_time = 30 - (int(time.time()) % 30)
                
                success_txt = (
                    f"━━━━━━━━━━━━━━━\n"
                    f"《 🔐 <b>2FA CODE</b> 》\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"🔐 <b>CODE:</b> <code>{code}</code>\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"🕓 <b>EXPIRES IN:</b> {remaining_time}s\n"
                    f"━━━━━━━━━━━━━━━"
                )
                kb = [[{"text": f"Click to copy {code}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": code}, "style": "success"}],
                      [{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"ref_2fa_{secret}", "style": "primary"},
                       {"text": "New Code", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "gen_2fa", "style": "danger"}],
                      [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
                
                edit_message(chat_id, msg_id_to_edit, render_body_text(success_txt), reply_markup={"inline_keyboard": kb})
                del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            except Exception:
                error_txt = "━━━━━━━━━━━━━━━\n《 🔑 <b>ENTER 2FA KEY</b> 》\n━━━━━━━━━━━━━━━\n📝 <b>SEND YOUR 2FA SECRET KEY</b>\n━━━━━━━━━━━━━━━\n❌ <b>Invalid Secret Key! Try again.</b>\n━━━━━━━━━━━━━━━"
                cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_2fa", "style": "danger"}]]}
                edit_message(chat_id, msg_id_to_edit, render_body_text(error_txt), reply_markup=cancel_kb)
            return

        elif state == "wait_for_withdraw_number":
            msg_id_to_edit = temp_data[chat_id].get("msg_id")
            
            method = temp_data[chat_id]["method"]
            amount = temp_data[chat_id]["amount"]
            number = text
            req_id = f"W_{str(uuid.uuid4())[:6].upper()}"
            
            first_name = msg.get("from", {}).get("first_name", "User")
            last_name = msg.get("from", {}).get("last_name", "")
            full_name = f"{first_name} {last_name}".strip()
            
            update_balance(chat_id, -amount)
            pending_withdrawals[req_id] = {"user_id": chat_id, "amount": amount, "method": method, "number": number, "full_name": full_name}
            save_db()
            
            # Save to local database for history
            if db:
                try:
                    db.collection('withdrawals').document(req_id).set({
                        "user_id": str(chat_id),
                        "amount": amount,
                        "method": method,
                        "status": "pending",
                        "timestamp": SERVER_TIMESTAMP
                    })
                except: pass
            
            kb = {"inline_keyboard": [[{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]}
            success_text = f"{PEM['ok']} Your withdrawal request has been submitted!\n\n🧾 <b>Req ID:</b> {req_id}\n💰 <b>Amount:</b> {format_money(amount)}\n🏦 <b>Method:</b> {method}\n📱 <b>Number:</b> <code>{number}</code>"
            
            if msg_id_to_edit:
                edit_message(chat_id, msg_id_to_edit, render_body_text(success_text), reply_markup=kb)
            else:
                send_message(chat_id, render_body_text(success_text), reply_markup=kb)
                
            del user_states[chat_id]
            del temp_data[chat_id]
            return

    # --- Regular Commands ---
    if text.startswith("/start"):
        get_user(chat_id)
        
        # --- PROCESS PENDING REFERRAL ---
        if db:
            doc = db.collection('users').document(str(chat_id)).get()
            if doc.exists:
                u_data = doc.to_dict()
                if u_data.get("referred_by") and not u_data.get("ref_paid"):
                    inviter = u_data["referred_by"]
                    db.collection('users').document(str(chat_id)).update({"ref_paid": True})
                    reward = bot_settings.get("refer_reward", 0.2)
                    update_balance(inviter, reward)
                    db.collection('users').document(str(inviter)).update({"total_refers": Increment(1), "ref_income": Increment(float(reward))})
                    if inviter in user_cache:
                        user_cache[inviter]["total_refers"] = user_cache[inviter].get("total_refers", 0) + 1
                    ref_msg = (
                        f"{PEM['gift']} <b>New Referral !</b>\n"
                        f"------------------\n"
                        f"🔥 <b>You Received {format_money(reward)}</b>\n"
                        f"------------------\n"
                        f"{PEM['user']} <b>From User ID:</b> <code>{chat_id}</code>"
                    )
                    send_message(inviter, render_body_text(ref_msg))
                    
        c_msg = bot_settings["custom_messages"].get("start", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['hi']} Welcome!"))
        kb = []
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        
        if kb:
            send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})
            send_message(chat_id, render_body_text(f"{PEM['gear']} Navigation Menu:"), reply_markup=main_menu(chat_id))
        else:
            send_message(chat_id, txt, reply_markup=main_menu(chat_id))
            
    elif text in ("Deposit", "DEPOSIT"):
        show_deposit(chat_id, chat_id)

    elif text == "Refer":
        u_data = get_user(chat_id)
        ref_link = f"https://t.me/{BOT_USERNAME}?start={chat_id}"
        c_msg = bot_settings["custom_messages"].get("refer", {})
        
        raw_txt = c_msg.get("text", f"{PEM['gift']} Refer").replace("{ref_link}", ref_link).replace("{total_ref}", str(u_data.get('total_refers', 0))).replace("{ref_reward}", str(bot_settings['refer_reward']))
        txt = render_body_text(raw_txt)
        
        kb = [[{"text": "COPY LINK", "icon_custom_emoji_id": "5192739271886282680", "copy_text": {"text": ref_link}, "style": "success"}]]
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "CLOSE", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text in ("My profile", "My Profile"):
        # Keep profile identity current from Telegram's message metadata.
        frm = msg.get("from", {})
        profile_name = " ".join([x for x in [frm.get("first_name", ""), frm.get("last_name", "")] if x]).strip() or "User"
        username = frm.get("username", "")
        u_data = get_user(chat_id)
        updates = {}
        if u_data.get("profile_name") != profile_name:
            updates["profile_name"] = profile_name
        if u_data.get("username", "") != username:
            updates["username"] = username
        if updates and db:
            try:
                db.collection("users").document(str(chat_id)).set(updates, merge=True)
                u_data.update(updates)
                user_cache[chat_id] = u_data
            except:
                pass
        send_message(chat_id, get_user_profile_text(chat_id), reply_markup=user_profile_keyboard())

    elif text == "WITHDRAWAL":
        if not bot_settings["withdraw_on"]:
            send_message(chat_id, render_body_text(f"{PEM['no']} Withdrawals are currently disabled."))
            return
        
        u_data = get_user(chat_id)
        bal = u_data.get('balance', 0.0)
        
        c_msg = bot_settings["custom_messages"].get("withdrawal", {})
        raw_txt = c_msg.get("text", "Withdrawal").replace("{bal}", str(bal)).replace("{total_otp}", str(u_data.get('total_otps', 0))).replace("{total_ref}", str(u_data.get('total_refers', 0))).replace("{min_w}", str(bot_settings['min_withdraw']))
        txt = render_body_text(raw_txt)
        
        kb = []
        for m in bot_settings["w_methods"]:
            kb.append([{"text": m.strip(), "icon_custom_emoji_id": "5190899075968441286", "callback_data": f"sel_wm_{m.strip()}", "style": "primary"}])
        
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "Cancel", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text in ["Admin panel", "Admin Panel"] and is_admin(chat_id):
        send_message(chat_id, get_admin_text(), reply_markup=admin_panel_keyboard())

    elif text in ["Get Number", "GET NUMBER"]:
        local_srvs = set([b["service"] for b in number_batches.values() if b["numbers"]])
        stex_srvs = set(bot_settings.get("stex_services", {}).keys())
        voltx_srvs = set(bot_settings.get("voltx_services", {}).keys())
        zenex_srvs = set(bot_settings.get("zenex_services", {}).keys())
        all_services = local_srvs.union(stex_srvs).union(voltx_srvs).union(zenex_srvs)
        
        if not all_services:
            send_message(chat_id, render_body_text(f"{PEM['no']} No numbers or services available!"))
        else:
            c_msg = bot_settings["custom_messages"].get("get_number", {})
            txt = render_body_text(c_msg.get("text", f"{PEM['pin']} Select Service"))
            
            apps_db = bot_settings.get("premium_apps", {})
            kb = []
            service_buttons = []
            for s in sorted(all_services, key=lambda x: str(x).lower()):
                emoji_id = "5352694861990501856" # Default icon
                for app_key, app_data in apps_db.items():
                    if s.upper() == app_key or s.upper() in app_key or app_key in s.upper():
                        if "id" in app_data:
                            emoji_id = app_data["id"]
                            break
                service_buttons.append({"text": f"{s}", "icon_custom_emoji_id": emoji_id, "callback_data": f"g_s_{s}", "style": "primary"})
            for i in range(0, len(service_buttons), 2):
                kb.append(service_buttons[i:i + 2])
            
            custom_buttons = []
            for b in c_msg.get("buttons", []): 
                b_copy = b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                custom_buttons.append(b_copy)
            for i in range(0, len(custom_buttons), 2):
                kb.append(custom_buttons[i:i + 2])
            kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
            
            send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "Search Number":
        user_states[chat_id] = "wait_for_search"
        c_msg = bot_settings["custom_messages"].get("search_number", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['num']} Search Number"))
        kb = [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]]
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "2FA ONLINE" or text == "🔐 2FA ONLINE":
        txt = "━━━━━━━━━━━━━━━\n《 🔐 <b>2FA ONLINE</b> 》\n━━━━━━━━━━━━━━━\n<i>Generate your 2FA security code instantly using your secret key.</i>\n━━━━━━━━━━━━━━━"
        kb = [[{"text": "Generate 2fa code", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "gen_2fa", "style": "success"}],
              [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
        send_message(chat_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif text in ["Support", "SUPPORT"]:
        txt = render_body_text(
            f"{PEM['msg']} <b>SUPPORT CENTER</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Need help? Send your message to our support team.\n\n"
            f"<i>Write your issue and our admin will reply here.</i>"
        )
        send_message(chat_id, txt, reply_markup=support_user_keyboard())

def render_new_number_message(country_emoji_html, country="", service=""):
    """Render the user-facing NEW NUMBER message from Admin > Menu Design."""
    c_msg = bot_settings.get("custom_messages", {}).get("new_number", {})
    raw_txt = c_msg.get("text", "{flag} NEW NUMBER")
    raw_txt = str(raw_txt).replace("{flag}", str(country_emoji_html))
    raw_txt = raw_txt.replace("{country}", str(country)).replace("{service}", str(service))
    txt = render_body_text(raw_txt)
    # Optional custom buttons for the NEW NUMBER message.
    kb = []
    btns = []
    for b in c_msg.get("buttons", []):
        b_copy = _premium_user_inline_button(b)
        btns.append(b_copy)
    for i in range(0, len(btns), 2):
        kb.append(btns[i:i + 2])
    return txt, kb

def expire_previous_number(chat_id):
    _cur = paid_user_current.get(chat_id)
    if _cur:
        finalize_paid_session(_cur, "changed")
    if chat_id in user_active_sessions:
        prev_data = user_active_sessions[chat_id]
        prev_msg_id = prev_data["msg_id"]
        nums = prev_data["nums"]
        
        # API সিস্টেম থেকে রিমুভ করা যাতে ইনবক্সে আর মেসেজ না যায়
        for num in nums:
            if num in stex_assigned_numbers: del stex_assigned_numbers[num]
            if num in voltx_assigned_numbers: del voltx_assigned_numbers[num]
            if num in zenex_assigned_numbers: del zenex_assigned_numbers[num]
        save_db()
        
        # আগের মেসেজ ইডিট করে Expired বাটন বসানো
        kb = [[{"text": "Number Expired", "icon_custom_emoji_id": "5336997731481193790", "callback_data": "ignore", "style": "danger"}]]
        try:
            edit_message(chat_id, prev_msg_id, "NEW NUMBER\n", reply_markup={"inline_keyboard": kb})
        except:
            pass
        del user_active_sessions[chat_id]

# ==========================================
# Callback Query Handler
# ==========================================
def handle_callback(call):
    global total_assigned_stats
    chat_id = call["message"]["chat"]["id"]
    chat_type = call["message"]["chat"].get("type", "private")
    data = call.get("data", "")
    msg_id = call["message"]["message_id"]
    callback_id = str(call.get("id", ""))

    # Ignore duplicate deliveries and rapid repeated taps on the same inline button.
    # The old eager async acknowledgement raced with branch-specific answers and
    # could answer one callback twice. Each branch now owns its single response.
    now = time.time()
    action_key = (str(chat_id), str(msg_id), str(data))
    with callback_guard_lock:
        if callback_id and callback_id in callback_seen_ids:
            return
        if callback_id:
            callback_seen_ids.add(callback_id)
        previous_action = callback_action_times.get(action_key, 0)
        if now - previous_action < 1.5:
            if len(callback_seen_ids) > 5000:
                callback_seen_ids.clear()
            answer_callback(call.get("id", ""), "Please wait, this action is already processing.")
            return
        callback_action_times[action_key] = now
        # Keep the in-memory guard bounded during long-running bot sessions.
        if len(callback_action_times) > 5000:
            cutoff = now - 30
            for old_key, old_time in list(callback_action_times.items()):
                if old_time < cutoff:
                    callback_action_times.pop(old_key, None)
        if len(callback_seen_ids) > 5000:
            callback_seen_ids.clear()
            if callback_id:
                callback_seen_ids.add(callback_id)

    if chat_type != "private" and not (data.startswith("wapp_") or data.startswith("wrej_")):
        return

    if chat_type == "private":
        if is_user_banned(chat_id):
            answer_callback(call["id"], "🚫 You are banned from using this bot!", show_alert=True)
            return
        if bot_settings.get("maintenance_mode", False) and not is_admin(chat_id):
            answer_callback(call["id"], str(bot_settings.get("maintenance_description") or "Bot is under maintenance."), show_alert=True)
            return

        if not check_force_join(chat_id) and data != "check_fj":
            send_force_join_msg(chat_id)
            return

    if data == "check_fj":
        if check_force_join(chat_id):
            delete_message(chat_id, msg_id)
            send_message(chat_id, render_body_text(f"{PEM['ok']} Thanks for joining! You can now use the bot."), reply_markup=main_menu(chat_id))
            
            # --- PROCESS PENDING REFERRAL ---
            if db:
                doc = db.collection('users').document(str(chat_id)).get()
                if doc.exists:
                    u_data = doc.to_dict()
                    if u_data.get("referred_by") and not u_data.get("ref_paid"):
                        inviter = u_data["referred_by"]
                        db.collection('users').document(str(chat_id)).update({"ref_paid": True})
                        reward = bot_settings.get("refer_reward", 0.2)
                        update_balance(inviter, reward)
                        db.collection('users').document(str(inviter)).update({"total_refers": Increment(1), "ref_income": Increment(float(reward))})
                        if inviter in user_cache:
                            user_cache[inviter]["total_refers"] = user_cache[inviter].get("total_refers", 0) + 1
                        ref_msg = (
                            f"{PEM['gift']} <b>New Referral !</b>\n"
                            f"------------------\n"
                            f"🔥 <b>You Received {format_money(reward)}</b>\n"
                            f"------------------\n"
                            f"{PEM['user']} <b>From User ID:</b> <code>{chat_id}</code>"
                        )
                        send_message(inviter, render_body_text(ref_msg))
        else:
            answer_callback(call["id"], "❌ You haven't joined all channels yet!", show_alert=True)
        return

    # Admin-only global currency and maintenance controls.
    if data == "maintenance_toggle":
        if not is_admin(chat_id):
            answer_callback(call["id"], "Admin only", show_alert=True)
            return
        if bot_settings.get("maintenance_mode", False):
            bot_settings["maintenance_mode"] = False
            save_db()
            edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} <b>Maintenance mode disabled.</b> Users can use the bot again."), reply_markup=system_settings_keyboard())
        else:
            user_states[chat_id] = "maintenance_wait_description"
            edit_message(chat_id, msg_id, render_body_text("🛠️ <b>Enable Maintenance Mode</b>\n\nSend the message/description users should receive when they start the bot. Maintenance will turn ON after you send it."), reply_markup=get_cancel_kb())
        answer_callback(call["id"])
        return

    if data == "currency_settings":
        if not is_admin(chat_id):
            answer_callback(call["id"], "Admin only", show_alert=True)
            return
        edit_message(chat_id, msg_id, render_body_text(
            f"💱 <b>CURRENCY SETTINGS</b>\n\nCurrent mode: <b>{get_currency_mode()}</b>\n"
            f"Exchange rate: <b>1 USD = BDT {currency_rate():,.4f}</b>\n\n"
            "Wallet balances and stock prices remain stored in BDT internally. User-facing amount displays and new number prices use the selected currency."),
            reply_markup={"inline_keyboard": [
                [{"text": "Use BDT", "icon_custom_emoji_id": "5352985330628730418", "callback_data": "currency_set_BDT", "style": "success"},
                 {"text": "Use USD", "icon_custom_emoji_id": "5352985330628730418", "callback_data": "currency_set_USD", "style": "primary"}],
                [{"text": "Set USD/BDT Rate", "icon_custom_emoji_id": "5420155432272438703", "callback_data": "currency_rate_set", "style": "primary"}],
                [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
            ]})
        answer_callback(call["id"])
        return

    if data in ("currency_set_BDT", "currency_set_USD"):
        if not is_admin(chat_id):
            answer_callback(call["id"], "Admin only", show_alert=True)
            return
        bot_settings["currency_mode"] = data.rsplit("_", 1)[1]
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} Currency mode changed to <b>{get_currency_mode()}</b>. Exchange rate: 1 USD = BDT {currency_rate():,.4f}."), reply_markup=system_settings_keyboard())
        answer_callback(call["id"])
        return

    if data == "currency_rate_set":
        if not is_admin(chat_id):
            answer_callback(call["id"], "Admin only", show_alert=True)
            return
        user_states[chat_id] = "currency_wait_rate"
        edit_message(chat_id, msg_id, render_body_text("Send the exchange rate: how many BDT equal 1 USD? Example: <code>125</code>."), reply_markup=get_cancel_kb())
        answer_callback(call["id"])
        return

    # ================= COMPLETE DEPOSIT SYSTEM =================
    if data == "deposit_open":
        return show_deposit(chat_id, chat_id)
    if data.startswith("dep:"):
        parts = data.split(":")
        action = parts[1] if len(parts) > 1 else ""
        if action in ("admin", "gateways", "gateway", "gateway_add", "gateway_add_confirm",
                      "gateway_add_cancel", "gateway_edit_menu", "gateway_toggle",
                      "gateway_delete", "gateway_remove_confirm", "gateway_remove_yes", "gateway_edit", "pending", "approve", "reject", "set_rate", "set_commission",
                      "select", "choose_gateway", "history", "cancel", "zini_create", "zverify"):
            if action in ("admin", "gateways", "gateway", "gateway_add", "gateway_add_confirm",
                          "gateway_add_cancel", "gateway_edit_menu", "gateway_toggle",
                          "gateway_delete", "gateway_remove_confirm", "gateway_remove_yes", "gateway_edit", "pending", "approve", "reject", "set_rate", "set_commission"):
                if not is_admin(chat_id):
                    answer_callback(call["id"], "Only admins can manage deposits.", show_alert=True)
                    return
            if action == "admin":
                return _deposit_admin_menu(chat_id, msg_id)
            if action == "gateways":
                return edit_message(chat_id, msg_id, render_body_text(
                    f"{PEM['money']} <b>PAYMENT GATEWAYS</b>\nSelect a gateway to manage:"
                ), reply_markup=_deposit_gateway_list_keyboard())
            if action == "select" and len(parts) == 3:
                return _deposit_start_gateway(chat_id, chat_id, parts[2], msg_id)
            if action == "choose_gateway":
                return edit_message(chat_id, msg_id, render_body_text(
                    f"{PEM['money']} <b>SELECT PAYMENT GATEWAY</b>\n"
                    f"Deposit Amount: <b>{format_money(temp_data.get(chat_id, {}).get('requested_amount', 0))}</b>\n"
                    "একটি active gateway নির্বাচন করুন।"
                ), reply_markup=_deposit_gateway_choice_keyboard())
            if action == "history":
                return _deposit_history(chat_id, chat_id)
            if action == "zini_create":
                amount = temp_data.get(chat_id, {}).get("requested_amount", 0)
                return _zinipay_create_invoice(chat_id, amount)
            if action == "zverify" and len(parts) == 3:
                return _zinipay_verify_deposit(chat_id, parts[2])
            if action == "cancel":
                user_states.pop(chat_id, None)
                temp_data.pop(chat_id, None)
                return delete_message(chat_id, msg_id)
            if action == "gateway" and len(parts) == 3:
                return _deposit_gateway_detail(chat_id, msg_id, parts[2])
            if action == "gateway_add":
                user_states[chat_id] = "dep_admin_gateway_name"
                temp_data[chat_id] = {}
                return edit_message(chat_id, msg_id, "Send the new Payment Gateway name:", reply_markup=get_cancel_kb())
            if action == "gateway_add_cancel":
                user_states.pop(chat_id, None)
                temp_data.pop(chat_id, None)
                return _deposit_admin_menu(chat_id, msg_id)
            if action == "gateway_add_confirm":
                data_new = temp_data.get(chat_id, {}).get("new_deposit_gateway", {})
                if not data_new:
                    return _deposit_admin_menu(chat_id, msg_id)
                _deposit_defaults()
                new_id = max([int(g.get("id", 0)) for g in bot_settings["deposit_gateways"]
                              if isinstance(g, dict)] + [0]) + 1
                data_new.update({"id": new_id, "enabled": True, "created_at": datetime.now().isoformat(timespec="seconds")})
                bot_settings["deposit_gateways"].append(data_new)
                _deposit_save()
                user_states.pop(chat_id, None)
                temp_data.pop(chat_id, None)
                return edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} Gateway added successfully."),
                                    reply_markup=_deposit_gateway_list_keyboard())
            if action == "gateway_edit_menu" and len(parts) == 3:
                gid = int(parts[2])
                g = _deposit_gateway(gid)
                if not g:
                    return edit_message(chat_id, msg_id, "Gateway not found.", reply_markup=_deposit_gateway_list_keyboard())
                kb = {"inline_keyboard": [
                    [{"text": "Gateway Name", "callback_data": f"dep:gateway_edit:{gid}:name", "style": "primary"}],
                    [{"text": "Account Number", "callback_data": f"dep:gateway_edit:{gid}:account_number", "style": "primary"}],
                    [{"text": "Description", "callback_data": f"dep:gateway_edit:{gid}:description", "style": "primary"}],
                    [{"text": "Minimum Limit", "callback_data": f"dep:gateway_edit:{gid}:min_limit", "style": "primary"},
                     {"text": "Maximum Limit", "callback_data": f"dep:gateway_edit:{gid}:max_limit", "style": "primary"}],
                    [{"text": "Back", "callback_data": f"dep:gateway:{gid}", "style": "danger"}]
                ]}
                return edit_message(chat_id, msg_id, "Select the gateway field to edit:", reply_markup=kb)
            if action == "gateway_edit" and len(parts) == 4:
                gid, field = int(parts[2]), parts[3]
                if not _deposit_gateway(gid) or field not in ("name", "account_number", "description", "min_limit", "max_limit"):
                    return answer_callback(call["id"], "Invalid gateway field.", show_alert=True)
                user_states[chat_id] = "dep_admin_gateway_edit"
                temp_data[chat_id] = {"edit_gateway_id": gid, "edit_gateway_field": field}
                return edit_message(chat_id, msg_id, f"Send the new {field.replace('_', ' ')}:",
                                    reply_markup=get_cancel_kb())
            if action == "gateway_toggle" and len(parts) == 3:
                g = _deposit_gateway(parts[2])
                if not g:
                    return answer_callback(call["id"], "Gateway not found.", show_alert=True)
                g["enabled"] = not bool(g.get("enabled", True))
                _deposit_save()
                return _deposit_gateway_detail(chat_id, msg_id, parts[2])
            if action == "gateway_remove_confirm" and len(parts) == 3:
                gid = int(parts[2])
                gateway = _deposit_gateway(gid)
                if not gateway:
                    return _deposit_gateway_list_keyboard()
                return edit_message(chat_id, msg_id, render_body_text(
                    f"{PEM['warn']} <b>REMOVE PAYMENT GATEWAY?</b>\n\n"
                    f"Gateway: <b>{html.escape(str(gateway.get('name', 'Gateway')))}</b>\n"
                    "এটি Remove করলে User আর এই Gateway দিয়ে Deposit করতে পারবে না।"
                ), reply_markup={"inline_keyboard": [
                    [{"text": "Yes, Remove", "callback_data": f"dep:gateway_remove_yes:{gid}", "style": "danger"}],
                    [{"text": "Cancel", "callback_data": f"dep:gateway:{gid}", "style": "primary"}]
                ]})
            if action in ("gateway_remove_yes", "gateway_delete") and len(parts) == 3:
                gid = int(parts[2])
                bot_settings["deposit_gateways"] = [g for g in bot_settings["deposit_gateways"]
                                                    if int(g.get("id", -1)) != gid]
                _deposit_save()
                return edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} Gateway removed successfully."),
                                    reply_markup=_deposit_gateway_list_keyboard())
            if action == "pending":
                page = int(parts[2]) if len(parts) > 2 else 0
                return _deposit_pending_page(chat_id, msg_id, page)
            if action in ("approve", "reject") and len(parts) == 3:
                return _deposit_review(chat_id, msg_id, parts[2], action == "approve")
            if action == "set_rate":
                user_states[chat_id] = "dep_admin_rate"
                return edit_message(chat_id, msg_id, "Send the USD to BDT exchange rate (e.g. 125):",
                                    reply_markup=get_cancel_kb())
            if action == "set_commission":
                user_states[chat_id] = "dep_admin_commission"
                return edit_message(chat_id, msg_id, "Send deposit referral commission percentage (0–100):",
                                    reply_markup=get_cancel_kb())
        return

    if data == "activity_group":
        if not is_admin(chat_id):
            return answer_callback(call["id"], "Only admins can manage Activity Group.", show_alert=True)
        return _activity_group_menu(chat_id, msg_id)
    if data == "activity_group_set":
        if not is_admin(chat_id):
            return answer_callback(call["id"], "Only admins can manage Activity Group.", show_alert=True)
        user_states[chat_id] = "activity_group_wait_id"
        return edit_message(chat_id, msg_id, render_body_text(
            f"{PEM['msg']} <b>SEND ACTIVITY GROUP ID</b>\n\n"
            "Bot-কে ওই গ্রুপে Admin করুন এবং Group ID পাঠান।\n"
            "Example: <code>-1001234567890</code>"
        ), reply_markup=get_cancel_kb())
    if data == "activity_group_remove":
        if not is_admin(chat_id):
            return answer_callback(call["id"], "Only admins can manage Activity Group.", show_alert=True)
        bot_settings["activity_group_id"] = ""
        save_db()
        return _activity_group_menu(chat_id, msg_id)

    if data.startswith("my_orders_"):
        try:
            page = int(data[len("my_orders_"):])
        except ValueError:
            page = 0
        body, markup = my_orders_page(chat_id, page)
        edit_message(chat_id, msg_id, body, reply_markup=markup)

    elif data == "close_msg":
        delete_message(chat_id, msg_id)
        
    elif data == "cancel_state":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        bulk_contexts.pop(chat_id, None)
        delete_message(chat_id, msg_id)

    # ================= PAID NUMBER REJECTION =================
    elif data.startswith("reject_num_"):
        num = data[len("reject_num_"):]
        rec = paid_sessions.get(num)
        if not rec or rec.get("user") != chat_id or rec.get("status") != "waiting":
            answer_callback(call["id"], "This number is no longer cancelable.", show_alert=True)
            return
        wait_seconds = max(0, int(bot_settings.get("cancel_cooldown_minutes", 5) or 5) * 60 - (time.time() - float(rec.get("time", 0) or 0)))
        if wait_seconds > 0:
            answer_callback(call["id"], f"Cancel is available in {wait_seconds // 60}m {wait_seconds % 60}s.", show_alert=True)
            return
        refund_minutes = max(1, int(bot_settings.get("paid_expiry_minutes", 720) or 720))
        display_num = str(rec.get("num", ""))
        if not display_num.startswith("+"):
            display_num = "+" + display_num
        with purchase_lock:
            # Do not refund immediately. Start the configured no-OTP refund
            # countdown from the cancellation request time.
            rec["status"] = "cancel_pending"
            rec["cancel_requested_at"] = time.time()
            rec["cancel_refund_minutes"] = refund_minutes
            rec["closed_at"] = rec["cancel_requested_at"]
            if paid_user_current.get(chat_id) == num:
                paid_user_current.pop(chat_id, None)
            save_db()
        if rec.get("msg_id"):
            cancel_text = (
                "❌ <b>Number canceled successfully.</b>\n\n"
                f"🎊 <b>Number:</b> <code>{html.escape(display_num)}</code>\n"
                f"✅ Amount will return to your balance within <b>{refund_minutes} minutes</b>."
            )
            cancel_kb = {"inline_keyboard": [[{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]}
            edit_message(chat_id, rec["msg_id"], render_body_text(cancel_text), reply_markup=cancel_kb)
        answer_callback(call["id"], "Number canceled. Refund is pending.", show_alert=True)

    elif data.startswith("paid_new:"):
        if time.time() - user_cooldowns.get(chat_id, 0) < bot_settings.get("cooldown", 10):
            left = int(bot_settings.get("cooldown", 10) - (time.time() - user_cooldowns.get(chat_id, 0)))
            answer_callback(call["id"], f"Please wait {max(1, left)}s.", show_alert=True)
            return
        user_cooldowns[chat_id] = time.time()
        parts = data[len("paid_new:"):].split(":", 1)
        if len(parts) != 2:
            answer_callback(call["id"], "Invalid service/country selection.", show_alert=True)
            return
        service, country = parts
        st, payload = try_buy_local(chat_id, service=service, country=country, kind="service", change_cb=data, country_cb=f"g_s_{service}")
        if st == "ok":
            answer_callback(call["id"])
            previous_msg_id = msg_id
            for old_num, old_rec in paid_sessions.items():
                if old_num != payload.get("num") and old_rec.get("user") == chat_id and old_rec.get("msg_id") == previous_msg_id:
                    old_rec["msg_id"] = None
            show_paid_number(chat_id, previous_msg_id, payload)
        elif st == "no_balance":
            answer_callback(call["id"], f"Insufficient balance! Price: {format_money(payload['price'])} | Balance: {format_money(payload['balance'])}.", show_alert=True)
            notify_no_balance(chat_id, payload)
        else:
            answer_callback(call["id"], "No more numbers available for this service and country.", show_alert=True)

    elif data == "paid_expiry_set":
        if not is_admin(chat_id):
            return
        user_states[chat_id] = "wait_for_paid_expiry"
        edit_message(chat_id, msg_id, render_body_text("Send no-OTP refund time in minutes (1–43200). Default: 720 minutes / 12 hours."), reply_markup=get_cancel_kb())

    elif data == "cancel_cooldown_set":
        if not is_admin(chat_id):
            return
        user_states[chat_id] = "wait_for_cancel_cooldown"
        edit_message(chat_id, msg_id, render_body_text("Send cancel cooldown in minutes (1–1440). Default: 5 minutes. A number can be canceled after this waiting period."), reply_markup=get_cancel_kb())

    elif data == "cancel_2fa":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        txt = "━━━━━━━━━━━━━━━\n《 🔐 <b>2FA ONLINE</b> 》\n━━━━━━━━━━━━━━━\n<i>Generate your 2FA security code instantly using your secret key.</i>\n━━━━━━━━━━━━━━━"
        kb = [[{"text": "Generate 2fa code", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "gen_2fa", "style": "success"}],
              [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data == "gen_2fa":
        user_states[chat_id] = "wait_for_2fa_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        txt = "━━━━━━━━━━━━━━━\n《 🔑 <b>ENTER 2FA KEY</b> 》\n━━━━━━━━━━━━━━━\n📝 <b>SEND YOUR 2FA SECRET KEY</b>\n━━━━━━━━━━━━━━━"
        kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_2fa", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup=kb)
        answer_callback(call["id"])

    elif data.startswith("ref_2fa_"):
        secret = data.replace("ref_2fa_", "")
        try:
            totp = pyotp.TOTP(secret)
            code = totp.now()
            remaining_time = 30 - (int(time.time()) % 30)
            
            success_txt = (
                f"━━━━━━━━━━━━━━━\n"
                f"《 🔐 <b>2FA CODE</b> 》\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🔐 <b>CODE:</b> <code>{code}</code>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🕓 <b>EXPIRES IN:</b> {remaining_time}s\n"
                f"━━━━━━━━━━━━━━━"
            )
            kb = [[{"text": f"Click to copy {code}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": code}, "style": "success"}],
                  [{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"ref_2fa_{secret}", "style": "primary"},
                   {"text": "New Code", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "gen_2fa", "style": "danger"}],
                  [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
            
            edit_message(chat_id, msg_id, render_body_text(success_txt), reply_markup={"inline_keyboard": kb})
        except:
            answer_callback(call["id"], "❌ Error refreshing code!", show_alert=True)

    elif data == "cancel_dxa_edit":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())
        
    elif data == "dummy_alert":
        answer_callback(call["id"], "This feature will be added later!", show_alert=True)
        
    elif data == "refresh_traffic":
        txt, markup = build_traffic_ui()
        edit_message(chat_id, msg_id, txt, reply_markup=markup)
        answer_callback(call["id"], "✅ Traffic Refreshed!", show_alert=False)

    elif data.startswith("exp_rng_"):
        srv_query = data.replace("exp_rng_", "")
        
        country_stats = {}
        current_time = time.time()
        for t in recent_traffic:
            if current_time - t.get("time", 0) <= 3600:
                if t.get("service", "").startswith(srv_query):
                    iso = t.get("iso", "XX")
                    flag = t.get("flag", "🌍")
                    if iso not in country_stats:
                        country_stats[iso] = {"count": 0, "flag": flag}
                    country_stats[iso]["count"] += 1
        
        if not country_stats:
            answer_callback(call["id"], "❌ No recent traffic found for this service!", show_alert=True)
            return
            
        kb = []
        for iso, c_data in sorted(country_stats.items(), key=lambda x: x[1]["count"], reverse=True):
            count = c_data["count"]
            c_name = iso
            emoji_id = "5780471598922337683"
            for code, fdata in bot_settings.get("premium_flags", {}).items():
                if fdata.get("iso") == iso:
                    c_name = fdata.get("name", iso)
                    if "id" in fdata: emoji_id = fdata["id"]
                    break
            
            btn_text = f"{c_name} ({iso}) - {count} OTP"
            kb.append([{"text": btn_text, "icon_custom_emoji_id": emoji_id, "callback_data": f"exp_c_{srv_query}_{iso}", "style": "primary"}])
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "refresh_traffic", "style": "danger"}])
        
        app_full_name, prem_app_html = get_service_info_html(srv_query)
        edit_message(chat_id, msg_id, render_body_text(f"📊 <b>Explore Service: {prem_app_html} {app_full_name}</b>\n\nSelect a country to view available ranges:"), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data.startswith("exp_c_"):
        parts = data.split("_")
        srv_query = parts[2]
        iso_query = parts[3]
        
        nums = []
        current_time = time.time()
        for t in recent_traffic:
            if current_time - t.get("time", 0) <= 3600:
                if t.get("service", "").startswith(srv_query) and t.get("iso") == iso_query:
                    # 🌟 X রিমুভ করে ক্লিন রেঞ্জ নেওয়া হলো
                    num = t.get("real_range", t.get("number", "").replace("X", "").replace("x", "")).replace("+", "").strip()
                    if num: nums.append(num)
        
        if not nums:
            answer_callback(call["id"], "❌ No recent numbers found for this country!", show_alert=True)
            return
            
        # শুধুমাত্র StexSMS Services থেকে রেঞ্জ নিবো (Search Countries নিবো না, কারণ ওগুলোতে শুধু দেশের কোড থাকে)
        known_ranges = set()
        for s_name, c_dict in bot_settings.get("stex_services", {}).items():
            for c_name, r_list in c_dict.items():
                for r in r_list:
                    # 🌟 এখানেও সেভ করা রেঞ্জ থেকে X সরিয়ে নিচ্ছি
                    known_ranges.add(r.replace("X", "").replace("x", ""))
                    
        sorted_known = sorted(list(known_ranges), key=len, reverse=True)
        
        r_counts = Counter()
        for num in nums:
            matched = False
            for r in sorted_known:
                if num.startswith(r):
                    r_counts[r] += 1
                    matched = True
                    break
            if not matched:
                if len(num) >= 7:
                    r_counts[num[:7]] += 1
                else:
                    r_counts[num] += 1
                    
        r_list = r_counts.most_common(12)
        
        kb = []
        temp_row = []
        for r, count in r_list:
            # 🌟 বাটনে এবং কলব্যাকে যাতে কোনো X না থাকে তা নিশ্চিত করা হলো
            clean_r = str(r).replace("X", "").replace("x", "")
            temp_row.append({"text": f"{clean_r} ({count})", "icon_custom_emoji_id": "5352862640592949843", "callback_data": f"c_n_s_{clean_r}_{srv_query}", "style": "primary"})
            if len(temp_row) == 2:
                kb.append(temp_row)
                temp_row = []
        if temp_row:
            kb.append(temp_row)
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"exp_rng_{srv_query}", "style": "danger"}])
        
        app_full_name, prem_app_html = get_service_info_html(srv_query)
        prem_flag_html = get_flag_info_html(iso_query)
        
        edit_message(chat_id, msg_id, render_body_text(f"📊 <b>Ranges for {prem_app_html} {app_full_name} - {prem_flag_html} {iso_query}</b>\n\nClick on any range to copy it."), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    # --- User Management Flows Integration ---
    elif data == "user_management":
        edit_message(chat_id, msg_id, get_user_management_text(), reply_markup=user_management_keyboard())

    elif data == "um_manage_balance":
        user_states[chat_id] = "wait_for_um_bal_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to Manage Balance:"), reply_markup=get_cancel_kb())
        
    elif data == "um_ban_unban":
        user_states[chat_id] = "wait_for_um_ban_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to Ban or Unban:"), reply_markup=get_cancel_kb())

    elif data == "um_user_profile":
        user_states[chat_id] = "wait_for_um_prof_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to View Profile:"), reply_markup=get_cancel_kb())

    elif data == "um_all_users":
        if not is_admin(chat_id): return
        rows = []
        for uid_s in sorted(all_known_users, key=lambda x: int(x) if str(x).isdigit() else 0):
            try:
                uid = int(uid_s)
                u = get_user(uid)
                uname = str(u.get("username") or "Not set")
                username = ("@" + uname.lstrip("@")) if uname != "Not set" else "Not set"
                rows.append(
                    f"{PEM['user']} <b>{html.escape(username)}</b>  |  {PEM['num']} <code>{uid}</code>\n"
                    f"{PEM['money']} <b>{format_money(u.get('balance', 0))}</b>  |  "
                    f"{PEM['gift']} Ref: <b>{int(u.get('total_refers', 0) or 0)}</b>  |  "
                    f"{PEM['msg']} OTP: <b>{int(u.get('total_otps', 0) or 0)}</b>"
                )
            except Exception:
                continue
        if not rows:
            rows = [f"{PEM['warn']} No users found."]
        header = (
            f"{PEM['admin']} <b>ALL USERS</b>\n━━━━━━━━━━━━━━━━━━\n"
            f"{PEM['user']} Username  |  {PEM['num']} User ID\n"
            f"{PEM['money']} Balance  |  {PEM['gift']} Refer  |  {PEM['msg']} OTP\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
        )
        for start_idx in range(0, len(rows), 20):
            send_message(chat_id, render_body_text(header + "\n━━━━━━━━━━━━━━━━━━\n".join(rows[start_idx:start_idx+20])))
        answer_callback(call["id"])

    # --- Menu Design Integration ---
    elif data == "menu_design_list":
        edit_message(chat_id, msg_id, render_body_text(f"🎨 <b>Menu Design Editor</b>\n\nSelect a menu block to edit its Body Text and Inline Buttons. You can use Premium Emojis too!"), reply_markup=menu_design_list_keyboard())

    elif data == "md_reset_defaults":
        bot_settings["custom_messages"] = DEFAULT_CUSTOM_MESSAGES.copy()
        save_db()
        answer_callback(call["id"], "✅ Resetted to Premium Defaults!", show_alert=True)

    elif data == "reply_keyboard_emoji_settings":
        if not is_admin(chat_id):
            answer_callback(call["id"], "Not authorized", show_alert=True)
            return
        edit_message(chat_id, msg_id, render_body_text("🎨 <b>Reply Keyboard Emoji</b>\n\nSelect a button to change its Premium Custom Emoji.\nSend the Premium Emoji itself, or send its Custom Emoji ID."), reply_markup=reply_keyboard_emoji_settings_keyboard())
        answer_callback(call["id"])

    elif data.startswith("rkemoji_set:"):
        if not is_admin(chat_id):
            answer_callback(call["id"], "Not authorized", show_alert=True)
            return
        button_name = data.split(":", 1)[1]
        user_states[chat_id] = "wait_for_reply_keyboard_emoji"
        temp_data[chat_id] = {"msg_id": msg_id, "reply_button": button_name}
        edit_message(chat_id, msg_id, render_body_text(f"🎨 <b>Set Emoji: {html.escape(button_name)}</b>\n\nSend the Premium Custom Emoji now, or send its Custom Emoji ID."), reply_markup=get_cancel_kb())
        answer_callback(call["id"])

    elif data == "md_edit_traffic":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        try:
            current_window = max(1, int(bot_settings.get("traffic_window_minutes", 30)))
        except Exception:
            current_window = 30
        mode = str(bot_settings.get("console_traffic_mode", "on")).lower()
        if mode not in ("off", "on", "all"):
            mode = "on" if bot_settings.get("console_traffic", True) else "off"
        mode_style = {"on": "success", "off": "primary", "all": "danger"}.get(mode, "success")
        traffic_kb = {"inline_keyboard": [
            [{"text": "Consol Traffic", "icon_custom_emoji_id": "5203993413346680064", "callback_data": "console_traffic_cycle", "style": mode_style}],
            [{"text": "Set Traffic Time", "icon_custom_emoji_id": "5420155432272438703", "callback_data": "traffic_time_custom", "style": "primary"}],
            [{"text": "Back to Menus", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "menu_design_list", "style": "danger"}]
        ]}
        edit_message(chat_id, msg_id, render_body_text(f"📊 <b>Edit TRAFFIC</b>\n\nCurrent traffic window: <b>{current_window} minutes</b>\n\nConsol Traffic mode is selected by the button color."), reply_markup=traffic_kb)
        answer_callback(call["id"])

    elif data == "traffic_time_custom":
        user_states[chat_id] = "wait_for_traffic_time"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📊 <b>Set Custom Traffic Time</b>\n\nSend the number of minutes. Example: <code>15</code> or <code>45</code>\n\nMinimum: 1 minute."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "md_edit_traffic", "style": "danger"}]]})
        answer_callback(call["id"])

    elif data.startswith("md_edit_"):
        answer_callback(call["id"])
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        key = data.replace("md_edit_", "")
        cm_text = render_body_text(bot_settings["custom_messages"].get(key, {}).get("text", "..."))
        try:
            edit_message(chat_id, msg_id, render_body_text(f"🎨 <b>Editing: {key.upper()}</b>\n\nPreview of current Text:\n{cm_text}"), reply_markup=menu_edit_options_keyboard(key))
        except: pass

    elif data.startswith("md_text_"):
        key = data.replace("md_text_", "")
        user_states[chat_id] = "wait_for_menu_text"
        temp_data[chat_id] = {"msg_id": msg_id, "menu_key": key}
        edit_message(chat_id, msg_id, render_body_text(f"📝 <b>Edit Body: {key.upper()}</b>\n\nSend the new text. You can use Premium Emojis directly here.\n(Use standard HTML like <b>bold</b>, <i>italic</i> for formatting)"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_edit_{key}", "style": "danger"}]]})

    elif data.startswith("md_btns_"):
        answer_callback(call["id"]) 
        if chat_id in user_states: del user_states[chat_id] 
        if chat_id in temp_data: del temp_data[chat_id]
        key = data.replace("md_btns_", "")
        try:
            edit_message(chat_id, msg_id, render_body_text(f"⚙️ <b>Edit Inline Buttons: {key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(key))
        except: pass

    elif data.startswith("md_addbtn_"):
        key = data.replace("md_addbtn_", "")
        user_states[chat_id] = "wait_for_menu_btn"
        temp_data[chat_id] = {"msg_id": msg_id, "menu_key": key}
        edit_message(chat_id, msg_id, render_body_text(f"➕ <b>Add Button: {key.upper()}</b>\n\nSend custom button in this format:\n<code>Button Text - https://link.com</code>\n\n<i>(Only normal Emojis supported here!)</i>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_btns_{key}", "style": "danger"}]]})

    elif data.startswith("md_delbtn_"):
        parts = data.split("_")
        key = parts[2]
        b_idx = int(parts[3])
        if b_idx < len(bot_settings["custom_messages"][key]["buttons"]):
            del bot_settings["custom_messages"][key]["buttons"][b_idx]
            save_db()
            answer_callback(call["id"], "✅ Button Deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"⚙️ <b>Edit Inline Buttons: {key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(key))

    elif data == "profile_withdraw":
        if not bot_settings.get("withdraw_on", True):
            answer_callback(call["id"], "Withdrawals are currently disabled.", show_alert=True)
            return
        # Reuse the existing withdrawal workflow from the profile button.
        u_data = get_user(chat_id)
        bal = u_data.get("balance", 0.0)
        min_w = bot_settings.get("min_withdraw", 0)
        if bal < min_w:
            answer_callback(call["id"], f"Minimum withdrawal is {format_money(min_w)}.", show_alert=True)
            return
        c_msg = bot_settings["custom_messages"].get("withdrawal", {})
        raw_txt = c_msg.get("text", "Withdrawal").replace("{bal}", str(bal)).replace("{total_otp}", str(u_data.get("total_otps", 0))).replace("{total_ref}", str(u_data.get("total_refers", 0))).replace("{min_w}", str(min_w))
        kb = []
        for m in bot_settings.get("w_methods", []):
            kb.append([{"text": m.strip(), "icon_custom_emoji_id": "5190899075968441286", "callback_data": f"sel_wm_{m.strip()}", "style": "primary"}])
        kb.append([{"text": "Cancel", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text(raw_txt), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data.startswith("sel_wm_"):
        method = data.replace("sel_wm_", "")
        bal = get_user(chat_id).get('balance', 0.0)
        min_w = bot_settings['min_withdraw']
        
        if bal < min_w:
            answer_callback(call["id"], f"❌ আপনার ব্যালেন্স অপর্যাপ্ত! মিনিমাম {format_money(min_w)} প্রয়োজন।", show_alert=True)
            return
            
        temp_data[chat_id] = {"method": method, "balance": bal, "msg_id": msg_id}
        user_states[chat_id] = "wait_for_withdraw_amount"
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} Method: {method}\n💰 Available Balance: {format_money(bal)}\n\n📝 Enter the amount you want to withdraw (Min: {format_money(min_w)}):"), reply_markup=get_cancel_kb())
        answer_callback(call["id"])

    elif data == "test_message_flow":
        user_states[chat_id] = "wait_for_test_service"
        temp_data[chat_id] = {}
        edit_message(chat_id, msg_id, render_body_text("🧪 <b>Test Mode</b>\n\n📝 Send the Service Name (e.g., IG):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]]})

    elif data == "manage_emojis":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['star']} <b>Premium Emoji Management</b>\n\nUpload your TXT files or manually add them below:"), reply_markup=emoji_settings_keyboard())

    elif data == "up_flags_txt":
        user_states[chat_id] = "wait_for_flag_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the <b>Flag Emojis</b> <code>.txt</code> file."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "up_apps_txt":
        user_states[chat_id] = "wait_for_app_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the <b>Service Apps</b> <code>.txt</code> file."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "add_single_emoji":
        user_states[chat_id] = "wait_for_emoji_extract"
        edit_message(chat_id, msg_id, render_body_text("📝 যেকোনো একটি Premium Emoji সেন্ড করুন (যেমন: 🇧🇩 বা 🚫):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "set_mask_emoji":
        user_states[chat_id] = "wait_for_mask_emoji"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send a Premium Custom Emoji OR plain text such as ABC12 / DXA to use between the first and last digits of masked numbers."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})
        answer_callback(call["id"])

    elif data == "dl_flags_txt":
        content = generate_emoji_txt("flags")
        if content:
            send_document(chat_id, "Flag_Emojis.txt", content)
            answer_callback(call["id"], "✅ Downloaded!")
        else:
            answer_callback(call["id"], "❌ No Flag Emojis found!", show_alert=True)

    elif data == "dl_apps_txt":
        content = generate_emoji_txt("apps")
        if content:
            send_document(chat_id, "Service_Apps.txt", content)
            answer_callback(call["id"], "✅ Downloaded!")
        else:
            answer_callback(call["id"], "❌ No App Emojis found!", show_alert=True)

    elif data == "del_all_flags":
        bot_settings["premium_flags"] = {}
        save_db()
        answer_callback(call["id"], "✅ All Premium Flags Deleted Successfully!", show_alert=True)

    elif data == "database_menu":
        edit_message(chat_id, msg_id, render_body_text(
            f"{PEM['file']} <b>DATABASE</b>\n\nManage the bot database backup and restore operations."
        ), reply_markup=database_keyboard())

    elif data == "db_download":
        backup = create_database_backup()
        if send_file_document(chat_id, "database_backup.zip", backup):
            answer_callback(call["id"], "Database backup sent.", show_alert=False)
        else:
            answer_callback(call["id"], "Database download failed.", show_alert=True)

    elif data == "db_upload":
        user_states[chat_id] = "wait_for_database_upload"
        edit_message(chat_id, msg_id, render_body_text(
            f"{PEM['upload']} <b>UPLOAD DATABASE</b>\n\nSend the database backup <code>.zip</code> file."
        ), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "database_menu", "style": "danger"}]]})

    elif data == "db_clear_confirm":
        edit_message(chat_id, msg_id, render_body_text(
            f"{PEM['warn']} <b>CLEAR ALL DATABASE DATA?</b>\n\nThis will permanently remove users, balances, referrals, withdrawals, number stock, traffic and saved settings.\n\nContinue only if you have a backup."
        ), reply_markup={"inline_keyboard": [
            [{"text": "Yes, Clear All Data", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "db_clear_all", "style": "danger"}],
            [{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "database_menu", "style": "primary"}]
        ]})

    elif data == "db_clear_all":
        if not is_admin(chat_id):
            return
        reset_all_database_data()
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} <b>All database data has been cleared.</b>"), reply_markup=admin_panel_keyboard())

    elif data == "broadcast_msg":
        user_states[chat_id] = "wait_for_broadcast"
        edit_message(chat_id, msg_id, render_body_text("📢 <b>Broadcast Mode</b>\n\nSend the message you want to broadcast (Text, Photo, Video, File etc)."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]})

    elif data == "upload_num":
        user_states[chat_id] = "wait_for_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the number file (.txt).\n\nEach line must be:\n<code>+13438839116 http://www.smstx.top/api/sms/record?key=XXXX</code>\n\nYou will enter Service, Country name and Price after upload."), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]})

    elif data == "special_users":
        if not is_admin(chat_id):
            answer_callback(call["id"], "Only Bot Admins can manage Special Users.", show_alert=True)
            return
        edit_message(chat_id, msg_id, special_user_management_text(), reply_markup={"inline_keyboard": [
            [{"text": "Set Special User", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "special_users_set", "style": "success"}],
            [{"text": "Clear Special Users", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "special_users_clear", "style": "danger"}],
            [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
        ]})

    elif data == "special_users_set":
        if not is_admin(chat_id):
            answer_callback(call["id"], "Only Bot Admins can manage Special Users.", show_alert=True)
            return
        user_states[chat_id] = "wait_for_special_users"
        edit_message(chat_id, msg_id, render_body_text(
            "<b>SET SPECIAL USER</b>\n\nSend Telegram user ID(s). You can send multiple IDs separated by comma, space, or new line.\n\n"
            "These users will receive the Special User OTP earning rate."
        ), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "special_users", "style": "danger"}]]})

    elif data == "special_users_clear":
        if not is_admin(chat_id):
            answer_callback(call["id"], "Only Bot Admins can manage Special Users.", show_alert=True)
            return
        bot_settings["special_users"] = []
        save_db()
        edit_message(chat_id, msg_id, special_user_management_text(), reply_markup={"inline_keyboard": [
            [{"text": "Set Special User", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "special_users_set", "style": "success"}],
            [{"text": "Clear Special Users", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "special_users_clear", "style": "danger"}],
            [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
        ]})

    elif data == "delete_files":
        kb = []
        for b_id, b_data in number_batches.items():
            # Do not expose the uploaded filename here. Show detected country + service instead.
            country_name = str(b_data.get("country") or "UNKNOWN").upper()
            service_name = str(b_data.get("service") or "UNKNOWN").upper()
            label = f"{country_name} • {service_name} ({len(b_data.get('numbers', []))})"
            kb.append([{"text": label, "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"del_b_{b_id}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "primary"}])
        txt = "🗑 Select a file to delete:" if len(kb) > 1 else f"{PEM['no']} No files found."
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_b_"):
        b_id = data.split("del_b_")[1]
        if b_id in number_batches:
            del number_batches[b_id]
            save_db()
            answer_callback(call["id"], "✅ File deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "delete_files", "id": call["id"]})

    elif data == "show_rejected":
        if not is_admin(chat_id): return
        kb = {"inline_keyboard": [
            [{"text": "Download TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_rejected", "style": "primary"}],
            [{"text": "Clear Rejected", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "clear_rejected", "style": "danger"}],
            [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "primary"}]
        ]}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['no']} <b>Total Rejected Numbers:</b> {len(rejected_numbers_list)}"), reply_markup=kb)

    elif data == "show_used":
        if not is_admin(chat_id): return
        kb = {"inline_keyboard": [
            [{"text": "Download TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_used", "style": "primary"}],
            [{"text": "Clear Used", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "clear_used", "style": "danger"}],
            [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "primary"}]
        ]}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} <b>Total Used Numbers:</b> {len(used_numbers_list)}"), reply_markup=kb)

    elif data == "show_unused":
        if not is_admin(chat_id): return
        unused_count = sum(len(b.get("numbers", [])) for b in number_batches.values())
        kb = {"inline_keyboard": [
            [{"text": "Download TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_unused", "style": "primary"}],
            [{"text": "Clear Unused", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "clear_unused", "style": "danger"}],
            [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "primary"}]
        ]}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['rocket']} <b>Total Unused Numbers:</b> {unused_count}"), reply_markup=kb)

    elif data in ("dl_used", "dl_unused", "dl_rejected"):
        if not is_admin(chat_id): return
        if data == "dl_used":
            values, filename = list(used_numbers_list), "used_numbers.txt"
        elif data == "dl_rejected":
            values, filename = list(rejected_numbers_list), "rejected_numbers.txt"
        else:
            # Keep each complete stock record so the exported TXT contains
            # both the phone number and its OTP API URL.
            values = [n for b in number_batches.values() for n in b.get("numbers", [])]
            filename = "unused_numbers.txt"
        if not values:
            answer_callback(call["id"], "No numbers found.", show_alert=True)
            return
        def _number_export_line(item):
            if isinstance(item, dict):
                number = str(item.get("num", "")).strip()
                api_url = str(item.get("url", "")).strip()
                return f"{number} {api_url}" if api_url else number
            return str(item)
        send_document(chat_id, filename, "\n".join(_number_export_line(x) for x in values), caption=f"{filename}: {len(values)}")
        answer_callback(call["id"])

    elif data in ("clear_used", "clear_unused", "clear_rejected"):
        if not is_admin(chat_id): return
        kind = data.replace("clear_", "")
        confirm_kb = {"inline_keyboard": [
            [{"text": "Yes, clear", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"confirm_clear_{kind}", "style": "danger"}],
            [{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"show_{kind}", "style": "primary"}]
        ]}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['warn']} <b>Confirm clearing {kind} numbers?</b>\nThis action cannot be undone."), reply_markup=confirm_kb)

    elif data.startswith("confirm_clear_"):
        if not is_admin(chat_id): return
        kind = data.replace("confirm_clear_", "")
        if kind == "used":
            used_numbers_list.clear()
        elif kind == "rejected":
            rejected_numbers_list.clear()
        elif kind == "unused":
            for batch in number_batches.values():
                if isinstance(batch, dict):
                    batch["numbers"] = []
        save_db()
        answer_callback(call["id"], "Number list cleared.", show_alert=True)
        next_data = {"used": "show_used", "rejected": "show_rejected", "unused": "show_unused"}.get(kind, "back_to_admin")
        handle_callback({"message": {"chat": {"id": chat_id, "type": "private"}, "message_id": msg_id}, "data": next_data, "id": call["id"]})

    elif data == "lb_main":
        txt = f"━━━━━━━━━━━━━━━\n《 {PEM['admin']} <b>LEADER BOARD MENU</b> 》\n━━━━━━━━━━━━━━━\n<i>Select a category to view the top performers or history.</i>\n━━━━━━━━━━━━━━━"
        kb = [
            [{"text": "Top Referrers", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "lb_top_refs", "style": "primary"}],
            [{"text": "Top OTP Receivers", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "lb_top_otps", "style": "primary"}],
            [{"text": "Back to Admin", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
        ]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("lb_"):
        sub = data.replace("lb_", "")
        edit_message(chat_id, msg_id, render_body_text("⌛ <i>Fetching Data...</i>"))
        
        num_map = {"1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣", "5": "5️⃣", "6": "6️⃣", "7": "7️⃣", "8": "8️⃣", "9": "9️⃣", "0": "0️⃣"}
        def get_p_num(n): return "".join([num_map.get(c, c) for c in str(n)])
        
        try:
            if sub == "top_refs":
                title, field, limit, icon = "TOP 5 REFERRERS", "total_refers", 5, PEM.get('user', '👥')
                users = db.collection('users').order_by(field, direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for u in users:
                    d = u.to_dict()
                    if d.get(field, 0) > 0:
                        p = "└" if count == limit else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={u.id}'>{u.id}</a> ➔ <b>{d.get(field,0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "top_otps":
                title, field, limit, icon = "TOP 5 OTP RECEIVERS", "total_otps", 5, PEM.get('msg', '📩')
                users = db.collection('users').order_by(field, direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for u in users:
                    d = u.to_dict()
                    if d.get(field, 0) > 0:
                        p = "└" if count == limit else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={u.id}'>{u.id}</a> ➔ <b>{d.get(field,0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "w_history":
                title, limit, icon = "LAST 10 WITHDRAWALS", 10, PEM.get('money', '💸')
                ws = db.collection('withdrawals').order_by('timestamp', direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for w in ws:
                    d = w.to_dict()
                    s = str(d.get('status','Pending')).lower()
                    stat_icon = PEM.get('ok','✅') if s in ["approved","success"] else PEM.get('no','❌') if s=="rejected" else "⏳"
                    uid = d.get('user_id','User')
                    p = "└" if count == limit else "├"
                    res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={uid}'>{uid}</a> ➔ <b>{format_money(d.get('amount',0))}</b> {stat_icon}\n"
                    count += 1
                if not res_txt: res_txt = "└ <i>No history found.</i>\n"

            final_msg = f"━━━━━━━━━━━━━━━\n{icon} <b>{title}</b>\n━━━━━━━━━━━━━━━\n{res_txt}━━━━━━━━━━━━━━━"
            kb = [[{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": data, "style": "success"}, {"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]
            edit_message(chat_id, msg_id, render_body_text(final_msg), reply_markup={"inline_keyboard": kb})

        except Exception as e:
            edit_message(chat_id, msg_id, render_body_text(f"❌ Error: {e}"), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]})

    elif data == "lb_main":
        txt = f"━━━━━━━━━━━━━━━\n《 {PEM['admin']} <b>LEADER BOARD MENU</b> 》\n━━━━━━━━━━━━━━━\n<i>Select a category to view the top performers or history.</i>\n━━━━━━━━━━━━━━━"
        kb = [
            [{"text": "Top Referrers", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "lb_top_refs", "style": "primary"}],
            [{"text": "Top OTP Receivers", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "lb_top_otps", "style": "primary"}],
            [{"text": "Back to Admin", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
        ]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("lb_"):
        sub = data.replace("lb_", "")
        edit_message(chat_id, msg_id, render_body_text("⌛ <i>Fetching Data...</i>"))
        
        num_map = {"1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣", "5": "5️⃣", "6": "6️⃣", "7": "7️⃣", "8": "8️⃣", "9": "9️⃣", "0": "0️⃣"}
        def get_p_num(n): return "".join([num_map.get(c, c) for c in str(n)])
        
        try:
            if sub == "top_refs":
                title, field, limit, icon = "TOP 5 REFERRERS", "total_refers", 5, PEM.get('user', '👥')
                users = db.collection('users').order_by(field, direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for u in users:
                    d = u.to_dict()
                    if d.get(field, 0) > 0:
                        p = "└" if count == limit else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={u.id}'>{u.id}</a> ➔ <b>{d.get(field,0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "top_otps":
                title, field, limit, icon = "TOP 5 OTP RECEIVERS", "total_otps", 5, PEM.get('msg', '📩')
                users = db.collection('users').order_by(field, direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for u in users:
                    d = u.to_dict()
                    if d.get(field, 0) > 0:
                        p = "└" if count == limit else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={u.id}'>{u.id}</a> ➔ <b>{d.get(field,0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "w_history":
                title, limit, icon = "LAST 10 WITHDRAWALS", 10, PEM.get('money', '💸')
                ws = db.collection('withdrawals').order_by('timestamp', direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for w in ws:
                    d = w.to_dict()
                    s = str(d.get('status','Pending')).lower()
                    stat_icon = PEM.get('ok','✅') if s in ["approved","success"] else PEM.get('no','❌') if s=="rejected" else "⏳"
                    uid = d.get('user_id','User')
                    p = "└" if count == limit else "├"
                    res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={uid}'>{uid}</a> ➔ <b>{format_money(d.get('amount',0))}</b> {stat_icon}\n"
                    count += 1
                if not res_txt: res_txt = "└ <i>No history found.</i>\n"

            final_msg = f"━━━━━━━━━━━━━━━\n{icon} <b>{title}</b>\n━━━━━━━━━━━━━━━\n{res_txt}━━━━━━━━━━━━━━━"
            kb = [[{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": data, "style": "success"}, {"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]
            edit_message(chat_id, msg_id, render_body_text(final_msg), reply_markup={"inline_keyboard": kb})

        except Exception as e:
            edit_message(chat_id, msg_id, render_body_text(f"❌ Error: {e}"), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]})

    elif data == "back_to_admin":
        if chat_id in user_states: del user_states[chat_id]
        edit_message(chat_id, msg_id, get_admin_text(), reply_markup=admin_panel_keyboard())
        
    elif data == "price_manager":
        if not is_admin(chat_id):
            return
        _price_manager_show(chat_id, msg_id)

    elif data.startswith("pm_sel_"):
        if not is_admin(chat_id):
            return
        try:
            item = _price_manager_pairs()[int(data[len("pm_sel_"):])]
        except Exception:
            answer_callback(call["id"], "Service/country not found. Refresh Price Manager.", show_alert=True)
            return
        temp_data[chat_id] = {"price_service": item["service"], "price_country": item["country"]}
        user_states[chat_id] = "wait_for_service_country_price"
        edit_message(chat_id, msg_id, render_body_text(
            f"<b>Service:</b> {html.escape(item['service'])}\n<b>Country:</b> {html.escape(item['country'])}\n"
            f"<b>Current price:</b> {format_money(item['price'])}\n\nNow send the updated price:"), reply_markup=get_cancel_kb())

    elif data == "system_settings":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['gear']} <b>System Settings</b>\nManage advanced bot configurations below:"), reply_markup=system_settings_keyboard())

    elif data == "stex_control":
        edit_message(chat_id, msg_id, render_body_text(f"🌐 <b>StexSMS Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('stex_keys', []))}\nManage your StexSMS API Keys below:"), reply_markup=stex_control_keyboard())

    elif data == "toggle_stex_auto":
        bot_settings["stex_auto"] = not bot_settings.get("stex_auto", False)
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"🌐 <b>StexSMS Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('stex_keys', []))}\nManage your StexSMS API Keys below:"), reply_markup=stex_control_keyboard())
        answer_callback(call["id"], f"✅ Stex Auto Range is now {'ON' if bot_settings['stex_auto'] else 'OFF'}!", show_alert=False)

    elif data == "add_stex_key":
        user_states[chat_id] = "wait_for_add_stex_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new StexSMS API Key (e.g. nxa_...):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "danger"}]]})

    elif data == "view_stex_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("stex_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_nxa_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select StexSMS Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_nxa_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("stex_keys", [])):
            del bot_settings["stex_keys"][idx]
            save_db()
            answer_callback(call["id"], "✅ StexSMS Key Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_stex_keys", "id": call["id"]})

    elif data == "stex_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_sc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Allowed Search Countries:</b>\nOnly these country codes will be allowed in Search Number."), reply_markup={"inline_keyboard": kb})

    elif data == "add_search_country":
        user_states[chat_id] = "wait_for_add_sc"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Country Code (e.g. 880 or 92):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_search_country", "style": "danger"}]]})

    elif data.startswith("del_sc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("search_countries", [])):
            del bot_settings["search_countries"][idx]
            save_db()
            answer_callback(call["id"], "✅ Country Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "stex_search_country", "id": call["id"]})

    elif data == "manage_stex_srv":
        kb = []
        srvs = bot_settings.get("stex_services", {})
        apps_db = bot_settings.get("premium_apps", {})
        for srv in srvs:
            emoji_id = "5257969839313526622"
            for app_key, app_data in apps_db.items():
                if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                    if "id" in app_data:
                        emoji_id = app_data["id"]
                        break
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": emoji_id, "callback_data": f"nx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "nx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("📦 <b>StexSMS Services Manager</b>\nManage your API-based dynamic services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "nx_add_srv":
        user_states[chat_id] = "wait_nx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("nx_srv_"):
        srv = data.replace("nx_srv_", "")
        kb = []
        countries = bot_settings["stex_services"].get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data:
                        emoji_id = flag_data["id"]
                        break
            kb.append([{"text": f"{c} ({len(countries[c])} Ranges)", "icon_custom_emoji_id": emoji_id, "callback_data": f"nx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"nx_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"nx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_stex_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("nx_add_cnt_"):
        srv = data.replace("nx_add_cnt_", "")
        user_states[chat_id] = "wait_nx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. BD, INDIA):"), reply_markup=get_cancel_kb())

    elif data.startswith("nx_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings["stex_services"][srv].get(cnt, [])
        
        kb = []
        row = []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"nx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2:
                kb.append(row)
                row = []
        if row: kb.append(row)
        
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"nx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"nx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"nx_srv_{srv}", "style": "primary"}])
        
        txt = f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}\n<i>Click on a range below to delete it, or add a new one.</i>"
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("nx_addr_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_nx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 88017):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"nx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("nx_dr_"):
        parts = data.split("_")
        srv, cnt, rng = parts[2], parts[3], parts[4]
        if rng in bot_settings["stex_services"].get(srv, {}).get(cnt, []):
            bot_settings["stex_services"][srv][cnt].remove(rng)
            save_db()
            answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"nx_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("nx_del_srv_"):
        srv = data.replace("nx_del_srv_", "")
        if srv in bot_settings["stex_services"]: del bot_settings["stex_services"][srv]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_stex_srv", "id": call["id"]})

    elif data.startswith("nx_del_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[3], parts[4]
        if cnt in bot_settings["stex_services"].get(srv, {}): del bot_settings["stex_services"][srv][cnt]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"nx_srv_{srv}", "id": call["id"]})

    elif data == "voltx_control":
        edit_message(chat_id, msg_id, render_body_text(f"⚡ <b>Voltx Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('voltx_keys', []))}\nManage your Voltx API Keys below:"), reply_markup=voltx_control_keyboard())

    elif data == "toggle_voltx_auto":
        bot_settings["voltx_auto"] = not bot_settings.get("voltx_auto", False)
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"⚡ <b>Voltx Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('voltx_keys', []))}\nManage your Voltx API Keys below:"), reply_markup=voltx_control_keyboard())
        answer_callback(call["id"], f"✅ Voltx Auto Range is now {'ON' if bot_settings['voltx_auto'] else 'OFF'}!", show_alert=False)

    elif data == "add_voltx_key":
        user_states[chat_id] = "wait_for_add_voltx_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new Voltx API Key:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "danger"}]]})

    elif data == "view_voltx_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("voltx_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_vtx_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select Voltx Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_vtx_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("voltx_keys", [])):
            del bot_settings["voltx_keys"][idx]
            save_db()
            answer_callback(call["id"], "✅ Voltx Key Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_voltx_keys", "id": call["id"]})

    elif data == "voltx_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("voltx_search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_vsc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_voltx_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Voltx Allowed Ranges:</b>\nOnly these ranges/codes will be allowed in Voltx Search Number."), reply_markup={"inline_keyboard": kb})

    elif data == "add_voltx_search_country":
        user_states[chat_id] = "wait_for_add_vsc"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Voltx Range Code (e.g. 26134):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_search_country", "style": "danger"}]]})

    elif data.startswith("del_vsc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("voltx_search_countries", [])):
            del bot_settings["voltx_search_countries"][idx]
            save_db()
            answer_callback(call["id"], "✅ Voltx Range Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "voltx_search_country", "id": call["id"]})

    elif data == "manage_voltx_srv":
        kb = []
        srvs = bot_settings.get("voltx_services", {})
        apps_db = bot_settings.get("premium_apps", {})
        for srv in srvs:
            emoji_id = "5257969839313526622"
            for app_key, app_data in apps_db.items():
                if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                    if "id" in app_data: emoji_id = app_data["id"]; break
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": emoji_id, "callback_data": f"vx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "vx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("⚡ <b>Voltx Services Manager</b>\nManage your API-based dynamic services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "vx_add_srv":
        user_states[chat_id] = "wait_vx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("vx_srv_"):
        srv = data.replace("vx_srv_", "")
        kb = []
        countries = bot_settings["voltx_services"].get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data: emoji_id = flag_data["id"]; break
            kb.append([{"text": f"{c} ({len(countries[c])} Ranges)", "icon_custom_emoji_id": emoji_id, "callback_data": f"vx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"vx_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"vx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_voltx_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("vx_add_cnt_"):
        srv = data.replace("vx_add_cnt_", "")
        user_states[chat_id] = "wait_vx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. BD, INDIA):"), reply_markup=get_cancel_kb())

    elif data.startswith("vx_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings["voltx_services"][srv].get(cnt, [])
        kb = []
        row = []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"vx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2:
                kb.append(row)
                row = []
        if row: kb.append(row)
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"vx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"vx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"vx_srv_{srv}", "style": "primary"}])
        txt = f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}\n<i>Click on a range below to delete it, or add a new one.</i>"
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("vx_addr_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_vx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 26134):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"vx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("vx_dr_"):
        parts = data.split("_")
        srv, cnt, rng = parts[2], parts[3], parts[4]
        if rng in bot_settings["voltx_services"].get(srv, {}).get(cnt, []):
            bot_settings["voltx_services"][srv][cnt].remove(rng)
            save_db()
            answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"vx_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("vx_del_srv_"):
        srv = data.replace("vx_del_srv_", "")
        if srv in bot_settings["voltx_services"]: del bot_settings["voltx_services"][srv]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_voltx_srv", "id": call["id"]})

    elif data.startswith("vx_del_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[3], parts[4]
        if cnt in bot_settings["voltx_services"].get(srv, {}): del bot_settings["voltx_services"][srv][cnt]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"vx_srv_{srv}", "id": call["id"]})

    # --- ZENEX CONTROL CALLBACKS ---
    elif data == "zenex_control":
        edit_message(chat_id, msg_id, render_body_text(f"💠 <b>Zenex Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('zenex_keys', []))}\nManage your Zenex API Keys below:"), reply_markup=zenex_control_keyboard())

    elif data == "toggle_zenex_auto":
        bot_settings["zenex_auto"] = not bot_settings.get("zenex_auto", False)
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"💠 <b>Zenex Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('zenex_keys', []))}\nManage your Zenex API Keys below:"), reply_markup=zenex_control_keyboard())
        answer_callback(call["id"], f"✅ Zenex Auto Range is now {'ON' if bot_settings['zenex_auto'] else 'OFF'}!", show_alert=False)

    elif data == "add_zenex_key":
        user_states[chat_id] = "wait_for_add_zenex_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new Zenex API Key:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_control", "style": "danger"}]]})

    elif data == "view_zenex_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("zenex_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_znx_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select Zenex Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_znx_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("zenex_keys", [])):
            del bot_settings["zenex_keys"][idx]
            save_db()
            answer_callback(call["id"], "✅ Zenex Key Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_zenex_keys", "id": call["id"]})

    elif data == "zenex_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("zenex_search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_zsc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_zenex_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Zenex Allowed Ranges:</b>\nOnly these codes will be allowed in Zenex Search Number."), reply_markup={"inline_keyboard": kb})

    elif data == "add_zenex_search_country":
        user_states[chat_id] = "wait_for_add_zsc"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Zenex Range Code (e.g. 447):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_search_country", "style": "danger"}]]})

    elif data.startswith("del_zsc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("zenex_search_countries", [])):
            del bot_settings["zenex_search_countries"][idx]
            save_db()
            answer_callback(call["id"], "✅ Zenex Range Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "zenex_search_country", "id": call["id"]})

    elif data == "manage_zenex_srv":
        kb = []
        for srv in bot_settings.get("zenex_services", {}):
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": "5257969839313526622", "callback_data": f"zx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "zx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("💠 <b>Zenex Services Manager</b>\nManage your API-based manual services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "zx_add_srv":
        user_states[chat_id] = "wait_zx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("zx_srv_"):
        srv = data.replace("zx_srv_", "")
        kb = []
        for c in bot_settings.get("zenex_services", {}).get(srv, {}):
            kb.append([{"text": f"{c} ({len(bot_settings['zenex_services'][srv][c])} Ranges)", "icon_custom_emoji_id": "5780471598922337683", "callback_data": f"zx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"zx_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"zx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_zenex_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("zx_add_cnt_"):
        srv = data.replace("zx_add_cnt_", "")
        user_states[chat_id] = "wait_zx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. UK, USA):"), reply_markup=get_cancel_kb())

    elif data.startswith("zx_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings["zenex_services"][srv].get(cnt, [])
        kb, row = [], []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"zx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2: kb.append(row); row = []
        if row: kb.append(row)
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"zx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"zx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"zx_srv_{srv}", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("zx_addr_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_zx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 4473845XXX):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"zx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("zx_dr_"):
        parts = data.split("_")
        srv, cnt, rng = parts[2], parts[3], parts[4]
        if rng in bot_settings["zenex_services"].get(srv, {}).get(cnt, []):
            bot_settings["zenex_services"][srv][cnt].remove(rng)
            save_db()
            answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"zx_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("zx_del_srv_"):
        srv = data.replace("zx_del_srv_", "")
        if srv in bot_settings["zenex_services"]: del bot_settings["zenex_services"][srv]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_zenex_srv", "id": call["id"]})

    elif data.startswith("zx_del_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[3], parts[4]
        if cnt in bot_settings["zenex_services"].get(srv, {}): del bot_settings["zenex_services"][srv][cnt]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"zx_srv_{srv}", "id": call["id"]})

    elif data == "manage_fj":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "toggle_fj":
        bot_settings["fj_on"] = not bot_settings["fj_on"]
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "add_fj":
        user_states[chat_id] = "wait_for_add_fj"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send Channel Username or Invite Link:\n<i>(Note: For private channels, use the numeric ID like -100...)</i>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_fj", "style": "danger"}]]})

    elif data.startswith("del_fj_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fj_channels"]):
            del bot_settings["fj_channels"][idx]
            save_db()
            answer_callback(call["id"], "✅ Channel deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "manage_admins":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['user']} <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())

    elif data == "add_adm":
        user_states[chat_id] = "wait_for_add_adm"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID of the new Admin:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_admins", "style": "danger"}]]})

    elif data.startswith("del_adm_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["admins"]):
            del bot_settings["admins"][idx]
            save_db()
            answer_callback(call["id"], "✅ Admin deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"{PEM['user']} <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())

    elif data == "manage_otp_groups":
        edit_message(chat_id, msg_id, render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())

    elif data == "add_fw":
        user_states[chat_id] = "wait_for_add_fw_id"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Group ID/Username to forward messages to:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})

    elif data.startswith("manage_fw_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            grp_id = bot_settings["fw_groups"][idx]["chat_id"]
            edit_message(chat_id, msg_id, render_body_text(f"🛡 <b>Manage Group:</b> {grp_id}"), reply_markup=specific_fw_group_keyboard(idx))

    elif data.startswith("add_fwbtn_"):
        idx = int(data.split("_")[2])
        user_states[chat_id] = "wait_for_add_fw_btn"
        temp_data[chat_id] = {"msg_id": msg_id, "fw_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send Custom Inline Button format:\n<code>Button Text - https://link.com</code>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_fw_{idx}", "style": "danger"}]]})

    elif data.startswith("del_fwbtn_"):
        parts = data.split("_")
        idx, b_idx = int(parts[2]), int(parts[3])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            if 0 <= b_idx < len(bot_settings["fw_groups"][idx]["buttons"]):
                del bot_settings["fw_groups"][idx]["buttons"][b_idx]
                save_db()
                answer_callback(call["id"], "✅ Button deleted!", show_alert=True)
                edit_message(chat_id, msg_id, render_body_text(f"🛡 <b>Manage Group:</b> {bot_settings['fw_groups'][idx]['chat_id']}"), reply_markup=specific_fw_group_keyboard(idx))

    elif data.startswith("del_fw_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            del bot_settings["fw_groups"][idx]
            save_db()
            answer_callback(call["id"], "✅ Group deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())

    elif data == "edit_otp_link":
        user_states[chat_id] = "wait_for_otp_link"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new OTP Group Link:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})

    elif data == "manage_panels":
        api_count = len([p for p in bot_settings["panels"] if p.get("type") == "API Panel"])
        cpt_count = len([p for p in bot_settings["panels"] if p.get("type", "API Panel") == "Auto Captcha Panel"])
        text = f"{PEM['gear']} <b>Panel Management</b>\n\nSelect which type of panel system you want to manage:"
        kb = {"inline_keyboard": [
            [{"text": "Bangla Panel", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "bangla_panel", "style": "success"}],
            [{"text": f"Manage API Panels ({api_count})", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "manage_api_panels", "style": "primary"}],
            [{"text": f"Manage Auto Captcha Panels ({cpt_count})", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "manage_cpt_panels", "style": "success"}],
            [{"text": "Back to System", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
        ]}
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=kb)

    elif data == "bangla_panel":
        kb = {"inline_keyboard": [
            [{"text": "StexSMS Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "stex_control", "style": "success"}],
            [{"text": "Voltx Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "voltx_control", "style": "primary"}],
            [{"text": "Zenex Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "zenex_control", "style": "success"}],
            [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_panels", "style": "danger"}]
        ]}
        edit_message(chat_id, msg_id, render_body_text("<b>Bangla Panel</b>\n\nManage Bangla Panel providers below:"), reply_markup=kb)

    elif data in ["manage_api_panels", "manage_cpt_panels"]:
        p_type = "API Panel" if data == "manage_api_panels" else "Auto Captcha Panel"
        p_list = [p for p in bot_settings["panels"] if p.get("type", "API Panel") == p_type]
        icon = f"{PEM['world']} API" if p_type == 'API Panel' else f"{PEM['lock']} Auto Captcha"
        
        text = f"{icon} <b>{p_type}s Management</b>\n\n👀 <b>Active Monitors:</b> {len(p_list)}\n\n🟢 <b>Available Providers:</b>\n"
        for p in p_list:
            status = "Monitoring" if p['status'] == 'ON' else "Stopped"
            login_state = p.get('login_status', '')
            if p['type'] == 'Auto Captcha Panel':
                conf = f" {login_state}" if login_state else f"{PEM['ok']} Configured"
            else:
                conf = f"{PEM['ok']} Configured" if p.get('api_url') else f"{PEM['no']} Not Configured"
            text += f"• {p['name']}: {PEM['ok'] if p['status']=='ON' else PEM['no']} {status} | {conf}\n"
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=typed_panels_list_keyboard(p_type))

    elif data in ["add_api_panel", "add_cpt_panel"]:
        user_states[chat_id] = "wait_for_panel_name"
        p_type = "api" if data == "add_api_panel" else "logc"
        temp_data[chat_id] = {"msg_id": msg_id, "add_type": p_type}
        edit_message(chat_id, msg_id, render_body_text("📝 Please send the name of the New Provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_{'api' if p_type=='api' else 'cpt'}_panels", "style": "danger"}]]})

    elif data.startswith("add_ptype_"):
        pass

    elif data in ["list_del_api", "list_del_cpt"]:
        p_type = "API Panel" if data == "list_del_api" else "Auto Captcha Panel"
        kb = []
        for idx, p in enumerate(bot_settings["panels"]):
            if p.get("type", "API Panel") == p_type:
                kb.append([{"text": f"Delete {p['name']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"do_del_pnl_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_{'api' if p_type=='API Panel' else 'cpt'}_panels", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['trash']} <b>Select a Provider to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("do_del_pnl_"):
        idx = int(data.split("_")[3])
        if 0 <= idx < len(bot_settings["panels"]):
            p_type = bot_settings["panels"][idx].get("type", "API Panel")
            del bot_settings["panels"][idx]
            save_db()
            answer_callback(call["id"], "✅ Provider Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"manage_{'api' if p_type=='API Panel' else 'cpt'}_panels", "id": "internal"})

    elif data.startswith("tog_pnl_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["panels"]):
            p = bot_settings["panels"][idx]
            
            p["status"] = "ON" if p["status"] == "OFF" else "OFF"
            save_db()
            
            if p["type"] == "Auto Captcha Panel":
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>Login Status:</b> {p.get('login_status', 'Unknown')}\n<b>Login URL:</b> <code>{p.get('login_url', 'None')}</code>\n<b>User:</b> <code>{p.get('username', 'None')}</code>"
            else:
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
            edit_message(chat_id, msg_id, render_body_text(text), reply_markup=panel_config_keyboard(idx))

    elif data.startswith("conf_pnl_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["panels"]):
            p = bot_settings["panels"][idx]
            if p["type"] == "Auto Captcha Panel":
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>Login Status:</b> {p.get('login_status', 'Unknown')}\n<b>Login URL:</b> <code>{p.get('login_url', 'None')}</code>\n<b>User:</b> <code>{p.get('username', 'None')}</code>\n<b>Num Col:</b> {p.get('num_col_name')} (Idx: {p.get('num_col_idx')})\n<b>Msg Col:</b> {p.get('msg_col_name')} (Idx: {p.get('msg_col_idx')})"
            else:
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>\n<b>Full API URL:</b> <code>{p.get('full_api_url', 'None')}</code>"
            edit_message(chat_id, msg_id, render_body_text(text), reply_markup=panel_config_keyboard(idx))

    elif data.startswith("set_p_api_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_api"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the API URL for this provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_tok_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_tok"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Token for this provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_fapi_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_fapi"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the FULL API URL (Example: http://api.com/get?key=YOUR_TOKEN&start=0):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_rec_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_rec"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the number of records to fetch (e.g. 10).\nType <code>0</code> for Unlimited:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("test_p_conn_"):
        idx = int(data.split("_")[3])
        p = bot_settings["panels"][idx]
        wait_msg = send_message(chat_id, render_body_text("⏳ Testing connection. Please wait..."))
        wait_msg_id = wait_msg.get("result", {}).get("message_id") if wait_msg else None
        answer_callback(call["id"])
        
        try:
            parsed = []
            raw_text = ""
            
            if p["type"] == "Auto Captcha Panel":
                sess = panel_sessions.get(idx)
                if not sess:
                    success = attempt_auto_login(p, idx)
                    if not success:
                        if wait_msg_id: delete_message(chat_id, wait_msg_id)
                        send_message(chat_id, render_body_text(f"❌ <b>Auto Login Failed!</b>\nReason: {html.escape(str(p.get('login_status', 'Unknown')))}"))
                        return
                    sess = panel_sessions.get(idx)
                    
                login_url = p.get("login_url", "").strip()
                if not login_url.startswith("http"): login_url = "http://" + login_url
                msg_link = p.get("msg_link", "").strip()
                if not msg_link.startswith("http") and msg_link != "": msg_link = "http://" + msg_link
                check_url = msg_link if msg_link else f"{login_url.split('/login')[0]}/client/SMSCDRStats"
                
                # 🌟 test connection supports sAjaxSource & HTML table parser
                parsed, raw_text = fetch_cpt_panel_cdrs(p, sess, check_url)
                
            else:
                full_url = p.get("full_api_url", "").strip()
                url = p.get("api_url", "").strip()
                token = p.get("token", "").strip()
                if not full_url and not url:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ Please Set API URL or Full API URL first!"))
                    return
                
                urls_to_try = []
                if full_url:
                    urls_to_try.append(full_url)
                else:
                    if "{token}" in url or "{key}" in url:
                        urls_to_try.append(url.replace("{token}", token).replace("{key}", token))
                    elif "token=" in url or "key=" in url:
                        urls_to_try.append(url)
                    else:
                        sep = '&' if '?' in url else '?'
                        urls_to_try.append(f"{url}{sep}token={token}")
                        urls_to_try.append(f"{url}{sep}key={token}&start=0")
                        urls_to_try.append(f"{url}{sep}key={token}")
                    
                parsed = []
                raw_text = ""
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                for try_url in urls_to_try:
                    try:
                        res = requests.get(try_url, headers=headers, timeout=10)
                        raw_text = res.text
                        parsed = parse_panel_response(raw_text, p)
                        if parsed:
                            if not full_url and try_url != url and token:
                                p["api_url"] = try_url.replace(token, "{token}")
                                save_db()
                            break
                    except: pass
                 
            if wait_msg_id: delete_message(chat_id, wait_msg_id)
                 
            if parsed:
                txt = f"✅ <b>Connection Successful!</b>\n\n🎯 <b>Parsed Data Sample (Max 3):</b>\n\n"
                
                for i, sample in enumerate(parsed[:3]):
                    num = sample['number']
                    msg = sample['message']
                    otp = sample['otp']
                    
                    detected_app = detect_service(msg)
                    app_name = detected_app if detected_app else p.get("name", "Unknown")
                    app_full_name, prem_app_html = get_service_info_html(app_name, msg)
                    
                    txt += f"<b>{i+1}.</b> {prem_app_html} <b>{app_full_name}</b>\n"
                    txt += f"📱 Number: <code>{num}</code>\n"
                    txt += f"📝 Full Msg: <code>{html.escape(msg)}</code>\n"
                    txt += f"🔐 OTP: <code>{otp}</code>\n"
                    txt += "➖" * 12 + "\n"
                    
                send_message(chat_id, render_body_text(txt))
            else:
                if p["type"] == "Auto Captcha Panel":
                    try:
                        soup = BeautifulSoup(raw_text, 'html.parser')
                        tables = soup.find_all('table')
                        if tables:
                            full_table_data = "🔍 FULL TABLE DATA (A-Z)\n" + "="*50 + "\n\n"
                            for t_idx, table in enumerate(tables):
                                full_table_data += f"--- Table {t_idx+1} ---\n"
                                rows = table.find_all('tr')
                                for r_idx, row in enumerate(rows):
                                    cols = row.find_all(['th', 'td'])
                                    col_texts = [f"[{c_idx+1}] {c.get_text(separator=' ', strip=True)}" for c_idx, c in enumerate(cols)]
                                    full_table_data += f"Row {r_idx+1}: {' | '.join(col_texts)}\n"
                                full_table_data += "\n" + "="*50 + "\n"
                            
                            send_document(chat_id, f"Full_Panel_Data_{idx}.txt", full_table_data.encode('utf-8'))
                            fail_txt = f"⚠️ <b>Connected, but couldn't parse OTP data!</b>\n\n<i>আমি ওই লিংকের সম্পূর্ণ (A-Z) ডাটা একটি Text File এ পাঠিয়েছি। ফাইলটি ওপেন করে সঠিক Column Number (যেমন: [1], [3]) চেক করে প্যানেলে আপডেট করে নাও।</i>"
                            send_message(chat_id, render_body_text(fail_txt))
                        else:
                            send_message(chat_id, render_body_text(f"⚠️ <b>Connected, but no HTML Table found!</b>\nMake sure the message link is correct."))
                    except Exception as e:
                        send_message(chat_id, render_body_text(f"❌ <b>Error parsing HTML:</b> {html.escape(str(e))}"))
                else:
                    safe_html = html.escape(str(raw_text)[:300])
                    send_message(chat_id, render_body_text(f"⚠️ <b>Connected, but couldn't find/parse OTP data.</b>\n\n<i>Make sure your API config is correct.</i>\n\nRaw HTML/Data (excerpt):\n<code>{safe_html}...</code>"))
        except Exception as e:
            if wait_msg_id: delete_message(chat_id, wait_msg_id)
            send_message(chat_id, render_body_text(f"❌ <b>Connection Failed!</b>\nError: {html.escape(str(e))}"))

    elif data == "support_management":
        if not is_admin(chat_id): return
        edit_message(chat_id, msg_id, support_management_text(), reply_markup=support_management_keyboard())
        answer_callback(call["id"])

    elif data == "support_edit_link":
        if not is_admin(chat_id): return
        user_states[chat_id] = "support_admin_link"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['msg']} <b>EDIT SUPPORT LINK</b>\n\nSend the new Telegram support link.\nExample: <code>https://t.me/your_support</code>"), reply_markup={"inline_keyboard":[[{"text":"CANCEL","icon_custom_emoji_id":"5267490665117275176","callback_data":"support_management","style":"danger"}]]})
        answer_callback(call["id"])

    elif data == "support_edit_name":
        if not is_admin(chat_id): return
        user_states[chat_id] = "support_admin_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['msg']} <b>EDIT SUPPORT BUTTON NAME</b>\n\nSend the new name for the Support button."), reply_markup={"inline_keyboard":[[{"text":"CANCEL","icon_custom_emoji_id":"5267490665117275176","callback_data":"support_management","style":"danger"}]]})
        answer_callback(call["id"])

    elif data == "support_start":
        user_states[chat_id] = "support_wait_message"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['msg']} <b>SUPPORT MESSAGE</b>\n\nSend your problem/message now. It will be delivered to the admin.\n\n<i>After sending, wait for the admin reply.</i>"), reply_markup={"inline_keyboard":[[{"text":"CANCEL","icon_custom_emoji_id":"5267490665117275176","callback_data":"close_msg","style":"danger"}]]})
        answer_callback(call["id"])

    elif data.startswith("support_reply_"):
        if not is_admin(chat_id): return
        target = data.replace("support_reply_", "", 1)
        user_states[chat_id] = "support_admin_reply"
        temp_data[chat_id] = {"msg_id": msg_id, "target_user": target}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['msg']} <b>REPLY TO USER</b>\n\nSend your reply message now."), reply_markup={"inline_keyboard":[[{"text":"CANCEL","icon_custom_emoji_id":"5267490665117275176","callback_data":"close_msg","style":"danger"}]]})
        answer_callback(call["id"])

    elif data.startswith("support_close_"):
        if not is_admin(chat_id): return
        target = data.replace("support_close_", "", 1)
        send_message(target, render_body_text(f"{PEM['msg']} <b>Support ticket closed.</b>\n\nIf you need more help, open Support again."), reply_markup=main_menu(target))
        delete_message(chat_id, msg_id)
        answer_callback(call["id"], "Support ticket closed.")

    elif data == "dxa_sup_link":
        if not is_admin(chat_id): return
        edit_message(chat_id, msg_id, support_management_text(), reply_markup=support_management_keyboard())
        answer_callback(call["id"])

    elif data == "console_otp_toggle":
        if not is_admin(chat_id):
            answer_callback(call["id"], "Only Bot Admins can change Console OTP.", show_alert=True)
            return
        bot_settings["console_otp"] = not bool(bot_settings.get("console_otp", False))
        save_db()
        style = "success" if bot_settings["console_otp"] else "danger"
        kb = admin_panel_keyboard()
        # admin_panel_keyboard reads the saved state and sets the correct color.
        edit_message(chat_id, msg_id, render_body_text(
            f"{PEM['ok'] if bot_settings['console_otp'] else PEM['no']} "
            f"<b>Console OTP {'Enabled' if bot_settings['console_otp'] else 'Disabled'}</b>"
        ), reply_markup=kb)
        answer_callback(call["id"])
        return

    elif data == "console_traffic_cycle":
        if not is_admin(chat_id):
            answer_callback(call["id"], "Only Bot Admins can change Consol Traffic.", show_alert=True)
            return
        mode = str(bot_settings.get("console_traffic_mode", "on")).lower()
        if mode not in ("off", "on", "all"):
            mode = "on" if bot_settings.get("console_traffic", True) else "off"
        # Cycle: ON (green) -> OFF (blue) -> ALL ON (red) -> ON
        next_mode = {"on": "off", "off": "all", "all": "on"}[mode]
        bot_settings["console_traffic_mode"] = next_mode
        # Keep legacy boolean in sync for compatibility.
        bot_settings["console_traffic"] = next_mode != "off"
        save_db()
        style = {"on": "success", "off": "primary", "all": "danger"}[next_mode]
        traffic_kb = {"inline_keyboard": [
            [{"text": "Consol Traffic", "icon_custom_emoji_id": "5203993413346680064", "callback_data": "console_traffic_cycle", "style": style}],
            [{"text": "Set Traffic Time", "icon_custom_emoji_id": "5420155432272438703", "callback_data": "traffic_time_custom", "style": "primary"}],
            [{"text": "Back to Menus", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "menu_design_list", "style": "danger"}]
        ]}
        answer_callback(call["id"])
        edit_message(chat_id, msg_id, render_body_text(f"📊 <b>Edit TRAFFIC</b>\n\nCurrent traffic window: <b>{max(1, int(bot_settings.get('traffic_window_minutes', 30)))} minutes</b>\n\nConsol Traffic mode updated."), reply_markup=traffic_kb)

    elif data == "dxa_control":
        if not is_admin(chat_id):
            answer_callback(call["id"], "Only Bot Admins can access DXA Control.", show_alert=True)
            return
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())
        answer_callback(call["id"])

    elif data == "dxa_toggle_w":
        bot_settings["withdraw_on"] = not bot_settings["withdraw_on"]
        save_db()
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())

    elif data == "manage_w_methods":
        edit_message(chat_id, msg_id, render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())

    elif data == "add_wm":
        user_states[chat_id] = "wait_for_add_wm"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the name of the new Withdrawal Method:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_w_methods", "style": "danger"}]]})

    elif data.startswith("del_wm_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["w_methods"]):
            del bot_settings["w_methods"][idx]
            save_db()
            answer_callback(call["id"], "✅ Method deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())

    elif data == "withdraw_requests":
        if not is_admin(chat_id):
            answer_callback(call["id"], "Only Bot Admins can view withdrawal requests.", show_alert=True)
            return
        count = len(pending_withdrawals)
        if count == 0:
            edit_message(chat_id, msg_id, render_body_text(f"{PEM['money']} <b>WITHDRAWAL REQUESTS</b>\n\n{PEM['ok']} No pending withdrawal requests."),
                         reply_markup={"inline_keyboard":[
                             [{"text":"REFRESH","icon_custom_emoji_id":"5352694861990501856","callback_data":"withdraw_requests","style":"primary"}],
                             [{"text":"BACK","icon_custom_emoji_id":"5267490665117275176","callback_data":"dxa_control","style":"danger"}]
                         ]})
            return
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['money']} <b>WITHDRAWAL REQUESTS</b>\n\n{PEM['lock']} <b>PENDING:</b> {count}"),
                     reply_markup={"inline_keyboard":[
                         [{"text":"REFRESH","icon_custom_emoji_id":"5352694861990501856","callback_data":"withdraw_requests","style":"primary"}],
                         [{"text":"BACK","icon_custom_emoji_id":"5267490665117275176","callback_data":"dxa_control","style":"danger"}]
                     ]})
        for req_id, req_data in list(pending_withdrawals.items()):
            result = send_message(chat_id, withdrawal_request_text(req_id, req_data), reply_markup=withdrawal_request_keyboard(req_id))
            if not result or result.get("ok") is not True:
                print(f"Withdrawal request message failed for {req_id}: {result}")

    elif data.startswith("dxa_"):
        key = data.replace("dxa_", "")
        key_map = {"min_w": "min_withdraw", "otp_r": "otp_reward", "ref_r": "refer_reward", "cool": "cooldown", "num_req": "num_req", "num_share": "num_share", "sup_link": "support_link"}
        if key in key_map:
            temp_data[chat_id] = {"msg_id": msg_id, "key": key_map[key]}
            user_states[chat_id] = "set_dxa"
            cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_dxa_edit", "style": "danger"}]]}
            edit_message(chat_id, msg_id, render_body_text(f"📝 Please send the new value for <code>{key_map[key]}</code>:"), reply_markup=cancel_kb)
            answer_callback(call["id"])

    elif data == "buy_once":
        ctx = bulk_contexts.get(chat_id) or {}
        service, country = ctx.get("service"), ctx.get("country")
        if not service or not country:
            answer_callback(call["id"], "Selection expired. Please choose the country again.", show_alert=True)
            return
        st, payload = try_buy_local(chat_id, service=service, country=country, kind="service",
                                    change_cb=f"paid_new:{service}:{country}", country_cb=f"g_s_{service}")
        if st == "ok":
            answer_callback(call["id"])
            show_paid_number(chat_id, msg_id, payload)
        elif st == "no_balance":
            answer_callback(call["id"], f"Insufficient balance! Price: {format_money(payload['price'])} | Balance: {format_money(payload['balance'])}.", show_alert=True)
            notify_no_balance(chat_id, payload)
        else:
            answer_callback(call["id"], "No numbers available for this service and country.", show_alert=True)

    elif data == "bulk_start":
        ctx = bulk_contexts.get(chat_id) or {}
        if not ctx.get("service") or not ctx.get("country"):
            answer_callback(call["id"], "Selection expired. Please choose the country again.", show_alert=True)
            return
        user_states[chat_id] = "wait_for_bulk_qty"
        answer_callback(call["id"])
        send_message(chat_id, render_body_text("Enter how many numbers you want to buy (1–1000):"), reply_markup=get_cancel_kb())

    elif data == "bulk_cancel":
        user_states.pop(chat_id, None)
        temp_data.pop(chat_id, None)
        bulk_contexts.pop(chat_id, None)
        answer_callback(call["id"], "Bulk purchase cancelled.")
        edit_message(chat_id, msg_id, render_body_text("Bulk purchase cancelled."))

    elif data == "bulk_confirm":
        info = temp_data.get(chat_id, {})
        service, country = info.get("bulk_service"), info.get("bulk_country")
        qty = int(info.get("bulk_qty", 0) or 0)
        if not service or not country or qty < 1:
            answer_callback(call["id"], "Bulk purchase session expired. Start again.", show_alert=True)
            return
        with purchase_lock:
            candidates = []
            for b_id, batch in number_batches.items():
                if batch.get("service") != service or batch.get("country") != country:
                    continue
                price = get_effective_batch_price(batch)
                for item in batch.get("numbers", []):
                    if item.get("url") and not item.get("used_by") and not item.get("shares"):
                        candidates.append((price, random.random(), b_id, item))
            # A number must only be sold once, even if an admin uploaded it in multiple files.
            deduped = []
            seen_numbers = set()
            for candidate in candidates:
                number_key = str(candidate[3].get("num", "")).strip()
                if number_key and number_key not in seen_numbers:
                    seen_numbers.add(number_key)
                    deduped.append(candidate)
            candidates = deduped
            if len(candidates) < qty:
                user_states[chat_id] = "wait_for_bulk_qty"
                answer_callback(call["id"], f"Stock changed. Only {len(candidates)} available. Enter a new quantity.", show_alert=True)
                send_message(chat_id, render_body_text(f"Available unused stock: <b>{len(candidates)}</b>. Enter a new quantity (1–1000):"), reply_markup=get_cancel_kb())
                return
            candidates.sort(key=lambda x: (x[0], x[1]))
            selected = candidates[:qty]
            total = sum(float(x[0]) for x in selected)
            balance = float(get_user(chat_id).get("balance", 0) or 0)
            if balance + 1e-9 < total:
                answer_callback(call["id"], f"Insufficient balance. Total: {format_money(total)} | Balance: {format_money(balance)}.", show_alert=True)
                return
            update_balance(chat_id, -total)
            selected_by_batch = {}
            purchased = []
            for price, _rand, b_id, item in selected:
                selected_by_batch.setdefault(b_id, set()).add(str(item.get("num", "")))
                purchased.append({"num": str(item.get("num", "")), "url": str(item.get("url", "")), "price": float(price), "batch_id": b_id})
            for b_id, nums in selected_by_batch.items():
                number_batches[b_id]["numbers"] = [n for n in number_batches[b_id].get("numbers", []) if str(n.get("num", "")) not in nums]
            sale_id = str(uuid.uuid4())[:10]
            bulk_sales[sale_id] = {"user": chat_id, "service": service, "country": country, "quantity": qty,
                                   "total": total, "time": time.time(), "numbers": purchased}
            total_assigned_stats += qty
            save_db()
        user_states.pop(chat_id, None)
        temp_data.pop(chat_id, None)
        bulk_contexts.pop(chat_id, None)
        file_text = "\n".join(f"{x['num']} {x['url']}" for x in purchased)
        delivery = send_document(chat_id, f"Bulk_{sale_id}.txt", file_text, caption=f"Bulk purchase complete: {qty} numbers | Total: {format_money(total)}")
        if not delivery or delivery.get("ok") is not True:
            with purchase_lock:
                for item in purchased:
                    b_id = item.get("batch_id")
                    if b_id in number_batches:
                        number_batches[b_id].setdefault("numbers", []).append({"num": item["num"], "url": item["url"], "shares": 0, "used_by": []})
                bulk_sales.pop(sale_id, None)
                update_balance(chat_id, total)
                total_assigned_stats = max(0, total_assigned_stats - qty)
                save_db()
            answer_callback(call["id"], "File delivery failed. Your balance has been refunded; please try again.", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text("❌ File delivery failed. Your balance has been refunded and stock restored."))
            return
        answer_callback(call["id"], "Bulk purchase completed.")
        edit_message(chat_id, msg_id, render_body_text(f"✅ <b>Bulk purchase completed.</b>\nQuantity: <b>{qty}</b>\nTotal paid: <b>{format_money(total)}</b>"))

    elif data == "bulk_selled":
        if not is_admin(chat_id):
            answer_callback(call["id"], "Admin only.", show_alert=True)
            return
        sales = sorted(bulk_sales.items(), key=lambda kv: kv[1].get("time", 0), reverse=True)
        lines = [f"Total bulk orders: <b>{len(sales)}</b>"]
        kb = []
        for sale_id, sale in sales[:30]:
            label = f"{sale.get('service','')} • {sale.get('country','')} ({sale.get('quantity',0)})"
            kb.append([{"text": label[:60], "icon_custom_emoji_id": "5352694861990501856", "callback_data": f"bulk_dl_{sale_id}", "style": "primary"}])
            lines.append(f"\n{html.escape(label)} — User <code>{sale.get('user')}</code> — {format_money(sale.get('total', 0))}")
        kb.insert(0, [{"text": "Download All TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "bulk_dl_all", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("<b>BULK SELLED</b>\n━━━━━━━━━━━━━━━━━━\n" + "\n".join(lines)), reply_markup={"inline_keyboard": kb})

    elif data.startswith("bulk_dl_"):
        if not is_admin(chat_id):
            answer_callback(call["id"], "Admin only.", show_alert=True)
            return
        if data == "bulk_dl_all":
            selected_sales = list(bulk_sales.items())
            filename = "Bulk_Selled_All.txt"
        else:
            sale_id = data[len("bulk_dl_"):]
            sale = bulk_sales.get(sale_id)
            selected_sales = [(sale_id, sale)] if sale else []
            filename = f"Bulk_Selled_{sale_id}.txt"
        if not selected_sales:
            answer_callback(call["id"], "No bulk sale records found.", show_alert=True)
            return
        out = []
        for sale_id, sale in selected_sales:
            out.append(f"# Sale: {sale_id} | User: {sale.get('user')} | Service: {sale.get('service')} | Country: {sale.get('country')} | Quantity: {sale.get('quantity')} | Total: {sale.get('total')}")
            out.extend(f"{x.get('num','')} {x.get('url','')}" for x in sale.get("numbers", []))
            out.append("")
        send_document(chat_id, filename, "\n".join(out), caption=f"Bulk sales export: {len(selected_sales)} order(s)")
        answer_callback(call["id"])

    elif data == "back_to_services":
        local_srvs = set([b["service"] for b in number_batches.values() if b["numbers"]])
        stex_srvs = set(bot_settings.get("stex_services", {}).keys())
        voltx_srvs = set(bot_settings.get("voltx_services", {}).keys())
        zenex_srvs = set(bot_settings.get("zenex_services", {}).keys())
        all_services = local_srvs.union(stex_srvs).union(voltx_srvs).union(zenex_srvs)
        
        if not all_services:
            answer_callback(call["id"], "❌ No numbers or services available!", show_alert=True)
            return
            
        c_msg = bot_settings["custom_messages"].get("get_number", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['pin']} Select Service"))
        
        apps_db = bot_settings.get("premium_apps", {})
        kb = []
        service_buttons = []
        for s in sorted(all_services, key=lambda x: str(x).lower()):
            emoji_id = "5352694861990501856"
            for app_key, app_data in apps_db.items():
                if s.upper() == app_key or s.upper() in app_key or app_key in s.upper():
                    if "id" in app_data:
                        emoji_id = app_data["id"]
                        break
            service_buttons.append({"text": f"{s}", "icon_custom_emoji_id": emoji_id, "callback_data": f"g_s_{s}", "style": "primary"})
        for i in range(0, len(service_buttons), 2):
            kb.append(service_buttons[i:i + 2])
        
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        
        edit_message(chat_id, msg_id, txt, reply_markup={"inline_keyboard": kb})

    elif data.startswith("g_s_"):
        service = data.split("g_s_")[1]
        local_cnts = set([b["country"] for b in number_batches.values() if b["service"] == service and b["numbers"]])
        stex_cnts = set(bot_settings.get("stex_services", {}).get(service, {}).keys())
        voltx_cnts = set(bot_settings.get("voltx_services", {}).get(service, {}).keys())
        zenex_cnts = set(bot_settings.get("zenex_services", {}).get(service, {}).keys())
        all_countries = local_cnts.union(stex_cnts).union(voltx_cnts).union(zenex_cnts)
        
        c_msg = bot_settings["custom_messages"].get("select_country", {})
        raw_txt = c_msg.get("text", "📌 Select a country for {service}:").replace("{service}", service)
        txt = render_body_text(raw_txt)
        
        flags_db = bot_settings.get("premium_flags", {})
        kb = []
        # Country buttons: show country name only (no TK/OTP price) and keep 2 per row.
        country_buttons = []
        for c in all_countries:
            emoji_id = "5780471598922337683" # Default flag
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data:
                        emoji_id = flag_data["id"]
                        break
            _p = paid_min_price(service, c)
            _label = f"{c} • {format_money(_p)}" if _p is not None else f"{c}"
            country_buttons.append({"text": _label, "icon_custom_emoji_id": emoji_id, "callback_data": f"g_c_{service}_{c}", "style": "success"})

        for i in range(0, len(country_buttons), 2):
            kb.append(country_buttons[i:i + 2])

        # Custom inline buttons: 2 per row.
        custom_buttons = []
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            custom_buttons.append(b_copy)
        for i in range(0, len(custom_buttons), 2):
            kb.append(custom_buttons[i:i + 2])

        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_services", "style": "danger"}])
        edit_message(chat_id, msg_id, txt, reply_markup={"inline_keyboard": kb})

    elif data.startswith("g_c_") or data.startswith("c_n_"):
        # Local uploaded stock offers Buy Once (OTP-managed) or store-style Bulk Buy.
        if data.startswith("g_c_"):
            _parts = data.split("_")
            _service = _parts[2] if len(_parts) > 2 else ""
            _country = _parts[3] if len(_parts) > 3 else ""
            _local_stock = sum(len(b.get("numbers", [])) for b in number_batches.values()
                               if b.get("service") == _service and b.get("country") == _country
                               and any(n.get("url") for n in b.get("numbers", [])))
            if _local_stock > 0:
                bulk_contexts[chat_id] = {"service": _service, "country": _country}
                _kb = {"inline_keyboard": [
                    [{"text": "Buy Once", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "buy_once", "style": "success"}],
                    [{"text": "Bulk Buy", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "bulk_start", "style": "primary"}],
                    [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"g_s_{_service}", "style": "danger"}]
                ]}
                answer_callback(call["id"])
                edit_message(chat_id, msg_id, render_body_text(
                    f"<b>{html.escape(_service)} • {html.escape(_country)}</b>\n\nChoose your purchase type.\nAvailable stock: <b>{_local_stock}</b>"), reply_markup=_kb)
                return
        # ১. গ্লোবাল কুলডাউন চেক (সকল নাম্বার মেথডের জন্য)
        now = time.time()
        if now - user_cooldowns.get(chat_id, 0) < bot_settings["cooldown"]:
            answer_callback(call["id"], f"⌛ Please wait {int(bot_settings['cooldown'] - (now - user_cooldowns.get(chat_id, 0)))}s.", show_alert=True)
            return
        
        # কুলডাউন আপডেট
        user_cooldowns[chat_id] = now
        
        # আগের নাম্বার এক্সপায়ার করা
        expire_previous_number(chat_id)

        # যদি সার্চ নাম্বার থেকে আসে
        if data.startswith("c_n_s_"):
            is_voltx_req = data.endswith("_vtx")
            clean_data = data[:-4] if is_voltx_req else data
            parts_s = clean_data.split("_", 4)
            
            query = parts_s[3] if len(parts_s) > 3 else ""
            service_from_cb = parts_s[4] if len(parts_s) > 4 else None

            # 💰 Paid uploaded numbers (number + API URL)
            if not is_voltx_req and not data.endswith("_znx"):
                _st, _payload = try_buy_local(chat_id, service=service_from_cb, prefix=query, kind="search", change_cb=f"c_n_s_{query}")
                if _st == "ok":
                    answer_callback(call["id"])
                    show_paid_number(chat_id, msg_id, _payload)
                    return
                elif _st == "no_balance":
                    answer_callback(call["id"], f"❌ Insufficient balance! Price: {format_money(_payload['price'])} | Balance: {format_money(_payload['balance'])}. Contact an admin to add balance.", show_alert=True)
                    notify_no_balance(chat_id, _payload)
                    return
            
            allowed_countries = bot_settings.get("search_countries", [])
            voltx_allowed = bot_settings.get("voltx_search_countries", [])
            
            zenex_allowed = bot_settings.get("zenex_search_countries", [])
            
            is_stex_allowed = any(query.startswith(c) for c in allowed_countries) if allowed_countries else False
            is_voltx_allowed = any(query.startswith(c) for c in voltx_allowed) if voltx_allowed else False
            is_zenex_allowed = any(query.startswith(c) for c in zenex_allowed) if zenex_allowed else False
            is_zenex_req = data.endswith("_znx")
            
            if not is_voltx_req and not is_zenex_req and not is_stex_allowed and not is_voltx_allowed and not is_zenex_allowed:
                answer_callback(call["id"], "❌ This country code is not allowed for search!", show_alert=True)
                return
                
            edit_message(chat_id, msg_id, render_body_text("⌛ <i>Processing... Finding Number...</i>"))
            wait_msg_id = msg_id
            
            found_indices = []
            for b_id, b_data in number_batches.items():
                for idx, n_obj in enumerate(b_data["numbers"]):
                    if n_obj["num"].replace("+", "").startswith(query) and chat_id not in n_obj.get("used_by", []):
                        found_indices.append((b_id, idx))
            
            fetched_nums = []
            if not found_indices:
                api_found = False
                req_count = bot_settings.get("num_req", 1)
                
                # প্রথমে Zenex চেক করবে
                if is_zenex_allowed or is_zenex_req:
                    zenex_keys = bot_settings.get("zenex_keys", [])
                    for _ in range(req_count):
                        if len(fetched_nums) >= req_count: break
                        for api_key in zenex_keys:
                            try:
                                headers = {"mapikey": api_key}
                                payload = {"range": query, "is_national": False, "remove_plus": False}
                                res = requests.post(f"{ZENEX_BASE_URL}/v1/getnum", json=payload, headers=headers, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("full_number", "")).replace("+", "")
                                    if not num_str: num_str = str(resp_data["data"].get("number", "")).replace("+", "")
                                    fetched_nums.append(num_str)
                                    zenex_assigned_numbers[num_str] = chat_id 
                                    api_found = True
                                    total_assigned_stats += 1
                                    is_zenex_req = True 
                                    break
                            except: continue

                # তারপর Voltx চেক করবে
                if len(fetched_nums) < req_count and (is_voltx_allowed or is_voltx_req) and not is_zenex_req:
                    voltx_keys = bot_settings.get("voltx_keys", [])
                    for _ in range(req_count):
                        if len(fetched_nums) >= req_count: break
                        for api_key in voltx_keys:
                            try:
                                headers = {"mauthapi": api_key}
                                payload = {"rid": query}
                                res = requests.post(f"{VOLTX_BASE_URL}/getnum", json=payload, headers=headers, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(resp_data["data"].get("national_number", ""))
                                    fetched_nums.append(num_str)
                                    voltx_assigned_numbers[num_str] = chat_id 
                                    api_found = True
                                    total_assigned_stats += 1
                                    is_voltx_req = True # মার্ক করে দিলাম যাতে পরবর্তীতে Voltx রিকোয়েস্ট হিসেবে কাজ করে
                                    break
                            except: continue

                # Voltx এ না পেলে বা আরও নাম্বার লাগলে StexSMS তে চেক করবে
                if len(fetched_nums) < req_count and (is_stex_allowed and not is_voltx_req and not is_zenex_req):
                    stex_keys = bot_settings.get("stex_keys", [])
                    for _ in range(req_count - len(fetched_nums)):
                        for api_key in stex_keys:
                            try:
                                headers = {"mauthapi": api_key}
                                res = requests.post(f"{STEX_BASE_URL}/getnum", json={"rid": query}, headers=headers, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(resp_data["data"].get("national_number", ""))
                                    fetched_nums.append(num_str)
                                    stex_assigned_numbers[num_str] = chat_id 
                                    api_found = True
                                    total_assigned_stats += 1
                                    break
                            except: continue
                        
                if not api_found:
                    answer_callback(call["id"], "❌ Number out of stock!", show_alert=True)
                    delete_message(chat_id, wait_msg_id)
                    return
                save_db()
            else:
                random.shuffle(found_indices)
                for b_id, idx in found_indices:
                    if len(fetched_nums) >= bot_settings.get("num_req", 1): break
                    n_obj = number_batches[b_id]["numbers"][idx]
                    num_str = n_obj["num"]
                    fetched_nums.append(num_str)
                    
                    # 🌟 Save File Specific Rate
                    assigned_number_rates[num_str] = {"normal": float(number_batches[b_id].get("normal_rate", number_batches[b_id].get("rate", bot_settings.get("otp_reward", 0.0)))), "special": float(number_batches[b_id].get("special_rate", number_batches[b_id].get("normal_rate", number_batches[b_id].get("rate", bot_settings.get("otp_reward", 0.0)))))}
                    
                    n_obj["shares"] += 1
                    n_obj["used_by"].append(chat_id)
                    total_assigned_stats += 1
                    if n_obj["shares"] >= bot_settings.get("num_share", 1):
                        n_obj["to_remove"] = True
                        used_numbers_list.append(num_str)
                for b_id in number_batches:
                    number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]
                save_db()
                
            kb = []
            if service_from_cb:
                app_full_name, _ = get_service_info_html(service_from_cb)
                emoji_id_srv = "5337302974806922068"
                for app_key, app_data in bot_settings.get("premium_apps", {}).items():
                    if service_from_cb.upper() == app_key or service_from_cb.upper() in app_key or app_key in service_from_cb.upper():
                        if "id" in app_data: emoji_id_srv = app_data["id"]; break
                kb.append([{"text": f"{app_full_name}", "icon_custom_emoji_id": emoji_id_srv, "callback_data": "ignore", "style": "primary"}])

            flags_db = bot_settings.get("premium_flags", {})
            country_emoji_html = ""
            for num in fetched_nums:
                char_flag, iso = get_flag_and_code(num)
                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                flag_emoji_id = "5780471598922337683"
                for flag_code, flag_data in flags_db.items():
                    if iso == flag_data.get("iso"):
                        if "id" in flag_data: 
                            flag_emoji_id = flag_data["id"]
                            country_emoji_html = f'<tg-emoji emoji-id="{flag_emoji_id}">{flag_data["char"]}</tg-emoji>'
                        break
                if not country_emoji_html: country_emoji_html = char_flag
                kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": flag_emoji_id, "copy_text": {"text": display_num}, "style": "success"}])
            
            vtx_ext = "_vtx" if is_voltx_req else "_znx" if is_zenex_req else ""
            srv_ext = f"_{service_from_cb}" if service_from_cb else ""
            change_buttons = [{"text": "Buy New", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"c_n_s_{query}{srv_ext}{vtx_ext}", "style": "danger"}]
            if service_from_cb:
                change_buttons.append({"text": "Change Country", "icon_custom_emoji_id": "5305517382138112561", "callback_data": f"g_s_{service_from_cb}", "style": "danger"})
            kb.append(change_buttons)

            # Custom inline buttons: 2 per row.
            c_btns = []
            for c_b in bot_settings["custom_messages"].get("search_number", {}).get("buttons", []):
                b_copy = _premium_user_inline_button(c_b)
                c_btns.append(b_copy)
            for i in range(0, len(c_btns), 2):
                kb.append(c_btns[i:i + 2])

            # OTP Group stays on its own row.
            kb.append([{"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
            
            # Build the NEW NUMBER message context from the search callback.
            # `country` and `service` are not defined in this c_n_s_ branch.
            # Derive them from the fetched number and callback service so a
            # custom NEW NUMBER template cannot break the number-delivery flow.
            display_country = get_flag_info_html(fetched_nums[0], return_full_name=True).title() if fetched_nums else query
            display_service = service_from_cb or ""
            if display_service:
                display_service, _ = get_service_info_html(display_service)

            text_numbers, new_number_custom_kb = render_new_number_message(
                country_emoji_html, display_country, display_service
            )
            kb.extend(new_number_custom_kb)
            edit_message(chat_id, wait_msg_id, text_numbers, reply_markup={"inline_keyboard": kb})
            user_active_sessions[chat_id] = {"msg_id": wait_msg_id, "nums": fetched_nums}
            return

        # যদি আপলোড করা বা সার্ভিস থেকে আসে
        parts = data.split("_")
        service = parts[2]
        country = parts[3]

        # 💰 Paid uploaded numbers (number + API URL): charge balance, then poll API for OTP
        _st, _payload = try_buy_local(chat_id, service=service, country=country, kind="service",
                                      change_cb=f"paid_new:{service}:{country}", country_cb=f"g_s_{service}")
        if _st == "ok":
            answer_callback(call["id"])
            show_paid_number(chat_id, msg_id, _payload)
            return
        elif _st == "no_balance":
            answer_callback(call["id"], f"❌ Insufficient balance! Price: {format_money(_payload['price'])} | Balance: {format_money(_payload['balance'])}. Contact an admin to add balance.", show_alert=True)
            notify_no_balance(chat_id, _payload)
            return

        available_indices = []
        # Check Local Stock First
        for b_id, b_data in number_batches.items():
            if b_data["service"] == service and b_data["country"] == country:
                for idx, n_obj in enumerate(b_data["numbers"]):
                    if chat_id not in n_obj.get("used_by", []):
                        available_indices.append((b_id, idx))

        # IF NO LOCAL STOCK, Check StexSMS, Voltx & Zenex Services
        if not available_indices:
            stex_srv_data = bot_settings.get("stex_services", {}).get(service, {}).get(country)
            voltx_srv_data = bot_settings.get("voltx_services", {}).get(service, {}).get(country)
            zenex_srv_data = bot_settings.get("zenex_services", {}).get(service, {}).get(country)
            
            target_range = None
            is_voltx = False
            is_zenex = False
            
            if stex_srv_data and len(stex_srv_data) > 0:
                target_range = random.choice(stex_srv_data)
            elif voltx_srv_data and len(voltx_srv_data) > 0:
                target_range = random.choice(voltx_srv_data)
                is_voltx = True
            elif zenex_srv_data and len(zenex_srv_data) > 0:
                target_range = random.choice(zenex_srv_data)
                is_zenex = True
                
            if target_range:
                user_cooldowns[chat_id] = 0
                vtx_flag = "_vtx" if is_voltx else "_znx" if is_zenex else ""
                handle_callback({"message": call["message"], "data": f"c_n_s_{target_range}_{service}{vtx_flag}", "id": call["id"]})
                return
            else:
                answer_callback(call["id"], "❌ Number out of stock or range missing!", show_alert=True)
                if data.startswith("c_n_"): delete_message(chat_id, msg_id)
                return

        random.shuffle(available_indices)
        
        fetched_nums = []
        for b_id, idx in available_indices:
            if len(fetched_nums) >= bot_settings["num_req"]: break
            n_obj = number_batches[b_id]["numbers"][idx]
            
            fetched_nums.append(n_obj["num"])
            
            # 🌟 Save File Specific Rate
            assigned_number_rates[n_obj["num"]] = {"normal": float(number_batches[b_id].get("normal_rate", number_batches[b_id].get("rate", bot_settings.get("otp_reward", 0.0)))), "special": float(number_batches[b_id].get("special_rate", number_batches[b_id].get("normal_rate", number_batches[b_id].get("rate", bot_settings.get("otp_reward", 0.0)))))}
            
            n_obj["shares"] += 1
            n_obj["used_by"].append(chat_id)
            total_assigned_stats += 1
            
            if n_obj["shares"] >= bot_settings.get("num_share", 1):
                n_obj["to_remove"] = True
                used_numbers_list.append(n_obj["num"])

        for b_id in number_batches:
            number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]
        save_db()

        if not fetched_nums:
            answer_callback(call["id"], "❌ You have already taken all numbers or stock is empty!", show_alert=True)
            if data.startswith("c_n_"): delete_message(chat_id, msg_id)
            return

        app_full_name, _ = get_service_info_html(service)
        emoji_id = "5337302974806922068"
        apps_db = bot_settings.get("premium_apps", {})
        for app_key, app_data in apps_db.items():
            if service.upper() == app_key or service.upper() in app_key or app_key in service.upper():
                if "id" in app_data:
                    emoji_id = app_data["id"]
                    break
        kb = [[{"text": f"{app_full_name}", "icon_custom_emoji_id": emoji_id, "callback_data": "ignore", "style": "primary"}]]
        
        flags_db = bot_settings.get("premium_flags", {})
        country_emoji_html = ""
        for num in fetched_nums:
            char_flag, iso = get_flag_and_code(num)
            display_num = f"+{num}" if not num.startswith("+") else num
            
            flag_emoji_id = "5780471598922337683" # Default Flag
            for flag_code, flag_data in flags_db.items():
                if iso == flag_data.get("iso"):
                    if "id" in flag_data: 
                        flag_emoji_id = flag_data["id"]
                        country_emoji_html = f'<tg-emoji emoji-id="{flag_emoji_id}">{flag_data["char"]}</tg-emoji>'
                    break
            
            if not country_emoji_html: country_emoji_html = char_flag
            kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": flag_emoji_id, "copy_text": {"text": display_num}, "style": "success"}])
            
        # Change Number + Change Country on the same row.
        kb.append([
            {"text": "Buy New", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"c_n_{service}_{country}", "style": "danger"},
            {"text": "Change Country", "icon_custom_emoji_id": "5305517382138112561", "callback_data": f"g_s_{service}", "style": "danger"}
        ])

        # Custom inline buttons: 2 per row.
        c_btns = []
        for c_b in bot_settings["custom_messages"].get("get_number", {}).get("buttons", []):
            b_copy = c_b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            c_btns.append(b_copy)
        for i in range(0, len(c_btns), 2):
            kb.append(c_btns[i:i + 2])

        # OTP Group stays on its own row.
        kb.append([{"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
        
        text_numbers, new_number_custom_kb = render_new_number_message(country_emoji_html, country, service)
        kb.extend(new_number_custom_kb)
        # সবসময় মেসেজ ইডিট করবে (Change Number করলেও নতুন মেসেজ আসবে না)
        try:
            edit_message(chat_id, msg_id, text_numbers, reply_markup={"inline_keyboard": kb})
            user_active_sessions[chat_id] = {"msg_id": msg_id, "nums": fetched_nums}
        except:
            # যদি মেসেজ ইডিট করা সম্ভব না হয় (যেমন অনেক আগের মেসেজ), তবে নতুন মেসেজ দিবে
            msg_res = send_message(chat_id, text_numbers, reply_markup={"inline_keyboard": kb})
            if msg_res and "result" in msg_res:
                user_active_sessions[chat_id] = {"msg_id": msg_res["result"]["message_id"], "nums": fetched_nums}

    elif data.startswith("wapp_") or data.startswith("wrej_"):
        # অ্যাডমিন চেক (User ID চেক করতে হবে)
        user_id_clicked = call["from"]["id"]
        if not is_admin(user_id_clicked):
            answer_callback(call["id"], "🚫 Only Bot Admins can process withdrawals!", show_alert=True)
            return
            
        action = "APPROVE" if data.startswith("wapp_") else "REJECT"
        req_id = data.replace("wapp_", "").replace("wrej_", "")
        
        if req_id in pending_withdrawals:
            req_data = pending_withdrawals[req_id]
            u_id, amt = req_data["user_id"], req_data["amount"]
            num = req_data["number"]
            full_name = req_data.get("full_name", u_id)
            
            if action == "APPROVE" and len(num) >= 7:
                masked_num = f"{num[:4]}❖DXA❖{num[-3:]}"
            else:
                masked_num = num
            
            if action == "REJECT":
                update_balance(u_id, amt) 
                send_message(u_id, render_body_text(f"❌ Your {amt} TK withdrawal request was rejected. Balance refunded."))
            else:
                send_message(u_id, render_body_text(f"{PEM['ok']} Your {amt} TK withdrawal request has been paid successfully!"))
            
            if db:
                try: db.collection('withdrawals').document(req_id).update({"status": "approved" if action == "APPROVE" else "rejected"})
                except: pass
                
            del pending_withdrawals[req_id]
            save_db()
            delete_message(chat_id, msg_id)
        else:
            answer_callback(call["id"], "❌ Request already processed!", show_alert=True)

# ==========================================
# Console OTP Forwarding
# ==========================================
def forward_console_otp_to_groups(number, service, message, iso=None):
    """Forward an OTP detected from Bangla/console panels to configured OTP groups."""
    try:
        if not bot_settings.get("console_otp", False):
            return
        message = str(message or "").strip()
        if not message:
            return
        otp = extract_otp_code(message)
        if not otp:
            return

        raw_num = str(number or "").strip()
        if not raw_num:
            return
        display_num = raw_num if raw_num.startswith("+") else "+" + raw_num

        # Console numbers can be incomplete, so the country calling code
        # must come from the detected country/ISO, not from the partial number.
        clean_console = ''.join(ch for ch in raw_num if ch.isdigit())
        _, detected_iso = get_flag_and_code(raw_num)
        detected_iso = str(iso or detected_iso or "XX").upper()

        # premium_flags is keyed by international calling code (e.g. 880 -> BD,
        # 382 -> ME). Reverse-lookup the calling code from the detected ISO.
        country_calling_code = None
        for calling_code, flag_data in bot_settings.get("premium_flags", {}).items():
            if str(flag_data.get("iso", "")).upper() == detected_iso:
                country_calling_code = str(calling_code)
                break

        # Fallback: if ISO lookup is unavailable, use the calling code detected
        # from the number itself.
        if not country_calling_code:
            clean_for_lookup = clean_console
            for calling_code in sorted(bot_settings.get("premium_flags", {}).keys(), key=len, reverse=True):
                if clean_for_lookup.startswith(str(calling_code)):
                    country_calling_code = str(calling_code)
                    break
        country_calling_code = country_calling_code or "000"

        mask_cfg = bot_settings.get("mask_emoji", {}) if "bot_settings" in globals() else {}
        mask_id = str(mask_cfg.get("id", "") or "")
        mask_char = str(mask_cfg.get("char", "") or "")
        if mask_id and mask_char:
            console_mask = f'<tg-emoji emoji-id="{mask_id}">{mask_char}</tg-emoji>'
        else:
            console_mask = mask_char or "DXA"

        # The prefix is the country's real international calling code.
        # It is NOT generated and is NOT taken from the partial console number.
        # Example: ME -> 382, BD -> 880.
        # Console numbers may be incomplete/reused, so the 4 digits after
        # the hide marker are intentionally randomized for each displayed OTP.
        suffix = f"{random.randint(0, 9999):04d}"
        masked = f"{country_calling_code}{console_mask}{suffix}"

        app_full_name, prem_app_html = get_service_info_html(
            str(service or "Unknown"), message
        )
        flag_html = get_premium_flag_html_by_iso(detected_iso)
        lang = detect_language(message)
        # Display the detected language as its short code: #EN, #BN, #AR, etc.
        lang_code = str(lang or "#EN").upper()
        if not lang_code.startswith("#"):
            lang_code = "#" + lang_code
        if len(lang_code) > 3:
            lang_code = lang_code[:3]

        # Same interface as the real OTP group message:
        # FLAG ISO | APP NUMBER | #LANG
        display_msg = render_body_text(
            f"{flag_html} {detected_iso} | {prem_app_html} {masked} | 💬 {lang_code}"
        )

        for fw in bot_settings.get("fw_groups", []):
            try:
                kb = [[{
                    "text": str(otp),
                    "icon_custom_emoji_id": "5296369303661067030",
                    "copy_text": {"text": str(otp)},
                    "style": "primary"
                }]]
                temp_row = []
                styles = ["danger", "success", "primary"]
                for i, btn in enumerate(fw.get("buttons", [])):
                    if not btn.get("url"):
                        continue
                    b_obj = {
                        "text": btn.get("text", ""),
                        "url": btn["url"],
                        "style": styles[i % 3]
                    }
                    if btn.get("icon_custom_emoji_id"):
                        b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                    temp_row.append(b_obj)
                    if len(temp_row) == 2:
                        kb.append(temp_row)
                        temp_row = []
                if temp_row:
                    kb.append(temp_row)
                send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
            except Exception:
                pass
    except Exception:
        pass

# ==========================================
# Polling Loop
# ==========================================
def poll_otp_with_status(number_id, num_str, owner_id, api_key):
    headers = {"X-API-Key": api_key}
    for _ in range(150): # 150 * 4 seconds = 10 Minutes Polling
        try:
            res = requests.get(f"{STEX_BASE_URL}/api/v1/numbers/{number_id}/sms", headers=headers, timeout=10)
            data = res.json()
            if data.get("success") and data.get("otp"):
                otp = str(data["otp"])
                msg_text = data.get("message", f"Your code is {otp}")
                
                # 🌟 সম্পূর্ণ মেসেজ থেকে ড্যাশসহ বা বড় OTP খোঁজার ফিক্স
                extracted_otp = extract_otp_code(msg_text)
                if extracted_otp and len(extracted_otp) > len(otp):
                    otp = extracted_otp
                    
                # 🌟 সম্পূর্ণ মেসেজ থেকে সার্ভিস/অ্যাপ চেনার ফিক্স
                app_name = data.get("service", "StexSMS Service")
                detected_app = detect_service(msg_text)
                if detected_app:
                    app_name = detected_app
                
                unique_id = f"POLL_{number_id}_{otp}"
                if unique_id not in processed_otps:
                    processed_otps.add(unique_id)
                    
                    char, iso = get_flag_and_code(num_str)
                    app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                    
                    global recent_traffic
                    current_time = time.time()
                    recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                    recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num_str, "time": current_time, "source": "bot"})
                    save_local_db()
                    
                    display_num = f"+{num_str}" if not str(num_str).startswith("+") else str(num_str)
                    masked = mask_number(display_num)
                    lang = detect_language(msg_text)
                    
                    display_msg = render_body_text(f"╔═══════════════╗\n║ {prem_app_html} {get_premium_flag_html_by_iso(iso)} {masked} {lang}\n╚═══════════════╝")
                    
                    for fw in bot_settings.get("fw_groups", []):
                        kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5296369303661067030", "copy_text": {"text": otp}, "style": "primary"}]]
                        temp_row = []
                        styles = ["danger", "success", "primary"]
                        for i, btn in enumerate(fw.get("buttons", [])):
                            b_obj = {"text": btn["text"], "url": btn["url"], "style": styles[i % 3]}
                            if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                            temp_row.append(b_obj)
                            if len(temp_row) == 2:
                                kb.append(temp_row)
                                temp_row = []
                        if temp_row: kb.append(temp_row)
                        send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                    
                    inbox_msg = render_body_text(f"╔═══════════════╗\n║ {prem_app_html} {get_premium_flag_html_by_iso(iso)} {display_num} {lang}\n╚═══════════════╝")
                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "primary"}]]
                    
                    reward = get_otp_reward_for_user(num_str, owner_id)
                    if reward > 0:
                        update_balance(owner_id, reward)
                        inbox_kb.append([{"text": f"Added {reward} tk", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "ignore", "style": "primary"}])
                    
                    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                    
                    if db:
                        try: db.collection('users').document(str(owner_id)).update({"total_otps": Increment(1)})
                        except: pass
                break
        except: pass
        time.sleep(4)

def stex_console_listener():
    global recent_traffic, bot_settings
    seen_console_hits = set()
    last_auto_update = time.time()
    
    while True:
        try:
            stex_keys = bot_settings.get("stex_keys", [])
            if stex_keys:
                api_key = stex_keys[0]
                headers = {"mauthapi": api_key}
                res = requests.get(f"{STEX_BASE_URL}/console", headers=headers, timeout=10)
                data = res.json()
                
                if data.get("meta", {}).get("code") == 200 and data.get("data", {}).get("hits"):
                    current_time = time.time()
                    new_hits = False
                    
                    for hit in data["data"]["hits"]:
                        range_str = str(hit.get("range", "")).replace("X", "")
                        if len(range_str) > 9:
                            range_str = range_str[:9]
                        sid = str(hit.get("sid", "Unknown"))
                        msg = str(hit.get("message", ""))
                        hit_time = hit.get("time", current_time * 1000) / 1000.0
                        
                        unique_hit = f"STEX_{range_str}_{sid}_{hit.get('time', 0)}"
                        if unique_hit not in seen_console_hits and range_str:
                            seen_console_hits.add(unique_hit)
                            if len(seen_console_hits) > 2000: seen_console_hits.clear()
                            
                            char, iso = get_flag_and_code(range_str)
                            app_full_name, _ = get_service_info_html(sid, msg)
                            forward_console_otp_to_groups(range_str, app_full_name, msg, iso)
                            
                            recent_traffic.append({
                                "service": app_full_name,
                                "iso": iso,
                                "flag": char,
                                "number": f"{range_str}XXX", 
                                "time": hit_time,
                                "real_range": range_str,
                                "source": "console"
                            })
                            new_hits = True
                            
                    if new_hits:
                        recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                        save_local_db()
                        
                    # 🌟 Auto ADD and DELETE logic for Stex every 2 minutes
                    if bot_settings.get("stex_auto", False) and current_time - last_auto_update > 120:
                        last_auto_update = current_time
                        changed = False
                        
                        if "stex_services" not in bot_settings: bot_settings["stex_services"] = {}
                        if "search_countries" not in bot_settings: bot_settings["search_countries"] = []
                        
                        srv_counts = Counter(t["service"].upper() for t in recent_traffic if "real_range" in t)
                        top_srvs = [s for s, c in srv_counts.most_common(6)]
                        
                        for srv in top_srvs:
                            if srv not in bot_settings["stex_services"]:
                                bot_settings["stex_services"][srv] = {}
                                changed = True
                                
                            iso_counts = Counter(t["iso"] for t in recent_traffic if t.get("service", "").upper() == srv and "real_range" in t)
                            top_isos = [i for i, c in iso_counts.most_common(3)]
                            
                            for iso in top_isos:
                                full_country_name = get_flag_info_html(iso, return_full_name=True).title()
                                if full_country_name not in bot_settings["stex_services"][srv]:
                                    bot_settings["stex_services"][srv][full_country_name] = []
                                    changed = True
                                    
                                rng_counts = Counter(t["real_range"] for t in recent_traffic if t.get("service", "").upper() == srv and t.get("iso") == iso and "real_range" in t)
                                top_rngs = [r for r, c in rng_counts.most_common(2)]
                                
                                for rng in top_rngs:
                                    if rng not in bot_settings["stex_services"][srv][full_country_name]:
                                        bot_settings["stex_services"][srv][full_country_name].append(rng)
                                        changed = True
                                        
                                    country_code = rng[:3]
                                    if country_code not in bot_settings["search_countries"]:
                                        bot_settings["search_countries"].append(country_code)
                                        changed = True

                        services_to_remove = []
                        for srv, countries in list(bot_settings["stex_services"].items()):
                            srv_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and "real_range" in t and current_time - t.get("time", 0) <= 120)
                            if srv_hit < 1:
                                services_to_remove.append(srv)
                                continue
                            
                            countries_to_remove = []
                            for country, ranges in list(countries.items()):
                                c_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and get_flag_info_html(t.get("iso"), return_full_name=True).title() == country and "real_range" in t and current_time - t.get("time", 0) <= 120)
                                if c_hit < 1:
                                    countries_to_remove.append(country)
                                    continue
                                
                                ranges_to_remove = []
                                for rng in ranges:
                                    r_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and t.get("real_range") == rng and current_time - t.get("time", 0) <= 120)
                                    if r_hit < 1: 
                                        ranges_to_remove.append(rng)
                                
                                for r in ranges_to_remove:
                                    ranges.remove(r)
                                    changed = True
                                    
                            for c in countries_to_remove:
                                del bot_settings["stex_services"][srv][c]
                                changed = True
                                
                        for s in services_to_remove:
                            del bot_settings["stex_services"][s]
                            changed = True
                            
                        if changed:
                            save_db()
                            
        except Exception as e:
            pass
        time.sleep(10)

def voltx_console_listener():
    global recent_traffic, bot_settings
    seen_console_hits = set()
    last_auto_update = time.time()
    
    while True:
        try:
            if not bot_settings.get("voltx_on", True):
                time.sleep(5)
                continue
            voltx_keys = bot_settings.get("voltx_keys", [])
            if voltx_keys:
                api_key = voltx_keys[0]
                headers = {"mauthapi": api_key}
                res = requests.get(f"{VOLTX_BASE_URL}/console", headers=headers, timeout=10)
                data = res.json()
                
                if data.get("meta", {}).get("code") == 200 and data.get("data", {}).get("hits"):
                    current_time = time.time()
                    new_hits = False
                    
                    for hit in data["data"]["hits"]:
                        range_str = str(hit.get("range", "")).replace("X", "")
                        if len(range_str) > 9:
                            range_str = range_str[:9] # 9 ডিজিটের বেশি হলে প্রথম 9 ডিজিট নেবে
                        sid = str(hit.get("sid", "Unknown"))
                        msg = str(hit.get("message", ""))
                        hit_time = hit.get("time", current_time * 1000) / 1000.0
                        
                        unique_hit = f"{range_str}_{sid}_{hit.get('time', 0)}"
                        if unique_hit not in seen_console_hits and range_str:
                            seen_console_hits.add(unique_hit)
                            if len(seen_console_hits) > 2000: seen_console_hits.clear()
                            
                            char, iso = get_flag_and_code(range_str)
                            app_full_name, _ = get_service_info_html(sid, msg)
                            forward_console_otp_to_groups(range_str, app_full_name, msg, iso)
                            
                            recent_traffic.append({
                                "service": app_full_name,
                                "iso": iso,
                                "flag": char,
                                "number": f"{range_str}XXX", 
                                "time": hit_time,
                                "real_range": range_str,
                                "source": "console"
                            })
                            new_hits = True
                            
                    if new_hits:
                        recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                        save_local_db()
                        
                    # 🌟 Auto ADD and DELETE logic every 2 minutes (120 seconds)
                    if bot_settings.get("voltx_auto", False) and current_time - last_auto_update > 120:
                        last_auto_update = current_time
                        changed = False
                        
                        if "voltx_services" not in bot_settings: bot_settings["voltx_services"] = {}
                        if "voltx_search_countries" not in bot_settings: bot_settings["voltx_search_countries"] = []
                        
                        # --- ১. Auto ADD Logic ---
                        srv_counts = Counter(t["service"].upper() for t in recent_traffic if "real_range" in t)
                        top_srvs = [s for s, c in srv_counts.most_common(6)] # Top 6 Services
                        
                        for srv in top_srvs:
                            if srv not in bot_settings["voltx_services"]:
                                bot_settings["voltx_services"][srv] = {}
                                changed = True
                                
                            iso_counts = Counter(t["iso"] for t in recent_traffic if t.get("service", "").upper() == srv and "real_range" in t)
                            top_isos = [i for i, c in iso_counts.most_common(3)] # Top 3 Countries
                            
                            for iso in top_isos:
                                full_country_name = get_flag_info_html(iso, return_full_name=True).title()
                                if full_country_name not in bot_settings["voltx_services"][srv]:
                                    bot_settings["voltx_services"][srv][full_country_name] = []
                                    changed = True
                                    
                                rng_counts = Counter(t["real_range"] for t in recent_traffic if t.get("service", "").upper() == srv and t.get("iso") == iso and "real_range" in t)
                                top_rngs = [r for r, c in rng_counts.most_common(2)] # Top 2 Ranges
                                
                                for rng in top_rngs:
                                    if rng not in bot_settings["voltx_services"][srv][full_country_name]:
                                        bot_settings["voltx_services"][srv][full_country_name].append(rng)
                                        changed = True
                                        
                                    # 🌟 শুধুমাত্র ৩ ডিজিট কান্ট্রি কোড অ্যাড করবে
                                    country_code = rng[:3]
                                    if country_code not in bot_settings["voltx_search_countries"]:
                                        bot_settings["voltx_search_countries"].append(country_code)
                                        changed = True

                        # --- ২. Auto DELETE Logic (Only if NO traffic in the LAST 120 SECONDS) ---
                        services_to_remove = []
                        for srv, countries in list(bot_settings["voltx_services"].items()):
                            # চেক করবে গত ১২০ সেকেন্ডে কোনো ট্রাফিক আছে কি না
                            srv_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and "real_range" in t and current_time - t.get("time", 0) <= 120)
                            if srv_hit < 1:
                                services_to_remove.append(srv)
                                continue
                            
                            countries_to_remove = []
                            for country, ranges in list(countries.items()):
                                c_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and get_flag_info_html(t.get("iso"), return_full_name=True).title() == country and "real_range" in t and current_time - t.get("time", 0) <= 120)
                                if c_hit < 1:
                                    countries_to_remove.append(country)
                                    continue
                                
                                ranges_to_remove = []
                                for rng in ranges:
                                    r_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and t.get("real_range") == rng and current_time - t.get("time", 0) <= 120)
                                    if r_hit < 1: 
                                        ranges_to_remove.append(rng)
                                
                                for r in ranges_to_remove:
                                    ranges.remove(r)
                                    changed = True
                                    
                            for c in countries_to_remove:
                                del bot_settings["voltx_services"][srv][c]
                                changed = True
                                
                        for s in services_to_remove:
                            del bot_settings["voltx_services"][s]
                            changed = True
                            
                        if changed:
                            save_db()
                            
        except Exception as e:
            pass
        time.sleep(10)

def voltx_sms_listener():
    global processed_otps, recent_traffic, voltx_assigned_numbers
    while True:
        try:
            voltx_keys = bot_settings.get("voltx_keys", [])
            for api_key in voltx_keys:
                try:
                    headers = {"mauthapi": api_key}
                    res = requests.get(f"{VOLTX_BASE_URL}/success-otp", headers=headers, timeout=10)
                    resp_data = res.json()
                    
                    if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data and "otps" in resp_data["data"]:
                        for item in resp_data["data"]["otps"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("message", ""))
                            otp = extract_otp_code(msg_text) or "CODE"
                            otp_id = str(item.get("otp_id", otp))
                            
                            app_name = "Voltx Service"
                            detected_app = detect_service(msg_text)
                            if detected_app: app_name = detected_app
                                
                            unique_id = f"VOLTX_{num}_{otp_id}"
                            
                            if unique_id not in processed_otps and num:
                                processed_otps.add(unique_id)
                                if len(processed_otps) > 5000: processed_otps.clear()
                                
                                char, iso = get_flag_and_code(num)
                                app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                                current_time = time.time()
                                
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time, "source": "bot"})
                                save_local_db()
                                
                                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                                masked = mask_number(display_num)
                                lang = detect_language(msg_text)
                                
                                lang_name = lang
                                display_msg = render_body_text(f"{get_premium_flag_html_by_iso(iso)} {iso} | {prem_app_html} {masked} | 💬 {lang}")
                                
                                for fw in bot_settings.get("fw_groups", []):
                                    kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5296369303661067030", "copy_text": {"text": otp}, "style": "primary"}]]
                                    temp_row = []
                                    styles = ["danger", "success", "primary"]
                                    for i, btn in enumerate(fw.get("buttons", [])):
                                        b_obj = {"text": btn["text"], "url": btn["url"], "style": styles[i % 3]}
                                        if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                                        temp_row.append(b_obj)
                                        if len(temp_row) == 2:
                                            kb.append(temp_row)
                                            temp_row = []
                                    if temp_row: kb.append(temp_row)
                                    send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                                    
                                owner_id = None
                                clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                
                                for uid, session_data in user_active_sessions.items():
                                    for act_num in session_data.get("nums", []):
                                        act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owner_id = uid
                                            break
                                    if owner_id: break
                                    
                                if not owner_id:
                                    for vtx_n, n_owner in voltx_assigned_numbers.items():
                                        clean_vtx = str(vtx_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if clean_vtx == clean_api_num or (len(clean_vtx) >= 8 and clean_vtx.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_vtx[-8:])):
                                            owner_id = n_owner
                                            break
                                        
                                if owner_id:
                                    lang_name = lang
                                    inbox_msg = render_body_text(f"{get_premium_flag_html_by_iso(iso)} {iso} | {prem_app_html} {display_num} | 💬 {lang}")
                                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "primary"}]]
                                    
                                    reward = get_otp_reward_for_user(num, owner_id)
                                    if reward > 0:
                                        update_balance(owner_id, reward)
                                        inbox_kb.append([{"text": f"Added {reward} tk", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "ignore", "style": "primary"}])
                                    
                                    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                    
                                    if db:
                                        try: 
                                            db.collection('users').document(str(owner_id)).update({"total_otps": Increment(1)})
                                            if owner_id in user_cache:
                                                user_cache[owner_id]["total_otps"] = user_cache[owner_id].get("total_otps", 0) + 1
                                        except: pass
                except: pass
        except: pass
        time.sleep(5)

def zenex_sms_listener():
    global processed_otps, recent_traffic, zenex_assigned_numbers
    while True:
        try:
            zenex_keys = bot_settings.get("zenex_keys", [])
            for api_key in zenex_keys:
                try:
                    headers = {"mapikey": api_key}
                    res = requests.get(f"{ZENEX_BASE_URL}/v1/numsuccess/info", headers=headers, timeout=10)
                    resp_data = res.json()
                    
                    if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data and "otps" in resp_data["data"]:
                        for item in resp_data["data"]["otps"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("otp", ""))
                            otp = extract_otp_code(msg_text) or "CODE"
                            otp_id = str(item.get("nid", otp))
                            
                            app_name = "Zenex Service"
                            detected_app = detect_service(msg_text)
                            if detected_app: app_name = detected_app
                                
                            unique_id = f"ZENEX_{num}_{otp_id}"
                            
                            if unique_id not in processed_otps and num:
                                processed_otps.add(unique_id)
                                if len(processed_otps) > 5000: processed_otps.clear()
                                
                                char, iso = get_flag_and_code(num)
                                app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                                current_time = time.time()
                                
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time, "source": "bot"})
                                save_local_db()
                                
                                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                                masked = mask_number(display_num)
                                lang = detect_language(msg_text)
                                
                                lang_name = lang
                                display_msg = render_body_text(f"{get_premium_flag_html_by_iso(iso)} {iso} | {prem_app_html} {masked} | 💬 {lang}")
                                
                                for fw in bot_settings.get("fw_groups", []):
                                    kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5296369303661067030", "copy_text": {"text": otp}, "style": "primary"}]]
                                    temp_row = []
                                    styles = ["danger", "success", "primary"]
                                    for i, btn in enumerate(fw.get("buttons", [])):
                                        b_obj = {"text": btn["text"], "url": btn["url"], "style": styles[i % 3]}
                                        if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                                        temp_row.append(b_obj)
                                        if len(temp_row) == 2:
                                            kb.append(temp_row)
                                            temp_row = []
                                    if temp_row: kb.append(temp_row)
                                    send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                                    
                                owner_id = None
                                clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                
                                for uid, session_data in user_active_sessions.items():
                                    for act_num in session_data.get("nums", []):
                                        act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owner_id = uid
                                            break
                                    if owner_id: break
                                    
                                if not owner_id:
                                    for znx_n, n_owner in zenex_assigned_numbers.items():
                                        clean_znx = str(znx_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if clean_znx == clean_api_num or (len(clean_znx) >= 8 and clean_znx.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_znx[-8:])):
                                            owner_id = n_owner
                                            break
                                        
                                if owner_id:
                                    inbox_msg = render_body_text(f"{get_premium_flag_html_by_iso(iso)} {iso} | {prem_app_html} {display_num} | 💬 {lang}")
                                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "primary"}]]
                                    
                                    reward = get_otp_reward_for_user(num, owner_id)
                                    if reward > 0:
                                        update_balance(owner_id, reward)
                                        inbox_kb.append([{"text": f"Added {reward} tk", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "ignore", "style": "primary"}])
                                    
                                    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                    
                                    if db:
                                        try: 
                                            db.collection('users').document(str(owner_id)).update({"total_otps": Increment(1)})
                                            if owner_id in user_cache:
                                                user_cache[owner_id]["total_otps"] = user_cache[owner_id].get("total_otps", 0) + 1
                                        except: pass
                except: pass
        except: pass
        time.sleep(5)

def global_sms_listener():
    global processed_otps, recent_traffic, stex_assigned_numbers
    while True:
        try:
            stex_keys = bot_settings.get("stex_keys", [])
            for api_key in stex_keys:
                try:
                    headers = {"mauthapi": api_key}
                    res = requests.get(f"{STEX_BASE_URL}/success-otp", headers=headers, timeout=10)
                    resp_data = res.json()
                    
                    if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data and "otps" in resp_data["data"]:
                        for item in resp_data["data"]["otps"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("message", ""))
                            otp = extract_otp_code(msg_text) or "CODE"
                            otp_id = str(item.get("otp_id", otp))
                            
                            app_name = "Stex Service"
                            detected_app = detect_service(msg_text)
                            if detected_app: app_name = detected_app
                                
                            unique_id = f"STEX_{num}_{otp_id}"
                            
                            if unique_id not in processed_otps and num:
                                processed_otps.add(unique_id)
                                if len(processed_otps) > 5000: processed_otps.clear()
                                
                                char, iso = get_flag_and_code(num)
                                app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                                current_time = time.time()
                                
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time, "source": "bot"})
                                save_local_db()
                                
                                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                                masked = mask_number(display_num)
                                lang = detect_language(msg_text)
                                
                                lang_name = lang
                                display_msg = render_body_text(f"{get_premium_flag_html_by_iso(iso)} {iso} | {prem_app_html} {masked} | 💬 {lang}")
                                
                                for fw in bot_settings.get("fw_groups", []):
                                    kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5296369303661067030", "copy_text": {"text": otp}, "style": "primary"}]]
                                    temp_row = []
                                    styles = ["danger", "success", "primary"]
                                    for i, btn in enumerate(fw.get("buttons", [])):
                                        b_obj = {"text": btn["text"], "url": btn["url"], "style": styles[i % 3]}
                                        if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                                        temp_row.append(b_obj)
                                        if len(temp_row) == 2:
                                            kb.append(temp_row)
                                            temp_row = []
                                    if temp_row: kb.append(temp_row)
                                    send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                                    
                                owner_id = None
                                clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                
                                for uid, session_data in user_active_sessions.items():
                                    for act_num in session_data.get("nums", []):
                                        act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owner_id = uid
                                            break
                                    if owner_id: break
                                    
                                if not owner_id:
                                    for stex_n, n_owner in stex_assigned_numbers.items():
                                        clean_stex = str(stex_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if clean_stex == clean_api_num or (len(clean_stex) >= 8 and clean_stex.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_stex[-8:])):
                                            owner_id = n_owner
                                            break
                                        
                                if owner_id:
                                    lang_name = lang
                                    inbox_msg = render_body_text(f"{get_premium_flag_html_by_iso(iso)} {iso} | {prem_app_html} {display_num} | 💬 {lang}")
                                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "primary"}]]
                                    
                                    reward = get_otp_reward_for_user(num, owner_id)
                                    if reward > 0:
                                        update_balance(owner_id, reward)
                                        inbox_kb.append([{"text": f"Added {reward} tk", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "ignore", "style": "primary"}])
                                    
                                    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                    
                                    if db:
                                        try: 
                                            db.collection('users').document(str(owner_id)).update({"total_otps": Increment(1)})
                                            if owner_id in user_cache:
                                                user_cache[owner_id]["total_otps"] = user_cache[owner_id].get("total_otps", 0) + 1
                                        except: pass
                except: pass
        except: pass
        time.sleep(5)

def zenex_console_listener():
    global recent_traffic, bot_settings
    last_auto_update = time.time()
    zenex_last_hits = {} 
    
    while True:
        try:
            zenex_keys = bot_settings.get("zenex_keys", [])
            if zenex_keys:
                api_key = zenex_keys[0]
                headers = {"mapikey": api_key}
                res = requests.get(f"{ZENEX_BASE_URL}/v1/active-ranges", headers=headers, timeout=10)
                data = res.json()
                
                if data.get("success") and "data" in data and "active_ranges" in data["data"]:
                    current_time = time.time()
                    new_hits_added = False
                    
                    for hit in data["data"]["active_ranges"]:
                        range_str = str(hit.get("range", "")).replace("X", "").replace("x", "")
                        sid = str(hit.get("service", "Unknown")).upper()
                        hits_count = int(hit.get("hits", 1))
                        
                        if range_str:
                            char, iso = get_flag_and_code(range_str)
                            app_full_name, _ = get_service_info_html(sid, "")
                            
                            range_key = f"{range_str}_{app_full_name}"
                            prev_hits = zenex_last_hits.get(range_key, 0)
                            
                            if hits_count > prev_hits:
                                new_hits = hits_count - prev_hits
                            else:
                                new_hits = hits_count
                                
                            zenex_last_hits[range_key] = hits_count
                            if new_hits > 150: new_hits = 150
                            
                            for _ in range(new_hits):
                                recent_traffic.append({
                                    "service": app_full_name,
                                    "iso": iso,
                                    "flag": char,
                                    "number": f"{range_str}XXX", 
                                    "time": current_time,
                                    "real_range": range_str,
                                    "source": "zenex"
                                })
                                new_hits_added = True
                            
                    if new_hits_added:
                        recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                        save_local_db()
                        
                    if bot_settings.get("zenex_auto", False) and current_time - last_auto_update > 120:
                        last_auto_update = current_time
                        changed = False
                        
                        if "zenex_services" not in bot_settings: bot_settings["zenex_services"] = {}
                        if "zenex_search_countries" not in bot_settings: bot_settings["zenex_search_countries"] = []
                        
                        srv_counts = Counter(t["service"].upper() for t in recent_traffic if t.get("source") == "zenex" and "real_range" in t)
                        top_srvs = [s for s, c in srv_counts.most_common(6)]
                        
                        for srv in top_srvs:
                            if srv not in bot_settings["zenex_services"]:
                                bot_settings["zenex_services"][srv] = {}
                                changed = True
                                
                            iso_counts = Counter(t["iso"] for t in recent_traffic if t.get("service", "").upper() == srv and t.get("source") == "zenex" and "real_range" in t)
                            top_isos = [i for i, c in iso_counts.most_common(3)]
                            
                            for iso in top_isos:
                                full_country_name = get_flag_info_html(iso, return_full_name=True).title()
                                if full_country_name not in bot_settings["zenex_services"][srv]:
                                    bot_settings["zenex_services"][srv][full_country_name] = []
                                    changed = True
                                    
                                rng_counts = Counter(t["real_range"] for t in recent_traffic if t.get("service", "").upper() == srv and t.get("iso") == iso and t.get("source") == "zenex" and "real_range" in t)
                                top_rngs = [r for r, c in rng_counts.most_common(2)]
                                
                                for rng in top_rngs:
                                    if rng not in bot_settings["zenex_services"][srv][full_country_name]:
                                        bot_settings["zenex_services"][srv][full_country_name].append(rng)
                                        changed = True
                                        
                                    country_code = rng[:3]
                                    if country_code not in bot_settings["zenex_search_countries"]:
                                        bot_settings["zenex_search_countries"].append(country_code)
                                        changed = True

                        services_to_remove = []
                        for srv, countries in list(bot_settings["zenex_services"].items()):
                            srv_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and t.get("source") == "zenex" and "real_range" in t and current_time - t.get("time", 0) <= 120)
                            if srv_hit < 1:
                                services_to_remove.append(srv)
                                continue
                            
                            countries_to_remove = []
                            for country, ranges in list(countries.items()):
                                c_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and get_flag_info_html(t.get("iso"), return_full_name=True).title() == country and t.get("source") == "zenex" and "real_range" in t and current_time - t.get("time", 0) <= 120)
                                if c_hit < 1:
                                    countries_to_remove.append(country)
                                    continue
                                
                                ranges_to_remove = []
                                for rng in ranges:
                                    r_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and t.get("real_range") == rng and t.get("source") == "zenex" and current_time - t.get("time", 0) <= 120)
                                    if r_hit < 1: 
                                        ranges_to_remove.append(rng)
                                
                                for r in ranges_to_remove:
                                    ranges.remove(r)
                                    changed = True
                                    
                            for c in countries_to_remove:
                                del bot_settings["zenex_services"][srv][c]
                                changed = True
                                
                        for s in services_to_remove:
                            del bot_settings["zenex_services"][s]
                            changed = True
                            
                        if changed:
                            save_db()
                            
        except Exception as e:
            pass
        time.sleep(10)

def main():
    global BOT_USERNAME
    _start_zinipay_webhook_server()
    res = api_call("getMe")
    if res.get("ok"): BOT_USERNAME = res["result"]["username"]
    print(f"🤖 Bot is starting... @{BOT_USERNAME}")
    
    threading.Thread(target=panel_monitor_thread, daemon=True).start()
    threading.Thread(target=paid_otp_poller, daemon=True).start()
    threading.Thread(target=global_sms_listener, daemon=True).start()
    threading.Thread(target=stex_console_listener, daemon=True).start()
    threading.Thread(target=voltx_sms_listener, daemon=True).start()
    threading.Thread(target=voltx_console_listener, daemon=True).start()
    threading.Thread(target=zenex_sms_listener, daemon=True).start()
    threading.Thread(target=zenex_console_listener, daemon=True).start()
    print("📡 Background APIs & Global SMS Listener Started!")
    
    # 🌟 PRO-LEVEL FAST SYSTEM: 500 Workers Pool
    executor = ThreadPoolExecutor(max_workers=500)
    
    offset = None
    while True:
        try:
            updates = api_call(f"getUpdates?timeout=50&offset={offset}")
            if updates and "result" in updates:
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    if "message" in update: 
                        executor.submit(handle_message, update["message"])
                    elif "callback_query" in update: 
                        executor.submit(handle_callback, update["callback_query"])
        except Exception as e:
            time.sleep(2)

if __name__ == "__main__":
    main()    
