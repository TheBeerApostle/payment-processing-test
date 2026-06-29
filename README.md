# Payment Processing Service


> Асинхронный микросервис для обработки платежей с использованием Outbox Pattern, RabbitMQ и PostgreSQL.

## Технологии

- **FastAPI** + Pydantic v2
- **SQLAlchemy 2.0** (async)
- **PostgreSQL** + asyncpg
- **RabbitMQ** + aio-pika
- **Alembic** для миграций
- **Docker** + Docker Compose
- **Pytest** для тестирования

## Быстрый старт

### Запуск через Docker

```bash
# Клонирование
git clone <your-repo-url>
cd test_processing

# Настройка окружения
cp .env.example .env

# Запуск всех сервисов
sudo docker compose up -d

# Проверка статуса
sudo docker compose ps

# Просмотр логов
sudo docker compose logs -f
```

## Локальный запуск (для разработки)


```bash
# Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Установка зависимостей
pip install -r requirements.txt

# Применение миграций
alembic upgrade head

# Запуск API
uvicorn app.main:app --reload

# В отдельных терминалах запустить:
python -m app.services.outbox_runner
python -m app.consumer.run_consumer
```

## API Endpoints
### Создание платежа

```bash
curl -X POST http://localhost:8001/api/v1/payments \
  -H "X-API-Key: test-api-key-12345" \
  -H "Idempotency-Key: unique-key-001" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "100.50",
    "currency": "RUB",
    "description": "Test payment",
    "meta": {"order_id": "12345"},
    "webhook_url": "https://webhook.site/your-id"
  }'
```
### Получение платежа
```bash
curl -X GET http://localhost:8001/api/v1/payments/{payment_id} \
  -H "X-API-Key: test-api-key-12345"
```

## Мониторинг
### Health Check
```bash
curl http://localhost:8001/health
```

### RabbitMQ Management UI
```bash
http://localhost:15673
Login: guest
Password: guest
```

### Логи сервисов
```bash
# Все логи
sudo docker compose logs -f

# Конкретный сервис
sudo docker compose logs api -f
sudo docker compose logs outbox_processor -f
sudo docker compose logs consumer -f
```

## Структура проекта
```bash
test_processing/
├── app/
│   ├── api/              # API эндпоинты
│   ├── consumer/         # Обработчик платежей
│   ├── repository/       # Работа с БД
│   ├── services/         # Бизнес-логика
│   ├── utils/            # Утилиты (webhook)
│   ├── models.py         # SQLAlchemy модели
│   ├── schemas.py        # Pydantic схемы
│   ├── database.py       # Подключение к БД
│   └── main.py           # Точка входа
├── alembic/              # Миграции БД
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```
## Тестирование
```bash
# Запуск тестов
python app/tests/test_api.py
```
## Миграции
```bash
# Создать новую миграцию
alembic revision --autogenerate -m "description"

# Применить миграции
alembic upgrade head

# Откатить последнюю
alembic downgrade -1
```

## Зависимости
```bash
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
psycopg2-binary==2.9.9
aiosqlite==0.19.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
aiohttp==3.9.1
aio-pika==9.3.0
aiormq==6.7.7
alembic==1.13.1
httpx==0.25.2
pytest==7.4.3
pytest-asyncio==0.21.1
```
## Особенности
✅ Асинхронная обработка платежей

✅ Outbox Pattern для гарантированной доставки

✅ Идемпотентность через Idempotency-Key

✅ Webhook уведомления с ретраями

✅ Dead Letter Queue для ошибочных сообщений

✅ Docker-контейнеризация
