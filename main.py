import telebot
import subprocess
import os
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def index():
    return "High Quality Bot is Live!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

API_TOKEN = '8752935054:AAGhVRbm-B7DDyzGROYvD5yKB3uCrhIDfJA'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(content_types=['video', 'document'])
def handle_video(message):
    chat_id = message.chat.id
    file_id = None
    
    if message.content_type == 'video':
        file_id = message.video.file_id
    elif message.content_type == 'document' and 'video' in message.document.mime_type:
        file_id = message.document.file_id
    else:
        return

    msg = bot.reply_to(message, "⏳ جاري المعالجة بالجودة الأصلية... انتظر قليلاً.")

    try:
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        input_fn = f"in_{chat_id}.mp4"
        output_fn = f"out_{chat_id}.mp4"

        with open(input_fn, 'wb') as f:
            f.write(downloaded_file)

        # أمر FFmpeg للحفاظ على الجودة الأصلية مع السرعة:
        # 1. شطبنا الـ Scale للحفاظ على الأبعاد كما هي.
        # 2. preset ultrafast لسرعة المعالجة.
        # 3. crf 18 لجودة خرافية مطابقة للأصل.
        ffmpeg_cmd = [
            'ffmpeg', '-y', 
            '-itsscale', '2', 
            '-i', input_fn,
            '-vf', "eq=saturation=1.8:contrast=1.3", # حذفنا فلاتر الحدة لأنها "تقتل" السرعة
            '-c:v', 'libx264', 
            '-preset', 'ultrafast', # أسرع نمط ضغط
            '-tune', 'zerolatency', # لتقليل التأخير
            '-crf', '20', 
            '-threads', '0', 
            output_fn
        ]

        subprocess.run(ffmpeg_cmd, check=True)

        with open(output_fn, 'rb') as video:
            bot.send_video(chat_id, video, caption="✅ تم التعديل بالجودة الأصلية")
        
        bot.delete_message(chat_id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {str(e)}", chat_id, msg.message_id)
    
    finally:
        if os.path.exists(input_fn): os.remove(input_fn)
        if os.path.exists(output_fn): os.remove(output_fn)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
