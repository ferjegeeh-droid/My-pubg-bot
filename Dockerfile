FROM python:3.9-slim

# تثبيت FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# إعداد ملفات العمل
WORKDIR /app
COPY . /app

# تثبيت مكتبات بايثون
RUN pip install --no-cache-dir -r requirements.txt

# تشغيل البوت
CMD ["python", "bot.py"]
