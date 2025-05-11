FROM python:3.12-slim
WORKDIR /app
COPY ./backend /app

COPY .env /app/.env
COPY .env.test /app/.env.test

RUN pip install --no-cache-dir -r requirements.txt -r requirements.dev.txt

ENV PYTHONPATH="/app/src"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
