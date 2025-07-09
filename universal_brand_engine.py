import re
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class UniversalBrandEngine:
    def __init__(self):
        # Enhanced brand premium multipliers with VEHICLES AND LUXURY FRAGRANCE
        self.brand_tiers = {
            'luxury_vehicles': {
                'multiplier': 1.0,
                'brands': ['ferrari', 'lamborghini', 'porsche', 'maserati', 'bentley', 'rolls royce', 'aston martin'],
                'retention_rate': 0.75,
                'base_price_override': 150000
            },
            'premium_vehicles': {
                'multiplier': 1.0,
                'brands': ['bmw', 'mercedes', 'audi', 'lexus', 'tesla', 'jaguar', 'land rover', 'volvo'],
                'retention_rate': 0.70,
                'base_price_override': 55000
            },
            'mainstream_vehicles': {
                'multiplier': 1.0,
                'brands': ['ford', 'holden', 'toyota', 'honda', 'mazda', 'hyundai', 'kia', 'nissan', 'subaru', 'mitsubishi', 'volkswagen', 'chevrolet'],
                'retention_rate': 0.75,
                'base_price_override': 50000
            },
            'commercial_vehicles': {
                'multiplier': 1.0,
                'brands': ['isuzu', 'iveco', 'man', 'scania', 'volvo trucks', 'ford commercial'],
                'retention_rate': 0.70,
                'base_price_override': 60000
            },
            'luxury_tier_1': {
                'multiplier': 2.5,
                'brands': ['hermes', 'chanel', 'louis vuitton', 'cartier', 'patek philippe', 'le labo', 'creed', 'tom ford', 'maison margiela'],
                'retention_rate': 0.7
            },
            'luxury_tier_2': {
                'multiplier': 1.8,
                'brands': ['prada', 'gucci', 'rolex', 'omega', 'versace', 'armani', 'yves saint laurent', 'dior'],
                'retention_rate': 0.6
            },
            'premium_tier_1': {
                'multiplier': 1.5,
                'brands': ['apple', 'gibson', 'fender'],
                'retention_rate': 0.55
            },
            'premium_tier_2': {
                'multiplier': 1.3,
                'brands': ['samsung', 'sony', 'nike', 'adidas', 'yamaha', 'roland'],
                'retention_rate': 0.5
            },
            'mainstream': {
                'multiplier': 1.0,
                'brands': ['hp', 'dell', 'casio', 'uniqlo'],
                'retention_rate': 0.4
            },
            'budget': {
                'multiplier': 0.7,
                'brands': ['kmart', 'target', 'walmart', 'generic'],
                'retention_rate': 0.3
            }
        }
        
        # REALISTIC VEHICLE PRICING
        self.category_base_prices = {
            # SPECIFIC VEHICLE MODELS
            'ford transit custom': 55000,
            'ford transit': 50000,
            'toyota hiace': 45000,
            'mercedes sprinter': 65000,
            'volkswagen crafter': 60000,
            'iveco daily': 55000,
            
            # VEHICLE CATEGORIES
            'van': 50000,
            'truck': 60000,
            'car': 35000,
            'ute': 45000,
            'suv': 50000,
            'sedan': 35000,
            'hatchback': 30000,
            'wagon': 40000,
            'vehicles': 40000,
            
            # FRAGRANCE CATEGORIES
            'cologne': 150,
            'perfume': 150,
            'fragrance': 150,
            'eau de toilette': 120,
            'eau de parfum': 180,
            
            # NON-VEHICLE CATEGORIES
            'handbag': 80,
            'purse': 60,
            'bag': 50,
            'laptop': 800,
            'phone': 400,
            'smartphone': 500,
            'tablet': 300,
            'watch': 200,
            'shoes': 80,
            'dress': 60,
            'shirt': 30,
            'sofa': 400,
            'chair': 150,
            'table': 250,
            'tv': 600,
            'speaker': 100,
            'headphones': 80,
            'camera': 500
        }
    
    def detect_brand_tier(self, brand_name: str, category: str = '') -> Dict:
        """Enhanced brand tier detection with vehicle support"""
        brand_lower = brand_name.lower().strip()
        
        logger.info(f"🔍 Brand tier detection for: '{brand_name}' in category: '{category}'")
        
        # Check all tiers including vehicle tiers
        for tier_name, tier_data in self.brand_tiers.items():
            for brand in tier_data['brands']:
                if brand in brand_lower or brand_lower in brand:
                    logger.info(f"✅ Brand '{brand_name}' matched tier: {tier_name}")
                    return {
                        'tier': tier_name,
                        'multiplier': tier_data['multiplier'],
                        'retention_rate': tier_data['retention_rate'],
                        'recognized': True,
                        'base_price_override': tier_data.get('base_price_override')
                    }
        
        # Default tiers based on category
        if 'vehicle' in category.lower():
            logger.info(f"🚗 Unknown vehicle brand, using mainstream vehicle tier")
            return {
                'tier': 'mainstream_vehicles',
                'multiplier': 1.0,
                'retention_rate': 0.75,
                'recognized': False,
                'base_price_override': 50000,
                'reason': 'unknown_vehicle_brand'
            }
        
        return {
            'tier': 'mainstream',
            'multiplier': 1.0,
            'retention_rate': 0.4,
            'recognized': False,
            'reason': 'unknown_brand'
        }
    
    def detect_item_category(self, description: str) -> str:
        """Enhanced item category detection with vehicle priority"""
        desc_lower = description.lower()
        
        # PRIORITY 1: Vehicle detection
        vehicle_keywords = [
            'car', 'truck', 'van', 'ute', 'suv', 'sedan', 'hatchback', 'wagon',
            'vehicle', 'automobile', 'motor', 'ford transit', 'hiace', 'sprinter',
            'motorcycle', 'bike', 'scooter', 'boat', 'caravan', 'trailer'
        ]
        
        if any(keyword in desc_lower for keyword in vehicle_keywords):
            logger.info(f"🚗 Vehicle category detected for: {description}")
            return 'vehicles'
        
        # PRIORITY 2: Fragrance detection
        fragrance_keywords = ['cologne', 'perfume', 'fragrance', 'eau de toilette', 'eau de parfum', 'edp', 'edt']
        
        if any(keyword in desc_lower for keyword in fragrance_keywords):
            logger.info(f"🌸 Fragrance category detected for: {description}")
            return 'cologne'
        
        # Try to match with specific category base prices
        for category in self.category_base_prices.keys():
            if category in desc_lower:
                if category in vehicle_keywords:
                    return 'vehicles'
                return category
        
        return 'general'
    
    def get_dynamic_pricing(self, brand: str, description: str, condition: str = 'good') -> Dict:
        """Enhanced dynamic pricing with vehicle support - MATCHES PRICING ENGINE EXPECTATIONS"""
        
        # Step 1: Detect brand tier with category context
        category = self.detect_item_category(description)
        brand_info = self.detect_brand_tier(brand, category)
        
        # Step 2: Get base price - prioritize vehicle pricing
        if brand_info.get('base_price_override'):
            base_price = brand_info['base_price_override']
            logger.info(f"🚗 Using vehicle base price override: ${base_price}")
        else:
            base_price = self.category_base_prices.get(category, 100)
            if 'vehicle' not in brand_info['tier']:
                base_price = base_price * brand_info['multiplier']
        
        # Step 3: Apply condition adjustments
        condition_multipliers = {
            'excellent': 1.2,
            'very_good': 1.0,
            'good': 0.85,
            'fair': 0.65,
            'poor': 0.45,
            'damaged': 0.25
        }
        
        condition_multiplier = condition_multipliers.get(condition.lower(), 0.85)
        
        # Step 4: Calculate final price
        final_price = base_price * condition_multiplier * brand_info['retention_rate']
        
        logger.info(f"🎯 UNIVERSAL PRICING CALCULATION:")
        logger.info(f"   Brand: {brand} ({brand_info['tier']})")
        logger.info(f"   Category: {category}")
        logger.info(f"   Base Price: ${base_price}")
        logger.info(f"   Condition: {condition} ({condition_multiplier})")
        logger.info(f"   Retention Rate: {brand_info['retention_rate']}")
        logger.info(f"   Final Price: ${final_price}")
        
        # RETURN STRUCTURE THAT MATCHES PRICING ENGINE EXPECTATIONS
        return {
            'pricing_analysis': {
                'quick_sale': round(final_price * 0.8, 0),
                'market_value': round(final_price, 0),
                'premium_price': round(final_price * 1.2, 0),
                'range_min': round(final_price * 0.7, 0),
                'range_max': round(final_price * 1.3, 0),
                'average': round(final_price, 0),
                'confidence': 'high',
                'data_points': 1,
                'confidence_score': 80
            },
            'sources': [
                {
                    'source': f'Universal Brand Engine ({brand_info["tier"]})',
                    'base_price': base_price,
                    'confidence': 'high',
                    'method': 'brand_tier_analysis'
                }
            ],
            'brand_analysis': brand_info,
            'calculation_details': {
                'base_price': base_price,
                'condition_multiplier': condition_multiplier,
                'retention_rate': brand_info['retention_rate'],
                'final_price': final_price,
                'category': category
            }
        }
