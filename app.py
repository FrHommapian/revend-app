from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
import os
import base64
import json
from datetime import datetime
import logging
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import io
import re
import hashlib
import time

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = f'revend-secret-key-{int(time.time())}'

def get_openai_client():
    """Working OpenAI client with correct model"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return None
        
        client = OpenAI(api_key=api_key)
        return client
    except Exception as e:
        logger.error(f"OpenAI client failed: {e}")
        return None

# BULLETPROOF PRICING ENGINE
class BulletproofPricingEngine:
    def __init__(self):
        self.brand_database = {
            # LUXURY TIER - $2000-8000
            'prada': {'handbag': 2500, 'wallet': 800, 'shoes': 1200, 'default': 2000},
            'gucci': {'handbag': 2200, 'wallet': 700, 'shoes': 1100, 'default': 1800},
            'chanel': {'handbag': 3200, 'wallet': 1200, 'shoes': 1600, 'default': 2500},
            'louis vuitton': {'handbag': 2800, 'wallet': 900, 'shoes': 1400, 'default': 2200},
            'hermes': {'handbag': 8000, 'wallet': 2000, 'shoes': 3000, 'default': 5000},
            'dior': {'handbag': 2400, 'wallet': 800, 'shoes': 1300, 'default': 2000},
            'versace': {'handbag': 1800, 'wallet': 600, 'shoes': 1000, 'default': 1500},
            'armani': {'handbag': 1600, 'wallet': 500, 'shoes': 900, 'default': 1200},
            'rolex': {'watch': 15000, 'default': 12000},
            'omega': {'watch': 5000, 'default': 4000},
            'cartier': {'watch': 8000, 'jewelry': 3000, 'default': 5000},
            
            # PREMIUM TIER - $500-2000
            'apple': {'phone': 1200, 'laptop': 2200, 'tablet': 800, 'watch': 500, 'default': 1000},
            'samsung': {'phone': 900, 'laptop': 1400, 'tablet': 600, 'tv': 1200, 'default': 800},
            'sony': {'camera': 1800, 'headphones': 400, 'tv': 1400, 'console': 700, 'default': 600},
            'canon': {'camera': 1600, 'lens': 800, 'default': 1200},
            'nikon': {'camera': 1500, 'lens': 700, 'default': 1100},
            'bose': {'headphones': 400, 'speaker': 300, 'default': 350},
            'beats': {'headphones': 300, 'speaker': 250, 'default': 275},
            'nike': {'shoes': 200, 'clothing': 100, 'default': 150},
            'adidas': {'shoes': 180, 'clothing': 90, 'default': 130},
            'coach': {'handbag': 800, 'wallet': 300, 'default': 600},
            'michael kors': {'handbag': 400, 'wallet': 150, 'default': 300},
            
            # STANDARD TIER - $100-500
            'zara': {'clothing': 80, 'shoes': 100, 'default': 90},
            'h&m': {'clothing': 50, 'shoes': 60, 'default': 55},
            'uniqlo': {'clothing': 60, 'shoes': 70, 'default': 65},
            'ikea': {'furniture': 200, 'decor': 50, 'default': 125},
            'target': {'clothing': 40, 'home': 60, 'default': 50}
        }
        
        self.item_patterns = {
            'handbag': ['handbag', 'bag', 'purse', 'clutch', 'tote', 'shoulder bag', 'crossbody'],
            'wallet': ['wallet', 'purse', 'cardholder', 'billfold'],
            'shoes': ['shoes', 'sneakers', 'boots', 'sandals', 'heels', 'flats'],
            'watch': ['watch', 'timepiece', 'smartwatch'],
            'phone': ['phone', 'smartphone', 'iphone', 'mobile'],
            'laptop': ['laptop', 'notebook', 'macbook', 'computer'],
            'tablet': ['tablet', 'ipad'],
            'camera': ['camera', 'dslr', 'mirrorless'],
            'headphones': ['headphones', 'earbuds', 'airpods'],
            'clothing': ['dress', 'shirt', 'jacket', 'pants', 'jeans', 'sweater'],
            'jewelry': ['necklace', 'bracelet', 'ring', 'earrings']
        }
        
        self.category_defaults = {
            'fashion_beauty': 120,
            'electronics': 200,
            'vehicles': 25000,
            'home_garden': 150,
            'baby_kids': 80
        }
    
    def detect_brand(self, text):
        """Detect brand from text"""
        text_lower = text.lower()
        
        for brand in self.brand_database.keys():
            if brand in text_lower:
                return brand
        return None
    
    def detect_item_type(self, text):
        """Detect item type from text"""
        text_lower = text.lower()
        
        for item_type, patterns in self.item_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                return item_type
        return 'item'
    
    def get_pricing(self, brand, item_type, category, condition):
        """Get pricing for brand + item combination"""
        condition_multipliers = {
            'excellent': 1.2,
            'very_good': 1.0,
            'good': 0.85,
            'fair': 0.65,
            'poor': 0.45
        }
        
        # Get base price
        if brand and brand in self.brand_database:
            brand_data = self.brand_database[brand]
            base_price = brand_data.get(item_type, brand_data.get('default', 500))
            logger.info(f"💎 BRAND PRICING: {brand} {item_type} → ${base_price}")
        else:
            base_price = self.category_defaults.get(category, 150)
            logger.info(f"📊 CATEGORY PRICING: {category} → ${base_price}")
        
        # Apply condition
        multiplier = condition_multipliers.get(condition, 0.85)
        final_price = base_price * multiplier
        
        logger.info(f"💰 FINAL: ${base_price} × {multiplier} = ${final_price}")
        
        return {
            'pricing_analysis': {
                'quick_sale': round(final_price * 0.85, 0),
                'market_value': round(final_price, 0),
                'premium_price': round(final_price * 1.15, 0),
                'range_min': round(final_price * 0.85, 0),
                'range_max': round(final_price * 1.15, 0),
                'average': round(final_price, 0),
                'confidence': 'high',
                'pricing_source': 'bulletproof_engine'
            },
            'sources': [{'source': 'Bulletproof Engine', 'confidence': 'high'}]
        }

pricing_engine = BulletproofPricingEngine()

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
    try:
        session_id = f"{int(time.time())}-{os.urandom(4).hex()}"
        filename = image_file.filename or 'unknown'
        
        image_file.seek(0)
        image_content = image_file.read()
        image_hash = hashlib.sha256(image_content + session_id.encode()).hexdigest()[:12]
        image_file.seek(0)
        
        logger.info(f"=== ANALYSIS SESSION {session_id} ===")
        logger.info(f"📁 File: {filename}")
        
        # Prepare image
        image = Image.open(image_file)
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Try OpenAI analysis
        client = get_openai_client()
        brand = None
        item_type = None
        category = 'electronics'
        condition = 'good'
        analysis_text = 'Analysis unavailable'
        
        if client:
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Analyze this image and identify: 1) The exact brand name, 2) The type of item, 3) The condition. Return JSON: {\"brand\": \"brand_name\", \"item_type\": \"item_type\", \"category\": \"fashion_beauty/electronics/vehicles/home_garden/baby_kids\", \"condition\": \"excellent/very_good/good/fair/poor\", \"description\": \"detailed description\"}"
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
                                }
                            ]
                        }
                    ],
                    max_tokens=500,
                    temperature=0.1
                )
                
                analysis_text = response.choices[0].message.content
                logger.info(f"🤖 OpenAI Response: {analysis_text}")
                
                # Parse response
                try:
                    # Clean JSON
                    clean_text = re.sub(r'```json\s*', '', analysis_text)
                    clean_text = re.sub(r'```\s*', '', clean_text)
                    
                    data = json.loads(clean_text)
                    brand = data.get('brand', '').lower().strip()
                    item_type = data.get('item_type', '').lower().strip()
                    category = data.get('category', 'electronics')
                    condition = data.get('condition', 'good')
                    
                    logger.info(f"✅ PARSED: Brand={brand}, Item={item_type}, Category={category}")
                    
                except Exception as e:
                    logger.error(f"JSON parsing failed: {e}")
                    # Extract info manually
                    text_lower = analysis_text.lower()
                    
                    # Brand detection
                    for brand_name in pricing_engine.brand_database.keys():
                        if brand_name in text_lower:
                            brand = brand_name
                            break
                    
                    # Item detection
                    item_type = pricing_engine.detect_item_type(analysis_text)
                    
                    logger.info(f"🔧 MANUAL EXTRACTION: Brand={brand}, Item={item_type}")
                
            except Exception as e:
                logger.error(f"OpenAI call failed: {e}")
        
        # Fallback detection
        if not brand:
            brand = pricing_engine.detect_brand(filename + ' ' + analysis_text)
        
        if not item_type:
            item_type = pricing_engine.detect_item_type(filename + ' ' + analysis_text)
        
        # Ensure we have something
        brand = brand or 'unknown'
        item_type = item_type or 'item'
        
        logger.info(f"🎯 FINAL DETECTION: Brand={brand}, Item={item_type}")
        
        # Get pricing
        pricing_data = pricing_engine.get_pricing(brand, item_type, category, condition)
        
        # Build item info
        item_info = {
            'brand': brand,
            'model': 'unknown',
            'category': category,
            'description': item_type,
            'condition': condition,
            'session_id': session_id,
            'image_hash': image_hash
        }
        
        category_info = MARKETPLACE_CATEGORIES.get(category, MARKETPLACE_CATEGORIES['electronics'])
        
        return {
            'category': category,
            'category_info': category_info,
            'analysis': analysis_text,
            'analysis_json': item_info,
            'pricing_data': pricing_data,
            'image_hash': image_hash,
            'session_id': session_id,
            'specific_item': item_type,
            'ai_suggested_category': category,
            'corrected_category': category,
            'ai_estimated_value': f"${pricing_data['pricing_analysis']['market_value']}"
        }
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return None

def generate_category_listing(analysis_data):
    analysis_json = analysis_data.get('analysis_json', {})
    pricing_analysis = analysis_data.get('pricing_data', {}).get('pricing_analysis', {})
    
    brand = analysis_json.get('brand', 'Unknown')
    model = analysis_json.get('model', 'Unknown')
    specific_item = analysis_data.get('specific_item', 'item')
    condition = analysis_json.get('condition', 'good')
    market_value = pricing_analysis.get('market_value', 100)
    
    logger.info(f"📝 LISTING: {brand} {model} {specific_item} - ${market_value}")
    
    return f"I'm selling my {brand} {model} {specific_item} in {condition} condition for ${market_value}. This item has been well-maintained and is ready for a new owner. It's a great opportunity to get a quality {specific_item} at a fair price. Please feel free to contact me if you have any questions or would like to arrange a viewing. Serious buyers only, please. Located in Australia with flexible pickup arrangements available."

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
        
        condition_multipliers = {'excellent': 1.2, 'very_good': 1.0, 'good': 0.85, 'fair': 0.65, 'poor': 0.45, 'damaged': 0.25}
        
        damage_keywords = ['crack', 'broken', 'damage', 'chip', 'scratch', 'dent', 'worn']
        damage_multiplier = 0.7 if any(keyword in additional_notes.lower() for keyword in damage_keywords) else 1.0
        
        original_condition = original_analysis['analysis_json']['condition']
        original_multiplier = condition_multipliers.get(original_condition, 1.0)
        new_multiplier = condition_multipliers.get(condition, 1.0)
        
        base_price = original_price / original_multiplier
        adjusted_price = base_price * new_multiplier * damage_multiplier
        
        new_market_value = round(adjusted_price, 0)
        
        updated_analysis = original_analysis.copy()
        updated_analysis['analysis_json']['condition'] = condition
        updated_analysis['pricing_data']['pricing_analysis']['market_value'] = new_market_value
        updated_analysis['pricing_data']['pricing_analysis']['quick_sale'] = round(adjusted_price * 0.85, 0)
        updated_analysis['pricing_data']['pricing_analysis']['premium_price'] = round(adjusted_price * 1.15, 0)
        
        session['current_analysis'] = updated_analysis
        updated_listing = generate_category_listing(updated_analysis)
        
        logger.info(f"💰 ADJUSTED: ${original_price} → ${new_market_value}")
        
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
