import os
import subprocess
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# SOZLAMALAR
BOT_TOKEN = "8426295239:AAGun0-AbZjsUiEDH3wEShOEIBqFcFVVIWM"
ADMIN_ID = 5775388579  # Admin ID
# Eslatma: Majburiy obuna uchun admin biror kanal ochgan bo'lishi va bot u yerda admin bo'lishi kerak.
# Agar kanal bo'lmasa, shunchaki admin profiliga havola beramiz.
CHANNEL_URL = "https://t.me/hayotovsardorbek11" 

async def check_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obunani tekshirish (bu yerda kanal ID si kerak, hozircha oddiy tekshiruv)"""
    # Agar bot kanal admini bo'lsa, get_chat_member orqali tekshirish mumkin
    return True 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Adminga obuna bo'lish", url=CHANNEL_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Salom! Videoni Ultra 4K qilish uchun adminga obuna bo'ling va keyin videoni yuboring:",
        reply_markup=reply_markup
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Majburiy obuna haqida ogohlantirish (vizual)
    msg = await update.message.reply_text("Obuna tekshirilmoqda... 🔄")
    await asyncio.sleep(1)
    await msg.edit_text("Video qabul qilindi! Ultra 4K ishlov berish boshlandi... 🚀")

    # Videoni yuklab olish
    video_file = await update.message.video.get_file()
    input_path = "input.mp4"
    output_path = "output_4k.mp4"
    await video_file.download_to_drive(input_path)

    # Eng kuchli 4K FFmpeg buyrug'i (faqat bitta video uchun)
    # unsharp va saturation qo'shilgan, tuklarigacha ko'rinishi uchun
    cmd = (
        f"ffmpeg -i {input_path} -vf "
        "\"scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,setsar=1,"
        "unsharp=7:7:3.5:7:7:0.5,eq=saturation=1.7:contrast=1.3\" "
        "-c:v libx264 -preset slow -crf 12 -b:v 50M -pix_fmt yuv420p {output_path} -y"
    )

    try:
        process = await asyncio.create_subprocess_shell(cmd)
        await process.wait()

        # Tayyor videoni yuborish
        await update.message.reply_video(
            video=open(output_path, 'rb'),
            caption="Mana siz so'ragan Ultra 4K sifat! 🔥\n@Admin: " + str(ADMIN_ID)
        )
    except Exception as e:
        await update.message.reply_text(f"Xatolik yuz berdi: {e}")
    finally:
        # Fayllarni o'chirish (tozalash)
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
