import telebot
import os
import subprocess
import threading
from flask import Flask

TOKEN = "8752935054:AAGhVRbm-B7DDyzGROYvD5yKB3uCrhIDfJA"
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🚀 بوت ببجي السريع جاهز!\nأرسل الفيديو وسأعالجُه بأقصى سرعة ممكنة.")

@bot.message_handler(content_types=['video', 'document'])
def handle_video(message):
    try:
        msg = bot.reply_to(message, "⚡ جاري المعالجة السريعة... انتظر ثواني.")
        
        file_id = message.video.file_id if message.video else message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open("in.mp4", 'wb') as f:
            f.write(downloaded_file)
        
        # --- أمر FFmpeg المطور للسرعة القصوى ---
        # 1. جعلنا الدقة 1080p (أسرع في المعالجة وأفضل للتيك توك)
        # 2. استخدمنا mi_mode=blend (سلاسة خرافية بجهد أقل)
        # 3. قللنا تعقيد الـ unsharp قليلاً للسرعة
        cmd = (
            'ffmpeg -y -i in.mp4 -vf '
            '"scale=w=\'if(gt(iw,ih),-1,1080)\':h=\'if(gt(iw,ih),1080,-1)\', ' # الحفاظ على الأبعاد مع سقف 1080p
            'minterpolate=fps=60:mi_mode=blend, ' # سلاسة سريعة
            'unsharp=3:3:0.8:3:3:0.4, ' # حدة متوازنة
            'eq=saturation=1.4:contrast=1.1" ' # ألوان ببجي
            '-c:v libx264 -crf 23 -preset ultrafast -threads 0 -pix_fmt yuv420p -c:a copy out.mp4'
        )
        
        subprocess.run(cmd, shell=True, check=True)
        
        with open("out.mp4", 'rb') as v:
            bot.send_document(message.chat.id, v, caption="✅ تم بنجاح بأقصى سرعة!\nانشره الآن واستمتع بالسلاسة.")
        
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ: {e}")
    finally:
        # مسح الملفات لتوفير مساحة السيرفر
        if os.path.exists("in.mp4"): os.remove("in.mp4")
        if os.path.exists("out.mp4"): os.remove("out.mp4")

@server.route("/")
def webhook():
    return "Bot is Running", 200

if __name__ == "__main__":
    threading.Thread(target=lambda: server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 10000)))).start()
    bot.infinity_polling()
