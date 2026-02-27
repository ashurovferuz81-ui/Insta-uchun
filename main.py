import os
import sqlite3
import time
import threading
from collections import defaultdict
from telebot import TeleBot, types
from instagrapi import Client

# ================== CONFIG ==================
# Railway yoki VPS uchun o'zgaruvchilarni oling
TOKEN = "8751050277:AAEIFn9G34tW0KNnGDUQJU599oHjwxj4Jig" # O'zingizni tokeningizni qo'ying
ADMIN_ID = 5775388579 # Sizning ID raqamingiz

bot = TeleBot(TOKEN, parse_mode="HTML")
DB_NAME = "smm_ultra.db"

# ================== RATE LIMIT ==================
user_last_request = defaultdict(int)

def rate_limit(user_id, delay=2):
    if time.time() - user_last_request[user_id] < delay:
        return False
    user_last_request[user_id] = time.time()
    return True

# ================== DATABASE ==================
def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    # Foydalanuvchilar
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance REAL DEFAULT 0,
            ref_count INTEGER DEFAULT 0,
            is_premium INTEGER DEFAULT 0,
            user_token TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Instagram akklar
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS insta_accounts (
            username TEXT PRIMARY KEY,
            password TEXT,
            status TEXT,
            last_checked TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ================== KEYBOARDS ==================
def main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📊 Hisobim", "💰 Pul ishlash")
    markup.add("🛍 Onlayn do'kon", "🗂 Xizmatlar")
    
    # Premium bo'lsa bot yaratish tugmasi chiqadi
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT is_premium FROM users WHERE user_id=?", (user_id,))
    res = cursor.fetchone()
    if res and res[0] == 1:
        markup.add("🤖 Bot yaratish")

    if user_id == ADMIN_ID:
        markup.add("👨‍💻 Admin Panel")

    return markup

# ================== START & REFERRAL ==================
@bot.message_handler(commands=['start'])
def start_handler(message):
    uid = message.from_user.id
    if not rate_limit(uid): return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id=?", (uid,))
    if not cursor.fetchone():
        # Referal tekshirish
        ref_id = message.text.split()[1] if len(message.text.split()) > 1 else None
        if ref_id and ref_id.isdigit() and int(ref_id) != uid:
            cursor.execute("UPDATE users SET balance = balance + 500, ref_count = ref_count + 1 WHERE user_id=?", (ref_id,))
            try: bot.send_message(ref_id, "🎉 Sizda yangi referal! +500 so'm qo'shildi.")
            except: pass
        
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (uid,))
        conn.commit()
    conn.close()

    bot.send_message(
        message.chat.id,
        f"🚀 <b>SMM ULTRA BOT</b>\nSalom {message.from_user.first_name}! Xush kelibsiz.",
        reply_markup=main_menu(uid)
    )

# ================== ACCOUNT INFO ==================
@bot.message_handler(func=lambda m: m.text == "📊 Hisobim")
def account_info(message):
    uid = message.from_user.id
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT balance, ref_count, is_premium FROM users WHERE user_id=?", (uid,))
    data = cursor.fetchone()
    conn.close()

    text = (f"👤 <b>Ism:</b> {message.from_user.first_name}\n"
            f"🆔 <b>ID:</b> <code>{uid}</code>\n"
            f"💰 <b>Balans:</b> {data[0]} so'm\n"
            f"👥 <b>Referallar:</b> {data[1]} ta\n"
            f"🌟 <b>Premium:</b> {'Faol ✅' if data[2] else 'Ochiq emas ❌'}")
    bot.send_message(uid, text)

# ================== EARN MONEY ==================
@bot.message_handler(func=lambda m: m.text == "💰 Pul ishlash")
def earn_money(message):
    uid = message.from_user.id
    ref_link = f"https://t.me/{(bot.get_me()).username}?start={uid}"
    bot.send_message(uid, f"🎁 <b>Do'stlarni taklif qiling!</b>\n\nHar bir do'st uchun 500 so'm beriladi.\n\n🔗 Havolangiz:\n<code>{ref_link}</code>")

# ================== ADMIN ACTIONS ==================
@bot.message_handler(func=lambda m: m.text == "👨‍💻 Admin Panel" and m.from_user.id == ADMIN_ID)
def admin_panel(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🌟 Premium Berish", "💳 Balans Qo'shish")
    markup.add("📂 Akklar Ro'yxati", "🔙 Orqaga")
    bot.send_message(message.chat.id, "🛠 <b>Admin Panel</b>", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🌟 Premium Berish" and m.from_user.id == ADMIN_ID)
def prem_give(message):
    msg = bot.send_message(message.chat.id, "Premium (Bot ochish) berish uchun foydalanuvchi ID yozing:")
    bot.register_next_step_handler(msg, process_prem)

def process_prem(message):
    try:
        uid = int(message.text)
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_premium = 1 WHERE user_id=?", (uid,))
        conn.commit()
        conn.close()
        bot.send_message(ADMIN_ID, "✅ Premium berildi.")
        bot.send_message(uid, "🎉 <b>Tabriklaymiz!</b> Admin sizga bot yaratish ruxsatini berdi.", reply_markup=main_menu(uid))
    except: bot.send_message(ADMIN_ID, "❌ Xato ID.")

# ================== RUN ==================
if __name__ == "__main__":
    print("SMM ULTRA BOT ISHGA TUSHDI...")
    bot.infinity_polling()
