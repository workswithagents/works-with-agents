FROM python:3.11-slim

LABEL org.opencontainers.image.title="Works With Agents - Knowledge Platform"
LABEL org.opencontainers.image.description="On-prem knowledge platform (FactBase, Skill Registry, Pitfall Registry). Syncs with workswithagents.dev."
LABEL org.opencontainers.image.source="https://workswithagents.dev"

ENV PYTHONUNBUFFERED=1
ENV FACTBASE_DIR=/app/data
ENV SKILLS_DIR=/app/skills
ENV SYNC_FROM=https://workswithagents.dev
ENV SYNC_INTERVAL=3600

RUN pip install fastapi uvicorn httpx

COPY api/main.py /app/main.py
COPY llms.txt /app/llms.txt
COPY llms-full.txt /app/llms-full.txt
COPY openapi.json /app/openapi.json

WORKDIR /app

# Create data, skills, and docs directories
RUN mkdir -p /app/data /app/skills /app/docs

EXPOSE 8499

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8499/v1/health')" || exit 1

# Run: API + optional sync daemon
CMD ["sh", "-c", "python -m uvicorn main:app --host 0.0.0.0 --port 8499 & \
  if [ -n \"$SYNC_FROM\" ]; then \
    sleep 10; \
    while true; do \
      echo '[sync] checking for updates from' $SYNC_FROM; \
      python -c \"\
import httpx, os, json, sqlite3, hashlib; \
from pathlib import Path; \
CACHE = '/app/data/.version'; \
SKILLS_DIR = Path('/app/skills'); \
DB = '/app/data/facts.db'; \
PDB = '/app/data/pitfalls.db'; \
r = httpx.get('$SYNC_FROM/v1/version'); \
if r.status_code != 200: \
    print('[sync] version check failed, retrying later'); \
    exit(0); \
v = r.json(); \
remote = v['version']; \
local = open(CACHE).read().strip() if os.path.exists(CACHE) else ''; \
if remote == local: \
    print('[sync] no changes'); \
    exit(0); \
print('[sync] changes detected, pulling data...'); \
\
facts_r = httpx.get('$SYNC_FROM/v1/facts', params={'limit': 10000}); \
if facts_r.status_code == 200: \
    facts = facts_r.json().get('facts', []); \
    conn = sqlite3.connect(DB); \
    conn.execute('PRAGMA journal_mode=WAL'); \
    for f in facts: \
        conn.execute('INSERT OR REPLACE INTO facts (entity, attribute, value, category, source, verified, note, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?)', \
            (f['entity'], f['attribute'], f['value'], f.get('category','reference'), f.get('source','agent'), f.get('verified',0), f.get('note',''), f.get('created_at',''), f.get('updated_at',''))); \
    conn.commit(); conn.close(); \
    print(f'[sync] {len(facts)} facts updated'); \
\
pit_r = httpx.get('$SYNC_FROM/v1/pitfalls', params={'limit': 10000}); \
if pit_r.status_code == 200: \
    pits = pit_r.json().get('pitfalls', []); \
    conn = sqlite3.connect(PDB); \
    conn.execute('PRAGMA journal_mode=WAL'); \
    existing = {r[0] for r in conn.execute('SELECT id FROM pitfalls_log').fetchall()}; \
    for p in pits: \
        if p['id'] not in existing: \
            conn.execute('INSERT INTO pitfalls_log (id, agent_id, tool, error, fix, session_id, logged_at) VALUES (?,?,?,?,?,?,?)', \
                (p['id'], p.get('agent_id',''), p.get('tool',''), p.get('error',''), p.get('fix',''), p.get('session_id',''), p.get('logged_at',''))); \
    conn.commit(); conn.close(); \
    print(f'[sync] {len(pits)} pitfalls updated'); \
\
skills_r = httpx.get('$SYNC_FROM/v1/skills'); \
if skills_r.status_code == 200: \
    skills = skills_r.json().get('skills', []); \
    for s in skills: \
        sr = httpx.get(f\"$SYNC_FROM/v1/skills/{s['name']}\"); \
        if sr.status_code == 200 and sr.json().get('body'): \
            skill_dir = SKILLS_DIR / s['category'] / s['name']; \
            skill_dir.mkdir(parents=True, exist_ok=True); \
            (skill_dir / 'SKILL.md').write_text(sr.json()['body']); \
    print(f'[sync] {len(skills)} skills updated'); \
\
open(CACHE, 'w').write(remote); \
print('[sync] complete'); \
\" || echo '[sync] failed (source may be offline)'; \
      sleep $SYNC_INTERVAL; \
    done \
  else \
    wait; \
  fi"]
