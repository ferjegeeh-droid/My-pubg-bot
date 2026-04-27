FROM python:3.9-slim

# تثبيت FFmpeg
RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6 && apt-get clean

# ضبط مجلد العمل
WORKDIR /app
COPY . /app

# تثبيت مكتبات بايثون
RUN pip install --no-cache-dir -r requirements.txt

# تشغيل البوت
CMD ["python", "main.py"]
