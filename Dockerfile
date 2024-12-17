FROM python:3.9-slim


WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PYTHONPATH="${PYTHONPATH}:/app/src"


CMD ["python3", "/app/src/websocket/websocket_client.py"]
