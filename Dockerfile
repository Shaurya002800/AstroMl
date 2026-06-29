FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_PORT=8501
ENV SERENOVA_SESSION_DIR=/app/runtime/sessions
ENV SERENOVA_FEEDBACK_PATH=/app/runtime/feedback/feedback.jsonl
ENV SERENOVA_AUDIT_LOG_PATH=/app/runtime/audit/audit.jsonl

WORKDIR /app

RUN useradd --create-home --shell /usr/sbin/nologin serenova

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /app/runtime/sessions /app/runtime/feedback /app/runtime/audit \
    && chown -R serenova:serenova /app/runtime

USER serenova

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=3).read()"

CMD ["streamlit", "run", "src/app.py"]
