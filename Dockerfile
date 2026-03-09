FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m assistant
USER assistant
WORKDIR /home/assistant/app

COPY --chown=assistant:assistant requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

COPY --chown=assistant:assistant . .

RUN chmod +x main.py

ENV PATH="/home/assistant/.local/bin:${PATH}"

CMD ["python", "main.py"]

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python -c "import os, time; f='data/health.check'; exit(0 if os.path.exists(f) and time.time() - os.path.getmtime(f) < 600 else 1)"
