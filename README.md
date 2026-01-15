

# Сервис обработки заявок на выплаты

Сервис управления онлайн-подписками пользователей. Написан на Python, использует Django 4.2, Celery, Guvicorn и Docker.

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
- `make make-migrations` - Создать новые миграции
- `make migrate`         - Накатить все миграции

## Как запустить дев окружение
1.  Скопировать файл `.env.example` в `.env`
2. `make up`

Сервис будет доступен на http://localhost:8000/api/v1/payouts/

http://localhost:8080/api/schema/ - Swagger документация


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

Внутри `app/subscriptions/` используется разделение по слоям:

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
│   │   ├── __init__.py
│   │   ├── settings/
│   │   │   ├── base.py        # базовые настройки
│   │   │   └── test.py        # модификация настроек тестов
│   │   ├── celery.py          # демон celery
│   │   ├── logging_filters.py # фильтры логов
│   │   ├── middleware.py      # мидлвари
│   │   ├── tracing.py         # контекст проброса trace_id
│   │   ├── urls.py            # общие ручки
│   │   └── wsgi.py            # демон uwsgi
│   ├── payouts/
│   │   ├── migrations/        # файлы миграций
│   │   │   └──── 0001_initial.py
│   │   ├── tests/
│   │   │   ├── factories.py   # фабрика тестовых моделей
│   │   │   ├── test_models.py # тестирование моделей
│   │   │   ├── test_tasks.py  # тестирование тасков celery
│   │   │   ├── test_views.py  # тестирование вьюх
│   │   ├── apps.py            # описание фичи
│   │   ├── models.py          # модели
│   │   ├── serializers.py     # серилизаторы
│   │   ├── services.py        # походы во внешние сервисы
|   |   ├── tasks.py           # таски celery
|   |   ├── urls.py            # ручки фичи
│   │   └── views.py           # вьюхи вичи
│   ├── manage.py
├───├── pyproject.toml         # настройки форматеров кода
│   └── pytest.ini             # настройки тестов
├── .env.example
├── docker-compose.yml
├── Makefile
├── Dockerfile
├── README.md
└── requirements.txt
```


