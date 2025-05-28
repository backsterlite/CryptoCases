FROM python:3.12-slim AS builder

# 1. Встановлюємо залежності для збірки
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ./backend /app

# 2. Встановлюємо Python-залежності
RUN pip install --no-cache-dir -r requirements.txt -r requirements.dev.txt

# 3. Фінальний образ без інструментів збірки
FROM python:3.12-slim
WORKDIR /app

# Копіюємо тільки потрібні файли з етапу збірки
COPY --from=builder /app /app
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

ENV PATH="/usr/local/bin:${PATH}"
ENV PYTHONPATH="/app/src"
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]