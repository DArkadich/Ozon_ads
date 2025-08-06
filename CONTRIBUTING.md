# 🤝 Contributing to Ozon Ads Bot

Спасибо за интерес к проекту! Мы приветствуем любые вклады в развитие бота.

## 🚀 Как начать

### 1. Fork репозитория
```bash
# Создайте fork на GitHub, затем клонируйте
git clone https://github.com/yourusername/ozon-ads-bot.git
cd ozon-ads-bot
```

### 2. Настройка окружения разработки
```bash
# Создайте ветку для фичи
git checkout -b feature/your-feature-name

# Запуск в режиме разработки с Docker
docker-compose -f docker-compose.dev.yml up -d
```

### 3. Внесение изменений
```bash
# Внесите изменения
# Протестируйте изменения
docker-compose exec ozon-ads-bot python -m pytest

# Проверьте код-стиль
docker-compose exec ozon-ads-bot flake8 .
```

### 4. Создание Pull Request
```bash
git add .
git commit -m "feat: добавить новую функцию"
git push origin feature/your-feature-name
# Создайте PR на GitHub
```

## 📋 Стандарты кода

### Python Code Style
- **PEP 8** для стиля кода
- **Type hints** для всех функций
- **Docstrings** для классов и функций
- **Maximum line length**: 127 символов

### Commit Messages
Используйте [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: добавить новую функцию
fix: исправить ошибку в анализе
docs: обновить документацию
style: исправить форматирование
refactor: рефакторинг кода
test: добавить тесты
chore: обновить зависимости
```

### Структура кода
```python
"""Module docstring."""
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ExampleClass:
    """Class docstring."""
    
    def __init__(self, param: str) -> None:
        """Initialize class."""
        self.param = param
    
    def method(self, data: Dict[str, Any]) -> Optional[str]:
        """Method docstring.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Processed string or None
        """
        logger.info(f"Processing data: {len(data)} items")
        return self._process(data)
    
    def _process(self, data: Dict[str, Any]) -> Optional[str]:
        """Private method."""
        # Implementation
        pass
```

## 🧪 Тестирование

### Запуск тестов
```bash
# Все тесты
docker-compose exec ozon-ads-bot python -m pytest

# С покрытием
docker-compose exec ozon-ads-bot python -m pytest --cov=.

# Конкретный файл
docker-compose exec ozon-ads-bot python -m pytest tests/test_analysis.py
```

### Написание тестов
```python
import pytest
from unittest.mock import Mock, patch
from data_analysis import CampaignAnalyzer


class TestCampaignAnalyzer:
    """Test campaign analyzer."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.analyzer = CampaignAnalyzer()
    
    def test_analyze_keywords(self):
        """Test keyword analysis."""
        mock_data = [
            {
                'keyword': 'test keyword',
                'ctr': 2.5,
                'cr': 5.0,
                'drr': 20.0,
                'clicks': 100,
                'orders': 5
            }
        ]
        
        result = self.analyzer.analyze_keywords(mock_data)
        
        assert len(result) == 1
        assert result[0]['action'] in ['pause', 'increase_bid', 'decrease_bid', 'keep', 'monitor']
```

## 📖 Документация

### Обновление README
- Обновите README.md при добавлении новых функций
- Добавьте примеры использования
- Обновите список зависимостей

### Docstrings
```python
def analyze_campaign(self, campaign_id: str, days: int = 7) -> Dict[str, Any]:
    """Analyze campaign performance.
    
    Analyzes campaign metrics for the specified period and provides
    recommendations for optimization.
    
    Args:
        campaign_id: Ozon campaign identifier
        days: Number of days to analyze (default: 7)
        
    Returns:
        Dictionary containing:
            - campaign_id: Campaign identifier
            - summary: Performance summary
            - analysis: Detailed keyword analysis
            - period: Analysis period
            
    Raises:
        OzonAPIError: If API request fails
        ValueError: If campaign_id is invalid
        
    Example:
        >>> bot = OzonAdsBot()
        >>> result = bot.analyze_campaign('12345', days=14)
        >>> print(result['summary']['performance_metrics']['overall_ctr'])
        2.45
    """
```

## 🔧 Типы вкладов

### 🐛 Bug Reports
- Используйте GitHub Issues
- Приложите логи и шаги воспроизведения
- Укажите версию и окружение

### ✨ Feature Requests
- Опишите проблему, которую решает фича
- Предложите решение
- Рассмотрите альтернативы

### 📝 Documentation
- README, DOCKER.md, API документация
- Комментарии в коде
- Примеры использования

### 🧪 Tests
- Unit tests для новых функций
- Integration tests для API
- Performance tests для критических путей

## 🏗️ Архитектура

### Добавление нового анализатора
```python
# В data_analysis.py
class NewAnalyzer:
    """New analysis functionality."""
    
    def analyze(self, data: List[Dict]) -> List[Dict]:
        """Analyze data and return recommendations."""
        pass

# Интеграция в CampaignAnalyzer
def analyze_keywords(self, keyword_stats: List[Dict]) -> List[Dict]:
    # ... existing code ...
    
    # Добавить новый анализатор
    new_analyzer = NewAnalyzer()
    additional_analysis = new_analyzer.analyze(keyword_stats)
    
    # Объединить результаты
    return self._merge_analysis(analysis, additional_analysis)
```

### Добавление нового типа отчёта
```python
# В report_generator.py
def generate_custom_report(self, data: Dict, filename: str = None) -> str:
    """Generate custom report format."""
    # Implementation
    pass
```

### Добавление новой команды CLI
```python
# В main.py
@cli.command()
@click.argument('param')
@click.option('--option', default='default', help='Option description')
def new_command(param, option):
    """New command description."""
    try:
        bot = OzonAdsBot()
        result = bot.new_functionality(param, option)
        click.echo(f"Result: {result}")
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")
```

## 🔄 Release Process

### Версионирование
Используем [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes

### Создание релиза
1. Обновите версию в коде
2. Обновите CHANGELOG.md
3. Создайте git tag: `git tag v1.2.3`
4. Push tag: `git push origin v1.2.3`
5. GitHub Actions автоматически создаст релиз

## 🛡️ Безопасность

### Секреты
- Никогда не коммитьте API ключи
- Используйте `.env.example` для примеров
- Проверяйте `.gitignore`

### Зависимости
- Регулярно обновляйте зависимости
- Проверяйте уязвимости: `pip audit`
- Используйте зафиксированные версии

## ❓ Вопросы?

- **GitHub Issues**: Для багов и фич
- **GitHub Discussions**: Для вопросов
- **Email**: your-email@example.com

Спасибо за вклад в проект! 🚀