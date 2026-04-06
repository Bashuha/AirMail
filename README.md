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

Сервис подключится к существующему RabbitMQ в сети `aviatx-net`.

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

| Переменная | Значение по умолчанию | Описание |
|------------|----------------------|----------|
| `DEBUG` | `True` | Режим отладки — письма только группе `admin` |
| `RMQ_HOST` | `rabbitmq` | Хост RabbitMQ (в Docker) |
| `RMQ_PORT` | `5672` | Порт RabbitMQ |
| `RMQ_USER` | `aviatx` | Пользователь RabbitMQ |
| `RMQ_PASSWORD` | `aviatx` | Пароль RabbitMQ |
| `RMQ_EXCHANGE` | `aviatx.services` | Exchange для сообщений |
| `RMQ_QUEUE` | `notifications.service` | Очередь |
| `RMQ_ROUTING_KEY` | `notify` | Routing key |
| `SMTP_HOST` | `smtp.yandex.ru` | SMTP сервер |
| `SMTP_PORT` | `587` | Порт SMTP |
| `SMTP_USER` | — | Пользователь SMTP (обязательно) |
| `SMTP_PASSWORD` | — | Пароль SMTP (обязательно) |
| `SMTP_FROM` | — | Email отправителя (обязательно) |
| `ZABBIX_URL` | — | URL Zabbix сервера (обязательно) |

## CLI-команды

### Создание группы

```bash
python cli.py create-group
```

Будет предложено ввести название новой группы. При инициализации приложения автоматически создаются группы `admins`, 'engineers'.

### Создание сотрудника (staff)

```bash
python cli.py create-staff
```

Интерактивно запросит:
1. Имя
2. Фамилию
3. Email
4. Группу из списка существующих (можно пропустить)

## Режим DEBUG

По умолчанию сервис запускается в режиме `DEBUG=True`. В этом режиме **все письма** перенаправляются только участникам группы `admins`, независимо от указанных получателей.

На продакшене необходимо явно задать `DEBUG=False` (уже прописано в `docker-compose.yml`).

| Режим | Получатели писем |
|-------|-----------------|
| `DEBUG=True` (по умолчанию) | Только группа `admin` |
| `DEBUG=False` (продакшен) | Указанные в сообщении |

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
