import telebot
from telebot import types
import sqlite3
import random
import os

# --- KONFIGURATSIYA ---
TOKEN = '8751050277:AAEIFn9G34tW0KNnGDUQJU599oHjwxj4Jig'
bot = telebot.TeleBot(TOKEN)

# BU SIZNING ID RAQAMINGIZ
ADMIN_ID = 5775388579 
ADMIN_USERNAME = "@Sardorbeko008"

# --- BAZA ---
def init_db():
    conn = sqlite3.connect('smm_pro_final.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, balance REAL DEFAULT 0, 
                       ref_count INTEGER DEFAULT 0, is_premium INTEGER DEFAULT 0, 
                       limit_count INTEGER DEFAULT 0, status TEXT DEFAULT 'active')''')
    conn.commit()
    conn.close()

init_db()

# --- KLAVIATURALAR ---
def get_main_keyboard(uid):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🛍 Onlayn do'kon", "🗂 Xizmatlar")
    
    # Faqat admin ruxsat berganlarga "Bot yaratish" tugmasi chiqadi
    conn = sqlite3.connect('smm_pro_final.db')
    cursor = conn.cursor()
    cursor.execute("SELECT is_premium FROM users WHERE user_id=?", (uid,))
    res = cursor.fetchone()
    if res and res[0] == 1:
        markup.add("🤖 Bot yaratish")
    
    markup.add("📊 Hisobim", "💰 Pul ishlash")
    markup.add("💳 Hisob to'ldirish", "☎️ Qo'llab - quvvatlash")
    return markup

# --- START ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    conn = sqlite3.connect('smm_pro_final.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    if not cursor.fetchone():
        ref_id = message.text.split()[1] if len(message.text.split()) > 1 else None
        if ref_id and int(ref_id) != uid:
            cursor.execute("UPDATE users SET balance = balance + 500, ref_count = ref_count + 1 WHERE user_id=?", (ref_id,))
            bot.send_message(ref_id, "💰 Yangi odam qo'shildi! +500 so'm.")
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (uid,))
        conn.commit()
    conn.close()
    bot.send_message(message.chat.id, f"👋 Salom! Smm botga xush kelibsiz!", reply_markup=get_main_keyboard(uid))

# --- BOT YARATISH (SIZ RUXSAT BERGANINGIZDAN KEYIN ISHLAYDI) ---
@bot.message_handler(func=lambda m: m.text == "🤖 Bot yaratish")
def create_own_bot(message):
    bot.send_message(message.chat.id, "✅ Sizda Premium ruxsat bor!\n\nBot yaratish uchun @BotFather ga kiring, tokenni oling va menga yuboring. Men uni tizimga ulayman.")

# --- ADMIN PANEL ---
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        m = types.ReplyKeyboardMarkup(resize_keyboard=True)
        m.add("🌟 Premium (Bot ochish) berish", "🎟 Limit berish")
        m.add("➕ Balans qo'shish", "📢 Xabar (Spam) yuborish")
        m.add("🚫 Block/Unblock", "🤖 Instagram Akk qo'shish")
        bot.send_message(message.chat.id, "👨‍✈️ **Admin Panel**\nBarcha boshqaruv sizda.", reply_markup=m)

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def admin_logic(message):
    if message.text == "🌟 Premium (Bot ochish) berish":
        msg = bot.send_message(message.chat.id, "Bot ochishga ruxsat beriladigan foydalanuvchi ID raqamini yozing:")
        bot.register_next_step_handler(msg, give_premium_access)
    
    elif message.text == "➕ Balans qo'shish":
        msg = bot.send_message(message.chat.id, "Format: `ID SUMMA` (Masalan: 6363659223 30000)")
        bot.register_next_step_handler(msg, add_money_admin)

def give_premium_access(message):
    target_id = message.text
    try:
        conn = sqlite3.connect('smm_pro_final.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_premium = 1 WHERE user_id=?", (target_id,))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f"✅ {target_id} ga Bot ochish ruxsati berildi.")
        bot.send_message(target_id, "🎉 **Xushxabar!** Admin sizga 'Bot yaratish' ruxsatini berdi. Menyuni tekshiring!", reply_markup=get_main_keyboard(int(target_id)))
    except:
        bot.send_message(message.chat.id, "❌ Xato. ID raqamni to'g'ri yozing.")

def add_money_admin(message):
    try:
        uid, cash = message.text.split()
        conn = sqlite3.connect('smm_pro_final.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (cash, uid))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f"✅ ID: {uid} ga {cash} so'm qo'shildi.")
        bot.send_message(uid, f"💳 Balansingiz admin tomonidan {cash} so'mga to'ldirildi.")
    except:
        bot.send_message(message.chat.id, "❌ Xato. Format: ID SUMMA")

# --- QOLGAN BO'LIMLAR ---
@bot.message_handler(func=lambda m: m.text == "📊 Hisobim")
def my_account(message):
    uid = message.from_user.id
    conn = sqlite3.connect('smm_pro_final.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance, ref_count FROM users WHERE user_id=?", (uid,))
    res = cursor.fetchone()
    conn.close()
    bot.send_message(message.chat.id, f"👤 **Ism:** {message.from_user.first_name}\n💰 **Balans:** {res[0]} so'm\n👥 **Takliflar:** {res[1]} ta", parse_mode="Markdown")

bot.infinity_polling()
