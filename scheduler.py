"""Task scheduler for automated campaign optimization."""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
import asyncio
import inspect
try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    ASYNC_AVAILABLE = True
except ImportError:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    ASYNC_AVAILABLE = False
from loguru import logger
from config import settings


class CampaignScheduler:
    """Scheduler for automated campaign management tasks."""
    
    def __init__(self, ozon_client=None, analyzer=None, keyword_manager=None, report_generator=None):
        """Initialize scheduler with required components."""
        # Always use BackgroundScheduler for simplicity
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            self.scheduler = BackgroundScheduler()
        except ImportError:
            logger.warning("APScheduler not available, scheduler disabled")
            self.scheduler = None
        
        self.ozon_client = ozon_client
        self.analyzer = analyzer
        self.keyword_manager = keyword_manager
        self.report_generator = report_generator
        self.is_running = False
        
        # Task callbacks
        self.callbacks = {
            'on_analysis_complete': [],
            'on_optimization_complete': [],
            'on_report_generated': [],
            'on_critical_issue': []
        }
    
    def add_callback(self, event: str, callback: Callable):
        """Add callback for specific events."""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    def start(self):
        """Start the scheduler."""
        if not self.is_running and self.scheduler is not None:
            logger.info("Starting campaign scheduler")
            try:
                self.scheduler.start()
                self.is_running = True
                
                # Schedule default tasks
                self._schedule_default_tasks()
                logger.info("Scheduler started successfully")
            except Exception as e:
                logger.error(f"Failed to start scheduler: {e}")
                self.is_running = False
        elif self.scheduler is None:
            logger.warning("Scheduler not available")
            self.is_running = False
    
    def stop(self):
        """Stop the scheduler."""
        if self.is_running and self.scheduler is not None:
            logger.info("Stopping campaign scheduler")
            try:
                self.scheduler.shutdown()
            except Exception as e:
                logger.error(f"Error stopping scheduler: {e}")
            finally:
                self.is_running = False
    
    def _schedule_default_tasks(self):
        """Schedule default recurring tasks."""
        if self.scheduler is None:
            logger.warning("Cannot schedule tasks - scheduler not available")
            return
            
        try:
            # Daily analysis at 9 AM
            self.schedule_daily_analysis(hour=9, minute=0)
            
            # Weekly report on Mondays at 10 AM
            self.schedule_weekly_report(day_of_week=0, hour=10, minute=0)
            
            # Hourly monitoring during business hours
            self.schedule_monitoring(interval_hours=1)
        except Exception as e:
            logger.error(f"Failed to schedule default tasks: {e}")
    
    def schedule_daily_analysis(self, hour: int = 9, minute: int = 0):
        """Schedule daily campaign analysis."""
        if self.scheduler is None:
            logger.warning("Cannot schedule daily analysis - scheduler not available")
            return
            
        logger.info(f"Scheduling daily analysis at {hour:02d}:{minute:02d}")
        
        try:
            self.scheduler.add_job(
                self._run_daily_analysis,
                trigger=CronTrigger(hour=hour, minute=minute),
                id='daily_analysis',
                name='Daily Campaign Analysis',
                replace_existing=True
            )
        except Exception as e:
            logger.error(f"Failed to schedule daily analysis: {e}")
    
    def schedule_weekly_report(self, day_of_week: int = 0, hour: int = 10, minute: int = 0):
        """Schedule weekly report generation (0=Monday, 6=Sunday)."""
        logger.info(f"Scheduling weekly report on day {day_of_week} at {hour:02d}:{minute:02d}")
        
        self.scheduler.add_job(
            self._run_weekly_report,
            trigger=CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute),
            id='weekly_report',
            name='Weekly Campaign Report',
            replace_existing=True
        )
    
    def schedule_monitoring(self, interval_hours: int = 1):
        """Schedule regular campaign monitoring."""
        logger.info(f"Scheduling monitoring every {interval_hours} hour(s)")
        
        self.scheduler.add_job(
            self._run_monitoring,
            trigger=IntervalTrigger(hours=interval_hours),
            id='monitoring',
            name='Campaign Monitoring',
            replace_existing=True
        )
    
    def schedule_optimization(self, hour: int = 11, minute: int = 0):
        """Schedule automated optimization."""
        if not settings.auto_optimization_enabled:
            logger.warning("Auto-optimization is disabled in settings")
            return
        
        logger.info(f"Scheduling optimization at {hour:02d}:{minute:02d}")
        
        self.scheduler.add_job(
            self._run_optimization,
            trigger=CronTrigger(hour=hour, minute=minute),
            id='optimization',
            name='Campaign Optimization',
            replace_existing=True
        )
    
    def _run_coro(self, coro):
        """Safely run a coroutine in its own event loop."""
        try:
            asyncio.run(coro)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(coro)
            finally:
                loop.close()

    def _run_daily_analysis(self):
        """Run daily campaign analysis (synchronous wrapper)."""
        logger.info("Running scheduled daily analysis")
        
        try:
            if not self.ozon_client or not self.analyzer:
                logger.error("Missing required components for analysis")
                return
            
            # Get all campaigns
            campaigns = self.ozon_client.get_all_campaigns()
            
            results = []
            date_to = datetime.now().strftime('%Y-%m-%d')
            date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            for campaign in campaigns[:5]:  # Limit to 5 campaigns
                campaign_id = str(campaign.get('id', ''))
                
                # Get campaign stats
                stats = self.ozon_client.get_campaign_stats(campaign_id, date_from, date_to)
                keyword_stats = self.ozon_client.get_keyword_stats(campaign_id, date_from, date_to)
                
                # Analyze keywords
                analysis = self.analyzer.analyze_keywords(keyword_stats)
                summary = self.analyzer.get_campaign_summary(stats, analysis)
                
                results.append({
                    'campaign_id': campaign_id,
                    'campaign_name': campaign.get('name', 'Unknown'),
                    'summary': summary,
                    'analysis': analysis
                })
                
                # Check for critical issues
                critical_issues = [k for k in analysis if k.get('priority', 0) >= 90]
                if critical_issues:
                    # Handle critical issues (callbacks may be async)
                    self._handle_critical_issues(campaign_id, critical_issues)
            
            # Trigger callbacks
            for callback in self.callbacks['on_analysis_complete']:
                try:
                    if inspect.iscoroutinefunction(callback):
                        self._run_coro(callback(results))
                    else:
                        callback(results)
                except Exception as e:
                    logger.error(f"Callback error: {e}")
            
            logger.info(f"Daily analysis completed for {len(results)} campaigns")
            
        except Exception as e:
            logger.error(f"Daily analysis failed: {e}")
    
    def _run_weekly_report(self):
        """Generate weekly reports (synchronous wrapper)."""
        logger.info("Running scheduled weekly report generation")
        
        try:
            if not self.ozon_client or not self.analyzer or not self.report_generator:
                logger.error("Missing required components for report generation")
                return
            
            campaigns = self.ozon_client.get_all_campaigns()
            date_to = datetime.now().strftime('%Y-%m-%d')
            date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            reports = []
            
            for campaign in campaigns[:3]:  # Limit to 3 campaigns for weekly reports
                campaign_id = str(campaign.get('id', ''))
                
                # Get data
                stats = self.ozon_client.get_campaign_stats(campaign_id, date_from, date_to)
                keyword_stats = self.ozon_client.get_keyword_stats(campaign_id, date_from, date_to)
                
                # Analyze
                analysis = self.analyzer.analyze_keywords(keyword_stats)
                summary = self.analyzer.get_campaign_summary(stats, analysis)
                
                # Generate reports
                excel_path = self.report_generator.generate_excel_report(summary, analysis)
                pdf_path = self.report_generator.generate_pdf_report(summary)
                
                reports.append({
                    'campaign_id': campaign_id,
                    'excel_path': excel_path,
                    'pdf_path': pdf_path
                })
            
            # Trigger callbacks
            for callback in self.callbacks['on_report_generated']:
                try:
                    if inspect.iscoroutinefunction(callback):
                        self._run_coro(callback(reports))
                    else:
                        callback(reports)
                except Exception as e:
                    logger.error(f"Report callback error: {e}")
            
            logger.info(f"Weekly reports generated for {len(reports)} campaigns")
            
        except Exception as e:
            logger.error(f"Weekly report generation failed: {e}")
    
    def _run_monitoring(self):
        """Run campaign monitoring (synchronous wrapper)."""
        logger.info("Running scheduled monitoring")
        
        try:
            if not self.ozon_client:
                return
            
            campaigns = self.ozon_client.get_all_campaigns()
            date_to = datetime.now().strftime('%Y-%m-%d')
            date_from = (datetime.now() - timedelta(hours=24)).strftime('%Y-%m-%d')
            
            alerts = []
            
            for campaign in campaigns:
                campaign_id = str(campaign.get('id', ''))
                stats = self.ozon_client.get_campaign_stats(campaign_id, date_from, date_to)
                
                # Check for alerts
                if stats.get('drr', 0) > 50:
                    alerts.append({
                        'type': 'high_drr',
                        'campaign_id': campaign_id,
                        'message': f"Высокий ДРР: {stats['drr']:.1f}%",
                        'severity': 'critical'
                    })
                
                if stats.get('spend', 0) > 10000:  # Spending over 10k rubles
                    alerts.append({
                        'type': 'high_spend',
                        'campaign_id': campaign_id,
                        'message': f"Высокие расходы: {stats['spend']:.2f} ₽",
                        'severity': 'warning'
                    })
            
            if alerts:
                logger.warning(f"Found {len(alerts)} monitoring alerts")
                # Handle alerts (could send to Telegram, email, etc.)
            
        except Exception as e:
            logger.error(f"Monitoring failed: {e}")
    
    def _run_optimization(self):
        """Run automated optimization (synchronous wrapper)."""
        logger.info("Running scheduled optimization")
        
        if not settings.auto_optimization_enabled:
            logger.warning("Auto-optimization is disabled")
            return
        
        try:
            if not all([self.ozon_client, self.analyzer, self.keyword_manager]):
                logger.error("Missing required components for optimization")
                return
            
            campaigns = self.ozon_client.get_all_campaigns()
            date_to = datetime.now().strftime('%Y-%m-%d')
            date_from = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
            
            optimization_results = []
            
            for campaign in campaigns[:2]:  # Limit to 2 campaigns for auto-optimization
                campaign_id = str(campaign.get('id', ''))
                
                # Get data and analyze
                keyword_stats = self.ozon_client.get_keyword_stats(campaign_id, date_from, date_to)
                analysis = self.analyzer.analyze_keywords(keyword_stats)
                
                # Apply optimizations
                actions_taken = 0
                
                # Pause critical keywords
                pause_keywords = [k['keyword'] for k in analysis if k['action'] == 'pause']
                if pause_keywords:
                    success = self.ozon_client.pause_keywords(campaign_id, pause_keywords)
                    if success:
                        actions_taken += len(pause_keywords)
                        logger.info(f"Paused {len(pause_keywords)} keywords in campaign {campaign_id}")
                
                # Adjust bids (only for high-confidence cases)
                bid_adjustments = self.keyword_manager.suggest_bid_adjustments(analysis)
                high_confidence_adjustments = [b for b in bid_adjustments if b['priority'] >= 70]
                
                for adjustment in high_confidence_adjustments[:5]:  # Limit to 5 bid changes
                    success = self.ozon_client.update_keyword_bid(
                        campaign_id, 
                        adjustment['keyword'], 
                        adjustment['suggested_bid']
                    )
                    if success:
                        actions_taken += 1
                
                optimization_results.append({
                    'campaign_id': campaign_id,
                    'actions_taken': actions_taken,
                    'paused_keywords': len(pause_keywords),
                    'bid_adjustments': len(high_confidence_adjustments)
                })
            
            # Trigger callbacks
            for callback in self.callbacks['on_optimization_complete']:
                try:
                    if inspect.iscoroutinefunction(callback):
                        self._run_coro(callback(optimization_results))
                    else:
                        callback(optimization_results)
                except Exception as e:
                    logger.error(f"Optimization callback error: {e}")
            
            total_actions = sum(r['actions_taken'] for r in optimization_results)
            logger.info(f"Optimization completed: {total_actions} actions taken")
            
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
    
    def _handle_critical_issues(self, campaign_id: str, critical_issues: List[Dict]):
        """Handle critical issues found during analysis (sync)."""
        logger.warning(f"Found {len(critical_issues)} critical issues in campaign {campaign_id}")
        
        # Trigger critical issue callbacks
        for callback in self.callbacks['on_critical_issue']:
            try:
                if inspect.iscoroutinefunction(callback):
                    self._run_coro(callback(campaign_id, critical_issues))
                else:
                    callback(campaign_id, critical_issues)
            except Exception as e:
                logger.error(f"Critical issue callback error: {e}")
    
    def get_scheduled_jobs(self) -> List[Dict]:
        """Get list of currently scheduled jobs."""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        return jobs
    
    def remove_job(self, job_id: str):
        """Remove a scheduled job."""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed job: {job_id}")
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {e}")