# Notify Service

Краткая инструкция по локальному запуску через Docker.

## 1) Обязательные переменные окружения

Перед запуском задай переменные в текущей shell-сессии:

```bash
export RMQ_USER="your_rabbit_user"
export RMQ_PASSWORD="your_rabbit_password"
export SMTP_USER="your_smtp_user"
export SMTP_PASSWORD="your_smtp_password"
export SMTP_FROM="noreply@example.com"
```

Опционально (если нужны нестандартные значения):

```bash
export RMQ_HOST="rabbitmq"
export RMQ_PORT="5672"
export RMQ_QUEUE="notifications.service"
export RMQ_EXCHANGE="notify"
export RMQ_ROUTING_KEY="send.messages"
export DATABASE_URL="sqlite:////app/data/notifications.db"
export SMTP_HOST="smtp.yandex.ru"
export SMTP_PORT="587"
```

## 2) Запуск локально

Из корня проекта:

```bash
docker compose up -d --build
```

Логи сервиса:

```bash
docker compose logs -f notify
```

Остановка:

```bash
docker compose down
```

## 3) Как передавать env без .env на проде

Не создавай `.env` в репозитории. Перед запуском экспортируй переменные в окружение хоста (или CI runner), затем запускай:

```bash
docker compose up -d
```

Так переменные подтянутся из окружения процесса `docker compose`.

## Примечание по RabbitMQ

В `docker-compose.yml` уже добавлен контейнер `rabbitmq`, он поднимется автоматически вместе с `notify`.
`RMQ_USER` и `RMQ_PASSWORD` используются одновременно и для `notify`, и для инициализации RabbitMQ.
