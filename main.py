import telebot
from telebot import types
import sqlite3
import threading
import time
import random
from instagrapi import Client
import os

# --- KONFIGURATSIYA ---
TOKEN = '8751050277:AAEIFn9G34tW0KNnGDUQJU599oHjwxj4Jig'
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

ADMIN_ID = 5775388579 
ADMIN_USERNAME = "@Sardorbeko008"
DB_NAME = 'smm_empire.db'

# --- BAZANI MUKAMMAL QURISH ---
def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    # Foydalanuvchilar jadvali
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, balance REAL DEFAULT 0, 
                       ref_count INTEGER DEFAULT 0, is_premium INTEGER DEFAULT 0, 
                       limit_count INTEGER DEFAULT 10, status TEXT DEFAULT 'active')''')
    # Multi-botlar jadvali
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_bots 
                      (owner_id INTEGER PRIMARY KEY, token TEXT, bot_username TEXT)''')
    # Instagram akkauntlari jadvali (Hujum uchun)
    cursor.execute('''CREATE TABLE IF NOT EXISTS insta_accs 
                      (username TEXT PRIMARY KEY, password TEXT, status TEXT DEFAULT 'live')''')
    conn.commit()
    conn.close()

init_db()

# --- INSTAGRAM AVTO-LOGIN TIZIMI ---
def get_insta_client(username, password):
    cl = Client()
    session_path = f"sessions/{username}.json"
    if not os.path.exists("sessions"): os.makedirs("sessions")
    
    try:
        if os.path.exists(session_path):
            cl.load_settings(session_path)
            cl.login(username, password)
        else:
            cl.login(username, password)
            cl.dump_settings(session_path)
        return cl
    except Exception as e:
        print(f"Login Error {username}: {e}")
        return None

# --- ASOSIY MENYU ---
def main_menu(uid):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT is_premium FROM users WHERE user_id=?", (uid,))
    res = cursor.fetchone()
    
    markup.add("🚀 SMM Hujum", "🛍 Onlayn do'kon")
    if res and res[0] == 1:
        markup.add("🤖 Mening Botim")
    markup.add("📊 Hisobim", "💰 Pul ishlash")
    markup.add("💳 Hisob to'ldirish", "☎️ Support")
    if uid == ADMIN_ID:
        markup.add("👨‍✈️ ADMIN PANEL")
    return markup

# --- MULTI-BOT PROCESSOR ---
def run_sub_bot(token, owner_id):
    try:
        sub_bot = telebot.TeleBot(token)
        @sub_bot.message_handler(commands=['start'])
        def sub_start(m):
            sub_bot.send_message(m.chat.id, f"<b>Xush kelibsiz!</b>\nBu bot @Sardorbeko008 tizimi orqali yaratildi.")
        sub_bot.infinity_polling()
    except: pass

# --- START ---
@bot.message_handler(commands=['start'])
def welcome(message):
    uid = message.from_user.id
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    if not cursor.fetchone():
        ref_id = message.text.split()[1] if len(message.text.split()) > 1 else None
        if ref_id and int(ref_id) != uid:
            cursor.execute("UPDATE users SET balance = balance + 500, ref_count = ref_count + 1 WHERE user_id=?", (ref_id,))
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (uid,))
        conn.commit()
    conn.close()
    bot.send_message(message.chat.id, "💎 <b>SMM EMPIRE BOT v5.0</b>\nEng kuchli Instagram avtomatizatsiyasi.", reply_markup=main_menu(uid))

# --- SMM HUJUM (LAYK/VIEW/FOLLOW) ---
@bot.message_handler(func=lambda m: m.text == "🚀 SMM Hujum")
def attack_start(message):
    msg = bot.send_message(message.chat.id, "🔗 <b>Instagram post/profil linkini yuboring:</b>")
    bot.register_next_step_handler(msg, perform_attack)

def perform_attack(message):
    url = message.text
    uid = message.from_user.id
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM insta_accs WHERE status='live'")
    accs = cursor.fetchall()
    conn.close()

    if not accs:
        bot.send_message(uid, "❌ Bazada ishchi akkauntlar yo'q! Admin akk qo'shishi kerak.")
        return

    status_msg = bot.send_message(uid, f"⚡ <b>Hujum boshlandi...</b>\nAkkauntlar soni: {len(accs)}")
    
    for acc in accs:
        def task():
            cl = get_insta_client(acc[0], acc[1])
            if cl:
                try:
                    media_id = cl.media_id(cl.media_pk_from_url(url))
                    cl.media_like(media_id)
                    cl.video_view(media_id)
                    print(f"Success: {acc[0]}")
                except: pass
        threading.Thread(target=task).start()

# --- ADMIN PANEL (MUKAMMAL) ---
@bot.message_handler(func=lambda m: m.text == "👨‍✈️ ADMIN PANEL" and m.from_user.id == ADMIN_ID)
def admin_p(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("➕ Akk Qo'shish", "🌟 Premium Berish", "💳 Balans To'ldirish", "📢 Global Spam", "🔙 Chiqish")
    bot.send_message(message.chat.id, "⚙️ <b>Boshqaruv tizimi:</b>", reply_markup=markup)

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def admin_logic(message):
    if message.text == "➕ Akk Qo'shish":
        msg = bot.send_message(message.chat.id, "Format: <code>user:pass</code>")
        bot.register_next_step_handler(msg, save_insta_acc)
    elif message.text == "🌟 Premium Berish":
        msg = bot.send_message(message.chat.id, "Foydalanuvchi ID:")
        bot.register_next_step_handler(msg, give_prem)

def save_insta_acc(message):
    try:
        data = message.text.split(":")
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO insta_accs (username, password) VALUES (?, ?)", (data[0], data[1]))
        conn.commit()
        conn.close()
        bot.send_message(ADMIN_ID, "✅ Akkaunt bazaga qo'shildi!")
    except:
        bot.send_message(ADMIN_ID, "❌ Xato! Format - user:pass")

def give_prem(message):
    uid = message.text
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_premium = 1 WHERE user_id=?", (uid,))
    conn.commit()
    conn.close()
    bot.send_message(ADMIN_ID, f"✅ {uid} premium bo'ldi.")
    bot.send_message(uid, "🌟 <b>Tabriklaymiz!</b> Sizda 'Mening Botim' bo'limi ochildi.", reply_markup=main_menu(int(uid)))

# --- BOTNI ISHGA TUSHIRISH ---
if __name__ == "__main__":
    print("Bot ishlamoqda...")
    bot.infinity_polling()
