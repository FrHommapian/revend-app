import logging
import re
from universal_brand_engine import UniversalBrandEngine
from enhanced_pricing_database import ENHANCED_PRICING_DATABASE, CONDITION_MULTIPLIERS

logger = logging.getLogger(__name__)

class RealPricingEngine:
    def __init__(self):
        self.brand_engine = UniversalBrandEngine()
        self.enhanced_db = ENHANCED_PRICING_DATABASE
        
        # Updated base prices with luxury support
        self.base_prices = {
            'electronics': 150,
            'fashion_beauty': 200,  # Increased for luxury support
            'home_garden': 100,
            'vehicles': 5000,
            'baby_kids': 50
        }
        
        # Luxury brand multipliers
        self.luxury_multipliers = {
            'prada': 15.0,
            'gucci': 12.0,
            'chanel': 20.0,
            'louis vuitton': 18.0,
            'lv': 18.0,
            'hermes': 25.0,
            'rolex': 30.0,
            'cartier': 20.0,
            'tiffany': 15.0,
            'dior': 12.0,
            'versace': 10.0,
            'armani': 8.0,
            'yves saint laurent': 10.0,
            'ysl': 10.0,
            'burberry': 8.0,
            'bottega veneta': 12.0,
            'balenciaga': 10.0,
            'fendi': 12.0
        }
    
    def get_brand_pricing(self, brand, description, condition, category):
        """Get pricing using Universal Brand Engine"""
        try:
            logger.info(f"🔍 BRAND ENGINE PRICING: {brand} - {description}")
            
            # Use Universal Brand Engine
            brand_pricing = self.brand_engine.get_dynamic_pricing(brand, description, condition)
            
            # Check if it's a meaningful price
            market_value = brand_pricing.get('pricing_analysis', {}).get('market_value', 0)
            
            if market_value > 100:
                logger.info(f"✅ BRAND ENGINE SUCCESS: ${market_value}")
                return brand_pricing
            else:
                logger.info(f"⚠️ BRAND ENGINE LOW PRICE: ${market_value}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Brand engine error: {e}")
            return None
    
    def get_database_pricing(self, brand, description, condition, category):
        """Get pricing from Enhanced Database"""
        try:
            logger.info(f"🔍 DATABASE PRICING: {brand} - {description}")
            
            brand_lower = brand.lower().strip()
            desc_lower = description.lower().strip()
            
            # Search enhanced database
            for item_key, item_data in self.enhanced_db.items():
                item_brand = item_data.get('brand', '').lower()
                item_keywords = item_data.get('keywords', [])
                
                # Brand match
                brand_match = (item_brand == brand_lower or 
                             brand_lower in item_brand or 
                             item_brand in brand_lower)
                
                # Keyword match
                keyword_match = any(keyword in desc_lower for keyword in item_keywords)
                
                if brand_match and keyword_match:
                    base_price = item_data.get('base_price', 100)
                    
                    # Apply condition multiplier
                    condition_multiplier = CONDITION_MULTIPLIERS.get(condition.lower(), 0.85)
                    final_price = base_price * condition_multiplier
                    
                    logger.info(f"✅ DATABASE MATCH: {item_key} - ${final_price}")
                    
                    return {
                        'pricing_analysis': {
                            'quick_sale': round(final_price * 0.85, 0),
                            'market_value': round(final_price, 0),
                            'premium_price': round(final_price * 1.15, 0),
                            'range_min': round(final_price * 0.85, 0),
                            'range_max': round(final_price * 1.15, 0),
                            'average': round(final_price, 0),
                            'confidence': 'high',
                            'pricing_source': 'enhanced_database'
                        },
                        'sources': [{'source': f'Enhanced Database ({item_key})', 'confidence': 'high'}]
                    }
            
            logger.info(f"⚠️ DATABASE: No match found")
            return None
            
        except Exception as e:
            logger.error(f"❌ Database error: {e}")
            return None
    
    def analyze_comprehensive_pricing(self, item_info):
        """Enhanced comprehensive pricing with luxury support"""
        try:
            category = item_info.get('category', 'electronics')
            condition = item_info.get('condition', 'good')
            brand = item_info.get('brand', 'Unknown').lower().strip()
            description = item_info.get('description', '')
            
            logger.info(f"📊 COMPREHENSIVE PRICING:")
            logger.info(f"   Brand: {brand}")
            logger.info(f"   Category: {category}")
            logger.info(f"   Condition: {condition}")
            
            # Base price from category
            base_price = self.base_prices.get(category, 100)
            
            # Check for luxury brands
            luxury_multiplier = self.luxury_multipliers.get(brand, 1.0)
            if luxury_multiplier > 1.0:
                base_price = base_price * luxury_multiplier
                logger.info(f"🏆 LUXURY BRAND DETECTED: {brand} (×{luxury_multiplier})")
            
            # Condition multipliers
            condition_multipliers = {
                'excellent': 1.2,
                'very_good': 1.0,
                'good': 0.85,
                'fair': 0.65,
                'poor': 0.45
            }
            
            multiplier = condition_multipliers.get(condition, 0.85)
            final_price = base_price * multiplier
            
            logger.info(f"💰 FINAL CALCULATION:")
            logger.info(f"   Base: ${base_price}")
            logger.info(f"   Condition: {condition} (×{multiplier})")
            logger.info(f"   Final: ${final_price}")
            
            return {
                'pricing_analysis': {
                    'quick_sale': round(final_price * 0.85, 0),
                    'market_value': round(final_price, 0),
                    'premium_price': round(final_price * 1.15, 0),
                    'range_min': round(final_price * 0.85, 0),
                    'range_max': round(final_price * 1.15, 0),
                    'average': round(final_price, 0),
                    'confidence': 'medium',
                    'pricing_source': 'comprehensive_engine'
                },
                'sources': [{'source': 'Enhanced Pricing Engine', 'confidence': 'medium'}]
            }
            
        except Exception as e:
            logger.error(f"❌ Error in comprehensive pricing: {e}")
            return {
                'pricing_analysis': {
                    'quick_sale': 50,
                    'market_value': 75,
                    'premium_price': 100,
                    'range_min': 50,
                    'range_max': 100,
                    'average': 75,
                    'confidence': 'low',
                    'pricing_source': 'fallback'
                },
                'sources': [{'source': 'Fallback Pricing', 'confidence': 'low'}]
            }
