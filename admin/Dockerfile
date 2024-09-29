FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
ENV PYTHONPATH=/app

COPY . .

CMD ["python", "app.py"]
