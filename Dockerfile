FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY README.md .
COPY cp_traintracking.py .
COPY favorite_stations.json .
RUN pip install --upgrade pip && pip install uv && pip install httpx mcp[cli]

CMD ["uv", "run", "cp_traintracking.py"] 