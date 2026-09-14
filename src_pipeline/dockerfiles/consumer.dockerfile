FROM python:3.13-slim-bookworm

WORKDIR /app

COPY pyproject.toml /app/
COPY uv.lock /app/

RUN pip install --no-cache-dir uv
RUN uv sync --frozen --no-dev

COPY src_pipeline/consumer.py /app/
COPY src_pipeline/database.py /app/

CMD ["uv", "run", "consumer.py"]
