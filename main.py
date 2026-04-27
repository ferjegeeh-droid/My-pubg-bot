import telebot
import subprocess
import os
from flask import Flask
import threading
import time

# إعداد Flask لمنصة Render
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# التوكن الجديد الخاص بك
API_TOKEN = '8752935054:AAEmRFpDOK-tWQNlLzrsPyF-9HOkYseh3kI'
bot = telebot.TeleBot(API_TOKEN)

# تنظيف أي اتصال قديم لمنع خطأ 409 Conflict
bot.remove_webhook()
time.sleep(1)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! أرسل لي الفيديو (كفيديو أو كملف) وسأقوم بتلوينه وتبطئه 2x بأعلى جودة ممكنة.")

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
            bot.reply_to(message, "❌ يرجى إرسال ملف فيديو فقط.")
            return

    msg = bot.reply_to(message, "⏳ جارِ المعالجة بالجودة الكاملة... (قد يستغرق الوقت حسب حجم المقطع)")

    try:
        # تحميل الملف
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        input_fn = f"in_{chat_id}.mp4"
        output_fn = f"out_{chat_id}.mp4"

        with open(input_fn, 'wb') as f:
            f.write(downloaded_file)

        # أمر FFmpeg (الجودة الأصلية + تبطئ 2x + تلوين سينمائي)
        # -itsscale 2 : للتبطئ
        # -preset ultrafast : لأقصى سرعة معالجة ممكنة
        # -crf 20 : للحفاظ على جودة عالية جداً قريبة من الأصل
        ffmpeg_cmd = [
            'ffmpeg', '-y', 
            '-itsscale', '2', 
            '-i', input_fn,
            '-vf', "eq=saturation=1.9:contrast=1.5:brightness=0.02,unsharp=7:7:1.2:7:7:0.5",
            '-c:v', 'libx264', 
            '-preset', 'ultrafast', 
            '-crf', '20', 
            '-threads', '0', 
            output_fn
        ]

        subprocess.run(ffmpeg_cmd, check=True)

        # إرسال النتيجة
        with open(output_fn, 'rb') as video:
            bot.send_video(chat_id, video, caption="✅ تم التلوين والتبطئ (الجودة الأصلية)")
        
        bot.delete_message(chat_id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ فشل المعالجة: {str(e)}", chat_id, msg.message_id)
    
    finally:
        if os.path.exists(input_fn): os.remove(input_fn)
        if os.path.exists(output_fn): os.remove(output_fn)

# تشغيل البوت
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
