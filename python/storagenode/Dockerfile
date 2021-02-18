FROM python:latest

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && \
    pip install -r requirements.txt


ADD . /app

EXPOSE 3000

CMD python app.py