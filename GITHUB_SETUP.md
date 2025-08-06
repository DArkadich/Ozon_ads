# 🚀 Публикация на GitHub

## Шаги для публикации:

1. **Создайте репозиторий на GitHub:**
   - Перейдите на https://github.com/new
   - Название: `ozon-ads-bot`
   - Описание: `🤖 Автоматизация рекламных кампаний на Ozon с Docker поддержкой`
   - Public репозиторий
   - НЕ добавляйте README, .gitignore, License (уже есть)

2. **Подключите локальный репозиторий:**
   ```bash
   git remote add origin https://github.com/YOURUSERNAME/ozon-ads-bot.git
   git branch -M main
   git push -u origin main
   ```

3. **Настройте GitHub Actions:**
   - Actions будут работать автоматически при push
   - Для публикации Docker образов нужны права на packages

4. **Создайте первый релиз:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

## Готово! 🎉
