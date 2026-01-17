# Расхождения между TZ.md и текущим кодом

## 1) Модель данных

- TZ требует поле валюта; в модели нет валюты (сейчас есть `payout_method` и `payout_details`).
- TZ требует реквизиты получателя; в модели есть `payout_details`, но по требованию их нужно удалить и заменить на отдельные реквизиты получателя.
- TZ требует дату обновления; в модели нет `updated_at`.
- TZ требует комментарий; в модели нет комментария.
- TZ требует сумма беззнаковая; сейчас `amount` допускает отрицательные значения на уровне валидации.
- По требованиям: убрать `payout_method` и `payout_details` из модели.

## 2) REST API

- TZ требует `GET /api/payouts/` (список), `PATCH /api/payouts/{id}/`, `DELETE /api/payouts/{id}/`.
- В коде есть только `POST /api/v1/payouts/` и `GET /api/v1/payouts/{id}/`.
- TZ требует путь `/api/payouts/` (без `v1`), а сейчас используется `/api/v1/payouts/`.

## 3) Сериализация и валидация

- Сериализатор включает `payout_method` и `payout_details`, которые должны быть удалены.
- Нет валидации `amount > 0` (беззнаковость) и выбора валюты из ISO 4217.

## 4) Celery задачи и сервисы

- Задача и gateway используют `payout_method` и `payout_details`, которые планируются к удалению.
- В `reconcile_processing_payouts` используется поле `processing_started_at`, которого нет в модели.

## 5) Тесты

- Тесты привязаны к старым путям `/api/v1/payouts/` и отсутствию list/patch/delete.
- Тесты используют старые поля `payout_method` и `payout_details`.

## 6) Документация и Swagger

- README указывает `/api/v1/payouts/`; требуется `/api/payouts/`.
- Примеры в Swagger (drf-spectacular) используют старые поля.

## 7) Прочие несоответствия

- В сериализаторе `amount` имеет `max_digits=12`, а в модели `max_digits=10`.
