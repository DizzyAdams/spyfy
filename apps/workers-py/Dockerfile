# SpyFy API — imagem de produção
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# deps (conjunto completo: chromadb+langgraph p/ os agents autônomos)
COPY requirements.docker.txt requirements.txt
RUN pip install -r requirements.txt

# código
COPY spyfy ./spyfy

# usuário não-root (segurança)
RUN useradd -m -u 10001 spyfy && chown -R spyfy:spyfy /app
USER spyfy

EXPOSE 8000

# healthcheck (usa $PORT quando definido)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import os,urllib.request as u; u.urlopen('http://localhost:{}/health'.format(os.environ.get('PORT','8000')))" || exit 1

# gunicorn + uvicorn workers (produção).
# WEB_CONCURRENCY=1 por padrão (free tier: ~512MB RAM; chromadb é pesado em memória).
# Honra $PORT (Render/HuggingFace/Space injetam a porta).
CMD ["sh", "-c", "gunicorn spyfy.api.app:app -k uvicorn.workers.UvicornWorker -w ${WEB_CONCURRENCY:-1} -b 0.0.0.0:${PORT:-8000} --timeout 60 --access-logfile -"]
