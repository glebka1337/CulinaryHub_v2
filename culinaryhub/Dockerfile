FROM python:3.12-alpine

WORKDIR /culuinaryhub
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install --upgrade pip
RUN pip install gunicorn
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
EXPOSE 8000
COPY . .