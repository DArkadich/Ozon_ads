# 🚀 Быстрое исправление проблем Docker

## Проблема: "Token must contain a colon" и права доступа

### ✅ Решение (v1.0.3+):

1. **Обновите проект:**
   ```bash
   git pull origin main
   ```

2. **Обновите .env файл:**
   ```bash
   # Добавьте эту строку в .env файл:
   DISABLE_FILE_LOGGING=1
   ```

3. **Пересоберите контейнер:**
   ```bash
   docker-compose down
   docker-compose up --build -d
   ```

4. **Проверьте работу:**
   ```bash
   docker-compose logs -f ozon-ads-bot
   ```

   Теперь должно показать:
   ```
   🤖 Запуск Ozon Ads Bot в daemon режиме...
   📅 Планировщик запущен
   ⚠️ Telegram бот не настроен, работает только планировщик
   ```

### 🔧 Что было исправлено:

1. **Telegram токен:** Добавлена проверка на пустые токены
2. **Права доступа:** Отключено файловое логирование при проблемах с правами
3. **Обработка ошибок:** Улучшена обработка ошибок инициализации

### 📝 Полный .env файл для тестирования:

```env
# Ozon API credentials (для тестирования)
OZON_CLIENT_ID=test_client_id
OZON_API_KEY=test_api_key

# Telegram Bot (отключен для тестирования)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Настройки приложения
LOG_LEVEL=INFO
REPORT_OUTPUT_DIR=./reports
AUTO_OPTIMIZATION_ENABLED=false

# Отключить файловое логирование
DISABLE_FILE_LOGGING=1
```

### 🎯 Команды для проверки:

```bash
# Статус контейнера
docker-compose ps

# Логи приложения
docker-compose logs -f ozon-ads-bot

# Проверка API (когда настроите реальные ключи)
docker-compose exec ozon-ads-bot python main.py status

# Интерактивный режим
docker-compose exec ozon-ads-bot python main.py interactive
```

### 🚀 Готово!

Теперь контейнер должен работать стабильно без ошибок "Token must contain a colon" и проблем с правами доступа. 