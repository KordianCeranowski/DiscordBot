FROM python:3.8-alpine

WORKDIR /app

RUN apk update && apk upgrade
RUN apk add gcc g++ make zlib-dev libc-dev libffi-dev chromium-chromedriver opus-dev openssl-dev ffmpeg

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . /app

CMD ["python3", "bot.py"]
