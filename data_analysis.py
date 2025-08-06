"""Data analysis module for Ozon advertising campaigns."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from loguru import logger
from config import settings


class CampaignAnalyzer:
    """Analyzer for campaign performance metrics."""
    
    def __init__(self):
        """Initialize analyzer with thresholds from settings."""
        self.min_ctr_threshold = settings.min_ctr_threshold
        self.max_drr_threshold = settings.max_drr_threshold
        self.high_ctr_threshold = settings.high_ctr_threshold
        self.high_cr_threshold = settings.high_cr_threshold
        self.max_acceptable_drr = settings.max_acceptable_drr
        self.critical_drr_threshold = settings.critical_drr_threshold
        self.min_clicks_for_analysis = settings.min_clicks_for_analysis
    
    def analyze_keywords(self, keyword_stats: List[Dict]) -> List[Dict]:
        """Analyze keyword performance and provide recommendations."""
        logger.info(f"Analyzing {len(keyword_stats)} keywords")
        
        analyzed_keywords = []
        
        for keyword_data in keyword_stats:
            analysis = self._analyze_single_keyword(keyword_data)
            analyzed_keywords.append(analysis)
        
        # Sort by priority (critical issues first)
        analyzed_keywords.sort(key=lambda x: x['priority'], reverse=True)
        
        logger.info(f"Analysis complete. Found {len([k for k in analyzed_keywords if k['action'] != 'keep'])} keywords needing attention")
        return analyzed_keywords
    
    def _analyze_single_keyword(self, keyword_data: Dict) -> Dict:
        """Analyze single keyword and provide recommendation."""
        keyword = keyword_data.get('keyword', '')
        ctr = keyword_data.get('ctr', 0)
        cr = keyword_data.get('cr', 0)
        drr = keyword_data.get('drr', 0)
        clicks = keyword_data.get('clicks', 0)
        orders = keyword_data.get('orders', 0)
        impressions = keyword_data.get('impressions', 0)
        spend = keyword_data.get('spend', 0)
        
        analysis = {
            **keyword_data,
            'action': 'keep',
            'recommendation': 'Продолжать мониторинг',
            'priority': 0,
            'issues': [],
            'bid_adjustment': 0
        }
        
        # Critical issues (highest priority)
        if clicks >= self.min_clicks_for_analysis and orders == 0:
            analysis['action'] = 'pause'
            analysis['recommendation'] = f'🔴 ОТКЛЮЧИТЬ: {clicks} кликов без заказов'
            analysis['priority'] = 100
            analysis['issues'].append('no_orders_with_clicks')
        
        elif drr > self.critical_drr_threshold:
            analysis['action'] = 'pause'
            analysis['recommendation'] = f'🔴 ОТКЛЮЧИТЬ: ДРР {drr:.1f}% критически высокий'
            analysis['priority'] = 95
            analysis['issues'].append('critical_drr')
        
        elif ctr < self.min_ctr_threshold and clicks > 10:
            analysis['action'] = 'pause'
            analysis['recommendation'] = f'🔴 ОТКЛЮЧИТЬ: CTR {ctr:.2f}% слишком низкий'
            analysis['priority'] = 90
            analysis['issues'].append('low_ctr')
        
        # Optimization opportunities (medium priority)
        elif (ctr > self.high_ctr_threshold and 
              cr > self.high_cr_threshold and 
              drr < self.max_acceptable_drr and
              drr > 0):
            analysis['action'] = 'increase_bid'
            analysis['bid_adjustment'] = settings.bid_increase_percent
            analysis['recommendation'] = f'📈 ПОВЫСИТЬ СТАВКУ на {settings.bid_increase_percent}%: отличные показатели'
            analysis['priority'] = 70
            analysis['issues'].append('high_performance')
        
        elif drr > self.max_drr_threshold and drr <= self.critical_drr_threshold:
            analysis['action'] = 'decrease_bid'
            analysis['bid_adjustment'] = -settings.bid_decrease_percent
            analysis['recommendation'] = f'📉 ПОНИЗИТЬ СТАВКУ на {settings.bid_decrease_percent}%: высокий ДРР {drr:.1f}%'
            analysis['priority'] = 60
            analysis['issues'].append('high_drr')
        
        # Warning issues (low priority)
        elif drr > self.max_drr_threshold:
            analysis['action'] = 'monitor'
            analysis['recommendation'] = f'⚠️ МОНИТОРИТЬ: ДРР {drr:.1f}% превышает норму'
            analysis['priority'] = 30
            analysis['issues'].append('warning_drr')
        
        elif impressions > 1000 and ctr < 1.0:
            analysis['action'] = 'monitor'
            analysis['recommendation'] = f'⚠️ МОНИТОРИТЬ: низкий CTR {ctr:.2f}% при высоких показах'
            analysis['priority'] = 20
            analysis['issues'].append('low_ctr_high_impressions')
        
        return analysis
    
    def get_campaign_summary(self, campaign_stats: Dict, keyword_analysis: List[Dict]) -> Dict:
        """Generate campaign summary with key insights."""
        total_keywords = len(keyword_analysis)
        
        # Count actions needed
        actions_count = {}
        for analysis in keyword_analysis:
            action = analysis['action']
            actions_count[action] = actions_count.get(action, 0) + 1
        
        # Calculate totals
        total_spend = sum(k.get('spend', 0) for k in keyword_analysis)
        total_revenue = sum(k.get('revenue', 0) for k in keyword_analysis)
        total_clicks = sum(k.get('clicks', 0) for k in keyword_analysis)
        total_impressions = sum(k.get('impressions', 0) for k in keyword_analysis)
        total_orders = sum(k.get('orders', 0) for k in keyword_analysis)
        
        # Top performers and worst performers
        high_performance = [k for k in keyword_analysis if 'high_performance' in k['issues']]
        critical_issues = [k for k in keyword_analysis if k['priority'] >= 90]
        
        summary = {
            'campaign_id': campaign_stats.get('campaign_id'),
            'total_keywords': total_keywords,
            'actions_needed': actions_count,
            'performance_metrics': {
                'total_spend': total_spend,
                'total_revenue': total_revenue,
                'total_clicks': total_clicks,
                'total_impressions': total_impressions,
                'total_orders': total_orders,
                'overall_ctr': (total_clicks / total_impressions * 100) if total_impressions > 0 else 0,
                'overall_cr': (total_orders / total_clicks * 100) if total_clicks > 0 else 0,
                'overall_drr': (total_spend / total_revenue * 100) if total_revenue > 0 else 0,
                'overall_roi': (total_revenue / total_spend) if total_spend > 0 else 0
            },
            'top_performers': sorted(high_performance, key=lambda x: x['revenue'], reverse=True)[:5],
            'critical_issues': sorted(critical_issues, key=lambda x: x['priority'], reverse=True)[:10],
            'recommendations': self._generate_campaign_recommendations(keyword_analysis, actions_count)
        }
        
        return summary
    
    def _generate_campaign_recommendations(self, keyword_analysis: List[Dict], actions_count: Dict) -> List[str]:
        """Generate high-level campaign recommendations."""
        recommendations = []
        
        pause_count = actions_count.get('pause', 0)
        increase_bid_count = actions_count.get('increase_bid', 0)
        decrease_bid_count = actions_count.get('decrease_bid', 0)
        
        if pause_count > 0:
            recommendations.append(f"🔴 Отключить {pause_count} неэффективных ключевых слов")
        
        if increase_bid_count > 0:
            recommendations.append(f"📈 Повысить ставки для {increase_bid_count} высокоэффективных ключей")
        
        if decrease_bid_count > 0:
            recommendations.append(f"📉 Понизить ставки для {decrease_bid_count} ключей с высоким ДРР")
        
        # Calculate potential savings
        pause_keywords = [k for k in keyword_analysis if k['action'] == 'pause']
        potential_savings = sum(k.get('spend', 0) for k in pause_keywords)
        
        if potential_savings > 0:
            recommendations.append(f"💰 Потенциальная экономия от отключения: {potential_savings:.2f} ₽")
        
        return recommendations
    
    def detect_trends(self, historical_data: List[Dict], days: int = 7) -> Dict:
        """Detect trends in campaign performance."""
        if len(historical_data) < 2:
            return {'trend': 'insufficient_data', 'message': 'Недостаточно данных для анализа трендов'}
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(historical_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Calculate trends for key metrics
        trends = {}
        
        for metric in ['ctr', 'cr', 'drr', 'spend', 'revenue']:
            if metric in df.columns:
                values = df[metric].values
                if len(values) >= 2:
                    # Simple linear trend
                    x = np.arange(len(values))
                    slope = np.polyfit(x, values, 1)[0]
                    
                    if abs(slope) < 0.01:  # Threshold for "stable"
                        trend = 'stable'
                    elif slope > 0:
                        trend = 'increasing'
                    else:
                        trend = 'decreasing'
                    
                    trends[metric] = {
                        'trend': trend,
                        'slope': slope,
                        'change_percent': ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
                    }
        
        return trends
    
    def find_keyword_opportunities(self, keyword_stats: List[Dict], competitor_keywords: List[str] = None) -> List[Dict]:
        """Find opportunities for new keywords based on performance patterns."""
        opportunities = []
        
        # Analyze high-performing keywords for patterns
        high_performers = [k for k in keyword_stats 
                          if k.get('ctr', 0) > self.high_ctr_threshold 
                          and k.get('cr', 0) > self.high_cr_threshold
                          and k.get('drr', 0) < self.max_acceptable_drr]
        
        if high_performers:
            # Extract common patterns
            keywords = [k['keyword'].lower() for k in high_performers]
            
            # Find common words
            all_words = []
            for keyword in keywords:
                all_words.extend(keyword.split())
            
            word_freq = pd.Series(all_words).value_counts()
            common_words = word_freq.head(10).index.tolist()
            
            opportunities.append({
                'type': 'pattern_based',
                'description': 'Ключевые слова на основе успешных паттернов',
                'suggestions': [f"Добавить вариации с словами: {', '.join(common_words)}"],
                'priority': 'high'
            })
        
        # Suggest long-tail variations
        if keyword_stats:
            short_keywords = [k for k in keyword_stats if len(k['keyword'].split()) <= 2]
            if short_keywords:
                opportunities.append({
                    'type': 'long_tail',
                    'description': 'Длинные ключевые фразы',
                    'suggestions': ['Добавить длинные вариации коротких ключей', 
                                   'Использовать geo-модификаторы', 
                                   'Добавить характеристики товара'],
                    'priority': 'medium'
                })
        
        return opportunities