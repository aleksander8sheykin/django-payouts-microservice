export BUILDKIT_PROGRESS=plain
.PHONY: $(MAKECMDGOALS)
%:
	@:


DOCKER_IMAGE=payouts-service
COMPOSE_DEV=docker compose


# =====================
# ПОМОЩЬ
# =====================
help:
	@echo "===== Команды для локальной разработки ====="
	@echo "make test            - Запуск интеграционных тестов"
	@echo "make test-coverage   - Отчет о покрытии кода тестами"
	@echo "make lint-format     - Отформатировать код"
	@echo "make lint-check      - Проверить код"
	@echo ""
	@echo "===== Работа с Docker ====="
	@echo "make up              - Поднять docker-compose"
	@echo "make down            - Остановить все контейнеры"
	@echo "make rebuild         - Пересобрать все контейнеры"
	@echo "make restart         - Рестартануть все контейнеры"
	@echo "make logs            - Просмотр логов API"
	@echo "make workerlogs      - Просмотр логов воркера"
	@echo "make beatlogs        - Просмотр логов сборщика"
	@echo "make build-prod TAG=0.1.8  - Сборка прод-образа с нужным тегом"
	@echo "make push-prod TAG=0.1.8   - Публикация прод-образа с нужным тегом"
	@echo ""
	@echo "===== Миграции ====="
	@echo "make makemigrations     - Создать миграции"
	@echo "make migrate            - Накатить миграции"

up:
	$(COMPOSE_DEV) up -d

down:
	$(COMPOSE_DEV) down

rebuild:
	$(COMPOSE_DEV) build

restart: down up

build-prod:
	docker build -t $(DOCKER_IMAGE):$(TAG) .

push-prod:
	docker push $(DOCKER_IMAGE):$(TAG)

logs:
	$(COMPOSE_DEV) logs -f web

workerlogs:
	$(COMPOSE_DEV) logs -f worker

beatlogs:
	$(COMPOSE_DEV) logs -f beat

make-migrations:
	$(COMPOSE_DEV) run --rm web python manage.py makemigrations
	 
migrate:
	$(COMPOSE_DEV) run --rm web python manage.py migrate

test:
	$(COMPOSE_DEV) run --rm web-test bash -c "python -m pytest"

test-coverage:
	$(COMPOSE_DEV) run --rm web-test python -m pytest --cov=payouts --cov-report=term-missing

lint-check:
	$(COMPOSE_DEV) run --rm web ruff check

lint-format:
	$(COMPOSE_DEV) run --rm web ruff check --fix && $(COMPOSE_DEV) run --rm web ruff format
