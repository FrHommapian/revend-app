import requests
from bs4 import BeautifulSoup
import re
import json
import time
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import hashlib
from urllib.parse import quote_plus
import sqlite3
from universal_brand_engine import UniversalBrandEngine

logger = logging.getLogger(__name__)

class RealPricingEngine:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.cache = {}
        self.universal_engine = UniversalBrandEngine()
        self.init_feedback_db()
    
    def init_feedback_db(self):
        """Initialize user feedback database"""
        try:
            conn = sqlite3.connect('pricing_feedback.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pricing_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_description TEXT,
                    brand TEXT,
                    model TEXT,
                    category TEXT,
                    condition TEXT,
                    our_estimate REAL,
                    user_feedback_price REAL,
                    actual_sold_price REAL,
                    feedback_type TEXT,
                    user_comment TEXT,
                    timestamp DATETIME,
                    session_id TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Could not initialize feedback database: {e}")
    
    def get_ebay_sold_prices(self, search_term: str) -> Dict:
        """Enhanced eBay scraping"""
        try:
            logger.info(f"Searching eBay for: '{search_term}'")
            
            clean_term = re.sub(r'[^\w\s\-]', '', search_term).strip()
            
            url = f"https://www.ebay.com.au/sch/i.html"
            params = {
                '_nkw': clean_term,
                'LH_Sold': '1',
                'LH_Complete': '1',
                '_ipg': '60'
            }
            
            response = self.session.get(url, params=params, timeout=8)
            
            if response.status_code != 200:
                return {'source': 'eBay Australia', 'prices': [], 'confidence': 'low'}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            prices = []
            
            price_elements = soup.find_all(['span'], class_=re.compile(r'.*price.*|.*notranslate.*'))
            
            for elem in price_elements[:20]:
                try:
                    price_text = elem.get_text().strip()
                    price_patterns = [
                        r'AU\s*\$\s*([\d,]+\.?\d*)',
                        r'\$\s*([\d,]+\.?\d*)\s*AUD',
                        r'\$\s*([\d,]+\.?\d*)'
                    ]
                    
                    for pattern in price_patterns:
                        price_match = re.search(pattern, price_text)
                        if price_match:
                            price = float(price_match.group(1).replace(',', ''))
                            if 10 <= price <= 50000:
                                prices.append(price)
                                break
                except:
                    continue
            
            if prices:
                logger.info(f"eBay found {len(prices)} prices")
                return {
                    'source': 'eBay Australia (Sold)',
                    'prices': prices,
                    'average': sum(prices) / len(prices),
                    'min': min(prices),
                    'max': max(prices),
                    'count': len(prices),
                    'confidence': 'high' if len(prices) >= 5 else 'medium'
                }
            
        except Exception as e:
            logger.warning(f"eBay search failed: {e}")
        
        return {'source': 'eBay Australia', 'prices': [], 'confidence': 'low'}
    
    def analyze_comprehensive_pricing(self, item_info: Dict) -> Dict:
        """Universal pricing for ANY brand/item combination"""
        search_key = hashlib.md5(json.dumps(item_info, sort_keys=True).encode()).hexdigest()[:10]
        
        logger.info(f"🔍 UNIVERSAL PRICING for: {item_info}")
        
        brand = item_info.get('brand', 'Unknown')
        model = item_info.get('model', '')
        description = item_info.get('description', '')
        condition = item_info.get('condition', 'good')
        
        all_prices = []
        sources = []
        
        # STRATEGY 1: Universal Brand Intelligence (Primary)
        if brand and brand != 'Unknown':
            logger.info(f"🎯 Using Universal Brand Engine for: {brand}")
            universal_result = self.universal_engine.get_dynamic_pricing(brand, description, condition)
            
            if universal_result:
                base_price = universal_result['pricing_analysis']['market_value']
                all_prices.extend([
                    base_price * 0.9,
                    base_price,
                    base_price * 1.1
                ])
                sources.append(universal_result['sources'][0])
                logger.info(f"✅ Universal pricing: ${base_price} (Brand tier: {universal_result['brand_analysis']['tier']})")
        
        # STRATEGY 2: eBay Market Data (Secondary)
        search_terms = []
        if brand and brand != 'Unknown':
            if model:
                search_terms.append(f"{brand} {model}")
            search_terms.append(f"{brand} {description}")
        search_terms.append(description)
        
        for search_term in search_terms[:2]:
            try:
                ebay_result = self.get_ebay_sold_prices(search_term)
                if ebay_result.get('prices'):
                    all_prices.extend(ebay_result['prices'][:5])
                    sources.append(ebay_result)
                    logger.info(f"✅ eBay: {len(ebay_result['prices'])} prices")
                    break
            except:
                continue
        
        # STRATEGY 3: Category Fallback (Tertiary)
        if len(all_prices) < 3:
            category_result = self.universal_engine.get_dynamic_pricing('Generic', description, condition)
            if category_result:
                fallback_price = category_result['pricing_analysis']['market_value']
                all_prices.append(fallback_price)
                sources.append({
                    'source': 'Category Intelligence',
                    'base_price': fallback_price,
                    'confidence': 'medium'
                })
                logger.info(f"✅ Category fallback: ${fallback_price}")
        
        # CALCULATE FINAL PRICING
        if all_prices:
            # Remove extreme outliers
            sorted_prices = sorted(all_prices)
            median_price = sorted_prices[len(sorted_prices)//2]
            
            # Filter outliers
            filtered_prices = [p for p in all_prices 
                             if median_price * 0.3 <= p <= median_price * 3]
            
            if len(filtered_prices) >= len(all_prices) * 0.7:
                all_prices = filtered_prices
            
            avg_price = sum(all_prices) / len(all_prices)
            min_price = min(all_prices)
            max_price = max(all_prices)
            
            # Pricing strategy
            quick_sale_price = avg_price * 0.8
            market_price = avg_price
            premium_price = avg_price * 1.2
            
            # Universal confidence scoring
            confidence_score = 0
            if any('Universal' in s.get('source', '') for s in sources):
                confidence_score += 50
            if any('eBay' in s.get('source', '') for s in sources):
                confidence_score += 30
            if any('Category' in s.get('source', '') for s in sources):
                confidence_score += 20
            
            confidence = 'high' if confidence_score >= 60 else 'medium' if confidence_score >= 30 else 'low'
            
            search_term = f"{brand} {model} {description}".strip()
            
            return {
                'pricing_analysis': {
                    'quick_sale': round(quick_sale_price, 0),
                    'market_value': round(market_price, 0),
                    'premium_price': round(premium_price, 0),
                    'range_min': round(min_price, 0),
                    'range_max': round(max_price, 0),
                    'average': round(avg_price, 0),
                    'confidence': confidence,
                    'data_points': len(all_prices),
                    'search_key': search_key,
                    'confidence_score': confidence_score
                },
                'sources': sources,
                'recommendation': f"Universal brand analysis. Price at ${avg_price:.0f}",
                'search_term': search_term,
                'brand_analysis': universal_result.get('brand_analysis') if 'universal_result' in locals() else None
            }
        
        # Ultimate fallback
        return self.get_universal_fallback(item_info)
    
    def get_universal_fallback(self, item_info: Dict) -> Dict:
        """Universal fallback for any item"""
        description = item_info.get('description', 'item')
        condition = item_info.get('condition', 'good')
        
        fallback_result = self.universal_engine.get_dynamic_pricing('Generic', description, condition)
        
        return {
            'pricing_analysis': fallback_result['pricing_analysis'],
            'sources': fallback_result['sources'],
            'recommendation': "Universal category analysis. Verify with market research.",
            'search_term': description
        }
