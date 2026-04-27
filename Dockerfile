FROM python:3.9-slim
# تثبيت النسخة الخفيفة من ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
# تحسين أداء البايثون
ENV PYTHONUNBUFFERED=1
CMD ["python", "main.py"]
