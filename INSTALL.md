# 🚀 Установка Ozon Ads Bot

## 📋 Требования

### Для Docker (рекомендуется)
- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Доступ к Ozon Seller API** (Client ID и API Key)

### Для локальной установки
- **Python 3.8+** (рекомендуется 3.11+)
- **pip** (менеджер пакетов Python)
- **Доступ к Ozon Seller API** (Client ID и API Key)

## 🐳 Установка с Docker (рекомендуется)

### 1. Клонирование репозитория
```bash
git clone https://github.com/yourusername/ozon-ads-bot.git
cd ozon-ads-bot
```

### 2. Настройка конфигурации
```bash
cp .env.example .env
# Отредактируйте .env файл с вашими API ключами
```

### 3. Запуск
```bash
# Базовый запуск
docker-compose up -d

# Проверка статуса
docker-compose exec ozon-ads-bot python main.py status
```

Подробнее см. [DOCKER.md](DOCKER.md)

## 💻 Локальная установка

### 1. Установка зависимостей
```bash
pip3 install -r requirements.txt
```

### 2. Создание директорий
```bash
mkdir -p logs reports data
```

### 3. Настройка конфигурации
```bash
cp .env.example .env
# Отредактируйте .env файл
```

### 4. Проверка работы
```bash
python3 main.py status
```

## 🤖 Telegram бот (опционально)

### 1. Создайте бота через @BotFather
### 2. Добавьте токен в `.env`:
```env
TELEGRAM_BOT_TOKEN=ваш_токен_бота
TELEGRAM_CHAT_ID=ваш_chat_id
```

### 3. Запустите бота:
```bash
python3 main.py telegram
```

## 🆘 Решение проблем

### Ошибка: `command not found: python`
Используйте `python3` вместо `python`

### Ошибка: `401 Unauthorized`
Проверьте правильность API ключей в `.env`

### Ошибка: `ModuleNotFoundError`
Переустановите зависимости:
```bash
pip3 install -r requirements.txt
```

### Проблемы с Excel/PDF отчётами
Установите дополнительные зависимости:
```bash
pip3 install openpyxl fpdf2
```

## 📊 Структура проекта

```
Ozon_ads/
├── main.py              # 🚪 Главная точка входа
├── demo.py              # 🎯 Демонстрация возможностей
├── setup.py             # ⚙️ Автоматический установщик
├── config.py            # 🔧 Конфигурация
├── ozon_api.py          # 🌐 Клиент Ozon API
├── data_analysis.py     # 📊 Анализ данных
├── keyword_manager.py   # 🔑 Управление ключами
├── report_generator.py  # 📋 Генерация отчётов
├── scheduler.py         # ⏰ Планировщик задач
├── telegram_bot.py      # 🤖 Telegram интеграция
├── requirements.txt     # 📦 Зависимости
├── .env                 # 🔐 Конфигурация (создаётся)
├── logs/               # 📝 Логи
└── reports/            # 📊 Отчёты
```

## 🎉 Готово!

После успешной установки вы можете:

1. **Анализировать кампании** - `python3 main.py analyze CAMPAIGN_ID`
2. **Оптимизировать ключи** - `python3 main.py optimize CAMPAIGN_ID --dry-run`
3. **Генерировать отчёты** - `python3 main.py report`
4. **Запускать автоматизацию** - `python3 main.py schedule`
5. **Использовать Telegram** - `python3 main.py telegram`

---

**💡 Совет:** Начните с команды `python3 main.py interactive` для знакомства с возможностями бота!