# VMS Áquila - Makefile para gestión del proyecto

.PHONY: help build up down logs clean dev test install-sdks

# Variables
COMPOSE_FILE = docker-compose.yml
PROJECT_NAME = vms-aquila

help: ## Mostrar ayuda
	@echo "VMS Áquila - Comandos disponibles:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Construir todas las imágenes Docker
	docker-compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME) build

up: ## Levantar todos los servicios
	docker-compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME) up -d

down: ## Detener todos los servicios
	docker-compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME) down

logs: ## Ver logs de todos los servicios
	docker-compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME) logs -f

logs-backend: ## Ver logs del backend
	docker-compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME) logs -f backend

logs-frontend: ## Ver logs del frontend
	docker-compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME) logs -f frontend

clean: ## Limpiar contenedores, volúmenes e imágenes
	docker-compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME) down -v --rmi all
	docker system prune -f

dev: ## Modo desarrollo (con rebuild automático)
	docker-compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME) up --build

restart: ## Reiniciar todos los servicios
	docker-compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME) restart

restart-backend: ## Reiniciar solo el backend
	docker-compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME) restart backend

status: ## Ver estado de los servicios
	docker-compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME) ps

shell-backend: ## Acceder al shell del backend
	docker-compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME) exec backend /bin/bash

shell-db: ## Acceder al shell de la base de datos
	docker-compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME) exec db psql -U postgres -d vmsdb

install-sdks: ## Crear directorios para SDKs
	@echo "Creando directorios para SDKs..."
	mkdir -p backend/sdk/hikvision
	mkdir -p backend/sdk/dahua
	@echo "Directorio creado. Coloca los binarios SDK en:"
	@echo "  - backend/sdk/hikvision/ (HCNetSDK.dll, etc.)"
	@echo "  - backend/sdk/dahua/ (dhnetsdk.dll, etc.)"

setup: install-sdks ## Configuración inicial del proyecto
	@echo "Configurando VMS Áquila..."
	cp .env.example .env
	@echo "Archivo .env creado. Ajusta las variables según tu configuración."
	@echo "Ejecuta 'make build' para construir las imágenes."

test: ## Ejecutar tests
	docker-compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME) exec backend python -m pytest

migrate: ## Ejecutar migraciones de base de datos
	docker-compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME) exec backend python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"

backup-db: ## Hacer backup de la base de datos
	docker-compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME) exec db pg_dump -U postgres vmsdb > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db: ## Restaurar base de datos (requiere archivo como argumento)
	@if [ -z "$(FILE)" ]; then echo "Uso: make restore-db FILE=backup.sql"; exit 1; fi
	docker-compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME) exec -T db psql -U postgres vmsdb < $(FILE)

monitor: ## Monitorear recursos del sistema
	docker stats $(shell docker-compose -f $(COMPOSE_FILE) -p $(PROJECT_NAME) ps -q)

health: ## Verificar salud de los servicios
	@echo "Verificando salud de los servicios..."
	@curl -f http://localhost:8000/api/health || echo "Backend no disponible"
	@curl -f http://localhost:3000 || echo "Frontend no disponible"
	@curl -f http://localhost/health || echo "Nginx no disponible"
