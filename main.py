import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8426295239:AAGun0-AbZjsUiEDH3wEShOEIBqFcFVVIWM"
ADMIN_ID = 5775388579
ADMIN_URL = "https://t.me/hayotovsardorbek11"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Просто приветствие и кнопка админа (без обязательств)
    keyboard = [[InlineKeyboardButton("Канал Админа 👑", url=ADMIN_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Привет! Я превращу твое видео в **Ultra 4K (2160p)**.\n"
        "Просто отправь мне видеофайл, и я начну обработку.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("📥 Видео получено. Начинаю Ultra 4K рендеринг... ⏳")
    
    chat_id = update.message.chat_id
    input_path = f"input_{chat_id}.mp4"
    output_path = f"output_4k_{chat_id}.mp4"
    
    try:
        # Загрузка видео
        video_file = await update.message.video.get_file()
        await video_file.download_to_drive(input_path)
        
        await status_msg.edit_text("⚙️ Обработка: улучшение деталей и апскейл до 4K... 🛠")

        # Настройки для "прорисовки каждого волоска":
        # scale=3840:2160 - апскейл до 4К
        # unsharp - резкость (максимальная детализация)
        # eq=saturation - сочные цвета
        cmd = [
            'ffmpeg', '-i', input_path,
            '-vf', 'scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,unsharp=7:7:3.5:7:7:0.5,eq=saturation=1.8:contrast=1.3',
            '-c:v', 'libx264', 
            '-preset', 'veryfast', # Для скорости на Railway
            '-crf', '12',           # Высочайшее качество
            '-b:v', '50M',          # Огромный битрейт для четкости
            '-pix_fmt', 'yuv420p', 
            output_path, '-y'
        ]

        process = await asyncio.create_subprocess_exec(*cmd)
        await process.wait()

        if os.path.exists(output_path):
            await status_msg.edit_text("✅ Готово! Отправляю Ultra 4K результат...")
            await update.message.reply_video(
                video=open(output_path, 'rb'),
                caption="🚀 Твое видео в Ultra 4K качестве!\n\nСделано через бота админа: @hayotovsardorbek11",
                supports_streaming=True
            )
        else:
            await status_msg.edit_text("❌ Ошибка при обработке видео.")

    except Exception as e:
        await status_msg.edit_text(f"❌ Произошла ошибка: {str(e)}")
    
    finally:
        # Удаляем временные файлы, чтобы не забивать память сервера
        for path in [input_path, output_path]:
            if os.path.exists(path):
                os.remove(path)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
