"""Keyword management module for Ozon advertising campaigns."""
import re
from typing import Dict, List, Set, Optional, Tuple
import requests
from loguru import logger
from config import settings


class KeywordManager:
    """Manager for keyword operations and suggestions."""
    
    def __init__(self, ozon_client=None):
        """Initialize keyword manager."""
        self.ozon_client = ozon_client
        self.stop_words = {
            'и', 'в', 'на', 'с', 'по', 'для', 'от', 'до', 'из', 'к', 'о', 'про', 'при', 
            'без', 'над', 'под', 'через', 'между', 'среди', 'около', 'вокруг', 'внутри',
            'снаружи', 'сверху', 'снизу', 'спереди', 'сзади', 'слева', 'справа'
        }
    
    def suggest_keywords_from_product(self, product_info: Dict) -> List[Dict]:
        """Generate keyword suggestions based on product information."""
        logger.info("Generating keywords from product info")
        
        suggestions = []
        
        # Extract text from product
        title = product_info.get('name', '')
        description = product_info.get('description', '')
        category = product_info.get('category_name', '')
        brand = product_info.get('brand', '')
        
        # Base keywords from title
        if title:
            base_keywords = self._extract_keywords_from_text(title)
            for keyword in base_keywords:
                suggestions.append({
                    'keyword': keyword,
                    'source': 'product_title',
                    'priority': 'high',
                    'suggested_bid': 25.0  # Default bid
                })
        
        # Brand + product combinations
        if brand and title:
            brand_combinations = self._generate_brand_combinations(brand, title)
            for combo in brand_combinations:
                suggestions.append({
                    'keyword': combo,
                    'source': 'brand_combination',
                    'priority': 'high',
                    'suggested_bid': 30.0
                })
        
        # Category-based keywords
        if category:
            category_keywords = self._generate_category_keywords(category, title)
            for keyword in category_keywords:
                suggestions.append({
                    'keyword': keyword,
                    'source': 'category',
                    'priority': 'medium',
                    'suggested_bid': 20.0
                })
        
        # Long-tail keywords from description
        if description:
            long_tail = self._extract_long_tail_keywords(description)
            for keyword in long_tail:
                suggestions.append({
                    'keyword': keyword,
                    'source': 'description',
                    'priority': 'medium',
                    'suggested_bid': 15.0
                })
        
        # Remove duplicates and filter
        suggestions = self._filter_and_deduplicate(suggestions)
        
        logger.info(f"Generated {len(suggestions)} keyword suggestions")
        return suggestions
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """Extract potential keywords from text."""
        # Clean text
        text = re.sub(r'[^\w\s-]', ' ', text.lower())
        words = text.split()
        
        # Remove stop words
        words = [w for w in words if w not in self.stop_words and len(w) > 2]
        
        keywords = []
        
        # Single words
        keywords.extend(words)
        
        # Two-word combinations
        for i in range(len(words) - 1):
            keywords.append(f"{words[i]} {words[i+1]}")
        
        # Three-word combinations (selective)
        for i in range(len(words) - 2):
            if len(words[i]) > 3 and len(words[i+1]) > 3:  # Only meaningful words
                keywords.append(f"{words[i]} {words[i+1]} {words[i+2]}")
        
        return list(set(keywords))
    
    def _generate_brand_combinations(self, brand: str, title: str) -> List[str]:
        """Generate brand + product keyword combinations."""
        combinations = []
        
        # Clean title
        title_words = re.sub(r'[^\w\s]', ' ', title.lower()).split()
        title_words = [w for w in title_words if w not in self.stop_words and len(w) > 2]
        
        brand_lower = brand.lower()
        
        # Brand + main product words
        for word in title_words[:5]:  # Top 5 words
            if brand_lower not in word:  # Avoid duplication
                combinations.append(f"{brand_lower} {word}")
        
        # Brand + two-word combinations
        for i in range(min(3, len(title_words) - 1)):
            combo = f"{brand_lower} {title_words[i]} {title_words[i+1]}"
            combinations.append(combo)
        
        return combinations
    
    def _generate_category_keywords(self, category: str, title: str) -> List[str]:
        """Generate category-based keywords."""
        keywords = []
        
        category_words = re.sub(r'[^\w\s]', ' ', category.lower()).split()
        title_words = re.sub(r'[^\w\s]', ' ', title.lower()).split()
        
        # Main category words
        for cat_word in category_words:
            if len(cat_word) > 3:
                keywords.append(cat_word)
                
                # Category + product combinations
                for title_word in title_words[:3]:
                    if len(title_word) > 3 and cat_word != title_word:
                        keywords.append(f"{cat_word} {title_word}")
        
        return keywords
    
    def _extract_long_tail_keywords(self, description: str) -> List[str]:
        """Extract long-tail keywords from product description."""
        # Clean description
        text = re.sub(r'[^\w\s.-]', ' ', description.lower())
        sentences = text.split('.')
        
        keywords = []
        
        for sentence in sentences:
            words = sentence.strip().split()
            words = [w for w in words if w not in self.stop_words and len(w) > 2]
            
            # Extract 3-4 word phrases
            for i in range(len(words) - 2):
                if len(words) >= 3:
                    phrase = ' '.join(words[i:i+3])
                    if len(phrase) > 10:  # Meaningful phrases only
                        keywords.append(phrase)
            
            # Extract 4-word phrases selectively
            for i in range(len(words) - 3):
                if len(words) >= 4:
                    phrase = ' '.join(words[i:i+4])
                    if len(phrase) > 15:
                        keywords.append(phrase)
        
        return keywords
    
    def _filter_and_deduplicate(self, suggestions: List[Dict]) -> List[Dict]:
        """Filter and remove duplicate keyword suggestions."""
        seen_keywords = set()
        filtered = []
        
        # Sort by priority (high first)
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        suggestions.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
        
        for suggestion in suggestions:
            keyword = suggestion['keyword'].strip().lower()
            
            # Skip if too short or too long
            if len(keyword) < 3 or len(keyword) > 100:
                continue
            
            # Skip if already seen
            if keyword in seen_keywords:
                continue
            
            # Skip if only numbers or special characters
            if not re.search(r'[а-яё]', keyword, re.IGNORECASE):
                continue
            
            seen_keywords.add(keyword)
            suggestion['keyword'] = keyword
            filtered.append(suggestion)
        
        return filtered[:50]  # Limit to top 50
    
    def generate_negative_keywords(self, poor_performing_keywords: List[Dict]) -> List[str]:
        """Generate negative keywords based on poor performers."""
        logger.info("Generating negative keywords from poor performers")
        
        negative_keywords = set()
        
        for keyword_data in poor_performing_keywords:
            keyword = keyword_data.get('keyword', '').lower()
            
            # Extract problematic words
            words = keyword.split()
            
            # Add single problematic words
            for word in words:
                if len(word) > 3:
                    # Common negative patterns
                    if any(pattern in word for pattern in ['дешев', 'подделк', 'копи', 'фейк']):
                        negative_keywords.add(word)
                    
                    # If keyword has very low CTR, consider words as negative
                    if keyword_data.get('ctr', 0) < 0.1 and keyword_data.get('clicks', 0) > 20:
                        negative_keywords.add(word)
            
            # Add full phrases for very poor performers
            if (keyword_data.get('clicks', 0) > 50 and 
                keyword_data.get('orders', 0) == 0):
                negative_keywords.add(keyword)
        
        # Add common negative keywords for e-commerce
        common_negatives = [
            'бесплатно', 'скачать', 'торрент', 'взлом', 'crack',
            'обзор', 'отзыв', 'видео', 'фото', 'картинки',
            'вакансия', 'работа', 'резюме', 'зарплата'
        ]
        negative_keywords.update(common_negatives)
        
        result = list(negative_keywords)[:100]  # Limit to 100
        logger.info(f"Generated {len(result)} negative keywords")
        return result
    
    def suggest_bid_adjustments(self, keyword_analysis: List[Dict]) -> List[Dict]:
        """Suggest bid adjustments based on keyword performance."""
        logger.info("Calculating bid adjustments")
        
        adjustments = []
        
        for analysis in keyword_analysis:
            if analysis.get('bid_adjustment', 0) != 0:
                current_bid = analysis.get('current_bid', 25.0)  # Default if not available
                adjustment_percent = analysis.get('bid_adjustment', 0)
                new_bid = current_bid * (1 + adjustment_percent / 100)
                
                # Ensure reasonable bid range
                new_bid = max(5.0, min(500.0, new_bid))
                
                adjustments.append({
                    'keyword': analysis['keyword'],
                    'current_bid': current_bid,
                    'suggested_bid': round(new_bid, 2),
                    'adjustment_percent': adjustment_percent,
                    'reason': analysis['recommendation'],
                    'priority': analysis['priority']
                })
        
        # Sort by priority
        adjustments.sort(key=lambda x: x['priority'], reverse=True)
        
        logger.info(f"Generated {len(adjustments)} bid adjustment suggestions")
        return adjustments
    
    def get_competitor_keywords(self, competitor_urls: List[str]) -> List[str]:
        """Get keyword suggestions from competitor analysis (placeholder)."""
        logger.info("Analyzing competitor keywords (placeholder)")
        
        # This would integrate with external services like:
        # - mpstats.io
        # - keys.so  
        # - Wordstat
        # - SemRush API
        
        # Placeholder implementation
        competitor_keywords = [
            "товар высокого качества",
            "быстрая доставка",
            "лучшая цена",
            "оригинальный товар",
            "гарантия качества"
        ]
        
        return competitor_keywords
    
    def optimize_keyword_match_types(self, keywords: List[str]) -> List[Dict]:
        """Suggest optimal match types for keywords."""
        optimized = []
        
        for keyword in keywords:
            word_count = len(keyword.split())
            
            if word_count == 1:
                match_type = "BROAD"  # Single words - broad match
            elif word_count == 2:
                match_type = "PHRASE"  # Two words - phrase match
            else:
                match_type = "EXACT"  # Long phrases - exact match
            
            optimized.append({
                'keyword': keyword,
                'suggested_match_type': match_type,
                'reason': f"Оптимально для {word_count}-словного запроса"
            })
        
        return optimized