import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from static_ffmpeg import add_paths

# FFmpeg yo'llarini avtomatik ulaymiz
add_paths()

# --- SOZLAMALAR ---
BOT_TOKEN = "8426295239:AAGun0-AbZjsUiEDH3wEShOEIBqFcFVVIWM"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Videoni yuboring, men uni **Super 4K** formatga o'tkazib beraman. 🚀\n\n"
        "Eslatma: Video sifati o'ta yuqori bo'lgani uchun uni ochishga telefoningiz biroz o'ylanishi mumkin.",
        parse_mode="Markdown"
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("📥 Video qabul qilindi. Super 4K render boshlanmoqda... ⏳")
    
    chat_id = update.message.chat_id
    input_path = f"in_{chat_id}.mp4"
    output_path = f"out_4k_{chat_id}.mp4"
    
    try:
        # Videoni yuklab olish
        video_file = await update.message.video.get_file()
        await video_file.download_to_drive(input_path)
        
        await status_msg.edit_text("⚙️ Sifat oshirilmoqda (H.264 High Profile)... 🛠")

        # Muammosiz 4K buyrug'i (Hamma telefonda ochiladi)
        cmd = [
            'ffmpeg', '-i', input_path,
            '-vf', 'scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,unsharp=7:7:3.5:7:7:0.5,eq=saturation=1.8:contrast=1.3',
            '-c:v', 'libx264', 
            '-profile:v', 'high',   # Standart High Profile
            '-level', '4.2',        # 4K uchun mos daraja
            '-preset', 'ultrafast', 
            '-crf', '18',           # Sifat va hajm muvozanati (juda tiniq)
            '-pix_fmt', 'yuv420p',  # Telefonlar tushunadigan rang formati
            '-c:a', 'aac',          # Standart audio formati
            '-movflags', '+faststart', # Videoni yuklanishini tezlashtiradi
            output_path, '-y'
        ]

        # Jarayonni ishga tushirish
        process = await asyncio.create_subprocess_exec(*cmd)
        await process.wait()

        if os.path.exists(output_path):
            await status_msg.edit_text("✅ Tayyor! Super 4K video yuborilmoqda...")
            with open(output_path, 'rb') as video:
                await update.message.reply_video(
                    video=video, 
                    caption="🚀 Super 4K (2160p) Sifat!\n\nHar bir detal (hatto yunglarigacha) maksimal aniqlikda!",
                    supports_streaming=True
                )
        else:
            await status_msg.edit_text("❌ Xato: Renderda muammo yuz berdi.")

    except Exception as e:
        await status_msg.edit_text(f"❌ Xato: {str(e)}")
    
    finally:
        # Fayllarni tozalash (xotira to'lib qolmasligi uchun)
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
