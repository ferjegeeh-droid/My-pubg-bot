import telebot
import subprocess
import os
from flask import Flask
import threading

# 1. إعداد Flask لمنصة Render
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is Running (SlowMotion + Colors + Documents)!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. توكن البوت الخاص بك
API_TOKEN = '8752935054:AAGhVRbm-B7DDyzGROYvD5yKB3uCrhIDfJA'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! أرسل المقطع (فيديو أو ملف) وسأقوم بتلوينه وتبطئه 2x فوراً.")

# 3. التعامل مع الفيديو والملفات
@bot.message_handler(content_types=['video', 'document'])
def handle_video(message):
    chat_id = message.chat.id
    file_id = None
    
    if message.content_type == 'video':
        file_id = message.video.file_id
    elif message.content_type == 'document':
        mime_type = message.document.mime_type
        if mime_type and 'video' in mime_type:
            file_id = message.document.file_id
        else:
            bot.reply_to(message, "❌ هذا الملف ليس فيديو.")
            return

    msg = bot.reply_to(message, "⏳ جاري التحميل والمعالجة... قد يستغرق الأمر دقيقة.")

    try:
        # تحميل الملف
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        input_fn = f"in_{chat_id}.mp4"
        output_fn = f"out_{chat_id}.mp4"

        with open(input_fn, 'wb') as f:
            f.write(downloaded_file)

        # 4. أمر FFmpeg (تبطئ 2x + تلوين قوي + حدة عالية)
        # تم استخدام -itsscale 2 لتبطئ الفيديو كما في صورتك
        ffmpeg_cmd = [
            'ffmpeg', '-y', 
            '-itsscale', '2', 
            '-i', input_fn,
            '-vf', "eq=saturation=2.0:contrast=1.5:brightness=0.03,unsharp=7:7:1.5:7:7:0.5",
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '26',
            output_fn
        ]

        subprocess.run(ffmpeg_cmd, check=True)

        # 5. إرسال النتيجة
        with open(output_fn, 'rb') as video:
            bot.send_video(chat_id, video, caption="✅ تم التلوين والتبطئ بنجاح!")
        
        bot.delete_message(chat_id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {str(e)}", chat_id, msg.message_id)
    
    finally:
        if os.path.exists(input_fn): os.remove(input_fn)
        if os.path.exists(output_fn): os.remove(output_fn)

# 6. تشغيل السيرفر والبوت
if __name__ == "__main__":
    # تشغيل Flask في الخلفية
    threading.Thread(target=run_flask, daemon=True).start()
    # تشغيل البوت للأبد
    bot.infinity_polling()
