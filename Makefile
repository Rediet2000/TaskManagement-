# Task Management - Development Makefile

.PHONY: up down build logs purge restart shell-backend shell-frontend

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose up -d --build

logs:
	docker-compose logs -f

restart:
	docker-compose restart

shell-backend:
	docker-compose exec backend bash

shell-frontend:
	docker-compose exec frontend bash

# Deep cleanup of the environment
purge:
	@echo "--- Purging Docker containers and volumes ---"
	docker-compose down -v --rmi all --remove-orphans || true
	@echo "--- Pruning Docker system ---"
	docker system prune -f
	@echo "--- Cleaning up local temporary files ---"
	rm -rf frontend/node_modules frontend/.angular backend/__pycache__ .pytest_cache
	@echo "--- Purge complete! ---"
	@echo "Recommendation: Run 'wsl --shutdown' in PowerShell if you still face read-only errors."
