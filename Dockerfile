FROM python:3.8.14-slim

WORKDIR /home

RUN /usr/local/bin/python -m pip install --upgrade pip && pip install py-cord==2.0.0b1 python-dotenv requests

RUN apt-get update && apt-get upgrade -y && apt-get install -y git && git clone https://github.com/SogeMoge/TF-1726.git

COPY elo.db TF-1726/elobot/
COPY .env TF-1726/

WORKDIR /home/TF-1726/elobot

CMD ["python3", "main.py"]