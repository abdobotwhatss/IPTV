import os, re, telebot, urllib3
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from flask import Flask
from threading import Thread

urllib3.disable_warnings()

# --- CONFIG MN RAILWAY (Variables) ---
API_ID = 39719995
API_HASH = '8f9b2cf0583c4e31193ce318a0ef0e7a'
BOT_TOKEN = "8510274862:AAGkSIrvwONolWc_6gynRbQw1AUb_iMhUus"

# Jbed m3lomat mn Railway Variables
SESSION_STR = os.getenv("STRING_SESSION")
TARGET_BOT = os.getenv("TARGET_BOT") 

bot = telebot.TeleBot(BOT_TOKEN)
client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)

# --- WEB SERVER (Bach Railway i-bqa Healthy) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- FORWARDER LOGIC (Jassous) ---
@client.on(events.NewMessage())
async def handler(event):
    if not event.text: return
    # Jbed links dyal IPTV
    links = re.findall(r'(https?://[^\s]+)', event.text)
    iptv_links = [l for l in links if any(k in l.lower() for k in ["get.php", "username=", ".m3u"])]
    
    if iptv_links:
        for l in list(set(iptv_links)):
            try:
                # Sift l l-bot l-khezna li 7eti f Railway
                await client.send_message(TARGET_BOT, f"🛰️ **New link found:**\n📍 Source: `{event.chat.title or 'Private'}`\n━━━━━━━━━━━━━━━\n🔗 `{l}`")
                print(f"🎯 Forwarded to {TARGET_BOT}")
            except Exception as e:
                print(f"❌ Error sending: {e}")

if __name__ == "__main__":
    # 1. Ch3el l-Web Server f l-khfa
    Thread(target=run_web).start()
    
    # 2. Lansi l-UserBot
    print(f"[*] Starting UserBot... Target: {TARGET_BOT}")
    with client:
        client.run_until_disconnected()
