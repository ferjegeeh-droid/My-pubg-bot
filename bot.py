import os
import subprocess
import logging
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# إعداد السجلات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8752935054:AAGhVRbm-B7DDyzGROYvD5yKB3uCrhIDfJA"

# سيرفر بسيط لإرضاء منصة Render ومنع توقف البوت
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running")

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

async def process_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.video: return
    
    msg = await update.message.reply_text("⏳ جاري معالجة الفيديو بـ Timescale 60000...")
    input_path = f"in_{update.message.chat_id}.mp4"
    output_path = f"out_{update.message.chat_id}.mp4"

    try:
        video_file = await update.message.video.get_file()
        await video_file.download_to_drive(input_path)

        ffmpeg_cmd = [
            'ffmpeg', '-y', '-i', input_
