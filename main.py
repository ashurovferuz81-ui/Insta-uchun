import telebot
from telebot import types
from instagrapi import Client
import time
import random
import logging
import os

# Railway logs bo'limida jarayonni kuzatish uchun
logging.basicConfig(level=logging.INFO)

# --- KONFIGURATSIYA ---
TOKEN = '8751050277:AAEIFn9G34tW0KNnGDUQJU599oHjwxj4Jig'
bot = telebot.TeleBot(TOKEN)

PASSWORD = "Sardorbeko008"

# SIZNING AKKAUNTLARINGIZ
REAL_ACCOUNTS = [
    "mahallaku0", "akkauntimmi3", "futbolme0120", "mamansj21", 
    "neamidk", "maylimijonim", "kino.com", "temurbek.m912", 
    "uzbm.malo", "likewisek.448", "sadkmi0", "uzb.mrek", 
    "ahmad_uzb0", "sarik008202"
]

# Sessiya uchun papka yaratish
if not os.path.exists("sessions"):
    os.makedirs("sessions")

def get_main_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(f"📂 Tayyor akklar ({len(REAL_ACCOUNTS)} ta)", callback_data="list_accs"),
        types.InlineKeyboardButton("🚀 Multi-Hujum (Like/View/Fol/Com)", callback_data="start_attack")
    )
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(
        message.chat.id, 
        "💎 **Instagram Mega-Bot v3.0**\n\nRailway serveri uchun optimallashtirildi.\nBarcha akkauntlar tayyor holatda!", 
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "list_accs":
        acc_list = "📋 **Ro'yxat:**\n\n" + "\n".join([f"{i+1}. `{a}`" for i, a in enumerate(REAL_ACCOUNTS)])
        bot.send_message(call.message.chat.id, acc_list, parse_mode="Markdown")
    
    elif call.data == "start_attack":
        msg = bot.send_message(call.message.chat.id, "🔗 Instagram post/video linkini yuboring:")
        bot.register_next_step_handler(msg, execute_action)

def execute_action(message):
    url = message.text
    if "instagram.com" not in url:
        bot.send_message(message.chat.id, "❌ Bu noto'g'ri link. Iltimos, Instagram linkini yuboring.")
        return

    status_msg = bot.send_message(message.chat.id, "⏳ Jarayon boshlandi. Har bir akkauntga kirilmoqda...")
    
    success_count = 0
    comments = ["Zo'r!", "🔥", "Gap yo'q!", "👍", "Ajoyib!", "Super!", "Menga yoqdi!", "Omad!"]

    for user in REAL_ACCOUNTS:
        cl = Client() # Har safar yangi xotira obyekti (RAMni tejaydi)
        session_file = f"sessions/{user}.json"
        
        try:
            logging.info(f"Ishlanmoqda: {user}")
            
            # Sessiya orqali kirish (Tez va xavfsiz)
            if os.path.exists(session_file):
                cl.load_settings(session_file)
                cl.login(user, PASSWORD)
            else:
                cl.login(user, PASSWORD)
                cl.dump_settings(session_file)

            media_pk = cl.media_pk_from_url(url)
            media_id = cl.media_id(media_pk)

            # 1. Video ko'rish
            cl.video_view(media_id)
            # 2. Like bosish
            cl.media_like(media_id)
            # 3. Komment yozish
            cl.media_comment(media_id, random.choice(comments))
            # 4. Obuna bo'lish
            user_id = cl.media_info(media_id).user.pk
            cl.user_follow(user_id)

            success_count += 1
            cl.logout()
            
            # Instagram bloklamasligi va Railway RAM to'lmasligi uchun tanaffus
            time.sleep(random.randint(5, 10))

        except Exception as e:
            logging.error(f"Xato ({user}): {e}")
            continue

    bot.send_message(
        message.chat.id, 
        f"🏁 **Vazifa yakunlandi!**\n\n✅ Muvaffaqiyatli: {success_count} ta\n❌ Xato: {len(REAL_ACCOUNTS) - success_count} ta",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

if __name__ == "__main__":
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
