.PHONY: dev frontend test eval clean docker-up docker-down docker-dev docker-dev-down docker-dev-build docker-dev-logs docker-dev-backend

# Local native development
dev:
	uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

frontend:
	cd frontend && npm run dev

# Docker development with live hot-reloading (via ./docker-dev.sh)
docker-dev:
	./docker-dev.sh up

docker-dev-d:
	./docker-dev.sh up -d

docker-dev-backend:
	./docker-dev.sh backend

docker-dev-build:
	./docker-dev.sh build

docker-dev-down:
	./docker-dev.sh down

docker-dev-logs:
	./docker-dev.sh logs

# Docker standard / production stack
docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

# Evaluation & Testing
eval:
	python3 -m eval.runners.run_benchmarks

test:
	pytest tests/ -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
