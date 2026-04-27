import telebot
import subprocess
import os
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is Running (Coloring + SlowMotion)!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# التوكن الخاص بك
API_TOKEN = '8752935054:AAGhVRbm-B7DDyzGROYvD5yKB3uCrhIDfJA'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! أرسل لي الفيديو وسأقوم بتلوينه وتبطئه (Slow Motion) كما في المقطع المطلوب.")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    chat_id = message.chat.id
    msg = bot.reply_to(message, "⏳ جاري تنفيذ التلوين والتبطئ... انتظر قليلاً.")

    try:
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        input_fn = f"in_{chat_id}.mp4"
        output_fn = f"out_{chat_id}.mp4"

        with open(input_fn, 'wb') as f:
            f.write(downloaded_file)

        # الأمر المدمج:
        # -itsscale 2: يقوم بتبطئ الفيديو (نفس الذي في صورتك)
        # eq + unsharp: التلوين والحدة
        ffmpeg_cmd = [
            'ffmpeg', '-y', 
            '-itsscale', '2',  # تبطئ الفيديو للضعف (Slow Motion)
            '-i', input_fn,
            '-vf', "eq=saturation=1.9:contrast=1.5:brightness=0.03,unsharp=7:7:1.5:7:7:0.5",
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28',
            output_fn
        ]

        subprocess.run(ffmpeg_cmd, check=True)

        with open(output_fn, 'rb') as video:
            bot.send_video(chat_id, video, caption="✅ تم التلوين + التبطئ بنجاح!")
        
        bot.delete_message(chat_id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {str(e)}", chat_id, msg.message_id)
    
    finally:
        if os.path.exists(input_fn): os.remove(input_fn)
        if os.path.exists(output_fn): os.remove(output_fn)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
