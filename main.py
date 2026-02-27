import os
import sqlite3
import time
from collections import defaultdict
from telebot import TeleBot, types

# ================== CONFIG ==================
TOKEN = "8751050277:AAEIFn9G34tW0KNnGDUQJU599oHjwxj4Jig"
ADMIN_ID = 5775388579 

bot = TeleBot(TOKEN, parse_mode="HTML")
DB_NAME = "smm_v2.db"

# ================== DATABASE ==================
def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance REAL DEFAULT 0,
            ref_count INTEGER DEFAULT 0,
            is_premium INTEGER DEFAULT 0
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
    
    # Admin bo'lsa panel chiqadi
    if user_id == ADMIN_ID:
        markup.add("👨‍💻 Admin Panel")
    return markup

# ================== MESSAGES ==================
@bot.message_handler(commands=['start'])
def start_handler(message):
    uid = message.from_user.id
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (uid,))
    conn.commit()
    conn.close()
    
    bot.send_message(
        message.chat.id, 
        f"👋 Salom {message.from_user.first_name}!\n<b>Smm Bot</b> tizimiga xush kelibsiz.",
        reply_markup=main_menu(uid)
    )

# --- TUGMALARNI TUTIB OLISH (ASOSIY QISM) ---
@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    uid = message.from_user.id
    text = message.text

    if text == "📊 Hisobim":
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT balance, ref_count FROM users WHERE user_id=?", (uid,))
        res = cursor.fetchone()
        conn.close()
        bot.send_message(uid, f"👤 <b>Foydalanuvchi:</b> {message.from_user.first_name}\n💰 <b>Balans:</b> {res[0]} so'm\n👥 <b>Referal:</b> {res[1]} ta")

    elif text == "💰 Pul ishlash":
        link = f"https://t.me/{(bot.get_me()).username}?start={uid}"
        bot.send_message(uid, f"💵 Har bir taklif uchun 500 so'm!\n🔗 Havolangiz: <code>{link}</code>")

    elif text == "🛍 Onlayn do'kon":
        bot.send_message(uid, "🤖 <b>Bot ochish (30.000 so'm)</b>\nTo'lov uchun @Sardorbeko008 ga yozing.")

    elif text == "🗂 Xizmatlar":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Layk (15k)", callback_data="buy"),
                   types.InlineKeyboardButton("Ko'rish (15k)", callback_data="buy"))
        bot.send_message(uid, "🛠 Kerakli xizmatni tanlang:", reply_markup=markup)

    elif text == "👨‍💻 Admin Panel" and uid == ADMIN_ID:
        adm_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        adm_markup.add("➕ Balans qo'shish", "🌟 Premium berish", "🔙 Orqaga")
        bot.send_message(uid, "⚙️ Admin boshqaruv paneli:", reply_markup=adm_markup)

    elif text == "🔙 Orqaga":
        bot.send_message(uid, "Asosiy menyu", reply_markup=main_menu(uid))

# ================== RUN ==================
if __name__ == "__main__":
    print("BOT ISHLAMOQDA...")
    bot.infinity_polling()
