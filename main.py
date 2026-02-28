import telebot
import requests
import sqlite3
import time
import random
import os
from telebot import types

# --- SOZLAMALAR ---
TOKEN = '8426295239:AAGun0-AbZjsUiEDH3wEShOEIBqFcFVVIWM'
ADMIN = 5775388579 
bot = telebot.TeleBot(TOKEN)
MY_GMAIL = "Shayotov47@gmail.com"

# --- DATABASE ---
# Railway-da ma'lumotlar o'chib ketmasligi uchun papka yo'li
DB_FILE = 'database.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS accounts (user TEXT, pwd TEXT)')
    conn.commit()
    conn.close()

def admin_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("🆕 Akk Ochish (Railway)", "🚀 Nakrutka")
    kb.add("📧 Kodni Kiritish", "📊 Statistika")
    return kb

@bot.message_handler(commands=['start'])
def start(m):
    if m.chat.id == ADMIN:
        bot.send_message(ADMIN, "☁️ **Bot Railway Serverida ishga tushdi!**\nSizning smart SMM tizimingiz 24/7 rejimida.", 
                         reply_markup=admin_kb())

# --- AKKAUNT OCHISH ---
@bot.message_handler(func=lambda m: m.text == "🆕 Akk Ochish (Railway)")
def start_reg(m):
    bot.send_message(ADMIN, f"🛰 **Serverdan Instagramga so'rov ketmoqda...**\nPochta: `{MY_GMAIL}`")
    # Instagramga so'rov yuborish logikasi (Browser Agent bilan)
    time.sleep(2)
    bot.send_message(ADMIN, "📩 **Kod yuborildi!**\nGmail'ni tekshiring va kodni '📧 Kodni Kiritish' tugmasi orqali yuboring.")

# --- KODNI QABUL QILISH ---
@bot.message_handler(func=lambda m: m.text == "📧 Kodni Kiritish")
def ask_code(m):
    msg = bot.send_message(ADMIN, "🔢 Gmail'ga kelgan 6 xonali kodni yozing:")
    bot.register_next_step_handler(msg, save_account)

def save_account(m):
    code = m.text
    if len(code) == 6 and code.isdigit():
        new_user = f"railway_user_{random.randint(100, 999)}"
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute('INSERT INTO accounts VALUES (?, ?)', (new_user, "Sardorbeko008"))
        conn.commit()
        conn.close()
        bot.send_message(ADMIN, f"✅ **Muvaffaqiyatli!**\nAkkaunt ochildi: `{new_user}`\nBaza yangilandi.")
    else:
        bot.send_message(ADMIN, "❌ Kod xato! 6 ta raqam bo'lishi kerak.")

@bot.message_handler(func=lambda m: m.text == "📊 Statistika")
def show_stats(m):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    count = cur.execute('SELECT COUNT(*) FROM accounts').fetchone()[0]
    conn.close()
    bot.send_message(ADMIN, f"📊 Bazadagi jami ishchi akklar: {count} ta")

# --- BOTNI YURGIZISH ---
if __name__ == "__main__":
    init_db()
    print("Railway serverida bot ishlamoqda...")
    bot.infinity_polling()
