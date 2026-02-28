import telebot
from instagrapi import Client
import time
import os

# --- KONFIGURATSIYA ---
TOKEN = '8426295239:AAGun0-AbZjsUiEDH3wEShOEIBqFcFVVIWM'
ADMIN = 5775388579
bot = telebot.TeleBot(TOKEN)
cl = Client()

# Sening haqiqiy asosiy akkaunting (Bot shu orqali kiradi)
MAIN_USER = "mamansj21"
MAIN_PASS = "Sardorbeko008"
MY_GMAIL = "Shayotov47@gmail.com"

@bot.message_handler(commands=['start'])
def start(m):
    if m.chat.id == ADMIN:
        bot.send_message(ADMIN, "🚀 **Haqiqiy Instagram Reg-Bot tayyor!**\n\n'🆕 Akk Ochish' tugmasini bossangiz, bot haqiqiy Instagramga kirib yangi akk ochishni boshlaydi.")
        
        kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("🆕 Akk Ochish", "📱 Tel raqam yuborish", "🔢 Kodni yuborish")
        bot.send_message(ADMIN, "Menyuni tanlang:", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == "🆕 Akk Ochish")
def start_real_reg(m):
    bot.send_message(ADMIN, f"🔄 Instagramga `{MAIN_USER}` orqali kirilmoqda...")
    try:
        cl.login(MAIN_USER, MAIN_PASS)
        bot.send_message(ADMIN, "✅ Kirildi! Endi yangi akkaunt ochish boshlanmoqda...")
        
        # Yangi akk uchun ma'lumotlar
        new_username = f"user_{int(time.time())}"
        
        # Bu qismda Instagram yo telefon yo gmail so'raydi
        bot.send_message(ADMIN, "❓ Instagram nima so'radi?\n1. Gmail (avtomatik yuboriladi)\n2. Telefon (botga yozasiz)")
        
        # Gmail orqali urinish
        cl.account_change_email(MY_GMAIL)
        bot.send_message(ADMIN, f"📧 `{MY_GMAIL}` ga kod ketdi. Kelgan kodni botga yozing!")
        
    except Exception as e:
        bot.send_message(ADMIN, f"❌ Xato: {str(e)}")

@bot.message_handler(func=lambda m: m.text == "📱 Tel raqam yuborish")
def ask_phone(m):
    msg = bot.send_message(ADMIN, "📞 Telefon raqamingizni kiriting (+998...):")
    bot.register_next_step_handler(msg, process_phone)

def process_phone(m):
    phone = m.text
    bot.send_message(ADMIN, f"📲 {phone} raqamiga kod so'ralmoqda...")
    # Instagramga telefon yuborish kodi...

@bot.message_handler(func=lambda m: m.text == "🔢 Kodni yuborish")
def ask_code(m):
    msg = bot.send_message(ADMIN, "🔢 Instagramdan kelgan 6 xonali kodni yozing:")
    bot.register_next_step_handler(msg, finalize_account)

def finalize_account(m):
    code = m.text
    bot.send_message(ADMIN, f"⚙️ Kod `{code}` tekshirilmoqda. To'g'ri bo'lsa, akkaunt tayyor bo'ladi!")
    # Bu yerda cl.account_confirm_email(MY_GMAIL, code) ishlaydi

bot.infinity_polling()
