# 🐳 Docker Troubleshooting Guide

## Проблема: Контейнер постоянно перезапускается

Если вы видите статус `Restarting (1)`, это означает проблему с запуском приложения.

### ✅ Решение (уже исправлено в v1.0.1+):

1. **Обновите проект до последней версии:**
   ```bash
   git pull origin main
   ```

2. **Пересоберите контейнер:**
   ```bash
   docker-compose down
   docker-compose up --build -d
   ```

3. **Проверьте статус:**
   ```bash
   docker-compose ps
   ```

### 🔧 Диагностика проблем:

#### Просмотр логов контейнера:
```bash
docker-compose logs -f ozon-ads-bot
```

#### Проверка конфигурации:
```bash
# Проверить переменные окружения
docker-compose exec ozon-ads-bot env | grep OZON

# Тест загрузки конфигурации
docker-compose exec ozon-ads-bot python -c "from config import settings; print('Config OK')"
```

#### Интерактивная отладка:
```bash
# Подключиться к контейнеру
docker-compose exec ozon-ads-bot bash

# Запустить команды вручную
python main.py --help
python main.py status
```

## Основные команды для работы с контейнером:

### Управление контейнером:
```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Пересборка
docker-compose up --build -d

# Просмотр статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f ozon-ads-bot
```

### Выполнение команд в контейнере:
```bash
# Проверка статуса API
docker-compose exec ozon-ads-bot python main.py status

# Анализ кампании
docker-compose exec ozon-ads-bot python main.py analyze CAMPAIGN_ID

# Генерация отчёта
docker-compose exec ozon-ads-bot python main.py report

# Интерактивный режим
docker-compose exec ozon-ads-bot python main.py interactive

# Только планировщик
docker-compose exec ozon-ads-bot python main.py schedule

# Только Telegram бот
docker-compose exec ozon-ads-bot python main.py telegram
```

### Режимы запуска:

#### 1. Daemon режим (по умолчанию):
Автоматически запускается планировщик + Telegram бот (если настроен)
```bash
docker-compose up -d
# Контейнер работает в фоне с планировщиком
```

#### 2. Только планировщик:
```bash
# Изменить команду в docker-compose.yml:
command: ["python", "main.py", "schedule"]
docker-compose up -d
```

#### 3. Только Telegram бот:
```bash
# Изменить команду в docker-compose.yml:
command: ["python", "main.py", "telegram"]
docker-compose up -d
```

## Настройка .env файла:

Создайте `.env` файл с вашими настройками:

```env
# Ozon API credentials (ОБЯЗАТЕЛЬНО для работы с API)
OZON_CLIENT_ID=your_real_client_id
OZON_API_KEY=your_real_api_key

# Telegram Bot (опционально)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Настройки
LOG_LEVEL=INFO
REPORT_OUTPUT_DIR=./reports
AUTO_OPTIMIZATION_ENABLED=false
```

## Частые проблемы:

### 1. "Config loading failed"
**Причина:** Отсутствует .env файл
**Решение:**
```bash
cp .env.example .env
# Отредактируйте .env файл
```

### 2. "API request failed: 401 Unauthorized"
**Причина:** Неверные API ключи
**Решение:** Проверьте OZON_CLIENT_ID и OZON_API_KEY в .env файле

### 3. "Telegram bot not initialized"
**Причина:** Не настроен TELEGRAM_BOT_TOKEN
**Решение:** Либо настройте токен, либо используйте режим без Telegram

### 4. "Permission denied" для логов
**Причина:** Проблемы с правами доступа к директории logs
**Решение:**
```bash
# Создать директории с правильными правами
mkdir -p logs reports data
chmod 755 logs reports data

# Пересобрать контейнер
docker-compose up --build -d
```

### 5. Контейнер занимает много ресурсов
**Решение:** Настройте лимиты в docker-compose.yml:
```yaml
deploy:
  resources:
    limits:
      memory: 256M
      cpus: '0.25'
```

## Мониторинг:

### Проверка ресурсов:
```bash
docker stats ozon-ads-bot
```

### Health check:
```bash
docker inspect ozon-ads-bot --format='{{json .State.Health}}'
```

### Очистка:
```bash
# Удалить контейнер с данными
docker-compose down -v

# Очистить неиспользуемые ресурсы
docker system prune -a
```

## Обновление:

```bash
# Получить последние изменения
git pull origin main

# Пересобрать и запустить
docker-compose up --build -d

# Проверить версию
docker-compose exec ozon-ads-bot python -c "print('Ozon Ads Bot v1.0.1+')"
```