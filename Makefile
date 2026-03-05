.PHONY: help install run test docker-build docker-up docker-down clean lint format

help:
	@echo "ThreatSense Commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make run           - Run development server"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run code linting"
	@echo "  make format        - Format code with black"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-up     - Start Docker containers"
	@echo "  make docker-down   - Stop Docker containers"
	@echo "  make clean         - Clean up build artifacts"

install:
	pip install -r requirements.txt

run:
	uvicorn main:app --reload

test:
	pytest -v

lint:
	black --check .
	pylint **/*.py

format:
	black .

docker-build:
	docker build -t threatsense:latest .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov *.db
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
