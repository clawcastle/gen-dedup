FROM debian:experimental

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN apt-get update && apt-get install -y \
    python3 \
    pip \
    build-essential \
    libpython3-dev \
    python3-dev \
    g++ \
    git-core 

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

ADD . /app

EXPOSE 3000

CMD python3 app.py