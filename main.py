import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from static_ffmpeg import add_paths

# FFmpeg-ni ishga tushirish
add_paths()

# --- SOZLAMALAR ---
BOT_TOKEN = "8426295239:AAGun0-AbZjsUiEDH3wEShOEIBqFcFVVIWM"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡️ **Super 4K Render Bot ishga tushdi!**\n\nVideoni yuboring, men uni maksimal aniqlikda tayyorlab beraman.",
        parse_mode="Markdown"
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("📥 Video qabul qilindi. Super 4K ishlov berilmoqda... ⏳")
    
    chat_id = update.message.chat_id
    input_path = f"in_{chat_id}.mp4"
    output_path = f"out_4k_{chat_id}.mp4"
    
    try:
        # Videoni xavfsiz yuklab olish
        video_file = await context.bot.get_file(update.message.video.file_id)
        await video_file.download_to_drive(input_path)
        
        await status_msg.edit_text("💎 **Sifat oshirilmoqda: 4K Ultra HD...** 🛠", parse_mode="Markdown")

        # --- SUPER 4K RENDER PARAMETRLARI ---
        cmd = [
            'ffmpeg', '-i', input_path,
            '-vf', (
                'scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,' # Haqiqiy 4K o'lcham
                'unsharp=7:7:2.5:7:7:0.5,' # Detallarni o'ta keskin qilish
                'eq=saturation=1.4:contrast=1.25' # Ranglarni boyitish
            ),
            '-c:v', 'libx264', 
            '-preset', 'ultrafast', 
            '-crf', '16',             # Sifat (CRF qancha past bo'lsa, sifat shuncha yuqori)
            '-pix_fmt', 'yuv420p',    # Hamma telefonlar uchun mos rang
            '-c:a', 'copy',           # Ovoz sifatini o'zgartirmasdan saqlab qolish
            '-movflags', '+faststart',
            output_path, '-y'
        ]

        # Renderlash jarayoni
        process = await asyncio.create_subprocess_exec(*cmd)
        await process.wait()

        if os.path.exists(output_path):
            await status_msg.edit_text("✅ **Tayyor! Super 4K video yuborilmoqda...**", parse_mode="Markdown")
            with open(output_path, 'rb') as video:
                await update.message.reply_video(
                    video=video, 
                    caption="🚀 **Super 4K (2160p) Sifat!**\n\nFiltr: Ultra Sharp & Vivid Colors",
                    parse_mode="Markdown",
                    supports_streaming=True
                )
        else:
            await status_msg.edit_text("❌ Renderlashda xatolik yuz berdi.")

    except Exception as e:
        print(f"XATO: {str(e)}")
        await status_msg.edit_text(f"❌ Xatolik: {str(e)}")
    
    finally:
        # Fayllarni o'chirish
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    print("Bot 4K rejimda ishlamoqda...")
    app.run_polling()

if __name__ == "__main__":
    main()
