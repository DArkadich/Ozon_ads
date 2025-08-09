"""Ozon API client for managing advertising campaigns."""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests
from loguru import logger
from config import settings


class OzonAPIError(Exception):
    """Custom exception for Ozon API errors."""
    pass


class OzonAPIClient:
    """Client for interacting with Ozon Ads API."""
    
    def __init__(self, client_id: str = None, api_key: str = None):
        """Initialize Ozon API client."""
        self.client_id = client_id or settings.ozon_client_id
        self.api_key = api_key or settings.ozon_api_key
        # Попробуем несколько вариантов базовых URL
        self.base_urls = [
            "https://api-seller.ozon.ru",
            "https://api.ozon.ru",
            "https://performance.ozon.ru/api"
        ]
        self.base_url = self.base_urls[0]  # По умолчанию
        self.session = requests.Session()
        self.session.headers.update({
            "Client-Id": self.client_id,
            "Api-Key": self.api_key,
            "Content-Type": "application/json"
        })
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make HTTP request to Ozon API with automatic fallback to alternative URLs."""
        for base_url in self.base_urls:
            url = f"{base_url}{endpoint}"
            try:
                logger.info(f"Trying API request to: {url}")
                if method.upper() == "GET":
                    response = self.session.get(url, params=data)
                else:
                    response = self.session.request(method, url, json=data)
                
                response.raise_for_status()
                # Если успешно, обновляем текущий базовый URL
                self.base_url = base_url
                logger.info(f"Successfully using base URL: {base_url}")
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"API request failed for {base_url}: {e}")
                continue
        
        # Если все URL не работают
        raise OzonAPIError(f"All API endpoints failed for endpoint: {endpoint}")
    
    def get_all_campaigns(self) -> List[Dict]:
        """Get all advertising campaigns."""
        logger.info("Fetching all campaigns")
        
        try:
            # Попробуем несколько вариантов API endpoints
            endpoints = [
                "/v2/performance/campaign/list",
                "/v1/performance/campaign/list", 
                "/v1/campaign/list",
                "/v2/campaign/list"
            ]
            
            for endpoint in endpoints:
                try:
                    logger.info(f"Trying endpoint: {endpoint}")
                    response = self._make_request("POST", endpoint, {})
                    campaigns = response.get("result", {}).get("campaigns", [])
                    
                    if campaigns:
                        logger.info(f"Found {len(campaigns)} campaigns using {endpoint}")
                        return campaigns
                except Exception as e:
                    logger.warning(f"Endpoint {endpoint} failed: {e}")
                    continue
            
            # Если все endpoints не работают, попробуем базовый endpoint
            logger.info("Trying base campaign endpoint")
            response = self._make_request("POST", "/v1/campaign/list", {})
            campaigns = response.get("result", {}).get("campaigns", [])
            
            logger.info(f"Found {len(campaigns)} campaigns")
            return campaigns
        
        except Exception as e:
            logger.error(f"Failed to fetch campaigns: {e}")
            return []
    
    def get_campaign_stats(self, campaign_id: str, date_from: str, date_to: str) -> Dict:
        """Get campaign statistics for specified period."""
        logger.info(f"Fetching stats for campaign {campaign_id} from {date_from} to {date_to}")
        
        data = {
            "campaigns": [{"id": int(campaign_id)}],
            "dateFrom": date_from,
            "dateTo": date_to,
            "groupBy": ["DATE"]
        }
        
        try:
            # Попробуем несколько вариантов API endpoints для статистики
            endpoints = [
                "/v2/performance/campaign/statistics",
                "/v1/performance/campaign/statistics",
                "/v1/campaign/statistics",
                "/v2/campaign/statistics"
            ]
            
            response = None
            for endpoint in endpoints:
                try:
                    logger.info(f"Trying statistics endpoint: {endpoint}")
                    response = self._make_request("POST", endpoint, data)
                    break
                except Exception as e:
                    logger.warning(f"Statistics endpoint {endpoint} failed: {e}")
                    continue
            
            if not response:
                raise Exception("All statistics endpoints failed")
            stats = response.get("result", {})
            
            if not stats:
                logger.warning(f"No stats found for campaign {campaign_id}")
                return {}
            
            # Aggregate stats
            totals = {
                "campaign_id": campaign_id,
                "impressions": 0,
                "clicks": 0,
                "orders": 0,
                "spend": 0.0,
                "revenue": 0.0
            }
            
            for item in stats.get("campaigns", []):
                for stat in item.get("statistics", []):
                    totals["impressions"] += stat.get("impressions", 0)
                    totals["clicks"] += stat.get("clicks", 0)
                    totals["orders"] += stat.get("orders", 0)
                    totals["spend"] += float(stat.get("spend", 0))
                    totals["revenue"] += float(stat.get("revenue", 0))
            
            # Calculate metrics
            totals["ctr"] = (totals["clicks"] / totals["impressions"] * 100) if totals["impressions"] > 0 else 0
            totals["cr"] = (totals["orders"] / totals["clicks"] * 100) if totals["clicks"] > 0 else 0
            totals["drr"] = (totals["spend"] / totals["revenue"] * 100) if totals["revenue"] > 0 else 0
            totals["roi"] = (totals["revenue"] / totals["spend"]) if totals["spend"] > 0 else 0
            
            return totals
        
        except Exception as e:
            logger.error(f"Failed to fetch campaign stats: {e}")
            return {}
    
    def get_campaign_keywords(self, campaign_id: str) -> List[Dict]:
        """Get keywords for specific campaign."""
        logger.info(f"Fetching keywords for campaign {campaign_id}")
        
        try:
            # Get keywords list
            data = {"campaignId": int(campaign_id)}
            
            # Попробуем несколько вариантов API endpoints для ключевых слов
            endpoints = [
                "/v2/performance/keyword/list",
                "/v1/performance/keyword/list",
                "/v1/keyword/list",
                "/v2/keyword/list"
            ]
            
            response = None
            for endpoint in endpoints:
                try:
                    logger.info(f"Trying keyword endpoint: {endpoint}")
                    response = self._make_request("POST", endpoint, data)
                    break
                except Exception as e:
                    logger.warning(f"Keyword endpoint {endpoint} failed: {e}")
                    continue
            
            if not response:
                raise Exception("All keyword endpoints failed")
            keywords = response.get("result", {}).get("keywords", [])
            
            logger.info(f"Found {len(keywords)} keywords for campaign {campaign_id}")
            return keywords
        
        except Exception as e:
            logger.error(f"Failed to fetch keywords: {e}")
            return []
    
    def get_keyword_stats(self, campaign_id: str, date_from: str, date_to: str) -> List[Dict]:
        """Get keyword statistics."""
        logger.info(f"Fetching keyword stats for campaign {campaign_id}")
        
        data = {
            "campaigns": [{"id": int(campaign_id)}],
            "dateFrom": date_from,
            "dateTo": date_to,
            "groupBy": ["KEYWORD"]
        }
        
        try:
            response = self._make_request("POST", "/v1/performance/keyword/statistics", data)
            stats = response.get("result", {}).get("campaigns", [])
            
            keyword_stats = []
            for campaign in stats:
                for stat in campaign.get("statistics", []):
                    keyword_data = {
                        "keyword": stat.get("keyword", ""),
                        "impressions": stat.get("impressions", 0),
                        "clicks": stat.get("clicks", 0),
                        "orders": stat.get("orders", 0),
                        "spend": float(stat.get("spend", 0)),
                        "revenue": float(stat.get("revenue", 0))
                    }
                    
                    # Calculate metrics
                    keyword_data["ctr"] = (keyword_data["clicks"] / keyword_data["impressions"] * 100) if keyword_data["impressions"] > 0 else 0
                    keyword_data["cr"] = (keyword_data["orders"] / keyword_data["clicks"] * 100) if keyword_data["clicks"] > 0 else 0
                    keyword_data["drr"] = (keyword_data["spend"] / keyword_data["revenue"] * 100) if keyword_data["revenue"] > 0 else 0
                    
                    keyword_stats.append(keyword_data)
            
            return keyword_stats
        
        except Exception as e:
            logger.error(f"Failed to fetch keyword stats: {e}")
            return []
    
    def update_keyword_bid(self, campaign_id: str, keyword: str, new_bid: float) -> bool:
        """Update keyword bid."""
        logger.info(f"Updating bid for keyword '{keyword}' to {new_bid}")
        
        try:
            data = {
                "campaignId": int(campaign_id),
                "keywords": [
                    {
                        "keyword": keyword,
                        "bid": new_bid
                    }
                ]
            }
            
            response = self._make_request("POST", "/v1/performance/keyword/bid/set", data)
            
            if response.get("result"):
                logger.info(f"Successfully updated bid for '{keyword}'")
                return True
            else:
                logger.error(f"Failed to update bid for '{keyword}': {response}")
                return False
        
        except Exception as e:
            logger.error(f"Error updating bid for '{keyword}': {e}")
            return False
    
    def add_negative_keywords(self, campaign_id: str, negative_keywords: List[str]) -> bool:
        """Add negative keywords to campaign."""
        logger.info(f"Adding {len(negative_keywords)} negative keywords to campaign {campaign_id}")
        
        try:
            data = {
                "campaignId": int(campaign_id),
                "negativeKeywords": negative_keywords
            }
            
            response = self._make_request("POST", "/v1/performance/keyword/negative/add", data)
            
            if response.get("result"):
                logger.info("Successfully added negative keywords")
                return True
            else:
                logger.error(f"Failed to add negative keywords: {response}")
                return False
        
        except Exception as e:
            logger.error(f"Error adding negative keywords: {e}")
            return False
    
    def pause_keywords(self, campaign_id: str, keywords: List[str]) -> bool:
        """Pause keywords in campaign."""
        logger.info(f"Pausing {len(keywords)} keywords in campaign {campaign_id}")
        
        try:
            data = {
                "campaignId": int(campaign_id),
                "keywords": [{"keyword": kw, "status": "PAUSED"} for kw in keywords]
            }
            
            response = self._make_request("POST", "/v1/performance/keyword/status/set", data)
            
            if response.get("result"):
                logger.info("Successfully paused keywords")
                return True
            else:
                logger.error(f"Failed to pause keywords: {response}")
                return False
        
        except Exception as e:
            logger.error(f"Error pausing keywords: {e}")
            return False
    
    def get_product_info(self, product_id: str) -> Dict:
        """Get product information."""
        try:
            data = {"product_id": int(product_id)}
            response = self._make_request("POST", "/v2/product/info", data)
            return response.get("result", {})
        except Exception as e:
            logger.error(f"Failed to get product info: {e}")
            return {}