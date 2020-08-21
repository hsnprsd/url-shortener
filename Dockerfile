FROM python:3.8

WORKDIR /app
ADD . .

RUN pip install -r requirements.txt

ENV FLASK_APP server:server

CMD ["flask", "run", "--host=0.0.0.0"]
