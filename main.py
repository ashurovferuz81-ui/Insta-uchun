import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from static_ffmpeg import add_paths

# FFmpeg yo'llarini ulaymiz
add_paths()

# --- SOZLAMALAR ---
BOT_TOKEN = "8426295239:AAGun0-AbZjsUiEDH3wEShOEIBqFcFVVIWM"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Kichik videolarni yuboring, sifatini oshirib beraman. 🚀")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("📥 Yuklanmoqda...")
    
    chat_id = update.message.chat_id
    input_path = f"in_{chat_id}.mp4"
    output_path = f"out_4k_{chat_id}.mp4"
    
    try:
        # Faylni yuklab olish (xotiraga emas, to'g'ridan-to'g'ri diskka)
        video_file = await context.bot.get_file(update.message.video.file_id)
        await video_file.download_to_drive(input_path)
        
        await status_msg.edit_text("⚙️ Sifat oshirilmoqda...")

        # Eng yengil render sozlamalari (Railway uchun)
        cmd = [
            'ffmpeg', '-i', input_path,
            '-vf', 'scale=1080:-2,unsharp=5:5:1.2', 
            '-c:v', 'libx264', 
            '-profile:v', 'main', 
            '-level', '3.1',
            '-preset', 'ultrafast', 
            '-crf', '22', # Hajmni kichikroq ushlab turish uchun
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',
            output_path, '-y'
        ]

        process = await asyncio.create_subprocess_exec(*cmd)
        await process.wait()

        if os.path.exists(output_path):
            await status_msg.edit_text("✅ Tayyor! Yuborilmoqda...")
            await update.message.reply_video(
                video=open(output_path, 'rb'), 
                supports_streaming=True
            )
        else:
            await status_msg.edit_text("❌ Renderda xato.")

    except Exception as e:
        # Xatoni aniqroq ko'rish uchun logga chiqaramiz
        print(f"XATO: {str(e)}")
        await status_msg.edit_text(f"❌ Xatolik yuz berdi. Iltimos qayta urinib ko'ring.")
    
    finally:
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)

def main():
    # ApplicationBuilder orqali limitlarni boshqarish
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    print("Bot tayyor...")
    app.run_polling()

if __name__ == "__main__":
    main()
