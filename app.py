import telebot, os, subprocess, threading
from flask import Flask

TOKEN = "8752935054:AAGhVRbm-B7DDyzGROYvD5yKB3uCrhIDfJA"
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🪄 بوت السلاسة الفائقة جاهز!\nأرسل المقطع الآن لتحويله إلى 60fps (Resampled) بجودة خرافية.")

@bot.message_handler(content_types=['video', 'document'])
def handle_video(message):
    try:
        msg = bot.reply_to(message, "⚡ جاري تطبيق خدعة السلاسة (Motion Blending)...")
        
        file_id = message.video.file_id if message.video else message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open("in.mp4", 'wb') as f:
            f.write(downloaded_file)
        
        # الأمر السري للمحترفين
        cmd = (
            'ffmpeg -y -i in.mp4 -vf '
            '"tblend=all_mode=average,framerate=fps=60,unsharp=3:3:0.7:3:3:0.0" '
            '-c:v libx264 -crf 22 -preset fast -pix_fmt yuv420p '
            '-map_metadata -1 -metadata:s:v:0 handler_name="VideoHandler" '
            '-c:a copy out.mp4'
        )
        
        subprocess.run(cmd, shell=True, check=True)
        
        with open("out.mp4", 'rb') as v:
            bot.send_document(message.chat.id, v, caption="✅ تم بنجاح!\n- سلاسة Motion Blur (إحساس 120fps)\n- حجم ملف مثالي\n- بصمة رقمية نظيفة 🛡️")
        
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ: {e}")
    finally:
        if os.path.exists("in.mp4"): os.remove("in.mp4")
        if os.path.exists("out.mp4"): os.remove("out.mp4")

@server.route("/")
def webhook(): return "OK", 200

if __name__ == "__main__":
    threading.Thread(target=lambda: server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 10000)))).start()
    bot.infinity_polling()
