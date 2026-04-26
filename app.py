import telebot
import os
import subprocess
import threading
from flask import Flask

# التوكن الخاص بك
TOKEN = "8752935054:AAGhVRbm-B7DDyzGROYvD5yKB3uCrhIDfJA"
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "✅ أهلاً بك! البوت يعمل الآن على Render.\nأرسل الفيديو وسأقوم بتنعيمه فوراً.")

@bot.message_handler(content_types=['video', 'document'])
def handle_video(message):
    try:
        msg = bot.reply_to(message, "⏳ جاري المعالجة بسلاسة فائقة... انتظر قليلاً.")
        
        file_id = message.video.file_id if message.video else message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open("in.mp4", 'wb') as f:
            f.write(downloaded_file)
        
        # أمر FFmpeg السحري (سلاسة + حدة + ألوان)
        cmd = 'ffmpeg -y -i in.mp4 -vf "minterpolate=fps=60:mi_mode=blend,unsharp=3:3:1.5:3:3:0.5,eq=saturation=1.5:contrast=1.2" -c:v libx264 -crf 23 -preset ultrafast -pix_fmt yuv420p -map_metadata -1 -c:a copy out.mp4'
        subprocess.run(cmd, shell=True, check=True)
        
        with open("out.mp4", 'rb') as v:
            bot.send_document(message.chat.id, v, caption="🔥 تم التجهيز! انشره الآن على تيك توك.")
        
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ: {e}")

@server.route("/")
def webhook():
    return "Bot is Alive", 200

if __name__ == "__main__":
    # تشغيل سيرفر ويب بسيط في الخلفية لمنع توقف Render
    threading.Thread(target=lambda: server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 10000)))).start()
    print("Bot is polling...")
    bot.infinity_polling()
