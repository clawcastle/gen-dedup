FROM python:latest

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt


ADD . /app

EXPOSE 3000

CMD python app.py