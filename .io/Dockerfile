FROM python:3.11-slim

LABEL org.opencontainers.image.title="Works With Agents - Blueprint Registry"
LABEL org.opencontainers.image.description="On-prem LLM blueprint registry. Syncs with workswithagents.io."
LABEL org.opencontainers.image.source="https://workswithagents.io"

ENV PYTHONUNBUFFERED=1
ENV BLUEPRINTS_DIR=/blueprints
ENV SYNC_FROM=https://workswithagents.io
ENV SYNC_INTERVAL=3600

RUN pip install fastapi uvicorn pyyaml httpx

COPY api/main.py /app/main.py
COPY llms.txt /app/llms.txt

WORKDIR /app

# Create blueprints volume and submitted dir
RUN mkdir -p /blueprints/submitted

# Copy starter blueprints if provided at build time
COPY blueprints/*.md /blueprints/ 2>/dev/null || true

EXPOSE 8200

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8200/v1/health')" || exit 1

# Run: API + optional sync daemon
CMD ["sh", "-c", "python -m uvicorn main:app --host 0.0.0.0 --port 8200 & \
  if [ -n \"$SYNC_FROM\" ]; then \
    while true; do \
      sleep $SYNC_INTERVAL; \
      echo \"[sync] pulling from $SYNC_FROM\"; \
      python -c \"\
import httpx, os, json; \
r = httpx.get('$SYNC_FROM/v1/blueprints'); \
if r.status_code == 200: \
  data = r.json(); \
  for bp in data.get('blueprints', []): \
    r2 = httpx.get(f'$SYNC_FROM/v1/blueprints/{bp[\"id\"]}'); \
    if r2.status_code == 200: \
      open(os.environ['BLUEPRINTS_DIR'] + '/' + bp['id'] + '.md', 'w').write(r2.text); \
  print(f'[sync] {len(data.get(\"blueprints\", []))} blueprints updated'); \
\" || echo '[sync] failed (registry may be offline)'; \
    done \
  else \
    wait; \
  fi"]
