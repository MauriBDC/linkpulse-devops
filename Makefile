.PHONY: up down logs test build

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f api

test:
	pytest -q

build:
	docker build -t linkpulse:local .
