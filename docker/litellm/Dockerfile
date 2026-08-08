# NOTE: main-latest for dev iteration speed.
# For production, pin to specific version (e.g., v1.55.0).
FROM ghcr.io/berriai/litellm:main-latest

COPY config.yaml /app/config.yaml

CMD ["--config", "/app/config.yaml", "--port", "4000"]
