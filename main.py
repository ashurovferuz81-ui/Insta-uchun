import telebot
from telebot import types
from instagrapi import Client
import time
import random
import os

# --- SOZLAMALAR ---
TOKEN = '8751050277:AAEIFn9G34tW0KNnGDUQJU599oHjwxj4Jig'
bot = telebot.TeleBot(TOKEN)

PASSWORD = "Sardorbeko008"
GMAIL = "Shayotov47@gmail.com"

# SIZNING 16 TA TERMUX AKKAUNTINGIZ
REAL_ACCOUNTS = [
    "mahallaku0", "akkauntimmi3", "futbolme0120", "mamansj21", 
    "neamidk", "maylimijonim", "kino.com", "temurbek.m912", 
    "uzbm.malo", "likewisek.448", "sadkmi0", "uzb.mrek", 
    "ahmad_uzb0", "sarik008202"
]

# Sessiya saqlash uchun papka (Instagram blokidan qochish uchun)
if not os.path.exists("sessions"):
    os.makedirs("sessions")

def get_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(f"📂 Tayyor akklar ({len(REAL_ACCOUNTS)} ta)", callback_data="list"),
        types.InlineKeyboardButton("➕ Yangi haqiqiy akk ochish", callback_data="reg"),
        types.InlineKeyboardButton("🚀 Hujum (Like/View/Fol/Com)", callback_data="go")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "💎 **Instagram Real-Action Bot**\nRailway serverida ishga tushdi.", 
                     reply_markup=get_menu(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def calls(call):
    if call.data == "list":
        bot.send_message(call.message.chat.id, "📋 **Akklar:**\n" + "\n".join([f"• `{a}`" for a in REAL_ACCOUNTS]), parse_mode="Markdown")
    
    elif call.data == "reg":
        cl = Client()
        user = "uzb_" + "".join(random.choices("abcdef", k=5)) + str(random.randint(10,99))
        bot.send_message(call.message.chat.id, f"🔄 `{user}` uchun Instagramga kod yuborilmoqda...", parse_mode="Markdown")
        try:
            if cl.account_register_email_send_verification_code(GMAIL):
                msg = bot.send_message(call.message.chat.id, f"📩 {GMAIL} ga kod bordi. Kiriting:")
                bot.register_next_step_handler(msg, finish_reg, cl, user)
            else:
                bot.send_message(call.message.chat.id, "❌ Instagram hozircha kod bermadi (IP blok).")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"⚠️ Xato: {str(e)}")

    elif call.data == "go":
        msg = bot.send_message(call.message.chat.id, "🔗 Post linkini yuboring:")
        bot.register_next_step_handler(msg, run_attack)

def finish_reg(message, cl, user):
    code = message.text.strip()
    try:
        cl.account_register_email_verify_code(GMAIL, code, user, PASSWORD, user)
        REAL_ACCOUNTS.append(user)
        bot.send_message(message.chat.id, f"✅ Akkaunt ochildi: `{user}`")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ochib bo'lmadi: {str(e)}")

def run_attack(message):
    url = message.text
    status = bot.send_message(message.chat.id, "🚀 Hujum boshlandi...")
    success = 0
    
    for user in REAL_ACCOUNTS:
        cl = Client()
        sess_path = f"sessions/{user}.json"
        try:
            # Sessiya yuklash yoki Login
            if os.path.exists(sess_path):
                cl.load_settings(sess_path)
                cl.login(user, PASSWORD)
            else:
                cl.login(user, PASSWORD)
                cl.dump_settings(sess_path)

            media_pk = cl.media_pk_from_url(url)
            cl.video_view(cl.media_id(media_pk)) # View
            cl.media_like(media_pk) # Like
            cl.media_comment(media_pk, random.choice(["🔥🔥🔥", "Gap yo'q", "👍👍", "Zo'r", "Omad!"]))
            
            success += 1
            cl.logout()
            time.sleep(random.randint(5, 10)) # Instagram sezib qolmasin
        except:
            continue
            
    bot.send_message(message.chat.id, f"🏁 **Natija:**\n✅ {success} ta akkaunt amallarni bajardi!", reply_markup=get_menu())

bot.infinity_polling()
