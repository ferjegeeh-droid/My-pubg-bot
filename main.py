import telebot
import subprocess
import os
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is Running (Supporting Documents)!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# التوكن الخاص بك
API_TOKEN = '8752935054:AAGhVRbm-B7DDyzGROYvD5yKB3uCrhIDfJA'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! أرسل لي المقطع (سواء كفيديو أو كملف Document) وسأقوم بتلوينه وتبطئه.")

# تعديل هنا ليقبل الفيديوهات والملفات
@bot.message_handler(content_types=['video', 'document'])
def handle_video(message):
    chat_id = message.chat.id
    file_id = None
    
    # التحقق هل المرسل فيديو أم ملف
    if message.content_type == 'video':
        file_id = message.video.file_id
    elif message.content_type == 'document':
        # التحقق من أن الملف المرسل هو فيديو (مثل mp4, mov, mkv)
        mime_type = message.document.mime_type
        if mime_type and 'video' in mime_type:
            file_id = message.document.file_id
        else:
            bot.reply_to(message, "❌ عذراً، هذا الملف ليس مقطع فيديو.")
            return

    msg = bot.reply_to(message, "⏳ جارِ التحميل والمعالجة (تلوين + تبطئ)...")

    try:
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        input_fn = f"in_{chat_id}.mp4"
        output_fn = f"out_{chat_id}.mp4"

        with open(input_fn, 'wb') as f:
            f.write(downloaded_file)

        # أمر FFmpeg (التبطئ -itsscale 2 + التلوين القوي والحدة)
        ffmpeg_cmd = [
            'ffmpeg', '-y',
