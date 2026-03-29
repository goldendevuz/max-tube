# =========================
# 1️⃣ Builder stage
# =========================
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -Ls https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy lockfile first
COPY requirements.lock .

# Install deps into system python
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system --no-cache-dir -r requirements.lock


# =========================
# 2️⃣ Runtime stage
# =========================
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Create user with same UID as host (IMPORTANT)
RUN useradd -u 1000 -m appuser

# Copy python + binaries
COPY --from=builder /usr/local /usr/local

# Copy app
COPY . /app/

# Ensure directories exist
RUN mkdir -p /app/data /app/staticfiles /app/media

# Fix permissions
RUN chown -R appuser:appuser /app

# Entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER appuser

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "60"]
