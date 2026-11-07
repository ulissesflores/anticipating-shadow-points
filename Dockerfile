# Track 1 replication in a clean container: derive, test, seal, verify.
FROM python:3.12-slim
WORKDIR /repo
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "run_all.py"]
