import os, re, telebot, urllib3
from curl_cffi import requests
from datetime import datetime
from flask import Flask
from threading import Thread

urllib3.disable_warnings()

# --- CONFIG ---
BOT_TOKEN = "8510274862:AAGkSIrvwONolWc_6gynRbQw1AUb_iMhUus"
bot = telebot.TeleBot(BOT_TOKEN)

# L-klmat dyal l-aflam o l-mosalsalat bach n-7iydouhoum mn l-list
VOD_KEYWORDS = ["MOVIE", "FILM", "SERIE", "VOD", "NETFLIX", "CINEMA", "4K RELAX", "V.O.D", "SEASON"]

# --- WEB SERVER (Bach Railway may-seddch l-bot) ---
app = Flask('')
@app.route('/')
def home(): return "Checker Bot is Online!"
def run_web(): 
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- CHECKER LOGIC ---
def get_live_folders(api_url):
    """Kiy-jbed gha l-folders dyal Live TV o kiy-zwaq-houm"""
    try:
        r = requests.get(f"{api_url}&action=get_live_categories", impersonate="chrome110", timeout=10, verify=False).json()
        if isinstance(r, list):
            # Khlli gha l-folders li ma-fihomch kelmet Movie/Serie
            live_only = [c['category_name'] for c in r if not any(k in c['category_name'].upper() for k in VOD_KEYWORDS)]
            # Zwaq l-folders b emojis o khod max 25 folder
            formatted_cats = ""
            for i, name in enumerate(live_only[:25], 1):
                formatted_cats += f"  {i:02d} ➔ 📁 {name}\n"
            return formatted_cats, len(live_only)
    except: pass
    return "None", 0

def check_link(url):
    try:
        match = re.search(r'(https?://[^/:]+[:\d]*).*username=([^& \n]+)&password=([^& \n]+)', url)
        if not match: return None
        
        base, user, pw = match.groups()
        api_url = f"{base}/player_api.php?username={user}&password={pw}"
        
        # Requete l l-API (Bypass l-block b Chrome)
        r = requests.get(api_url, impersonate="chrome110", timeout=15, verify=False).json()
        u = r.get('user_info', {})
        
        if u.get('auth') == 1:
            # Jbed Expiry
            exp = u.get('exp_date')
            expiry = datetime.fromtimestamp(int(exp)).strftime('%d/%m/%Y') if exp and exp != "null" else "Unlimited"
            
            # Jbed l-Folders dyal Live TV
            folders_str, folders_count = get_live_folders(api_url)
            
            msg = (
                f"💎 **IPTV CHECKER HIT** 💎\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 **User:** `{user}`\n"
                f"🔑 **Pass:** `{pw}`\n"
                f"⏳ **Expiry:** `{expiry}`\n"
                f"🚀 **Conn:** `{u.get('active_cons', '0')}/{u.get('max_connections', '0')}`\n"
                f"📊 **Status:** `{u.get('status', 'Active').upper()}`\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📺 **LIVE TV FOLDERS [{folders_count}]**\n"
                f"{folders_str}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🌐 **Host:** {base}\n"
                f"🔗 **M3U:** `{url}`"
            )
            return msg
        return None
    except: return None

# --- BOT COMMANDS ---
@bot.message_handler(commands=['start'])
def welcome(m):
    bot.reply_to(m, "🦁 **IPTV CHECKER BOT**\n\nSift ayye link Xtream (fih user o pass) o ghan-jbed lik l-Expiry o l-Folders dyal l-Live TV!")

@bot.message_handler(content_types=['text'])
def handle_msg(m):
    text = m.text
    urls = re.findall(r'(https?://[^\s]+)', text)
    if not urls: return

    bot.send_chat_action(m.chat.id, 'typing')
    found = False
    
    for u in list(set(urls)):
        if "username=" in u.lower():
            res = check_link(u)
            if res:
                # Ila l-message twil bzaf 3la Telegram, n-qsmouh
                if len(res) > 4000: bot.send_message(m.chat.id, res[:4000], parse_mode="Markdown")
                else: bot.send_message(m.chat.id, res, parse_mode="Markdown")
                found = True
    
    if not found:
        bot.reply_to(m, "❌ L-Link DEAD oula m-bloqui.")

if __name__ == "__main__":
    Thread(target=run_web).start()
    print("[*] Checker Bot is Running...")
    bot.polling(none_stop=True)
