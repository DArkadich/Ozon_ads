# 🐳 Docker Guide для Ozon Ads Bot

## 🚀 Быстрый старт с Docker

### 1. Подготовка
```bash
# Клонирование репозитория
git clone https://github.com/yourusername/ozon-ads-bot.git
cd ozon-ads-bot

# Настройка окружения
cp .env.example .env
# Отредактируйте .env файл с вашими API ключами
```

### 2. Базовый запуск
```bash
# Запуск основного контейнера
docker-compose up -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f ozon-ads-bot
```

### 3. Выполнение команд
```bash
# Проверка подключения к API
docker-compose exec ozon-ads-bot python main.py status

# Анализ кампании
docker-compose exec ozon-ads-bot python main.py analyze CAMPAIGN_ID

# Интерактивный режим
docker-compose exec ozon-ads-bot python main.py interactive
```

## 🔧 Конфигурации

### Базовая конфигурация
Только основной бот без дополнительных сервисов:
```bash
docker-compose up -d
```

### С Redis (кэширование)
Для улучшения производительности:
```bash
docker-compose --profile with-redis up -d
```

### С PostgreSQL (база данных)
Для хранения исторических данных:
```bash
docker-compose --profile with-db up -d
```

### Полная конфигурация
Все сервисы включены:
```bash
docker-compose --profile with-redis --profile with-db up -d
```

## 📁 Структура томов

Docker Compose автоматически создаёт тома для:

- `./logs` → `/app/logs` - логи приложения
- `./reports` → `/app/reports` - сгенерированные отчёты  
- `./data` → `/app/data` - дополнительные данные

## ⚙️ Переменные окружения

Создайте `.env` файл со следующими параметрами:

```env
# Ozon API (обязательно)
OZON_CLIENT_ID=your_client_id_here
OZON_API_KEY=your_api_key_here

# Telegram Bot (опционально)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Настройки приложения
LOG_LEVEL=INFO
REPORT_OUTPUT_DIR=./reports
AUTO_OPTIMIZATION_ENABLED=false

# База данных (если используете PostgreSQL)
POSTGRES_PASSWORD=your_secure_password_here
```

## 🔄 Управление контейнерами

### Основные команды
```bash
# Запуск в фоне
docker-compose up -d

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Пересборка и запуск
docker-compose up --build -d

# Удаление с данными
docker-compose down -v
```

### Просмотр состояния
```bash
# Статус контейнеров
docker-compose ps

# Логи всех сервисов
docker-compose logs

# Логи конкретного сервиса
docker-compose logs ozon-ads-bot

# Следить за логами в реальном времени
docker-compose logs -f ozon-ads-bot
```

### Выполнение команд
```bash
# Интерактивная оболочка
docker-compose exec ozon-ads-bot bash

# Выполнение Python команд
docker-compose exec ozon-ads-bot python main.py --help

# Запуск Telegram бота
docker-compose exec ozon-ads-bot python main.py telegram

# Запуск планировщика
docker-compose exec ozon-ads-bot python main.py schedule
```

## 🛠️ Разработка

### Локальная разработка с Docker
```bash
# Монтирование исходного кода для разработки
docker-compose -f docker-compose.dev.yml up -d

# Пересборка после изменений
docker-compose up --build -d
```

### Отладка
```bash
# Подключение к контейнеру
docker-compose exec ozon-ads-bot bash

# Проверка переменных окружения
docker-compose exec ozon-ads-bot env

# Проверка конфигурации
docker-compose exec ozon-ads-bot python -c "from config import settings; print(settings.dict())"
```

## 📊 Мониторинг

### Health Check
Docker Compose включает health check для основного контейнера:
```bash
# Проверка состояния
docker-compose ps

# Детальная информация о health check
docker inspect ozon-ads-bot --format='{{json .State.Health}}'
```

### Ресурсы
Контейнер настроен с ограничениями:
- **Memory**: 512MB (лимит), 256MB (резерв)
- **CPU**: 0.5 ядра (лимит), 0.25 ядра (резерв)

### Логирование
Логи ограничены:
- **Размер файла**: 10MB
- **Количество файлов**: 3

## 🔐 Безопасность

### Пользователь
Контейнер запускается от непривилегированного пользователя `ozonbot`.

### Сеть
Все сервисы изолированы в отдельной сети `ozon-bot-network`.

### Секреты
Используйте Docker secrets для production:
```bash
# Создание секрета
echo "your_api_key" | docker secret create ozon_api_key -

# Использование в docker-compose
secrets:
  ozon_api_key:
    external: true
```

## 🚀 Production

### Рекомендации для production
1. **Используйте внешнюю базу данных** вместо контейнера PostgreSQL
2. **Настройте backup** для томов с данными
3. **Используйте reverse proxy** (nginx) для веб-интерфейса
4. **Настройте мониторинг** (Prometheus + Grafana)
5. **Используйте Docker Swarm или Kubernetes** для оркестрации

### Пример production docker-compose
```yaml
version: '3.8'
services:
  ozon-ads-bot:
    image: your-registry/ozon-ads-bot:latest
    restart: always
    env_file: .env.production
    volumes:
      - /opt/ozon-bot/logs:/app/logs
      - /opt/ozon-bot/reports:/app/reports
    networks:
      - production-network
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
```

## ❓ Troubleshooting

### Частые проблемы

#### Контейнер не запускается
```bash
# Проверьте логи
docker-compose logs ozon-ads-bot

# Проверьте конфигурацию
docker-compose config
```

#### Ошибки API
```bash
# Проверьте переменные окружения
docker-compose exec ozon-ads-bot env | grep OZON

# Тест подключения
docker-compose exec ozon-ads-bot python main.py status
```

#### Проблемы с правами доступа
```bash
# Проверьте владельца файлов
docker-compose exec ozon-ads-bot ls -la /app

# Исправление прав (если нужно)
sudo chown -R 1000:1000 logs reports data
```

#### Нехватка ресурсов
```bash
# Проверьте использование ресурсов
docker stats ozon-ads-bot

# Увеличьте лимиты в docker-compose.yml
```

### Полезные команды
```bash
# Очистка неиспользуемых ресурсов
docker system prune -a

# Информация о Docker
docker info

# Проверка версии
docker --version
docker-compose --version
```