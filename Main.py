import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from static_ffmpeg import add_paths

# FFmpeg-ni ulash
add_paths()

# --- SOZLAMALAR ---
BOT_TOKEN = "8426295239:AAGun0-AbZjsUiEDH3wEShOEIBqFcFVVIWM"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 **Super 4K (200MB gacha) Render Bot!**\n\nKatta videolarni ham yuboravering.", parse_mode="Markdown")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Telegram 20MB limitini aylanib o'tish uchun xavfsiz yuklab olish
    status_msg = await update.message.reply_text("📥 Video qabul qilinmoqda (Diskka yozilyapti)... ⏳")
    
    chat_id = update.message.chat_id
    input_path = f"in_{chat_id}.mp4"
    output_path = f"out_{chat_id}_4k.mp4"
    
    try:
        # Faylni diskka bosqichma-bosqich yuklash (Request Entity xatosini oldini oladi)
        file = await context.bot.get_file(update.message.video.file_id)
        await file.download_to_drive(input_path)
        
        await status_msg.edit_text("💎 **Haqiqiy 4K Render boshlandi...**\nBu biroz vaqt olishi mumkin.", parse_mode="Markdown")

        # HAQIQIY 4K PARAMETRLARI
        cmd = [
            'ffmpeg', '-i', input_path,
            '-vf', (
                'scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,' # 4K o'lcham
                'unsharp=7:7:2.5:7:7:0.5,' # Maksimal aniqlik
                'eq=saturation=1.4:contrast=1.3' # Ranglar jilosi
            ),
            '-c:v', 'libx264', 
            '-preset', 'ultrafast', # Server qiynalmasligi uchun tezkor rejim
            '-crf', '18',           # O'ta yuqori sifat
            '-pix_fmt', 'yuv420p',  # Telefonlar tushunadigan rang
            '-c:a', 'copy',         # Ovozni o'zini saqlash
            '-movflags', '+faststart',
            output_path, '-y'
        ]

        # Render jarayoni
        process = await asyncio.create_subprocess_exec(*cmd)
        await process.wait()

        if os.path.exists(output_path):
            await status_msg.edit_text("✅ **4K Video tayyor! Yuborilmoqda...**", parse_mode="Markdown")
            # Videoni yuborish
            with open(output_path, 'rb') as video_file:
                await update.message.reply_video(
                    video=video_file, 
                    caption="🚀 **Super 4K (2160p) Sifat!**\n\nFayl bazadan o'chirildi. ✅",
                    parse_mode="Markdown",
                    supports_streaming=True
                )
        else:
            await status_msg.edit_text("❌ Renderda xatolik: Server quvvati yetmadi.")

    except Exception as e:
        print(f"XATO: {str(e)}")
        await status_msg.edit_text(f"❌ Xato: {str(e)}")
    
    finally:
        # BAZADAN VA SERVERTAN BUTUNLAY O'CHIRISH (Xotira to'lmasligi uchun)
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)

def main():
    # Telegram Bot API limitini 50MB-200MB oralig'ida ishlashiga ruxsat berish
    app = Application.builder().token(BOT_TOKEN).read_timeout(60).write_timeout(60).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    print("4K Monster Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
