# builder
FROM python:3.11-slim AS builder
WORKDIR /app
COPY pyproject.toml poetry.lock* requirements*.txt* ./ 
RUN pip install --upgrade pip
RUN if [ -f requirements.txt ]; then pip wheel --wheel-dir=/wheels -r requirements.txt; fi

# runtime
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN addgroup --system app && adduser --system --ingroup app app
COPY --from=builder /wheels /wheels
COPY . /app
RUN pip install --no-cache-dir --find-links=/wheels -r requirements.txt || true
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz', timeout=5)" || exit 1
CMD ["uvicorn","cvrgpt_api.api:app","--host","0.0.0.0","--port","8000"]
