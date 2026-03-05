# Notification Service

Микросервис для рассылки сообщений. Работает через RabbitMQ.

## Требования

- Docker и Docker Compose

## Запуск

```bash
sudo chmod +x setup.sh
sudo bash setup.sh
```
После запуска Вам будет предложено ввести переменные окружения.

В итоге у нас поднимутся два сервиса:
- **RabbitMQ** (порты 5672) — брокер сообщений
- **Notify** — сервис уведомлений

## Обновление сервиса

При наличии изменений в репозитории:

```bash
# Получить последние изменения
git pull

# Пересобрать и перезапустить контейнеры
docker compose up -d --build
```

Если нужно только перезапустить без пересборки:
```bash
docker compose restart
```

## Переменные окружения

| Переменная | Значение по умолчанию |
|------------|----------------------|
| `RMQ_HOST` | `rabbitmq` |
| `RMQ_PORT` | `5672` |
| `RMQ_USER` | `aviatx` |
| `RMQ_PASSWORD` | `aviatx` |
| `RMQ_EXCHANGE` | `notify` |
| `RMQ_QUEUE` | `notifications.service` |
| `RMQ_ROUTING_KEY` | `send.messages` |
| `SMTP_USER` | - |
| `SMTP_PASSWORD` | - |
| `SMTP_FROM` | - |
| `SMTP_PORT` | `587` |
| `SMTP_HOST` | `smtp.yandex.ru` |

## Логи

Логи сохраняются в директорию `./logs/` (монтируется из контейнера).

## Локальный запуск (без Docker)

1. Установить зависимости:
```bash
pip install -r requirements.txt
```

2. Создать файл `.env` с переменными окружения:
```env
SMTP_USER=your_user
SMTP_PASSWORD=your_pass
SMTP_FROM=your_sender
```

3. Запустить сервис:
```bash
python consumer.py
```
