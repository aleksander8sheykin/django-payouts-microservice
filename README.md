

# Сервис обработки заявок на выплаты

Сервис управления онлайн-подписками пользователей. Написан на Python, использует Django 4.2, Redis, Celery, Guvicorn и Docker.

## Особенности конфигурации

Нужно скопировать файл `.env.example` в `.env`

Файл `.env.example` используется только как пример для Docker Compose.

## Makefile команды
###  Команды для локальной разработки
- `make test`            - Запуск интеграционных тестов
- `make coverage`        - Отчет о покрытии кода тестами

### Работа с Docker
- `make up`              - Поднять docker-compose
- `make down`            - Остановить все контейнеры
- `make build`           - Пересобрать базовый образ
- `make restart`         - Рестартануть все контейнеры
- `make logs`            - Просмотр логов API
- `make workerlogs`      - Просмотр логов воркера
- `make beatlogs`        - Просмотр логов сборщика
- `make build-prod TAG=0.1.8`   - Сборка прод-образа с нужным тегом
- `make push-prod TAG=0.1.8`    - Публикация прод-образа с нужным тегом


### Миграции
- `make makemigrations`  - Создать новые миграции
- `make migrate`         - Накатить все миграции

## Как запустить дев окружение
1.  Скопировать файл `.env.example` в `.env`
2. `make up`

Сервис будет доступен на http://localhost:8000/api/payouts/

http://localhost:8080/api/schema/ - Swagger документация

## API ручки

Базовый URL: `http://localhost:8000`

### Проверка здоровья

`GET /healthz/`

**Пример запроса**
```bash
curl http://localhost:8000/healthz/
```

**Пример ответа**
```json
{"status": "ok"}
```

### Получить список заявок

`GET /api/payouts/`

Ответ — пагинированный список (по умолчанию до 100 записей на страницу).

**Параметры запроса**
- `user_id` (обязательный) — идентификатор пользователя. Без него список пуст.
- `page` — номер страницы (по умолчанию `1`).

**Пример запроса**
```bash
curl "http://localhost:8000/api/payouts/?user_id=123&page=2"
```

**Пример ответа**
```json
{
  "count": 120,
  "next": "http://localhost:8000/api/payouts/?user_id=123&page=3",
  "previous": "http://localhost:8000/api/payouts/?user_id=123&page=1",
  "results": [
    {
      "id": 101,
      "user_id": 123,
      "amount": 100.5,
      "currency": "RUB",
      "status": "pending",
      "created_at": "2026-01-14T12:00:00Z",
      "updated_at": "2026-01-14T12:05:00Z",
      "processed_at": null
    }
  ]
}
```

### Создать заявку

`POST /api/payouts/`

**Пример запроса**
```bash
curl -X POST http://localhost:8000/api/payouts/ \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: aabbccdd12345" \
  -d '{
    "user_id": 123,
    "amount": 100.50,
    "currency": "RUB",
    "recipient_details": {"card": "0000 1111 2222 3333"},
    "comment": "Оплата бонуса"
  }'
```

**Пример ответа**
```json
{
  "id": 1,
  "user_id": 123,
  "amount": 100.5,
  "currency": "RUB",
  "recipient_details": {"card": "0000 1111 2222 3333"},
  "comment": "Оплата бонуса",
  "status": "pending",
  "created_at": "2026-01-14T12:00:00Z",
  "updated_at": "2026-01-14T12:00:00Z",
  "processed_at": null
}
```

Если заголовок `X-Request-ID` не передан, он будет сгенерирован и вернётся в ответе.

### Получить заявку по ID

`GET /api/payouts/{id}/`

**Пример запроса**
```bash
curl http://localhost:8000/api/payouts/1/
```

**Пример ответа**
```json
{
  "id": 1,
  "user_id": 123,
  "amount": 100.5,
  "currency": "RUB",
  "status": "pending",
  "created_at": "2026-01-14T12:00:00Z",
  "updated_at": "2026-01-14T12:05:00Z",
  "processed_at": null
}
```

### Обновить статус заявки

`PATCH /api/payouts/{id}/`

Разрешено менять только поле `status`.

**Пример запроса**
```bash
curl -X PATCH http://localhost:8000/api/payouts/1/ \
  -H "Content-Type: application/json" \
  -d '{"status": "processed"}'
```

**Пример ответа**
```json
{
  "id": 1,
  "user_id": 123,
  "amount": 100.5,
  "currency": "RUB",
  "recipient_details": {"card": "0000 1111 2222 3333"},
  "comment": "Оплата бонуса",
  "status": "processed",
  "created_at": "2026-01-14T12:00:00Z",
  "updated_at": "2026-01-14T12:10:00Z",
  "processed_at": "2026-01-14T12:10:00Z"
}
```

### Удалить заявку

`DELETE /api/payouts/{id}/`

**Пример запроса**
```bash
curl -X DELETE http://localhost:8000/api/payouts/1/
```

**Пример ответа**
```
HTTP/1.1 204 No Content
```

### Схема OpenAPI

`GET /api/schema/`

**Пример запроса**
```bash
curl http://localhost:8080/api/schema/
```

## Прод‑деплой в Kubernetes (описание)

### Предпосылки
- Контейнерный образ собирается из [`Dockerfile`](Dockerfile:1) и использует переменные окружения из [`.env.example`](.env.example:1). В проде значения должны храниться в Secret/ConfigMap.
- Django читает настройки из переменных окружения, см. [`src/core/settings/base.py`](src/core/settings/base.py:1).

### Состав сервисов и ресурсов
- **web**: Deployment с Gunicorn, контейнер из образа приложения. Рекомендуемая команда: `gunicorn core.wsgi:application --bind 0.0.0.0:8000`.
- **worker**: Deployment Celery worker (`celery -A core worker -l info`).
- **beat**: Deployment или CronJob для Celery beat (`celery -A core beat -l info`).
- **db**: PostgreSQL (StatefulSet + PVC) или управляемая БД.
- **redis**: Redis (StatefulSet + PVC) или управляемый Redis.
- **ingress**: Ingress + TLS сертификаты.
- **secrets/configmaps**: `DJANGO_SECRET_KEY`, параметры БД, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`, `LOG_LEVEL`.

### Минимальные шаги (примерный порядок)
1. Собрать и опубликовать образ: `make build-prod TAG=...` и `make push-prod TAG=...` (или через CI/CD).
2. Создать namespace, Secret и ConfigMap для всех переменных из [`.env.example`](.env.example:1).
3. Применить манифесты БД и Redis (или подключить управляемые сервисы).
4. Применить Deployment для **web**, **worker**, **beat**, Service для web и Ingress с TLS.
5. Выполнить миграции как Job: `python manage.py migrate`.
6. Проверить доступность `/api/payouts/` и `/api/schema/` через Ingress.

### Health‑checks и масштабирование
- **web**: readiness/liveness probes на `/api/payouts/` или `/api/schema/`.
- **worker/beat**: liveness probe на процесс (TCP или exec). Масштабировать worker по длине очереди (HPA/KEDA).

### CI/CD и откаты
- В CI: тесты → сборка → пуш образа → применение манифестов.
- Рекомендуется тегировать образ по commit SHA.
- Использовать `kubectl rollout status` для контроля и `kubectl rollout undo` для отката Deployment.

### Логи, мониторинг и бэкапы
- Логи в stdout (уже настроено в [`src/core/settings/base.py`](src/core/settings/base.py:1)); собирать через Loki/ELK.
- Метрики: Prometheus + Grafana (Gunicorn/Django и Celery).
- Бэкапы PostgreSQL: регулярные снапшоты/pg_dump.


### Запуск тестов

В проекте представлены только интеграционные тесты, так как логика микросервиса
не подразумевает сложное деление кода и перепроверка каждого изолированного слоя
избыточна.

Интеграционные тесты используют базу проекта с постфиксом `_test`

- Интеграционные тесты:
```bash
make test
```

-  Отчёт тестов с покрытием:
```bash
make test-coverage
```

## Архитектура

Проект построен по feature-based подходу, где вся логика собрана по фичам, которы находятя в папке src

Фича `payouts` - отвечает за заявки

Внутри `src/payouts/` используется разделение по слоям:

- urls — голые ручки
- views — бизнес логика
- tasks — Celery задачи
- models — модели данных

`src/core` - Отвечает за общие модули между фичами


Структура проекта
```
project/
├── src/
│   ├── core/
│   │   ├── __init__.py         # пакет core
│   │   ├── celery.py           # демон celery
│   │   ├── logging_filters.py  # фильтры логов
│   │   ├── middleware.py       # мидлвари
│   │   ├── tracing.py          # контекст проброса trace_id
│   │   ├── urls.py             # общие ручки
│   │   ├── views.py            # healthcheck
│   │   ├── wsgi.py             # демон uwsgi
│   │   ├── settings/
│   │   │   ├── __init__.py     # пакет настроек
│   │   │   ├── base.py         # базовые настройки
│   │   │   └── test.py         # модификация настроек тестов
│   │   └── tests/
│   │       ├── __init__.py     # пакет тестов core
│   │       └── test_tracing.py # тесты trace_id
│   ├── payouts/
│   │   ├── __init__.py         # пакет фичи
│   │   ├── apps.py             # описание фичи
│   │   ├── currency_choices.py # справочник валют
│   │   ├── migrations/         # файлы миграций
│   │   │   ├── __init__.py     # пакет миграций
│   │   │   └── 0001_initial.py # начальная миграция
│   │   ├── pagination.py       # пагинация
│   │   ├── models.py           # модели
│   │   ├── serializers.py      # сериализаторы
│   │   ├── services.py         # походы во внешние сервисы
│   │   ├── tasks.py            # таски celery
│   │   ├── urls.py             # ручки фичи
│   │   ├── views.py            # вьюхи фичи
│   │   └── tests/
│   │       ├── __init__.py     # пакет тестов
│   │       ├── factories.py    # фабрика тестовых моделей
│   │       ├── test_models.py  # тестирование моделей
│   │       ├── test_serializers.py # тестирование сериализаторов
│   │       ├── test_services.py    # тестирование сервисов
│   │       ├── test_tasks.py   # тестирование тасков celery
│   │       └── test_views.py   # тестирование вьюх
│   ├── manage.py
│   ├── pyproject.toml          # настройки форматеров кода
│   └── pytest.ini              # настройки тестов
├── .env.example
├── .gitignore
├── .roo/                       # служебные файлы Roo
├── AGENTS.md
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── README.md
├── requirements.txt
├── TZ.md
└── plans/
    ├── fixes_summary.md
    ├── project_schema_overview.md
    └── tz_gap_analysis.md
```
