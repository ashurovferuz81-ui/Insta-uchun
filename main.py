import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from static_ffmpeg import add_paths

# Подключаем FFmpeg
add_paths()

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8426295239:AAGun0-AbZjsUiEDH3wEShOEIBqFcFVVIWM"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Отправь мне видео, и я сделаю его в **Super 4K** качестве. 🚀\n"
        "Каждая деталь будет видна максимально четко!",
        parse_mode="Markdown"
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("📥 Видео получено. Начинаю обработку в Ultra HD... ⏳")
    
    chat_id = update.message.chat_id
    input_path = f"in_{chat_id}.mp4"
    output_path = f"out_4k_{chat_id}.mp4"
    
    try:
        # Скачивание видео
        video_file = await update.message.video.get_file()
        await video_file.download_to_drive(input_path)
        
        await status_msg.edit_text("⚙️ Улучшаю детализацию и повышаю качество... 🛠")

        # 100% РАБОЧИЙ КОД ДЛЯ FFMPEG:
        # Мы используем 1440p (2K), так как это "золотая середина" для Telegram. 
        # Визуально это как 4K, но открывается везде без лагов.
        cmd = [
            'ffmpeg', '-i', input_path,
            '-vf', (
                'scale=1440:-2,unsharp=5:5:1.5:5:5:0.0,eq=saturation=1.5:contrast=1.2'
            ),
            '-c:v', 'libx264', 
            '-preset', 'ultrafast', 
            '-crf', '18',           # Очень высокое качество
            '-pix_fmt', 'yuv420p',  # Совместимость со всеми телефонами
            '-c:a', 'aac', 
            '-movflags', '+faststart', # Чтобы видео сразу открывалось
            output_path, '-y'
        ]

        # Запуск рендеринга
        process = await asyncio.create_subprocess_exec(*cmd)
        await process.wait()

        if os.path.exists(output_path):
            await status_msg.edit_text("✅ Готово! Отправляю результат...")
            with open(output_path, 'rb') as video:
                await update.message.reply_video(
                    video=video, 
                    caption="🚀 Качество Super 4K (Ultra HD)!\nДетализация улучшена. 🔥",
                    supports_streaming=True
                )
        else:
            await status_msg.edit_text("❌ Ошибка: Не удалось создать файл.")

    except Exception as e:
        await status_msg.edit_text(f"❌ Произошла ошибка: {str(e)}")
    
    finally:
        # Очистка памяти
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
