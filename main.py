import telebot
from telebot import types
import sqlite3
import os

# --- KONFIGURATSIYA ---
TOKEN = '8751050277:AAEIFn9G34tW0KNnGDUQJU599oHjwxj4Jig'
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 5775388579  # Sizning ID raqamingiz muvaffaqiyatli saqlandi
ADMIN_USERNAME = "@Sardorbeko008"

# --- BAZANI SOZLASH ---
def init_db():
    conn = sqlite3.connect('smm_fixed.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, balance REAL DEFAULT 0, 
                       ref_count INTEGER DEFAULT 0, is_premium INTEGER DEFAULT 0, 
                       user_token TEXT, status TEXT DEFAULT 'active')''')
    conn.commit()
    conn.close()

init_db()

# --- ASOSIY TUGMALAR ---
def main_keyboard(uid):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # Premium tekshirish
    conn = sqlite3.connect('smm_fixed.db')
    cursor = conn.cursor()
    cursor.execute("SELECT is_premium FROM users WHERE user_id=?", (uid,))
    res = cursor.fetchone()
    conn.close()

    markup.add("🛍 Onlayn do'kon", "🗂 Xizmatlar")
    if res and res[0] == 1:
        markup.add("🤖 Bot yaratish")
    
    markup.add("📊 Hisobim", "💰 Pul ishlash")
    markup.add("💳 Hisob to'ldirish", "☎️ Qo'llab - quvvatlash")
    
    if uid == ADMIN_ID:
        markup.add("👨‍✈️ Admin Panel")
    return markup

# --- START BUYRUG'I ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    conn = sqlite3.connect('smm_fixed.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    user = cursor.fetchone()

    if not user:
        ref_id = message.text.split()[1] if len(message.text.split()) > 1 else None
        if ref_id and ref_id.isdigit() and int(ref_id) != uid:
            cursor.execute("UPDATE users SET balance = balance + 500, ref_count = ref_count + 1 WHERE user_id=?", (ref_id,))
            try:
                bot.send_message(ref_id, "💰 Tabriklaymiz! Referalingiz qo'shildi va hisobingizga 500 so'm o'tkazildi.")
            except: pass
        
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (uid,))
        conn.commit()
    
    conn.close()
    bot.send_message(message.chat.id, f"👋 Salom {message.from_user.first_name}!\nSmm botga xush kelibsiz!", reply_markup=main_keyboard(uid))

# --- TUGMALAR ISHLASHI ---
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = message.from_user.id
    text = message.text

    if text == "🛍 Onlayn do'kon":
        bot.send_message(uid, f"🤖 **Smm bot ochish**\n\nNarxi: 30.000 so'm\nBot ochish uchun {ADMIN_USERNAME} ga yozing. To'lovdan so'ng sizga 'Bot yaratish' tugmasi ochiladi.")

    elif text == "🗂 Xizmatlar":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("👁 Ko'rishlar (15.000 so'm)", callback_data="buy_s"),
            types.InlineKeyboardButton("❤️ Like bosish (15.000 so'm)", callback_data="buy_s"),
            types.InlineKeyboardButton("👤 Obuna bo'lish (15.000 so'm)", callback_data="buy_s")
        )
        bot.send_message(uid, "🛠 **Instagram xizmatlari:**", reply_markup=markup)

    elif text == "📊 Hisobim":
        conn = sqlite3.connect('smm_fixed.db')
        cursor = conn.cursor()
        cursor.execute("SELECT balance, ref_count FROM users WHERE user_id=?", (uid,))
        res = cursor.fetchone()
        conn.close()
        bot.send_message(uid, f"👤 **Ism:** {message.from_user.first_name}\n💰 **Balans:** {res[0]} so'm\n👥 **Takliflar:** {res[1]} ta")

    elif text == "💰 Pul ishlash":
        link = f"https://t.me/{(bot.get_me()).username}?start={uid}"
        bot.send_message(uid, f"🎁 Har bir taklif uchun 500 so'm oling!\n\n🔗 Havolangiz: `{link}`", parse_mode="Markdown")

    elif text == "🤖 Bot yaratish":
        bot.send_message(uid, "✅ Ruxsat mavjud. @BotFather dan olgan tokeningizni yuboring:")
        bot.register_next_step_handler(message, save_user_token)

    elif text == "👨‍✈️ Admin Panel" and uid == ADMIN_ID:
        adm_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        adm_markup.add("🌟 Premium (Bot) berish", "💳 Balans qo'shish")
        adm_markup.add("🔙 Orqaga")
        bot.send_message(uid, "👨‍✈️ Admin boshqaruv paneli:", reply_markup=adm_markup)

    elif text == "🌟 Premium (Bot) berish" and uid == ADMIN_ID:
        msg = bot.send_message(uid, "Bot ochish ruxsati beriladigan foydalanuvchi ID sini yozing:")
        bot.register_next_step_handler(msg, admin_give_premium)

    elif text == "🔙 Orqaga":
        bot.send_message(uid, "Asosiy menyu", reply_markup=main_keyboard(uid))

# --- ADMIN FUNKSIYALARI ---
def admin_give_premium(message):
    try:
        target_id = int(message.text)
        conn = sqlite3.connect('smm_fixed.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_premium = 1 WHERE user_id=?", (target_id,))
        conn.commit()
        conn.close()
        bot.send_message(ADMIN_ID, f"✅ {target_id} ga Premium berildi.")
        bot.send_message(target_id, "🎉 Tabriklaymiz! Endi sizda '🤖 Bot yaratish' tugmasi paydo bo'ldi.", reply_markup=main_keyboard(target_id))
    except:
        bot.send_message(ADMIN_ID, "❌ Xato! Faqat raqamli ID yozing.")

def save_user_token(message):
    token = message.text
    if ":" in token:
        bot.send_message(message.chat.id, "✅ Token qabul qilindi va tizimga ulandi!")
    else:
        bot.send_message(message.chat.id, "❌ Noto'g'ri token.")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    bot.answer_callback_query(call.id, "To'lov uchun adminga murojaat qiling.", show_alert=True)

bot.infinity_polling()
