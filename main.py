"""Main entry point for Ozon Ads Bot."""
import asyncio
import os
import sys
from datetime import datetime, timedelta
from typing import Optional
import click
from loguru import logger

# Import our modules
from config import settings
from ozon_api import OzonAPIClient
from data_analysis import CampaignAnalyzer
from keyword_manager import KeywordManager
from report_generator import ReportGenerator
from scheduler import CampaignScheduler
from telegram_bot import TelegramBot


class OzonAdsBot:
    """Main bot class that coordinates all components."""
    
    def __init__(self):
        """Initialize the bot with all components."""
        logger.info("Initializing Ozon Ads Bot")
        
        # Initialize components
        self.ozon_client = OzonAPIClient()
        self.analyzer = CampaignAnalyzer()
        self.keyword_manager = KeywordManager(self.ozon_client)
        self.report_generator = ReportGenerator()
        
        # Initialize scheduler
        self.scheduler = CampaignScheduler(
            ozon_client=self.ozon_client,
            analyzer=self.analyzer,
            keyword_manager=self.keyword_manager,
            report_generator=self.report_generator
        )
        
        # Initialize Telegram bot
        self.telegram_bot = TelegramBot(
            ozon_client=self.ozon_client,
            analyzer=self.analyzer,
            keyword_manager=self.keyword_manager,
            report_generator=self.report_generator,
            scheduler=self.scheduler
        )
        
        # Setup scheduler callbacks
        self._setup_callbacks()
    
    def _setup_callbacks(self):
        """Setup callbacks between components."""
        if self.telegram_bot.bot:
            self.scheduler.add_callback('on_analysis_complete', self.telegram_bot.notify_analysis_complete)
            self.scheduler.add_callback('on_optimization_complete', self.telegram_bot.notify_optimization_complete)
            self.scheduler.add_callback('on_critical_issue', self.telegram_bot.notify_critical_issue)
    
    def start_scheduler(self):
        """Start the scheduler."""
        self.scheduler.start()
        logger.info("Scheduler started")
    
    def start_telegram_bot(self):
        """Start Telegram bot."""
        if self.telegram_bot.bot:
            self.telegram_bot.start_polling()
        else:
            logger.warning("Telegram bot not configured")
    
    def analyze_campaign(self, campaign_id: str, days: int = 7) -> dict:
        """Analyze specific campaign."""
        logger.info(f"Analyzing campaign {campaign_id}")
        
        date_to = datetime.now().strftime('%Y-%m-%d')
        date_from = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Get data
        stats = self.ozon_client.get_campaign_stats(campaign_id, date_from, date_to)
        keyword_stats = self.ozon_client.get_keyword_stats(campaign_id, date_from, date_to)
        
        # Analyze
        analysis = self.analyzer.analyze_keywords(keyword_stats)
        summary = self.analyzer.get_campaign_summary(stats, analysis)
        
        return {
            'campaign_id': campaign_id,
            'summary': summary,
            'analysis': analysis,
            'period': f"{date_from} - {date_to}"
        }
    
    def optimize_campaign(self, campaign_id: str, dry_run: bool = True) -> dict:
        """Optimize specific campaign."""
        logger.info(f"Optimizing campaign {campaign_id} (dry_run={dry_run})")
        
        # Analyze first
        analysis_result = self.analyze_campaign(campaign_id)
        analysis = analysis_result['analysis']
        
        optimization_results = {
            'campaign_id': campaign_id,
            'dry_run': dry_run,
            'actions_planned': 0,
            'actions_executed': 0,
            'paused_keywords': [],
            'bid_adjustments': [],
            'errors': []
        }
        
        # Find keywords to pause
        pause_keywords = [k['keyword'] for k in analysis if k['action'] == 'pause']
        optimization_results['actions_planned'] += len(pause_keywords)
        
        if pause_keywords:
            if not dry_run:
                success = self.ozon_client.pause_keywords(campaign_id, pause_keywords)
                if success:
                    optimization_results['actions_executed'] += len(pause_keywords)
                    optimization_results['paused_keywords'] = pause_keywords
                else:
                    optimization_results['errors'].append("Failed to pause keywords")
            else:
                optimization_results['paused_keywords'] = pause_keywords
        
        # Find bid adjustments
        bid_adjustments = self.keyword_manager.suggest_bid_adjustments(analysis)
        high_confidence = [b for b in bid_adjustments if b['priority'] >= 70]
        
        optimization_results['actions_planned'] += len(high_confidence)
        
        for adjustment in high_confidence:
            if not dry_run:
                success = self.ozon_client.update_keyword_bid(
                    campaign_id,
                    adjustment['keyword'],
                    adjustment['suggested_bid']
                )
                if success:
                    optimization_results['actions_executed'] += 1
                    optimization_results['bid_adjustments'].append(adjustment)
                else:
                    optimization_results['errors'].append(f"Failed to update bid for {adjustment['keyword']}")
            else:
                optimization_results['bid_adjustments'].append(adjustment)
        
        return optimization_results
    
    def generate_report(self, campaign_id: str = None, format_type: str = "excel") -> str:
        """Generate report for campaign(s)."""
        if campaign_id:
            analysis_result = self.analyze_campaign(campaign_id)
            summary = analysis_result['summary']
            analysis = analysis_result['analysis']
        else:
            # Get first available campaign
            campaigns = self.ozon_client.get_all_campaigns()
            if not campaigns:
                raise ValueError("No campaigns found")
            
            campaign_id = str(campaigns[0].get('id', ''))
            analysis_result = self.analyze_campaign(campaign_id)
            summary = analysis_result['summary']
            analysis = analysis_result['analysis']
        
        if format_type == "excel":
            return self.report_generator.generate_excel_report(summary, analysis)
        elif format_type == "pdf":
            return self.report_generator.generate_pdf_report(summary)
        elif format_type == "html":
            return self.report_generator.generate_html_report(summary, analysis)
        else:
            raise ValueError(f"Unsupported format: {format_type}")


# CLI Interface
@click.group()
@click.option('--log-level', default='INFO', help='Log level')
def cli(log_level):
    """Ozon Ads Bot - автоматизация рекламных кампаний на Ozon."""
    logger.remove()
    logger.add(sys.stdout, level=log_level)
    logger.add("logs/ozon_ads_bot.log", rotation="1 day", retention="30 days", level=log_level)


@cli.command()
def status():
    """Проверить статус подключения к API."""
    try:
        bot = OzonAdsBot()
        campaigns = bot.ozon_client.get_all_campaigns()
        
        click.echo(f"✅ Подключение к Ozon API: OK")
        click.echo(f"📊 Найдено кампаний: {len(campaigns)}")
        
        for campaign in campaigns[:5]:  # Show first 5
            click.echo(f"   • {campaign.get('name', 'Без названия')} (ID: {campaign.get('id')})")
        
        if len(campaigns) > 5:
            click.echo(f"   ... и ещё {len(campaigns) - 5} кампаний")
    
    except Exception as e:
        click.echo(f"❌ Ошибка: {str(e)}")


@cli.command()
@click.argument('campaign_id')
@click.option('--days', default=7, help='Период анализа в днях')
def analyze(campaign_id, days):
    """Анализ эффективности кампании."""
    try:
        bot = OzonAdsBot()
        result = bot.analyze_campaign(campaign_id, days)
        
        summary = result['summary']
        metrics = summary['performance_metrics']
        
        click.echo(f"\n📊 Анализ кампании {campaign_id}")
        click.echo(f"📅 Период: {result['period']}")
        click.echo(f"\n💰 Показатели:")
        click.echo(f"   • Расходы: {metrics['total_spend']:.2f} ₽")
        click.echo(f"   • Выручка: {metrics['total_revenue']:.2f} ₽")
        click.echo(f"   • CTR: {metrics['overall_ctr']:.2f}%")
        click.echo(f"   • CR: {metrics['overall_cr']:.2f}%")
        click.echo(f"   • ДРР: {metrics['overall_drr']:.2f}%")
        click.echo(f"   • ROI: {metrics['overall_roi']:.2f}")
        
        actions = summary.get('actions_needed', {})
        if any(actions.values()):
            click.echo(f"\n🎯 Необходимые действия:")
            if actions.get('pause', 0) > 0:
                click.echo(f"   • 🔴 Отключить: {actions['pause']} ключей")
            if actions.get('increase_bid', 0) > 0:
                click.echo(f"   • 📈 Повысить ставки: {actions['increase_bid']} ключей")
            if actions.get('decrease_bid', 0) > 0:
                click.echo(f"   • 📉 Понизить ставки: {actions['decrease_bid']} ключей")
        
        recommendations = summary.get('recommendations', [])
        if recommendations:
            click.echo(f"\n💡 Рекомендации:")
            for rec in recommendations:
                click.echo(f"   • {rec}")
    
    except Exception as e:
        click.echo(f"❌ Ошибка анализа: {str(e)}")


@cli.command()
@click.argument('campaign_id')
@click.option('--dry-run', is_flag=True, help='Показать план без выполнения')
def optimize(campaign_id, dry_run):
    """Оптимизация кампании."""
    if not dry_run and not settings.auto_optimization_enabled:
        click.echo("⚠️ Автооптимизация отключена в настройках. Используйте --dry-run для просмотра плана.")
        return
    
    try:
        bot = OzonAdsBot()
        result = bot.optimize_campaign(campaign_id, dry_run)
        
        mode = "План оптимизации" if dry_run else "Результат оптимизации"
        click.echo(f"\n⚙️ {mode} для кампании {campaign_id}")
        
        click.echo(f"📋 Запланировано действий: {result['actions_planned']}")
        if not dry_run:
            click.echo(f"✅ Выполнено действий: {result['actions_executed']}")
        
        if result['paused_keywords']:
            click.echo(f"\n🔴 Ключи для отключения ({len(result['paused_keywords'])}):")
            for keyword in result['paused_keywords'][:10]:  # Show first 10
                click.echo(f"   • {keyword}")
        
        if result['bid_adjustments']:
            click.echo(f"\n💰 Корректировка ставок ({len(result['bid_adjustments'])}):")
            for adj in result['bid_adjustments'][:10]:  # Show first 10
                direction = "↗️" if adj['adjustment_percent'] > 0 else "↘️"
                click.echo(f"   • {adj['keyword']}: {direction} {abs(adj['adjustment_percent']):.1f}%")
        
        if result['errors']:
            click.echo(f"\n❌ Ошибки:")
            for error in result['errors']:
                click.echo(f"   • {error}")
    
    except Exception as e:
        click.echo(f"❌ Ошибка оптимизации: {str(e)}")


@cli.command()
@click.option('--campaign-id', help='ID кампании (по умолчанию - первая найденная)')
@click.option('--format', 'format_type', default='excel', 
              type=click.Choice(['excel', 'pdf', 'html']), help='Формат отчёта')
def report(campaign_id, format_type):
    """Генерация отчёта."""
    try:
        bot = OzonAdsBot()
        filepath = bot.generate_report(campaign_id, format_type)
        
        click.echo(f"📊 Отчёт создан: {filepath}")
        
        # Show file size
        size = os.path.getsize(filepath) / 1024  # KB
        click.echo(f"📁 Размер файла: {size:.1f} KB")
    
    except Exception as e:
        click.echo(f"❌ Ошибка создания отчёта: {str(e)}")


@cli.command()
def schedule():
    """Запуск планировщика задач."""
    try:
        bot = OzonAdsBot()
        bot.start_scheduler()
        
        click.echo("📅 Планировщик запущен")
        click.echo("⏰ Расписание:")
        click.echo("   • Ежедневный анализ: 09:00")
        click.echo("   • Еженедельный отчёт: Понедельник 10:00")
        click.echo("   • Мониторинг: каждый час")
        
        if settings.auto_optimization_enabled:
            click.echo("   • Автооптимизация: 11:00")
        else:
            click.echo("   • Автооптимизация: отключена")
        
        click.echo("\nНажмите Ctrl+C для остановки")
        
        # Keep running
        try:
            while True:
                asyncio.sleep(1)
        except KeyboardInterrupt:
            click.echo("\n🛑 Остановка планировщика...")
            bot.scheduler.stop()
    
    except Exception as e:
        click.echo(f"❌ Ошибка планировщика: {str(e)}")


@cli.command()
def telegram():
    """Запуск Telegram бота."""
    if not settings.telegram_bot_token:
        click.echo("❌ Telegram bot token не настроен в .env файле")
        return
    
    try:
        bot = OzonAdsBot()
        
        click.echo("🤖 Запуск Telegram бота...")
        click.echo(f"📱 Bot token: {settings.telegram_bot_token[:20]}...")
        
        if settings.telegram_chat_id:
            click.echo(f"💬 Chat ID: {settings.telegram_chat_id}")
        
        click.echo("\nНажмите Ctrl+C для остановки")
        
        # Start both scheduler and telegram bot
        bot.start_scheduler()
        bot.start_telegram_bot()  # This will block
    
    except KeyboardInterrupt:
        click.echo("\n🛑 Остановка бота...")
    except Exception as e:
        click.echo(f"❌ Ошибка Telegram бота: {str(e)}")


@cli.command()
def interactive():
    """Интерактивный режим."""
    try:
        bot = OzonAdsBot()
        
        click.echo("🚀 Добро пожаловать в Ozon Ads Bot!")
        click.echo("Доступные команды: analyze, optimize, report, schedule, quit")
        
        while True:
            command = click.prompt("\nВведите команду", type=str).lower().strip()
            
            if command == 'quit' or command == 'exit':
                break
            
            elif command == 'analyze':
                campaigns = bot.ozon_client.get_all_campaigns()
                if campaigns:
                    click.echo("\nДоступные кампании:")
                    for i, camp in enumerate(campaigns[:10]):
                        click.echo(f"{i+1}. {camp.get('name', 'Без названия')} (ID: {camp.get('id')})")
                    
                    try:
                        choice = click.prompt("Выберите номер кампании", type=int)
                        if 1 <= choice <= len(campaigns):
                            campaign_id = str(campaigns[choice-1].get('id'))
                            result = bot.analyze_campaign(campaign_id)
                            
                            # Show summary
                            summary = result['summary']
                            metrics = summary['performance_metrics']
                            
                            click.echo(f"\n📊 Результат анализа:")
                            click.echo(f"CTR: {metrics['overall_ctr']:.2f}% | "
                                     f"CR: {metrics['overall_cr']:.2f}% | "
                                     f"ДРР: {metrics['overall_drr']:.2f}%")
                        else:
                            click.echo("❌ Неверный номер кампании")
                    except (ValueError, click.Abort):
                        click.echo("❌ Отменено")
                else:
                    click.echo("❌ Кампании не найдены")
            
            elif command == 'schedule':
                bot.start_scheduler()
                click.echo("✅ Планировщик запущен в фоновом режиме")
            
            elif command == 'report':
                try:
                    filepath = bot.generate_report()
                    click.echo(f"✅ Отчёт создан: {filepath}")
                except Exception as e:
                    click.echo(f"❌ Ошибка: {str(e)}")
            
            else:
                click.echo("❌ Неизвестная команда. Доступные: analyze, optimize, report, schedule, quit")
    
    except KeyboardInterrupt:
        click.echo("\n👋 До свидания!")
    except Exception as e:
        click.echo(f"❌ Ошибка: {str(e)}")


if __name__ == '__main__':
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    cli()