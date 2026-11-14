FROM python:3.12.11-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app

#RUN pip install --upgrade pip
#RUN pip install -r requirements.txt
RUN pip install -i https://mirror-pypi.runflare.com/simple --upgrade pip
RUN pip install -i https://mirror-pypi.runflare.com/simple -r requirements.txt
COPY . /app
