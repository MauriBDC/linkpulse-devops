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

Create the local configuration and edit its example values as needed:

```bash
cp .env.example .env
```

If reusing an existing PostgreSQL volume, set `POSTGRES_PASSWORD` and the password
in `DATABASE_URL` to the credentials already stored in that database. Changing
these variables does not change credentials in an initialized volume.

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

## Application configuration

Settings live in `app/core/config.py` and are shared by the API and Alembic.
They read `.env` from the current working directory; run commands from the
repository root. Process environment variables override `.env` values.
Settings are cached per process, so restart the API after changing them.

| Variable | Default | Purpose |
| --- | --- | --- |
| `APP_NAME` | `LinkPulse API` | FastAPI application title |
| `APP_ENV` | `development` | `development`, `test`, or `production` |
| `DATABASE_URL` | Required | SQLAlchemy connection URL; no credential fallback |
| `LOG_LEVEL` | `INFO` | Application logging: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |

`LOG_LEVEL` configures Python application logging. Uvicorn's own access/server
logs can be configured with its `--log-level` option; Alembic keeps its logging
configuration in `alembic.ini`.

Compose passes the application variables explicitly and uses `POSTGRES_DB`,
`POSTGRES_USER`, and `POSTGRES_PASSWORD` to initialize PostgreSQL. Keep these
values consistent with `DATABASE_URL`. The example URL uses the Compose service
hostname `db`. For Python running outside Docker, use a reachable database host
and port; the Compose database does not publish a host port by default.

For production, inject `APP_ENV=production` and the other variables through the
runtime environment. `.env.example` contains examples only; `.env` is ignored
by Git and excluded from Docker builds. Tests set `APP_ENV=test` and an isolated
SQLite URL, so they do not need PostgreSQL or a local `.env`.

Both migration modes use the same settings:

```bash
alembic upgrade head
alembic upgrade head --sql
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
ruff check app tests migrations
pytest
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
ruff check app tests migrations
pytest
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
