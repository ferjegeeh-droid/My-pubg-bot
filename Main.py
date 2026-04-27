import telebot
import subprocess
import os
from flask import Flask
import threading

# إعداد Flask لكي يعمل على Render
app = Flask('')
@app.route('/')
def home():
    return "Bot is Running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# توكن البوت
API_TOKEN = '8752935054:AAGhVRbm-B7DDyzGROYvD5yKB3uCrhIDfJA'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(content_types=['video'])
def handle_video(message):
    chat_id = message.chat.id
    bot.reply_to(message, "⏳ جاري التلوين والمعالجة... قد يستغرق الأمر دقيقة.")

    file_info = bot.get_file(message.video.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    input_filename = f"in_{chat_id}.mp4"
    output_filename = f"out_{chat_id}.mp4"

    with open(input_filename, 'wb') as f:
        f.write(downloaded_file)

    # فلتر التلوين والحدة (نفس النتيجة المطلوبة)
    # saturation=1.8 (تلوين قوي) | unsharp (حدة عالية)
    cmd = [
        'ffmpeg', '-y', '-i', input_filename,
        '-vf', "eq=saturation=1.8:contrast=1.4:brightness=0.02,unsharp=7:7:1.5:7:7:0.5",
        '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '23',
        output_filename
    ]

    try:
        subprocess.run(cmd, check=True)
        with open(output_filename, 'rb') as v:
            bot.send_video(chat_id, v, caption="✅ تم التلوين بنجاح!")
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {e}")

    if os.path.exists(input_filename): os.remove(input_filename)
    if os.path.exists(output_filename): os.remove(output_filename)

# تشغيل Flask في خيط منفصل
threading.Thread(target=run_flask).start()

# تشغيل البوت
bot.polling(none_stop=True)
