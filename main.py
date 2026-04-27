import telebot
import subprocess
import os
from flask import Flask
import threading

# إعداد Flask لمنصة Render
app = Flask(__name__)

@app.route('/')
def index():
    return "The Coloring Bot is Live!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# توكن البوت الخاص بك
API_TOKEN = '8752935054:AAGhVRbm-B7DDyzGROYvD5yKB3uCrhIDfJA'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك في بوت تلوين ببجي! 🎮\nأرسل لي الفيديو وسأقوم بتعديله فوراً.")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    chat_id = message.chat.id
    msg = bot.reply_to(message, "⏳ جارِ تحميل الفيديو ومعالجته (قد يستغرق ذلك دقيقة)...")

    try:
        # تحميل الفيديو
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        input_fn = f"in_{chat_id}.mp4"
        output_fn = f"out_{chat_id}.mp4"

        with open(input_fn, 'wb') as f:
            f.write(downloaded_file)

        # فلتر التلوين والحدة الاحترافي (نفس المقطع المطلوب)
        # saturation=1.9 (ألوان مشبعة) | contrast=1.5 (تباين عالي) | unsharp (حدة قوية)
        ffmpeg_cmd = [
            'ffmpeg', '-y', '-i', input_fn,
            '-vf', "eq=saturation=1.9:contrast=1.5:brightness=0.03,unsharp=7:7:1.5:7:7:0.5",
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28',
            output_fn
        ]

        # تشغيل FFmpeg
        subprocess.run(ffmpeg_cmd, check=True)

        # إرسال النتيجة
        with open(output_fn, 'rb') as video:
            bot.send_video(chat_id, video, caption="✅ تم التلوين بنمط المونتاج الاحترافي.")
        
        bot.delete_message(chat_id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ فشل المعالجة: {str(e)}", chat_id, msg.message_id)
    
    finally:
        # تنظيف الملفات
        if os.path.exists(input_fn): os.remove(input_fn)
        if os.path.exists(output_fn): os.remove(output_fn)

# تشغيل السيرفر والبوت
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("Bot is starting...")
    bot.infinity_polling()
