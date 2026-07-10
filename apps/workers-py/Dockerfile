# SpyFy API — imagem de produção
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# deps
COPY requirements.txt .
RUN pip install -r requirements.txt

# código
COPY spyfy ./spyfy

# usuário não-root (segurança)
RUN useradd -m -u 10001 spyfy && chown -R spyfy:spyfy /app
USER spyfy

EXPOSE 8000

# healthcheck
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request as u; u.urlopen('http://localhost:8000/health')" || exit 1

# gunicorn + uvicorn workers (produção)
CMD ["gunicorn", "spyfy.api.app:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-w", "4", "-b", "0.0.0.0:8000", \
     "--timeout", "60", "--access-logfile", "-"]
