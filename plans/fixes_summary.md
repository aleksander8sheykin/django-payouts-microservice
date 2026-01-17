# Список исправлений по TZ.md

## Модель данных

- Добавлены поля `currency`, `recipient_details`, `comment`, `updated_at` в модель [`Payout`](src/payouts/models.py:4).
- Удалены поля `payout_method` и `payout_details` (по требованиям).
- Для `amount` добавлен валидатор `MinValueValidator(0.01)` для беззнаковости.
- Добавлен справочник валют ISO 4217 в [`src/payouts/currency_choices.py`](src/payouts/currency_choices.py).
- Обновлена миграция [`src/payouts/migrations/0001_initial.py`](src/payouts/migrations/0001_initial.py:1) под новые поля и валидаторы.

## API и маршруты

- Обновлён корневой путь API на `/api/payouts/` в [`src/core/urls.py`](src/core/urls.py:1).
- Реализованы все ручки из TZ: список, создание, получение, PATCH статуса, удаление в [`src/payouts/views.py`](src/payouts/views.py:1).
- Упрощён роутинг payouts до двух endpoint’ов: `/api/payouts/` и `/api/payouts/{id}/` в [`src/payouts/urls.py`](src/payouts/urls.py:1).
- Для списка настроен пагинатор с лимитом 100 и исключением чувствительных полей в ответах: [`src/payouts/pagination.py`](src/payouts/pagination.py), [`PayoutPublicSerializer`](src/payouts/serializers.py:24).

## Сериализация и валидация

- Обновлён [`PayoutSerializer`](src/payouts/serializers.py:6): новые поля, `amount` с точностью 10, валидация `amount > 0`, `currency` только из ISO 4217.
- Добавлен [`PayoutPublicSerializer`](src/payouts/serializers.py:24) для исключения `recipient_details` и `comment` в списке и GET по id.
- Добавлен [`PayoutStatusUpdateSerializer`](src/payouts/serializers.py:29) для PATCH только статуса.

## Celery и сервисы

- Обновлены параметры `send_payment` на `currency` и `recipient_details` в [`src/payouts/services.py`](src/payouts/services.py:15).
- Исправлено использование несуществующего поля в `reconcile_processing_payouts` (заменено на `updated_at`) в [`src/payouts/tasks.py`](src/payouts/tasks.py:62).

## Тесты

- Обновлены фабрики и тесты моделей/задач/вьюх под новые поля и URL `/api/payouts/`:
  - [`src/payouts/tests/factories.py`](src/payouts/tests/factories.py:1)
  - [`src/payouts/tests/test_models.py`](src/payouts/tests/test_models.py:1)
  - [`src/payouts/tests/test_tasks.py`](src/payouts/tests/test_tasks.py:1)
  - [`src/payouts/tests/test_views.py`](src/payouts/tests/test_views.py:1)
- Добавлены тесты списка, PATCH статуса и DELETE.

## Документация

- README: путь сервиса исправлен на `/api/payouts/` в [`README.md`](README.md:34).
