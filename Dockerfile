FROM python:3.9-slim

# تثبيت FFmpeg (ضروري جداً)
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# تأكد أن اسم الملف هنا يطابق اسم ملف الكود (main.py)
CMD ["python", "main.py"]
