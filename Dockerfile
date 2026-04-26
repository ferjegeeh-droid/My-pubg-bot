FROM python:3.9-slim
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean
WORKDIR /app
COPY . .
RUN pip install python-telegram-bot
EXPOSE 8080
CMD ["python", "bot.py"]
