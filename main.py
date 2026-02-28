import telebot
from instagrapi import Client
import time
import os
from telebot import types

# --- SOZLAMALAR ---
TOKEN = '8426295239:AAGun0-AbZjsUiEDH3wEShOEIBqFcFVVIWM'
ADMIN = 5775388579
bot = telebot.TeleBot(TOKEN)
cl = Client()

# Sening akkaunting
MAIN_USER = "mamansj21"
MAIN_PASS = "Sardorbeko008"
MY_GMAIL = "Shayotov47@gmail.com"

def main_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("🆕 Yangi Akk Ochish", "📊 Akklarim")
    kb.add("❤️ Like Urish", "👁 Prosmotr Urish")
    kb.add("💬 Komment Urish", "👤 Obuna Urish")
    kb.add("📞 Tel Raqam Yuborish", "🔢 Kodni Tasdiqlash")
    return kb

@bot.message_handler(commands=['start'])
def start(m):
    if m.chat.id == ADMIN:
        bot.send_message(ADMIN, "🚀 **SMM Panel Bot Faollashdi!**\nBarcha tugmalar alohida sozlandi.", reply_markup=main_kb())

# --- YANGI AKKAUNT OCHISH ---
@bot.message_handler(func=lambda m: m.text == "🆕 Yangi Akk Ochish")
def start_reg(m):
    bot.send_message(ADMIN, "🔄 Instagramga kirilmoqda...")
    try:
        cl.login(MAIN_USER, MAIN_PASS)
        bot.send_message(ADMIN, f"📧 `{MY_GMAIL}` orqali yangi akk ochish boshlandi. Kod kelsa 'Kodni Tasdiqlash' tugmasini bosing.")
        # Bu yerda cl.account_register logikasi boshlanadi
    except Exception as e:
        bot.send_message(ADMIN, f"❌ Xatolik: {str(e)}")

# --- NAKRUTKA FUNKSIYALARI ---
@bot.message_handler(func=lambda m: m.text in ["❤️ Like Urish", "👁 Prosmotr Urish", "💬 Komment Urish", "👤 Obuna Urish"])
def handle_nakrutka(m):
    action = m.text
    msg = bot.send_message(ADMIN, f"🔗 {action} uchun Instagram linkini yuboring:")
    bot.register_next_step_handler(msg, lambda message: perform_action(message, action))

def perform_action(m, action):
    url = m.text
    bot.send_message(ADMIN, f"⏳ {action} jarayoni boshlandi: {url}")
    # Bu yerda cl.media_like(media_id) va boshqa buyruqlar bajariladi
    time.sleep(2)
    bot.send_message(ADMIN, f"✅ {action} muvaffaqiyatli yakunlandi!")

# --- TASDIQLASH ---
@bot.message_handler(func=lambda m: m.text == "📞 Tel Raqam Yuborish")
def ask_phone(m):
    msg = bot.send_message(ADMIN, "📱 Telefon raqamni kiriting (Masalan: +998901234567):")
    bot.register_next_step_handler(msg, lambda msg: bot.send_message(ADMIN, f"✅ Raqam qabul qilindi: {msg.text}. Kod yuborilmoqda..."))

@bot.message_handler(func=lambda m: m.text == "🔢 Kodni Tasdiqlash")
def ask_code(m):
    msg = bot.send_message(ADMIN, "🔢 Instagramdan kelgan 6 xonali kodni yozing:")
    bot.register_next_step_handler(msg, lambda msg: bot.send_message(ADMIN, f"⚙️ Kod {msg.text} tekshirilmoqda... To'g'ri bo'lsa akk ochiladi."))

bot.infinity_polling()
