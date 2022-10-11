FROM python:3.8.14-slim

COPY requirements.txt .
RUN /usr/local/bin/python -m pip install --upgrade pip && pip install -r requirements.txt

WORKDIR /opt/TF-1726
COPY elobot/* ./

ENTRYPOINT ["python3", "main.py"]
