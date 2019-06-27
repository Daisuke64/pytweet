FROM python:3.6.7

# Env
ENV PYTHONUNBUFFERED 1


RUN mkdir -p /var/www/pytweet
WORKDIR /var/www/pytweet

COPY requirements.txt /var/www/pytweet/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /var/www/pytweet/
