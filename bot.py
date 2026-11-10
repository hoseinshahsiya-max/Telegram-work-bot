from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime
import pytz
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

BOT_TOKEN = "9074050669:AAHKb-oe6el5PI9UM-c2B6OJkaj0GHGN1kE"
ALLOWED_USERS = ["hosein_shahsiah", "farhad_shahabifar", "masoud_haddadiii", "sinaa779"]
OWNER_USERNAME = "hosein_shahsiah"

DATA_FILE = "data.json"
tehran_tz = pytz.timezone('Asia/Tehran')

BTN_IN = "\U0001F7E2 \u062b\u0628\u062a \u0648\u0631\u0648\u062f"
BTN_OUT = "\U0001F534 \u062b\u0628\u062a \u062e\u0631\u0648\u062c"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

active_sessions = load_data()

def get_current_time():
    return datetime.now(tehran_tz)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.username is None or user.username.lower() not in [u.lower() for u in ALLOWED_USERS]:
        await update.message.reply_text("\u0634\u0645\u0627 \u0645\u062c\u0627\u0632 \u0628\u0647 \u0627\u0633\u062a\u0641\u0627\u062f\u0647 \u0646\u06cc\u0633\u062a\u06cc\u062f.")
        return

    keyboard = [[KeyboardButton(BTN_IN), KeyboardButton(BTN_OUT)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(text="\u2063", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message
    text = message.text
    username_lower = user.username.lower() if user.username else ""
    is_group = message.chat.type in ["group", "supergroup"]
    is_owner = (username_lower == OWNER_USERNAME.lower())

    if is_group and text not in [BTN_IN, BTN_OUT]:
        if not is_owner:
            try: await message.delete()
            except: pass
        return

    if text in [BTN_IN, BTN_OUT]:
        if username_lower not in [u.lower() for u in ALLOWED_USERS]:
            if is_group:
                try: await message.delete()
                except: pass
                await message.reply_text("\u0634\u0645\u0627 \u0645\u062c\u0627\u0632 \u0628\u0647 \u0627\u0633\u062a\u0641\u0627\u062f\u0647 \u0646\u06cc\u0633\u062a\u06cc\u062f.")
            return

        now = get_current_time()
        time_str = now.strftime("%H:%M")

        if text == BTN_IN:
            active_sessions[username_lower] = time_str
            save_data(active_sessions)
            msg = f"\U0001F4CC \u062b\u0628\u062a {user.first_name}: \u0648\u0631\u0648\u062f \u06a9\u0627\u0631\u06af\u0627\u0647 \u062f\u0631 \u0633\u0627\u0639\u062a {time_str}"
            await message.reply_text(msg)

        elif text == BTN_OUT:
            if username_lower in active_sessions:
                entry_time_str = active_sessions[username_lower]
                entry_dt = datetime.strptime(entry_time_str, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
                exit_dt = now
                
                duration = exit_dt - entry_dt
                total_seconds = int(duration.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                
                del active_sessions[username_lower]
                save_data(active_sessions)
                
                msg = (
                    f"\U0001F4CC \u062b\u0628\u062a {user.first_name}:\n"
                    f"\u0648\u0631\u0648\u062f: {entry_time_str}\n"
                    f"\u062e\u0631\u0648\u062c: {time_str}\n"
                    f"\u0645\u062f\u062a \u062d\u0636\u0648\u0631: {hours} \u0633\u0627\u0639\u062a \u0648 {minutes} \u062f\u0642\u06cc\u0642\u0647"
                )
                await message.reply_text(msg)
            else:
                msg = "\u26a0\ufe0f \u0634\u0645\u0627 \u0647\u0646\u0648\u0632 \u0648\u0631\u0648\u062f \u062e\u0648\u062f \u0631\u0627 \u062b\u0628\u062a \u0646\u06a9\u0631\u062f\u0647\u200c\u0627\u06cc\u062f!"
                await message.reply_text(msg)

# یک وب‌سرور ساده برای جلوگیری از خوابیدن Render
def keep_alive():
    class WebServer(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is alive!")
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), WebServer)
    server.serve_forever()

def main():
    threading.Thread(target=keep_alive, daemon=True).start()
    
    app = Application.builder() \
        .token(BOT_TOKEN) \
        .read_timeout(30) \
        .write_timeout(30) \
        .connect_timeout(30) \
        .pool_timeout(30) \
        .build()
        
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Robot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()