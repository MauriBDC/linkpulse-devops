# LinkPulse

Production-style URL shortener used as a DevOps portfolio workload.

The application is intentionally small. The goal of the repository is to evolve the same workload through containerization, automated testing, CI/CD, Infrastructure as Code, cloud deployment, security, observability and Kubernetes.

## Current stage — v0.1

- FastAPI REST API
- PostgreSQL
- Docker / Docker Compose
- Liveness and readiness endpoints
- Automated tests with pytest
- GitHub Actions CI
- Persistent database volume

## Architecture

```text
Client
  |
  v
FastAPI
  |
  v
PostgreSQL
```

Later stages will add AWS, Terraform, image publishing, deployment automation, observability and Kubernetes.

## Run locally

Requirements:

- Docker
- Docker Compose

Start the database, apply migrations, and start the API:

```bash
docker compose up -d db
docker compose run --build --rm api alembic upgrade head
docker compose up --build -d api
```

Check container status:

```bash
docker compose ps
```

Check readiness:

```bash
curl http://localhost:8000/health/ready
```

Expected response:

```json
{"status":"ready"}
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

## Create a short URL

```bash
curl -X POST http://localhost:8000/links   -H "Content-Type: application/json"   -d '{"url":"https://example.com/article"}'
```

Example response:

```json
{
  "short_code": "Ab12Cd3",
  "original_url": "https://example.com/article",
  "clicks": 0,
  "created_at": "2026-09-23T20:00:00Z",
  "last_accessed_at": null
}
```

Open:

```text
http://localhost:8000/Ab12Cd3
```

The API responds with an HTTP 302 redirect.

## Statistics

```bash
curl http://localhost:8000/links/Ab12Cd3/stats
```

## Run tests

With Python installed locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest -q
```

## Repository roadmap

### v0.1 — Local foundation
- [x] API
- [x] PostgreSQL
- [x] Docker
- [x] Docker Compose
- [x] Health checks
- [x] Tests
- [x] CI

### v0.2 — Application maturity
- [x] Alembic migrations
- [ ] Structured logging
- [ ] Coverage gate
- [ ] Linting
- [ ] Rate limiting
- [ ] Redis cache

### v0.3 — AWS + IaC
- [ ] Terraform
- [ ] VPC
- [ ] ECR
- [ ] Compute
- [ ] IAM role
- [ ] Secrets handling
- [ ] Remote Terraform state

### v0.4 — Delivery
- [ ] Build and push Docker image
- [ ] Automated deployment
- [ ] Environment separation
- [ ] Rollback strategy

### v0.5 — Observability
- [ ] Metrics
- [ ] Centralized logs
- [ ] Dashboard
- [ ] Alerts

### v0.6 — Kubernetes
- [ ] Kubernetes manifests
- [ ] Helm
- [ ] Probes
- [ ] Resource requests/limits
- [ ] HPA

## Why this project exists

This repository is designed to demonstrate DevOps engineering decisions rather than application complexity. Each infrastructure and delivery decision should be documented with its trade-offs.

## License

MIT
