import telebot
from telebot import types
import sqlite3
import os

# --- KONFIGURATSIYA ---
TOKEN = '8751050277:AAEIFn9G34tW0KNnGDUQJU599oHjwxj4Jig'
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 6363659223 
ADMIN_USERNAME = "@Sardorbeko008"

# --- BAZANI SOZLASH ---
def init_db():
    conn = sqlite3.connect('smm_final.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, balance REAL DEFAULT 0, 
                       ref_count INTEGER DEFAULT 0, is_premium INTEGER DEFAULT 0, 
                       user_token TEXT, status TEXT DEFAULT 'active')''')
    conn.commit()
    conn.close()

init_db()

# --- TUGMALAR ---
def main_keyboard(uid):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🛍 Onlayn do'kon", "🗂 Xizmatlar")
    
    # Premium bo'lsa "Botni sozlash" tugmasi chiqadi
    conn = sqlite3.connect('smm_final.db')
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
    conn = sqlite3.connect('smm_final.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    if not cursor.fetchone():
        ref_id = message.text.split()[1] if len(message.text.split()) > 1 else None
        if ref_id and int(ref_id) != uid:
            cursor.execute("UPDATE users SET balance = balance + 500, ref_count = ref_count + 1 WHERE user_id=?", (ref_id,))
            bot.send_message(ref_id, "💰 Do'stingiz qo'shildi! +500 so'm.")
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (uid,))
        conn.commit()
    conn.close()
    bot.send_message(message.chat.id, "👋 Smm botga xush kelibsiz!", reply_markup=main_keyboard(uid))

# --- BOT YARATISH (FAQAT PREMIUM UCHUN) ---
@bot.message_handler(func=lambda m: m.text == "🤖 Bot yaratish")
def create_bot(message):
    bot.send_message(message.chat.id, "✅ Sizda ruxsat bor!\nBot ochish uchun @BotFather ga kiring, /newbot buyrug'ini bering va olgan API TOKENingizni shu yerga yuboring:")
    bot.register_next_step_handler(message, save_token)

def save_token(message):
    token = message.text
    if ":" in token and len(token) > 20:
        conn = sqlite3.connect('smm_final.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET user_token = ? WHERE user_id=?", (token, message.from_user.id))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, "🎉 Bot muvaffaqiyatli ulandi! Endi sizning botingiz ham bizning panel orqali ishlaydi.")
    else:
        bot.send_message(message.chat.id, "❌ Noto'g'ri token yubordingiz.")

# --- ADMIN PANEL ---
@bot.message_handler(commands=['admin'])
def admin(message):
    if message.from_user.id == ADMIN_ID:
        m = types.ReplyKeyboardMarkup(resize_keyboard=True)
        m.add("🌟 Premium berish (Bot ochish)", "💳 Balans qo'shish")
        m.add("📢 Xabar yuborish", "🔙 Chiqish")
        bot.send_message(message.chat.id, "👨‍✈️ Admin Panel", reply_markup=m)

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def admin_logic(message):
    if message.text == "🌟 Premium berish (Bot ochish)":
        msg = bot.send_message(message.chat.id, "Bot ochishga ruxsat beriladigan foydalanuvchi ID sini yozing:")
        bot.register_next_step_handler(msg, give_premium)

def give_premium(message):
    uid = message.text
    conn = sqlite3.connect('smm_final.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_premium = 1 WHERE user_id=?", (uid,))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, f"✅ {uid} ga bot ochish ruxsati berildi.")
    bot.send_message(uid, "🎉 Tabriklaymiz! Admin sizga bot yaratish huquqini berdi. Endi menyuda '🤖 Bot yaratish' tugmasi chiqdi!", reply_markup=main_keyboard(int(uid)))

# --- QOLGAN FUNKSIYALAR ---
@bot.message_handler(func=lambda m: m.text == "📊 Hisobim")
def my_acc(message):
    conn = sqlite3.connect('smm_final.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance, ref_count FROM users WHERE user_id=?", (message.from_user.id,))
    res = cursor.fetchone()
    conn.close()
    bot.send_message(message.chat.id, f"👤 Ism: {message.from_user.first_name}\n💰 Balans: {res[0]} so'm\n👥 Takliflar: {res[1]} ta")

bot.infinity_polling()
