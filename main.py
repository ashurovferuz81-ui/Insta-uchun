import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from static_ffmpeg import add_paths

# FFmpeg-ni avtomatik sozlash
add_paths()

# --- SOZLAMALAR ---
BOT_TOKEN = "8426295239:AAGun0-AbZjsUiEDH3wEShOEIBqFcFVVIWM"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Sifatni oshiruvchi botga xush kelibsiz! 🚀\n"
        "Videoni yuboring, men uni o'ta tiniq (Super HD) qilib beraman."
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("📥 Video olindi. Ishlov berilmoqda... ⏳")
    
    chat_id = update.message.chat_id
    input_path = f"in_{chat_id}.mp4"
    output_path = f"out_{chat_id}.mp4"
    
    try:
        # Videoni yuklab olish
        video_file = await context.bot.get_file(update.message.video.file_id)
        await video_file.download_to_drive(input_path)
        
        await status_msg.edit_text("⚙️ Sifat va ranglar ustida ishlanmoqda... 🛠")

        # UNIVERSAL VA TINIQ FORMAT (Hamma telefonda ochiladi)
        cmd = [
            'ffmpeg', '-i', input_path,
            '-vf', (
                'scale=1440:-2,'              # 2K o'lcham (Tiniq va yengil)
                'unsharp=5:5:1.5:5:5:0.0,'    # Keskinlikni oshirish (detallar uchun)
                'eq=saturation=1.5:contrast=1.2' # Ranglarni yorqin qilish
            ),
            '-c:v', 'libx264', 
            '-profile:v', 'high',         # Sifatli profil
            '-level', '4.2',              # Standart moslik
            '-preset', 'ultrafast',       # Tezroq render qilish
            '-crf', '20',                 # Sifat darajasi (qancha past bo'lsa, shuncha tiniq)
            '-pix_fmt', 'yuv420p',        # Eng muhim: Galereyada ochilishi uchun
            '-c:a', 'aac',                # Standart ovoz
            '-movflags', '+faststart',    # Videoni tez ochilishi uchun
            output_path, '-y'
        ]

        # Renderlashni boshlash
        process = await asyncio.create_subprocess_exec(*cmd)
        await process.wait()

        if os.path.exists(output_path):
            await status_msg.edit_text("✅ Tayyor! Galereyada bemalol ko'rishingiz mumkin.")
            with open(output_path, 'rb') as video:
                await update.message.reply_video(
                    video=video, 
                    caption="🚀 Super HD Sifat!\nEndi galereyangizda ham ochiladi. 🔥",
                    supports_streaming=True
                )
        else:
            await status_msg.edit_text("❌ Renderda xatolik yuz berdi.")

    except Exception as e:
        await status_msg.edit_text(f"❌ Xatolik: {str(e)}")
    
    finally:
        # Fayllarni o'chirish
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    print("Bot tayyor...")
    app.run_polling()

if __name__ == "__main__":
    main()
