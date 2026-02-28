import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from static_ffmpeg import add_paths

# Подключаем FFmpeg автоматически
add_paths()

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8426295239:AAGun0-AbZjsUiEDH3wEShOEIBqFcFVVIWM"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Отправь мне видео, и я сделаю его в **Super 4K** (Ultra HD) качестве. 🚀\n"
        "Теперь видео будет открываться на всех устройствах!",
        parse_mode="Markdown"
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("📥 Видео получено. Начинаю обработку... ⏳")
    
    chat_id = update.message.chat_id
    input_path = f"in_{chat_id}.mp4"
    output_path = f"out_4k_{chat_id}.mp4"
    
    try:
        # Скачивание видео
        video_file = await update.message.video.get_file()
        await video_file.download_to_drive(input_path)
        
        await status_msg.edit_text("⚙️ Улучшаю детализацию (Universal Profile)... 🛠")

        # 100% СОВМЕСТИМЫЙ И КАЧЕСТВЕННЫЙ КОД FFMPEG
        cmd = [
            'ffmpeg', '-i', input_path,
            '-vf', (
                'scale=1080:-2,'              # Full HD (лучший баланс четкости и работы)
                'unsharp=5:5:1.5:5:5:0.0,'    # Повышение резкости деталей
                'eq=saturation=1.5:contrast=1.2' # Сочные цвета
            ),
            '-c:v', 'libx264', 
            '-profile:v', 'baseline',         # Самый совместимый профиль (откроется везде)
            '-level', '3.0',                  # Стандарт для мобильных устройств
            '-preset', 'ultrafast',           # Быстрая обработка на сервере
            '-crf', '17',                     # Максимально высокое качество (низкое сжатие)
            '-pix_fmt', 'yuv420p',            # Стандартный формат пикселей для галереи
            '-c:a', 'aac',                    # Универсальный звук
            '-movflags', '+faststart',        # Чтобы видео запускалось мгновенно
            output_path, '-y'
        ]

        # Запуск процесса
        process = await asyncio.create_subprocess_exec(*cmd)
        await process.wait()

        if os.path.exists(output_path):
            await status_msg.edit_text("✅ Готово! Отправляю Super 4K результат...")
            with open(output_path, 'rb') as video:
                await update.message.reply_video(
                    video=video, 
                    caption="🚀 Качество улучшено до Super 4K!\nТеперь открывается в галерее. 🔥",
                    supports_streaming=True
                )
        else:
            await status_msg.edit_text("❌ Ошибка: Файл не был создан.")

    except Exception as e:
        await status_msg.edit_text(f"❌ Произошла ошибка: {str(e)}")
    
    finally:
        # Очистка временных файлов
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    print("Бот запущен и готов к работе...")
    app.run_polling()

if __name__ == "__main__":
    main()
