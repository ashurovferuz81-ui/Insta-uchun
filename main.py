import os
import asyncio
import subprocess
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from static_ffmpeg import add_paths

# FFmpeg yo'llarini tizimga ulaymiz
add_paths()

# --- SOZLAMALAR ---
BOT_TOKEN = "8426295239:AAGun0-AbZjsUiEDH3wEShOEIBqFcFVVIWM"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Videoni yuboring, men uni **Super 4K** formatga o'tkazib beraman. 🚀",
        parse_mode="Markdown"
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("📥 Video olindi. Super 4K render boshlandi... ⏳")
    
    chat_id = update.message.chat_id
    input_path = f"in_{chat_id}.mp4"
    output_path = f"out_4k_{chat_id}.mp4"
    
    try:
        # Videoni yuklab olish
        video_file = await update.message.video.get_file()
        await video_file.download_to_drive(input_path)
        
        await status_msg.edit_text("⚙️ Sifat oshirilmoqda (Ultra HD)... 🛠")

        # FFmpeg buyrug'i - endi 'static_ffmpeg' orqali ishlaydi
        cmd = [
            'ffmpeg', '-i', input_path,
            '-vf', 'scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,unsharp=7:7:3.5:7:7:0.5,eq=saturation=1.8:contrast=1.3',
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '18', 
            '-b:v', '30M', '-pix_fmt', 'yuv420p', output_path, '-y'
        ]

        # Jarayonni ishga tushirish
        process = await asyncio.create_subprocess_exec(*cmd)
        await process.wait()

        if os.path.exists(output_path):
            await status_msg.edit_text("✅ Tayyor! Super 4K video yuborilmoqda...")
            with open(output_path, 'rb') as video:
                await update.message.reply_video(
                    video=video, 
                    caption="🚀 Super 4K (2160p) Sifat!",
                    supports_streaming=True
                )
        else:
            await status_msg.edit_text("❌ Renderda xatolik: FFmpeg faylni yarata olmadi.")

    except Exception as e:
        await status_msg.edit_text(f"❌ Xato yuz berdi: {str(e)}")
    
    finally:
        # Fayllarni tozalash
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
