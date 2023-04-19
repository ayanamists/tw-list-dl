FROM python:3.12-rc-alpine

RUN mkdir /data
RUN mkdir /log
WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]