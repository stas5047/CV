FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml ./
RUN pip install --no-cache-dir .

COPY app ./app
COPY alembic.ini ./
COPY migrations ./migrations
COPY startup.sh ./startup.sh
RUN chmod +x ./startup.sh

EXPOSE 8000

CMD ["./startup.sh"]
