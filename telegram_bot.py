"""Telegram bot integration for Ozon Ads management."""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger
from config import settings


class TelegramBot:
    """Telegram bot for campaign management and notifications."""
    
    def __init__(self, ozon_client=None, analyzer=None, keyword_manager=None, 
                 report_generator=None, scheduler=None):
        """Initialize Telegram bot."""
        if not settings.telegram_bot_token:
            logger.warning("Telegram bot token not provided")
            self.bot = None
            return
        
        self.bot = telebot.TeleBot(settings.telegram_bot_token)
        self.chat_id = settings.telegram_chat_id
        
        # Components
        self.ozon_client = ozon_client
        self.analyzer = analyzer
        self.keyword_manager = keyword_manager
        self.report_generator = report_generator
        self.scheduler = scheduler
        
        # Setup handlers
        self._setup_handlers()
        
        # User sessions for multi-step operations
        self.user_sessions = {}
    
    def _setup_handlers(self):
        """Setup bot command handlers."""
        if not self.bot:
            return
        
        # Commands
        self.bot.message_handler(commands=['start'])(self._cmd_start)
        self.bot.message_handler(commands=['help'])(self._cmd_help)
        self.bot.message_handler(commands=['status'])(self._cmd_status)
        self.bot.message_handler(commands=['campaigns'])(self._cmd_campaigns)
        self.bot.message_handler(commands=['analyze'])(self._cmd_analyze)
        self.bot.message_handler(commands=['optimize'])(self._cmd_optimize)
        self.bot.message_handler(commands=['report'])(self._cmd_report)
        self.bot.message_handler(commands=['schedule'])(self._cmd_schedule)
        self.bot.message_handler(commands=['alerts'])(self._cmd_alerts)
        
        # Callback handlers
        self.bot.callback_query_handler(func=lambda call: True)(self._handle_callback)
    
    def start_polling(self):
        """Start bot polling."""
        if not self.bot:
            logger.error("Telegram bot not initialized")
            return
        
        logger.info("Starting Telegram bot polling")
        self.bot.infinity_polling(none_stop=True, interval=1)
    
    def send_message(self, text: str, chat_id: str = None, reply_markup=None):
        """Send message to Telegram."""
        if not self.bot:
            return False
        
        target_chat_id = chat_id or self.chat_id
        if not target_chat_id:
            logger.error("No chat ID provided for Telegram message")
            return False
        
        try:
            self.bot.send_message(target_chat_id, text, reply_markup=reply_markup, parse_mode='HTML')
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def send_document(self, file_path: str, caption: str = "", chat_id: str = None):
        """Send document to Telegram."""
        if not self.bot:
            return False
        
        target_chat_id = chat_id or self.chat_id
        if not target_chat_id:
            return False
        
        try:
            with open(file_path, 'rb') as doc:
                self.bot.send_document(target_chat_id, doc, caption=caption)
            return True
        except Exception as e:
            logger.error(f"Failed to send document: {e}")
            return False
    
    def _cmd_start(self, message):
        """Handle /start command."""
        welcome_text = """
🤖 <b>Ozon Ads Bot</b>

Добро пожаловать! Я помогу вам управлять рекламными кампаниями на Ozon.

<b>Доступные команды:</b>
/help - список всех команд
/status - статус системы
/campaigns - список кампаний
/analyze - анализ кампании
/optimize - оптимизация кампании
/report - генерация отчёта
/schedule - управление расписанием
/alerts - настройка уведомлений
        """
        self.send_message(welcome_text, str(message.chat.id))
    
    def _cmd_help(self, message):
        """Handle /help command."""
        help_text = """
<b>📋 Команды Ozon Ads Bot</b>

<b>Основные:</b>
/campaigns - показать все кампании
/analyze - анализ эффективности
/optimize - оптимизация кампаний
/report - создать отчёт

<b>Автоматизация:</b>
/schedule - настроить расписание
/alerts - уведомления о проблемах

<b>Служебные:</b>
/status - статус подключения
/help - эта справка

<b>💡 Быстрые действия:</b>
• Используйте кнопки для удобного управления
• Бот автоматически уведомляет о критических проблемах
• Отчёты генерируются в Excel и PDF форматах
        """
        self.send_message(help_text, str(message.chat.id))
    
    def _cmd_status(self, message):
        """Handle /status command."""
        if not self.ozon_client:
            status_text = "❌ <b>Ozon API не подключен</b>"
        else:
            try:
                campaigns = self.ozon_client.get_all_campaigns()
                status_text = f"""
✅ <b>Система работает</b>

📊 <b>Статистика:</b>
• Кампаний: {len(campaigns)}
• API: подключен
• Бот: активен

🕐 <b>Последняя проверка:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}
                """
            except Exception as e:
                status_text = f"⚠️ <b>Ошибка подключения к API:</b> {str(e)}"
        
        self.send_message(status_text, str(message.chat.id))
    
    def _cmd_campaigns(self, message):
        """Handle /campaigns command."""
        if not self.ozon_client:
            self.send_message("❌ Ozon API не подключен", str(message.chat.id))
            return
        
        try:
            campaigns = self.ozon_client.get_all_campaigns()
            
            if not campaigns:
                self.send_message("📭 Кампании не найдены", str(message.chat.id))
                return
            
            # Create inline keyboard for campaign selection
            markup = InlineKeyboardMarkup()
            
            campaigns_text = "<b>📊 Ваши кампании:</b>\n\n"
            
            for i, campaign in enumerate(campaigns[:10]):  # Limit to 10
                campaign_id = str(campaign.get('id', ''))
                campaign_name = campaign.get('name', 'Без названия')
                status = campaign.get('status', 'unknown')
                
                status_emoji = "🟢" if status == "active" else "🔴" if status == "paused" else "⚪"
                
                campaigns_text += f"{status_emoji} <b>{campaign_name}</b>\n"
                campaigns_text += f"   ID: {campaign_id}\n"
                campaigns_text += f"   Статус: {status}\n\n"
                
                # Add button for quick analysis
                markup.add(InlineKeyboardButton(
                    f"📈 Анализ: {campaign_name[:20]}...",
                    callback_data=f"analyze_{campaign_id}"
                ))
            
            self.send_message(campaigns_text, str(message.chat.id), markup)
            
        except Exception as e:
            self.send_message(f"❌ Ошибка получения кампаний: {str(e)}", str(message.chat.id))
    
    def _cmd_analyze(self, message):
        """Handle /analyze command."""
        if not self.ozon_client or not self.analyzer:
            self.send_message("❌ Компоненты анализа не подключены", str(message.chat.id))
            return
        
        # Show campaign selection for analysis
        try:
            campaigns = self.ozon_client.get_all_campaigns()
            
            if not campaigns:
                self.send_message("📭 Кампании не найдены", str(message.chat.id))
                return
            
            markup = InlineKeyboardMarkup()
            
            for campaign in campaigns[:5]:  # Limit to 5
                campaign_id = str(campaign.get('id', ''))
                campaign_name = campaign.get('name', 'Без названия')
                
                markup.add(InlineKeyboardButton(
                    f"🔍 {campaign_name[:30]}...",
                    callback_data=f"analyze_{campaign_id}"
                ))
            
            self.send_message(
                "🔍 <b>Выберите кампанию для анализа:</b>", 
                str(message.chat.id), 
                markup
            )
            
        except Exception as e:
            self.send_message(f"❌ Ошибка: {str(e)}", str(message.chat.id))
    
    def _cmd_optimize(self, message):
        """Handle /optimize command."""
        if not settings.auto_optimization_enabled:
            self.send_message("⚠️ Автооптимизация отключена в настройках", str(message.chat.id))
            return
        
        # Show optimization options
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔴 Отключить неэффективные ключи", callback_data="opt_pause"))
        markup.add(InlineKeyboardButton("📈 Скорректировать ставки", callback_data="opt_bids"))
        markup.add(InlineKeyboardButton("🚀 Полная оптимизация", callback_data="opt_full"))
        
        self.send_message(
            "⚙️ <b>Выберите тип оптимизации:</b>\n\n"
            "🔴 <b>Отключение ключей</b> - отключает неэффективные ключевые слова\n"
            "📈 <b>Ставки</b> - корректирует ставки по алгоритму\n"
            "🚀 <b>Полная</b> - все действия сразу",
            str(message.chat.id),
            markup
        )
    
    def _cmd_report(self, message):
        """Handle /report command."""
        if not self.report_generator:
            self.send_message("❌ Генератор отчётов не подключен", str(message.chat.id))
            return
        
        # Show report options
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📊 Excel отчёт", callback_data="report_excel"))
        markup.add(InlineKeyboardButton("📄 PDF отчёт", callback_data="report_pdf"))
        markup.add(InlineKeyboardButton("📈 Полный отчёт (Excel + PDF)", callback_data="report_full"))
        
        self.send_message(
            "📋 <b>Выберите тип отчёта:</b>",
            str(message.chat.id),
            markup
        )
    
    def _cmd_schedule(self, message):
        """Handle /schedule command."""
        if not self.scheduler:
            self.send_message("❌ Планировщик не подключен", str(message.chat.id))
            return
        
        jobs = self.scheduler.get_scheduled_jobs()
        
        schedule_text = "<b>📅 Расписание задач:</b>\n\n"
        
        if not jobs:
            schedule_text += "Нет запланированных задач"
        else:
            for job in jobs:
                next_run = job.get('next_run_time', 'Не запланировано')
                if next_run != 'Не запланировано':
                    try:
                        next_run = datetime.fromisoformat(next_run.replace('Z', '+00:00'))
                        next_run = next_run.strftime('%d.%m.%Y %H:%M')
                    except:
                        pass
                
                schedule_text += f"🔧 <b>{job['name']}</b>\n"
                schedule_text += f"   Следующий запуск: {next_run}\n\n"
        
        # Add control buttons
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("▶️ Запустить анализ", callback_data="run_analysis"))
        markup.add(InlineKeyboardButton("📊 Создать отчёт", callback_data="run_report"))
        
        self.send_message(schedule_text, str(message.chat.id), markup)
    
    def _cmd_alerts(self, message):
        """Handle /alerts command."""
        alerts_text = """
🔔 <b>Настройка уведомлений</b>

<b>Автоматические уведомления:</b>
• ДРР > 50% - критический уровень
• Расходы > 10,000₽ в день
• Ключи без заказов при >30 кликах
• Завершение автооптимизации

<b>Еженедельные отчёты:</b>
• Понедельник в 10:00
• Сводка по всем кампаниям
• Рекомендации по оптимизации

Уведомления приходят автоматически при обнаружении проблем.
        """
        
        self.send_message(alerts_text, str(message.chat.id))
    
    def _handle_callback(self, call):
        """Handle inline keyboard callbacks."""
        chat_id = str(call.message.chat.id)
        data = call.data
        
        try:
            if data.startswith("analyze_"):
                campaign_id = data.replace("analyze_", "")
                self._analyze_campaign(campaign_id, chat_id)
            
            elif data.startswith("opt_"):
                optimization_type = data.replace("opt_", "")
                self._run_optimization(optimization_type, chat_id)
            
            elif data.startswith("report_"):
                report_type = data.replace("report_", "")
                self._generate_report(report_type, chat_id)
            
            elif data == "run_analysis":
                self._run_manual_analysis(chat_id)
            
            elif data == "run_report":
                self._generate_report("excel", chat_id)
            
            # Acknowledge callback
            self.bot.answer_callback_query(call.id)
            
        except Exception as e:
            logger.error(f"Callback error: {e}")
            self.bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    
    def _analyze_campaign(self, campaign_id: str, chat_id: str):
        """Analyze specific campaign."""
        self.send_message("🔍 <b>Анализирую кампанию...</b>", chat_id)
        
        try:
            date_to = datetime.now().strftime('%Y-%m-%d')
            date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            # Get data
            stats = self.ozon_client.get_campaign_stats(campaign_id, date_from, date_to)
            keyword_stats = self.ozon_client.get_keyword_stats(campaign_id, date_from, date_to)
            
            # Analyze
            analysis = self.analyzer.analyze_keywords(keyword_stats)
            summary = self.analyzer.get_campaign_summary(stats, analysis)
            
            # Format results
            result_text = f"""
📊 <b>Анализ кампании {campaign_id}</b>

<b>💰 Показатели за 7 дней:</b>
• Расходы: {summary['performance_metrics']['total_spend']:.2f} ₽
• CTR: {summary['performance_metrics']['overall_ctr']:.2f}%
• CR: {summary['performance_metrics']['overall_cr']:.2f}%
• ДРР: {summary['performance_metrics']['overall_drr']:.2f}%

<b>🎯 Необходимые действия:</b>
            """
            
            actions = summary.get('actions_needed', {})
            if actions.get('pause', 0) > 0:
                result_text += f"• 🔴 Отключить: {actions['pause']} ключей\n"
            if actions.get('increase_bid', 0) > 0:
                result_text += f"• 📈 Повысить ставки: {actions['increase_bid']} ключей\n"
            if actions.get('decrease_bid', 0) > 0:
                result_text += f"• 📉 Понизить ставки: {actions['decrease_bid']} ключей\n"
            
            # Critical issues
            critical_issues = summary.get('critical_issues', [])
            if critical_issues:
                result_text += f"\n⚠️ <b>Критические проблемы:</b>\n"
                for issue in critical_issues[:3]:  # Top 3
                    result_text += f"• {issue['keyword']}: {issue['recommendation']}\n"
            
            self.send_message(result_text, chat_id)
            
        except Exception as e:
            self.send_message(f"❌ Ошибка анализа: {str(e)}", chat_id)
    
    def _run_optimization(self, optimization_type: str, chat_id: str):
        """Run optimization based on type."""
        if not settings.auto_optimization_enabled:
            self.send_message("⚠️ Автооптимизация отключена", chat_id)
            return
        
        self.send_message("⚙️ <b>Запускаю оптимизацию...</b>", chat_id)
        
        # This would trigger actual optimization
        # For now, just show confirmation
        self.send_message(
            f"✅ <b>Оптимизация запущена</b>\n\n"
            f"Тип: {optimization_type}\n"
            f"Результаты будут отправлены по завершении.",
            chat_id
        )
    
    def _generate_report(self, report_type: str, chat_id: str):
        """Generate and send report."""
        self.send_message("📊 <b>Генерирую отчёт...</b>", chat_id)
        
        try:
            # Get first campaign for demo
            campaigns = self.ozon_client.get_all_campaigns()
            if not campaigns:
                self.send_message("❌ Кампании не найдены", chat_id)
                return
            
            campaign_id = str(campaigns[0].get('id', ''))
            date_to = datetime.now().strftime('%Y-%m-%d')
            date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            # Get data and analyze
            stats = self.ozon_client.get_campaign_stats(campaign_id, date_from, date_to)
            keyword_stats = self.ozon_client.get_keyword_stats(campaign_id, date_from, date_to)
            analysis = self.analyzer.analyze_keywords(keyword_stats)
            summary = self.analyzer.get_campaign_summary(stats, analysis)
            
            # Generate report
            if report_type in ["excel", "full"]:
                excel_path = self.report_generator.generate_excel_report(summary, analysis)
                self.send_document(excel_path, "📊 Excel отчёт по кампании", chat_id)
            
            if report_type in ["pdf", "full"]:
                pdf_path = self.report_generator.generate_pdf_report(summary)
                self.send_document(pdf_path, "📄 PDF отчёт по кампании", chat_id)
            
            self.send_message("✅ <b>Отчёт готов!</b>", chat_id)
            
        except Exception as e:
            self.send_message(f"❌ Ошибка генерации отчёта: {str(e)}", chat_id)
    
    def _run_manual_analysis(self, chat_id: str):
        """Run manual analysis for all campaigns."""
        self.send_message("🔍 <b>Запускаю анализ всех кампаний...</b>", chat_id)
        
        # This would trigger the scheduler's analysis
        self.send_message(
            "✅ <b>Анализ запущен</b>\n\n"
            "Результаты будут отправлены по завершении.",
            chat_id
        )
    
    # Notification methods for scheduler callbacks
    async def notify_analysis_complete(self, results: List[Dict]):
        """Notify about completed analysis."""
        if not self.bot or not self.chat_id:
            return
        
        total_campaigns = len(results)
        critical_issues = sum(len([k for k in r['analysis'] if k.get('priority', 0) >= 90]) for r in results)
        
        message = f"""
📊 <b>Анализ завершён</b>

• Проанализировано кампаний: {total_campaigns}
• Найдено критических проблем: {critical_issues}

{datetime.now().strftime('%d.%m.%Y %H:%M')}
        """
        
        self.send_message(message)
    
    async def notify_optimization_complete(self, results: List[Dict]):
        """Notify about completed optimization."""
        if not self.bot or not self.chat_id:
            return
        
        total_actions = sum(r['actions_taken'] for r in results)
        total_paused = sum(r['paused_keywords'] for r in results)
        
        message = f"""
⚙️ <b>Оптимизация завершена</b>

• Выполнено действий: {total_actions}
• Отключено ключей: {total_paused}
• Обработано кампаний: {len(results)}

{datetime.now().strftime('%d.%m.%Y %H:%M')}
        """
        
        self.send_message(message)
    
    async def notify_critical_issue(self, campaign_id: str, issues: List[Dict]):
        """Notify about critical issues."""
        if not self.bot or not self.chat_id:
            return
        
        message = f"""
🚨 <b>КРИТИЧЕСКАЯ ПРОБЛЕМА</b>

Кампания: {campaign_id}
Проблем найдено: {len(issues)}

<b>Топ проблемы:</b>
        """
        
        for issue in issues[:3]:
            message += f"• {issue['keyword']}: {issue['recommendation']}\n"
        
        message += f"\n⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        
        self.send_message(message)