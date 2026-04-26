FROM python:3.10-slim
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean
WORKDIR /code
RUN pip install pyTelegramBotAPI
COPY . .
# Render يمرر المنفذ تلقائياً عبر متغير بيئة
CMD ["python", "app.py"]
