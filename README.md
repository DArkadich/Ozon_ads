# 🤖 Ozon Ads Bot

Автоматизированный Python-агент для управления рекламными кампаниями на Ozon. Анализирует эффективность, управляет ставками и ключевыми словами, подбирает новые ключи и даёт рекомендации по оптимизации.

## 🚀 Возможности

### 📊 Анализ кампаний
- **Автоматический анализ эффективности** - CTR, CR, ДРР, ROI
- **Выявление проблемных ключевых слов** - низкий CTR, высокий ДРР, отсутствие конверсий
- **Трендовый анализ** - отслеживание динамики показателей
- **Интеллектуальные рекомендации** - на основе алгоритмов машинного обучения

### ⚙️ Оптимизация
- **Автоматическое управление ставками** - повышение/понижение на основе эффективности
- **Отключение неэффективных ключей** - ключи без заказов при большом количестве кликов
- **Добавление минус-слов** - автоматическое формирование списка негативных ключей
- **Умные пороги** - настраиваемые критерии для принятия решений

### 📈 Управление ключевыми словами
- **Подбор новых ключей** - на основе анализа товаров и конкурентов
- **Анализ семантического ядра** - выявление наиболее эффективных запросов
- **Группировка ключей** - автоматическая кластеризация по темам
- **Оптимизация типов соответствия** - точное, фразовое, широкое

### 📋 Отчётность
- **Excel отчёты** - детальная аналитика с графиками и таблицами
- **PDF отчёты** - краткие сводки для руководства
- **HTML дашборды** - интерактивные веб-отчёты
- **Автоматическая отправка** - по расписанию в Telegram или email

### 🤖 Автоматизация
- **Планировщик задач** - ежедневный анализ, еженедельные отчёты
- **Telegram бот** - управление и уведомления через мессенджер
- **Мониторинг в реальном времени** - оповещения о критических проблемах
- **Безопасный режим** - dry-run для проверки изменений

## 📦 Установка

### 🐳 Docker (рекомендуется)

#### 1. Клонирование репозитория
```bash
git clone https://github.com/yourusername/ozon-ads-bot.git
cd ozon-ads-bot
```

#### 2. Настройка конфигурации
Создайте `.env` файл:
```bash
cp .env.example .env
```

Отредактируйте `.env` файл:
```env
# Ozon API credentials (обязательно)
OZON_CLIENT_ID=your_client_id_here
OZON_API_KEY=your_api_key_here

# Telegram Bot (опционально)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Настройки
LOG_LEVEL=INFO
REPORT_OUTPUT_DIR=./reports
AUTO_OPTIMIZATION_ENABLED=false
```

#### 3. Запуск с Docker Compose
```bash
# Базовый запуск
docker-compose up -d

# С Redis (для кэширования)
docker-compose --profile with-redis up -d

# С PostgreSQL (для хранения данных)
docker-compose --profile with-db up -d

# Полная конфигурация
docker-compose --profile with-redis --profile with-db up -d
```

#### 4. Управление контейнером
```bash
# Просмотр логов
docker-compose logs -f ozon-ads-bot

# Выполнение команд в контейнере
docker-compose exec ozon-ads-bot python main.py status

# Остановка
docker-compose down

# Пересборка после изменений
docker-compose up --build -d
```

### 🔧 Локальная установка (альтернатива)

#### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

#### 2. Создание директорий
```bash
mkdir -p logs reports data
```

## 🎯 Быстрый старт

### 🐳 С Docker
```bash
# Проверка подключения
docker-compose exec ozon-ads-bot python main.py status

# Анализ кампании
docker-compose exec ozon-ads-bot python main.py analyze CAMPAIGN_ID --days 7

# Оптимизация (план)
docker-compose exec ozon-ads-bot python main.py optimize CAMPAIGN_ID --dry-run

# Генерация отчёта
docker-compose exec ozon-ads-bot python main.py report --format excel

# Интерактивный режим
docker-compose exec ozon-ads-bot python main.py interactive

# Telegram бот
docker-compose exec ozon-ads-bot python main.py telegram

# Планировщик
docker-compose exec ozon-ads-bot python main.py schedule
```

### 💻 Локально
```bash
# Проверка подключения
python main.py status

# Анализ кампании
python main.py analyze CAMPAIGN_ID --days 7

# Оптимизация (план)
python main.py optimize CAMPAIGN_ID --dry-run

# Генерация отчёта
python main.py report --format excel

# Интерактивный режим
python main.py interactive
```

## 📚 Подробное использование

### CLI команды

#### `status` - Проверка статуса
```bash
python main.py status
```
Показывает статус подключения к API и список доступных кампаний.

#### `analyze` - Анализ кампании
```bash
python main.py analyze CAMPAIGN_ID [--days 7]
```
Анализирует эффективность кампании за указанный период.

**Параметры:**
- `CAMPAIGN_ID` - ID кампании в Ozon
- `--days` - период анализа в днях (по умолчанию 7)

#### `optimize` - Оптимизация
```bash
python main.py optimize CAMPAIGN_ID [--dry-run]
```
Оптимизирует кампанию согласно алгоритму.

**Параметры:**
- `CAMPAIGN_ID` - ID кампании
- `--dry-run` - показать план без выполнения

#### `report` - Генерация отчётов
```bash
python main.py report [--campaign-id ID] [--format excel|pdf|html]
```
Создаёт отчёт по кампании.

**Параметры:**
- `--campaign-id` - ID кампании (по умолчанию первая найденная)
- `--format` - формат отчёта: excel, pdf, html

#### `schedule` - Планировщик
```bash
python main.py schedule
```
Запускает планировщик для автоматических задач:
- Ежедневный анализ в 09:00
- Еженедельные отчёты по понедельникам в 10:00
- Мониторинг каждый час

#### `telegram` - Telegram бот
```bash
python main.py telegram
```
Запускает Telegram бота для интерактивного управления.

### Telegram бот команды

После запуска бота доступны команды:

- `/start` - приветствие и список команд
- `/help` - справка по командам
- `/status` - статус системы
- `/campaigns` - список кампаний с кнопками
- `/analyze` - анализ выбранной кампании
- `/optimize` - оптимизация кампании
- `/report` - генерация и отправка отчётов
- `/schedule` - информация о расписании
- `/alerts` - настройка уведомлений

## ⚙️ Конфигурация

### Основные настройки (config.py)

```python
# Пороги для анализа
min_ctr_threshold: float = 0.5          # Минимальный CTR (%)
max_drr_threshold: float = 15.0         # Максимальный ДРР (%)
high_ctr_threshold: float = 3.0         # Высокий CTR для повышения ставок (%)
high_cr_threshold: float = 4.0          # Высокий CR для повышения ставок (%)
max_acceptable_drr: float = 25.0        # Приемлемый ДРР (%)
critical_drr_threshold: float = 50.0    # Критический ДРР (%)
min_clicks_for_analysis: int = 30       # Минимум кликов для анализа

# Корректировка ставок
bid_increase_percent: float = 20.0      # Повышение ставки (%)
bid_decrease_percent: float = 30.0      # Понижение ставки (%)
```

### Алгоритм принятия решений

#### 🔴 Критические проблемы (приоритет 90-100)
1. **Ключи без заказов** - ≥30 кликов, 0 заказов → ОТКЛЮЧИТЬ
2. **Критический ДРР** - ДРР >50% → ОТКЛЮЧИТЬ  
3. **Очень низкий CTR** - CTR <0.5%, >10 кликов → ОТКЛЮЧИТЬ

#### 📈 Возможности масштабирования (приоритет 70)
- **Высокая эффективность** - CTR >3%, CR >4%, ДРР <25% → ПОВЫСИТЬ СТАВКУ на 20%

#### 📉 Корректировка ставок (приоритет 60)
- **Высокий ДРР** - ДРР 15-50% → ПОНИЗИТЬ СТАВКУ на 30%

#### ⚠️ Предупреждения (приоритет 20-30)
- **Превышение ДРР** - ДРР >15% → МОНИТОРИТЬ
- **Низкий CTR при высоких показах** - >1000 показов, CTR <1% → МОНИТОРИТЬ

## 📊 Структура отчётов

### Excel отчёт включает:
1. **Сводка кампании** - основные метрики и рекомендации
2. **Анализ ключевых слов** - детальная таблица с цветовой индикацией
3. **Детальные рекомендации** - приоритизированный список действий

### PDF отчёт включает:
- Краткую сводку показателей
- Топ-5 рекомендаций
- Критические проблемы

## 🛡️ Безопасность

### Режим dry-run
Все оптимизационные операции по умолчанию выполняются в режиме предварительного просмотра. Для применения изменений:

1. Установите `AUTO_OPTIMIZATION_ENABLED=true` в `.env`
2. Или используйте команды без флага `--dry-run`

### Ограничения
- Максимум 5 кампаний для автоанализа
- Максимум 5 корректировок ставок за сеанс
- Автоматические уведомления о критических изменениях

## 🔧 Разработка

### Структура проекта
```
Ozon_ads/
├── main.py              # Точка входа и CLI
├── config.py            # Конфигурация
├── ozon_api.py          # Клиент Ozon API
├── data_analysis.py     # Анализ данных
├── keyword_manager.py   # Управление ключами
├── report_generator.py  # Генерация отчётов
├── scheduler.py         # Планировщик задач
├── telegram_bot.py      # Telegram интеграция
├── requirements.txt     # Зависимости
├── .env.example        # Пример конфигурации
└── README.md           # Документация
```

### Добавление новых функций

#### Новый анализатор
```python
# В data_analysis.py
def custom_analyzer(self, keyword_stats: List[Dict]) -> List[Dict]:
    # Ваша логика анализа
    pass
```

#### Новый тип отчёта
```python
# В report_generator.py  
def generate_custom_report(self, data: Dict) -> str:
    # Генерация отчёта
    pass
```

#### Новая команда CLI
```python
# В main.py
@cli.command()
def custom_command():
    """Описание команды."""
    # Логика команды
    pass
```

## 📞 Поддержка

### Логи
Логи сохраняются в директории `logs/`:
- `ozon_ads_bot.log` - основной лог с ротацией

### Типичные проблемы

#### Ошибка подключения к API
```
❌ API request failed: 401 Unauthorized
```
**Решение:** Проверьте правильность `OZON_CLIENT_ID` и `OZON_API_KEY` в `.env`

#### Telegram бот не отвечает
```
❌ Telegram bot not initialized
```
**Решение:** Убедитесь, что `TELEGRAM_BOT_TOKEN` указан в `.env`

#### Нет данных для анализа
```
⚠️ No stats found for campaign
```
**Решение:** Проверьте ID кампании и наличие данных за указанный период

## 🎉 Примеры использования

### Ежедневный мониторинг
```bash
# Утром проверяем статус
python main.py status

# Анализируем основные кампании
python main.py analyze 12345 --days 1
python main.py analyze 67890 --days 1

# Создаём сводный отчёт
python main.py report --format excel
```

### Еженедельная оптимизация
```bash
# Анализ за неделю
python main.py analyze 12345 --days 7

# Планируем оптимизацию
python main.py optimize 12345 --dry-run

# Применяем изменения (осторожно!)
python main.py optimize 12345
```

### Автоматический режим
```bash
# Запуск планировщика
python main.py schedule &

# Запуск Telegram бота
python main.py telegram &
```

## 📄 Лицензия

MIT License - используйте свободно для коммерческих и некоммерческих целей.

---

**Создано с ❤️ для эффективного управления рекламой на Ozon**