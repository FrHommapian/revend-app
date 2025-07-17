from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
import os
import base64
import json
from datetime import datetime
import logging
from dotenv import load_dotenv
from PIL import Image
import io
import re
import hashlib
import time
import requests
from textblob import TextBlob
import numpy as np

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = f'revend-secret-key-{int(time.time())}'

def call_openai_api(image_base64, prompt_type="analysis"):
    """Advanced OpenAI API calls with multiple prompt strategies"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return None
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        # Different prompts for different analysis types
        prompts = {
            "analysis": """You are an expert appraiser analyzing second-hand items for Australian marketplace pricing. 

Analyze this image thoroughly and provide:
1. EXACT brand name (if visible)
2. Specific item type and model
3. Condition assessment (excellent/very_good/good/fair/poor)
4. Market category (fashion_beauty/electronics/vehicles/home_garden/baby_kids)
5. Australian market value estimate in AUD
6. Key factors affecting price (age, condition, rarity, demand)

Consider current Australian market conditions, depreciation rates, and actual resale values.

Return JSON: {
    "brand": "exact brand name or unknown",
    "model": "specific model/variant",
    "item_type": "specific item description",
    "category": "market category",
    "condition": "condition assessment",
    "estimated_value_aud": "price in AUD",
    "confidence_level": "high/medium/low",
    "price_factors": ["factor1", "factor2", "factor3"],
    "market_notes": "brief analysis of market positioning"
}""",
            
            "condition": """Focus specifically on the condition of this item. Assess:
- Physical wear and tear
- Functionality issues
- Aesthetic condition
- Signs of use or damage
- Overall preservation state

Rate from: excellent, very_good, good, fair, poor

Return JSON: {
    "condition": "condition_rating",
    "condition_details": "specific observations",
    "condition_impact": "how condition affects value"
}""",
            
            "pricing": """You are a pricing expert for Australian second-hand markets. 

Based on this item, provide realistic Australian market pricing considering:
- Current market demand
- Depreciation from retail
- Condition impact
- Brand positioning
- Seasonal factors
- Competition analysis

Return JSON: {
    "quick_sale_price": "conservative price for fast sale",
    "market_value": "realistic market value",
    "premium_price": "optimistic but achievable price",
    "pricing_confidence": "high/medium/low",
    "market_analysis": "brief market context"
}"""
        }
        
        prompt = prompts.get(prompt_type, prompts["analysis"])
        
        payload = {
            'model': 'gpt-4o',
            'messages': [
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': prompt
                        },
                        {
                            'type': 'image_url',
                            'image_url': {'url': f'data:image/jpeg;base64,{image_base64}'}
                        }
                    ]
                }
            ],
            'max_tokens': 800,
            'temperature': 0.1
        }
        
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=payload, timeout=45)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        return None

def search_market_data(brand, item_type, model):
    """Search for market data to supplement AI analysis"""
    try:
        # Search terms for market research
        search_terms = [
            f"{brand} {model} {item_type} price Australia",
            f"{brand} {item_type} second hand market value",
            f"{brand} {model} resale value AUD"
        ]
        
        market_data = []
        
        for term in search_terms:
            try:
                # This is a placeholder for market research
                # In production, you'd integrate with real market data APIs
                market_data.append({
                    'source': 'market_research',
                    'search_term': term,
                    'relevance': 'high'
                })
            except:
                continue
        
        return market_data
        
    except Exception as e:
        logger.error(f"Market research failed: {e}")
        return []

class IntelligentPricingEngine:
    def __init__(self):
        # LUXURY BRAND BASE PRICES (Australian market)
        self.luxury_base_prices = {
            # Ultra-luxury tier
            'hermes': {'handbag': 8000, 'wallet': 2500, 'shoes': 3000, 'default': 6000},
            'chanel': {'handbag': 4500, 'wallet': 1500, 'shoes': 2000, 'default': 3500},
            'louis vuitton': {'handbag': 3800, 'wallet': 1200, 'shoes': 1800, 'default': 3000},
            
            # High-luxury tier
            'prada': {'handbag': 2200, 'wallet': 800, 'shoes': 1200, 'default': 1800},
            'gucci': {'handbag': 2000, 'wallet': 700, 'shoes': 1100, 'default': 1600},
            'dior': {'handbag': 2400, 'wallet': 900, 'shoes': 1400, 'default': 2000},
            'versace': {'handbag': 1800, 'wallet': 600, 'shoes': 1000, 'default': 1400},
            'armani': {'handbag': 1600, 'wallet': 500, 'shoes': 900, 'default': 1200},
            
            # Luxury watches
            'rolex': {'watch': 15000, 'default': 12000},
            'patek philippe': {'watch': 25000, 'default': 20000},
            'audemars piguet': {'watch': 18000, 'default': 15000},
            'omega': {'watch': 4000, 'default': 3500},
            'cartier': {'watch': 6000, 'jewelry': 2500, 'default': 4000},
            'tag heuer': {'watch': 2500, 'default': 2000},
            
            # Premium fashion
            'coach': {'handbag': 600, 'wallet': 200, 'default': 400},
            'michael kors': {'handbag': 300, 'wallet': 100, 'default': 200},
            'kate spade': {'handbag': 350, 'wallet': 120, 'default': 250},
            'marc jacobs': {'handbag': 400, 'wallet': 150, 'default': 300},
            'tory burch': {'handbag': 380, 'wallet': 140, 'default': 280},
            
            # Technology premium
            'apple': {'phone': 1200, 'laptop': 2200, 'tablet': 800, 'watch': 500, 'default': 1000},
            'samsung': {'phone': 900, 'laptop': 1400, 'tablet': 600, 'tv': 1200, 'default': 800},
            'sony': {'camera': 1800, 'headphones': 400, 'tv': 1400, 'console': 700, 'default': 600},
            'canon': {'camera': 1600, 'lens': 800, 'default': 1200},
            'nikon': {'camera': 1500, 'lens': 700, 'default': 1100},
            'leica': {'camera': 4000, 'lens': 2000, 'default': 3000},
            
            # Premium sports/fashion
            'nike': {'shoes': 180, 'clothing': 80, 'default': 130},
            'adidas': {'shoes': 160, 'clothing': 70, 'default': 115},
            'dr. martens': {'shoes': 200, 'default': 180},
            'timberland': {'shoes': 180, 'default': 160},
            'converse': {'shoes': 100, 'default': 90},
            'vans': {'shoes': 90, 'default': 80}
        }
        
        # Standard category bases for non-luxury items
        self.category_bases = {
            'fashion_beauty': {
                'handbag': 80, 'wallet': 40, 'shoes': 60, 'clothing': 30,
                'jewelry': 50, 'watch': 100, 'sunglasses': 40, 'belt': 25
            },
            'electronics': {
                'smartphone': 300, 'laptop': 600, 'tablet': 200, 'camera': 400,
                'headphones': 60, 'smartwatch': 150, 'gaming_console': 250,
                'tv': 400, 'speaker': 80
            },
            'vehicles': {
                'car': 15000, 'motorcycle': 5000, 'bicycle': 300, 'boat': 8000,
                'caravan': 20000, 'trailer': 2000
            },
            'home_garden': {
                'furniture': 150, 'appliance': 250, 'tool': 60, 'decor': 30,
                'kitchen': 80, 'bedding': 50, 'lighting': 40
            },
            'baby_kids': {
                'stroller': 120, 'crib': 180, 'car_seat': 100, 'toy': 25,
                'clothing': 15, 'books': 8, 'gear': 60
            }
        }
        
        # Condition multipliers
        self.condition_multipliers = {
            'excellent': 1.0,    # No reduction for excellent
            'very_good': 0.90,   # 10% reduction
            'good': 0.75,        # 25% reduction
            'fair': 0.55,        # 45% reduction
            'poor': 0.35         # 65% reduction
        }
    
    def calculate_base_price(self, category, item_type, brand=None):
        """Calculate base price with proper luxury pricing"""
        brand_lower = brand.lower() if brand else None
        
        # Check luxury brand first
        if brand_lower and brand_lower in self.luxury_base_prices:
            luxury_data = self.luxury_base_prices[brand_lower]
            base_price = luxury_data.get(item_type, luxury_data.get('default', 500))
            logger.info(f"💎 LUXURY PRICING: {brand} {item_type} → ${base_price}")
            return base_price
        
        # Standard category pricing
        category_data = self.category_bases.get(category, {})
        base_price = category_data.get(item_type, category_data.get('default', 80))
        logger.info(f"📊 STANDARD PRICING: {category} {item_type} → ${base_price}")
        return base_price
    
    def generate_dynamic_pricing(self, analysis_data, market_data=None):
        """Generate dynamic pricing with proper luxury handling"""
        try:
            brand = analysis_data.get('brand', 'unknown')
            item_type = analysis_data.get('item_type', 'item').lower()
            category = analysis_data.get('category', 'electronics')
            condition = analysis_data.get('condition', 'good')
            confidence = analysis_data.get('confidence_level', 'medium')
            
            # Get base price (already handles luxury vs standard)
            base_price = self.calculate_base_price(category, item_type, brand)
            
            # Apply condition multiplier
            condition_multiplier = self.condition_multipliers.get(condition, 0.75)
            final_price = base_price * condition_multiplier
            
            logger.info(f"💰 PRICE CALCULATION:")
            logger.info(f"   Base: ${base_price}")
            logger.info(f"   Condition: {condition} (×{condition_multiplier})")
            logger.info(f"   Final: ${final_price}")
            
            # Generate price range (clean integers)
            market_value = round(final_price)
            quick_sale = round(final_price * 0.80)
            premium_price = round(final_price * 1.20)
            
            # Confidence adjustment (minimal for luxury items)
            confidence_adjustments = {
                'high': 1.0,
                'medium': 0.95,
                'low': 0.90
            }
            
            # For luxury brands, use minimal confidence adjustment
            is_luxury = brand and brand.lower() in self.luxury_base_prices
            confidence_adj = confidence_adjustments.get(confidence, 0.95)
            if is_luxury:
                confidence_adj = max(confidence_adj, 0.95)  # Minimum 95% for luxury
            
            # Apply final adjustment
            final_market_value = round(market_value * confidence_adj)
            final_quick_sale = round(quick_sale * confidence_adj)
            final_premium_price = round(premium_price * confidence_adj)
            
            logger.info(f"🎯 FINAL PRICING:")
            logger.info(f"   Market: ${final_market_value}")
            logger.info(f"   Quick Sale: ${final_quick_sale}")
            logger.info(f"   Premium: ${final_premium_price}")
            logger.info(f"   Confidence: {confidence} (×{confidence_adj})")
            
            return {
                'pricing_analysis': {
                    'quick_sale': final_quick_sale,
                    'market_value': final_market_value,
                    'premium_price': final_premium_price,
                    'range_min': final_quick_sale,
                    'range_max': final_premium_price,
                    'average': final_market_value,
                    'confidence': confidence,
                    'pricing_source': 'ai_luxury_analysis'
                },
                'pricing_breakdown': {
                    'base_price': base_price,
                    'condition_impact': condition_multiplier,
                    'is_luxury_brand': is_luxury,
                    'confidence_adjustment': confidence_adj,
                    'final_calculation': f"${base_price} × {condition_multiplier} × {confidence_adj} = ${final_market_value}"
                },
                'sources': [
                    {'source': 'AI Visual Analysis', 'confidence': confidence},
                    {'source': 'Luxury Brand Database', 'confidence': 'high' if is_luxury else 'medium'},
                    {'source': 'Market Intelligence', 'confidence': 'medium'}
                ]
            }
            
        except Exception as e:
            logger.error(f"Dynamic pricing failed: {e}")
            return self.fallback_pricing(analysis_data)
    
    def fallback_pricing(self, analysis_data):
        """Fallback pricing when main analysis fails"""
        category = analysis_data.get('category', 'electronics')
        condition = analysis_data.get('condition', 'good')
        
        base_price = 120  # Conservative fallback
        condition_multiplier = self.condition_multipliers.get(condition, 0.75)
        final_price = round(base_price * condition_multiplier)
        
        return {
            'pricing_analysis': {
                'quick_sale': round(final_price * 0.8),
                'market_value': final_price,
                'premium_price': round(final_price * 1.2),
                'range_min': round(final_price * 0.8),
                'range_max': round(final_price * 1.2),
                'average': final_price,
                'confidence': 'low',
                'pricing_source': 'fallback_estimation'
            },
            'sources': [{'source': 'Fallback Estimation', 'confidence': 'low'}]
        }

pricing_engine = IntelligentPricingEngine()

MARKETPLACE_CATEGORIES = {
    "electronics": {
        "name": "Electronics & Technology",
        "subcategories": ["smartphones", "laptops", "tablets", "gaming", "audio", "cameras", "smart_home", "wearables"],
        "keywords": ["phone", "laptop", "computer", "gaming", "headphones", "camera", "smart", "tech", "speaker", "bluetooth"],
        "condition_factors": ["screen_damage", "battery_life", "functionality", "accessories"],
        "depreciation_rate": 0.25,
        "analysis_focus": "brand, model, storage, specs, condition, functionality"
    },
    "vehicles": {
        "name": "Vehicles & Transportation",
        "subcategories": ["cars", "trucks", "vans", "motorcycles", "boats", "bicycles", "scooters", "caravans", "trailers"],
        "keywords": ["car", "truck", "van", "vehicle", "motorcycle", "bike", "boat", "scooter", "caravan", "trailer"],
        "condition_factors": ["mileage", "service_history", "body_condition", "mechanical_condition"],
        "depreciation_rate": 0.15,
        "analysis_focus": "make, model, year, mileage, condition, features"
    },
    "fashion_beauty": {
        "name": "Fashion & Beauty",
        "subcategories": ["clothing", "shoes", "bags", "jewelry", "accessories", "beauty", "watches"],
        "keywords": ["dress", "shirt", "shoes", "bag", "jewelry", "watch", "beauty", "fashion", "handbag", "purse"],
        "condition_factors": ["fabric_condition", "fit", "brand_authenticity", "wear_signs"],
        "depreciation_rate": 0.30,
        "analysis_focus": "brand, size, material, condition, style, authenticity"
    },
    "home_garden": {
        "name": "Home & Garden",
        "subcategories": ["furniture", "appliances", "decor", "tools", "lighting", "outdoor", "kitchenware"],
        "keywords": ["furniture", "sofa", "table", "chair", "appliance", "tool", "garden"],
        "condition_factors": ["wear_tear", "functionality", "structural_integrity", "cleanliness"],
        "depreciation_rate": 0.30,
        "analysis_focus": "brand, material, size, condition, style, functionality"
    },
    "baby_kids": {
        "name": "Baby & Kids",
        "subcategories": ["toys", "clothing", "furniture", "strollers", "car_seats", "books"],
        "keywords": ["toy", "baby", "kids", "children", "stroller", "crib"],
        "condition_factors": ["safety_standards", "hygiene", "functionality", "age_appropriateness"],
        "depreciation_rate": 0.40,
        "analysis_focus": "brand, age_range, safety, condition, completeness"
    }
}

def analyze_item_photo(image_file):
    """Comprehensive AI-powered item analysis"""
    try:
        session_id = f"{int(time.time())}-{os.urandom(4).hex()}"
        filename = image_file.filename or 'unknown'
        
        image_file.seek(0)
        image_content = image_file.read()
        image_hash = hashlib.sha256(image_content + session_id.encode()).hexdigest()[:12]
        image_file.seek(0)
        
        logger.info(f"=== AI ANALYSIS SESSION {session_id} ===")
        logger.info(f"📁 File: {filename}")
        
        # Prepare image for analysis
        image = Image.open(image_file)
        
        # Optimize image for AI analysis
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if too large (maintain aspect ratio)
        max_size = 1024
        if max(image.size) > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=85)
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        logger.info(f"🖼️ Image processed: {image.size}")
        
        # Multi-stage AI analysis
        analysis_results = {}
        
        # Stage 1: Primary analysis
        logger.info("🤖 Stage 1: Primary AI analysis...")
        primary_analysis = call_openai_api(img_base64, "analysis")
        
        if primary_analysis:
            try:
                # Clean and parse JSON
                clean_text = re.sub(r'```json\s*', '', primary_analysis)
                clean_text = re.sub(r'```\s*', '', clean_text)
                
                analysis_results = json.loads(clean_text)
                logger.info(f"✅ Primary analysis successful")
                logger.info(f"🏷️ Brand: {analysis_results.get('brand', 'unknown')}")
                logger.info(f"📱 Item: {analysis_results.get('item_type', 'unknown')}")
                logger.info(f"💎 Condition: {analysis_results.get('condition', 'unknown')}")
                
            except Exception as e:
                logger.error(f"Primary analysis parsing failed: {e}")
                # Manual extraction fallback
                analysis_results = extract_analysis_manually(primary_analysis)
        
        # Stage 2: Condition-specific analysis (if primary was successful)
        if analysis_results.get('confidence_level') != 'high':
            logger.info("🔍 Stage 2: Detailed condition analysis...")
            condition_analysis = call_openai_api(img_base64, "condition")
            
            if condition_analysis:
                try:
                    condition_data = json.loads(re.sub(r'```json\s*', '', condition_analysis).replace('```', ''))
                    analysis_results.update(condition_data)
                    logger.info(f"✅ Condition analysis enhanced")
                except:
                    logger.warning("Condition analysis parsing failed")
        
        # Stage 3: Market research
        brand = analysis_results.get('brand', 'unknown')
        item_type = analysis_results.get('item_type', 'item')
        model = analysis_results.get('model', 'unknown')
        
        if brand != 'unknown' and item_type != 'item':
            logger.info("📊 Stage 3: Market research...")
            market_data = search_market_data(brand, item_type, model)
            analysis_results['market_data'] = market_data
        
        # Stage 4: Dynamic pricing calculation
        logger.info("💰 Stage 4: Dynamic pricing calculation...")
        pricing_data = pricing_engine.generate_dynamic_pricing(analysis_results)
        
        # Build comprehensive result
        item_info = {
            'brand': analysis_results.get('brand', 'unknown'),
            'model': analysis_results.get('model', 'unknown'),
            'category': analysis_results.get('category', 'electronics'),
            'description': analysis_results.get('item_type', 'item'),
            'condition': analysis_results.get('condition', 'good'),
            'session_id': session_id,
            'image_hash': image_hash
        }
        
        category_info = MARKETPLACE_CATEGORIES.get(item_info['category'], MARKETPLACE_CATEGORIES['electronics'])
        
        logger.info(f"🎯 FINAL RESULT:")
        logger.info(f"   Brand: {item_info['brand']}")
        logger.info(f"   Item: {item_info['description']}")
        logger.info(f"   Category: {item_info['category']}")
        logger.info(f"   Condition: {item_info['condition']}")
        logger.info(f"   Price: ${pricing_data['pricing_analysis']['market_value']}")
        logger.info(f"   Confidence: {pricing_data['pricing_analysis']['confidence']}")
        
        return {
            'category': item_info['category'],
            'category_info': category_info,
            'analysis': primary_analysis or 'AI analysis completed',
            'analysis_json': item_info,
            'pricing_data': pricing_data,
            'ai_analysis_data': analysis_results,
            'image_hash': image_hash,
            'session_id': session_id,
            'specific_item': item_info['description'],
            'ai_suggested_category': item_info['category'],
            'corrected_category': item_info['category'],
            'ai_estimated_value': f"${pricing_data['pricing_analysis']['market_value']}"
        }
        
    except Exception as e:
        logger.error(f"Comprehensive analysis failed: {e}")
        return None

def extract_analysis_manually(text):
    """Manual extraction when JSON parsing fails"""
    try:
        result = {
            'brand': 'unknown',
            'item_type': 'item',
            'category': 'electronics',
            'condition': 'good',
            'confidence_level': 'low'
        }
        
        text_lower = text.lower()
        
        # Brand detection
        luxury_brands = ['hermes', 'chanel', 'louis vuitton', 'prada', 'gucci', 'dior', 'rolex', 'cartier']
        premium_brands = ['coach', 'michael kors', 'apple', 'samsung', 'sony', 'canon', 'nike', 'adidas']
        
        for brand in luxury_brands + premium_brands:
            if brand in text_lower:
                result['brand'] = brand
                break
        
        # Item type detection
        if any(word in text_lower for word in ['handbag', 'bag', 'purse']):
            result['item_type'] = 'handbag'
            result['category'] = 'fashion_beauty'
        elif any(word in text_lower for word in ['phone', 'smartphone', 'iphone']):
            result['item_type'] = 'smartphone'
            result['category'] = 'electronics'
        elif any(word in text_lower for word in ['watch', 'timepiece']):
            result['item_type'] = 'watch'
            result['category'] = 'fashion_beauty'
        
        # Condition detection
        conditions = ['excellent', 'very good', 'good', 'fair', 'poor']
        for condition in conditions:
            if condition in text_lower:
                result['condition'] = condition.replace(' ', '_')
                break
        
        return result
        
    except Exception as e:
        logger.error(f"Manual extraction failed: {e}")
        return {
            'brand': 'unknown',
            'item_type': 'item',
            'category': 'electronics',
            'condition': 'good',
            'confidence_level': 'low'
        }

def generate_category_listing(analysis_data):
    """Generate intelligent listing based on comprehensive analysis"""
    analysis_json = analysis_data.get('analysis_json', {})
    pricing_analysis = analysis_data.get('pricing_data', {}).get('pricing_analysis', {})
    ai_analysis = analysis_data.get('ai_analysis_data', {})
    
    brand = analysis_json.get('brand', 'Unknown')
    model = analysis_json.get('model', 'Unknown')
    specific_item = analysis_data.get('specific_item', 'item')
    condition = analysis_json.get('condition', 'good')
    market_value = pricing_analysis.get('market_value', 100)
    
    # Get additional context from AI analysis
    market_notes = ai_analysis.get('market_notes', '')
    price_factors = ai_analysis.get('price_factors', [])
    
    logger.info(f"📝 INTELLIGENT LISTING: {brand} {model} {specific_item} - ${market_value}")
    
    # Generate contextual listing
    brand_text = f" {brand}" if brand != 'Unknown' and brand != 'unknown' else ""
    model_text = f" {model}" if model != 'Unknown' and model != 'unknown' else ""
    
    listing = f"I'm selling my{brand_text}{model_text} {specific_item} in {condition} condition for ${market_value}. "
    
    # Add AI-generated context
    if market_notes:
        listing += f"{market_notes[:100]}... "
    
    listing += f"This item has been well-maintained and is ready for a new owner. "
    
    # Add price factors if available
    if price_factors:
        listing += f"Key features: {', '.join(price_factors[:3])}. "
    
    listing += f"It's a great opportunity to get a quality {specific_item} at a fair market price. Please feel free to contact me if you have any questions or would like to arrange a viewing. Serious buyers only, please. Located in Australia with flexible pickup arrangements available."
    
    return listing

@app.route('/')
def index():
    session.clear()
    return render_template('index.html', categories=MARKETPLACE_CATEGORIES)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'photo' not in request.files or request.files['photo'].filename == '':
            flash('No photo uploaded')
            return redirect(url_for('index'))
        
        photo = request.files['photo']
        analysis_data = analyze_item_photo(photo)
        
        if not analysis_data:
            flash('Error analyzing photo')
            return redirect(url_for('index'))
        
        session['current_analysis'] = analysis_data
        listing = generate_category_listing(analysis_data)
        
        return render_template('results.html', analysis_data=analysis_data, listing=listing)
        
    except Exception as e:
        logger.error(f"Route error: {e}")
        flash('Error processing request')
        return redirect(url_for('index'))

@app.route('/refine-analysis', methods=['POST'])
def refine_analysis():
    try:
        original_analysis = session.get('current_analysis')
        if not original_analysis:
            return redirect(url_for('index'))
        
        condition = request.form.get('condition', original_analysis['analysis_json']['condition']).strip()
        additional_notes = request.form.get('additional_notes', '').strip()
        
        original_price = original_analysis['pricing_data']['pricing_analysis']['market_value']
        
        # Intelligent condition adjustment
        condition_multipliers = {
            'excellent': 1.0,
            'very_good': 0.90,
            'good': 0.75,
            'fair': 0.55,
            'poor': 0.35,
            'damaged': 0.25
        }
        
        # Damage keyword detection
        damage_keywords = ['crack', 'broken', 'damage', 'chip', 'scratch', 'dent', 'worn', 'faded', 'stain']
        damage_multiplier = 0.8 if any(keyword in additional_notes.lower() for keyword in damage_keywords) else 1.0
        
        # Positive keyword detection
        positive_keywords = ['mint', 'pristine', 'like new', 'barely used', 'excellent', 'perfect']
        positive_multiplier = 1.05 if any(keyword in additional_notes.lower() for keyword in positive_keywords) else 1.0
        
        # Calculate adjustment
        original_condition = original_analysis['analysis_json']['condition']
        original_multiplier = condition_multipliers.get(original_condition, 0.75)
        new_multiplier = condition_multipliers.get(condition, 0.75)
        
        # Calculate base price from original
        base_price = original_price / original_multiplier
        adjusted_price = base_price * new_multiplier * damage_multiplier * positive_multiplier
        
        new_market_value = round(adjusted_price)
        
        # Update analysis
        updated_analysis = original_analysis.copy()
        updated_analysis['analysis_json']['condition'] = condition
        updated_analysis['pricing_data']['pricing_analysis']['market_value'] = new_market_value
        updated_analysis['pricing_data']['pricing_analysis']['quick_sale'] = round(adjusted_price * 0.8)
        updated_analysis['pricing_data']['pricing_analysis']['premium_price'] = round(adjusted_price * 1.2)
        
        session['current_analysis'] = updated_analysis
        updated_listing = generate_category_listing(updated_analysis)
        
        logger.info(f"💰 INTELLIGENT ADJUSTMENT: ${original_price} → ${new_market_value}")
        logger.info(f"📊 Factors: condition={condition}, damage={damage_multiplier}, positive={positive_multiplier}")
        
        return render_template('results.html', analysis_data=updated_analysis, listing=updated_listing, updated=True)
        
    except Exception as e:
        logger.error(f"Refine error: {e}")
        return redirect(url_for('index'))

@app.route('/categories')
def categories():
    return jsonify(MARKETPLACE_CATEGORIES)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
