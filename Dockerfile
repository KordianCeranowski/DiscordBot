FROM arm32v7/python:3.8-alpine

WORKDIR /code

RUN apk update && apk upgrade
RUN apk add gcc g++ make zlib-dev libc-dev libffi-dev chromium-chromedriver ffmpeg

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . /code

CMD ["python3", "bot.py"]
