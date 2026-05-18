import os, re, telebot, urllib3
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from curl_cffi import requests
from datetime import datetime
from flask import Flask
from threading import Thread

urllib3.disable_warnings()

# --- CONFIGURATION (Railway Variables) ---
API_ID = 39719995
API_HASH = '8f9b2cf0583c4e31193ce318a0ef0e7a'
BOT_TOKEN = "8510274862:AAGkSIrvwONolWc_6gynRbQw1AUb_iMhUus"
TARGET_BOT = os.getenv("TARGET_BOT")
STORAGE_BOT = "@CheckerM3U_bot" # <-- Beddelha

bot = telebot.TeleBot(BOT_TOKEN)
client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

# --- WEB SERVER (For Health Check) ---
app = Flask('')
@app.route('/')
def home(): return "Healthy"
def run_web(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# --- CHECKER LOGIC ---
def check_iptv(url):
    try:
        match = re.search(r'(https?://[^/:]+[:\d]*).*username=([^& \n]+)&password=([^& \n]+)', url)
        if not match: return None
        base, user, pw = match.groups()
        api = f"{base}/player_api.php?username={user}&password={pw}"
        r = requests.get(api, impersonate="chrome110", timeout=12, verify=False).json()
        if r.get('user_info', {}).get('auth') == 1:
            exp = r['user_info'].get('exp_date')
            expiry = datetime.fromtimestamp(int(exp)).strftime('%d/%m/%Y') if exp and exp != "null" else "Unlimited"
            return f"✅ **HIT:** `{user}` | **Exp:** `{expiry}`\n🔗 `{url}|User-Agent=VLC/3.0.18`"
    except: pass
    return None

# --- FORWARDER LOGIC ---
@client.on(events.NewMessage())
async def handler(event):
    if not event.text: return
    links = re.findall(r'(https?://[^\s]+)', event.text)
    iptv_links = [l for l in links if "username=" in l.lower()]
    if iptv_links:
        for l in list(set(iptv_links)):
            await client.send_message(STORAGE_BOT, f"🛰️ **New link found:**\n`{l}`")

if __name__ == "__main__":
    Thread(target=run_web).start()
    print("[*] UserBot & Web Server starting...")
    client.start()
    client.run_until_disconnected()
