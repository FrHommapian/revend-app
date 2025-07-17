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

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = f'revend-secret-key-{int(time.time())}'

def get_openai_client():
    """Ultimate OpenAI client with old version fallback"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.error("❌ OPENAI_API_KEY not found")
            return None
        
        logger.info(f"🔑 API Key found: {api_key[:12]}...")
        
        # Try new version first
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            logger.info("✅ OpenAI v1+ client working!")
            return client
        except:
            pass
        
        # Try old version
        try:
            import openai
            openai.api_key = api_key
            logger.info("✅ OpenAI v0.28 client working!")
            return openai
        except:
            pass
        
        logger.error("❌ All OpenAI versions failed")
        return None
        
    except Exception as e:
        logger.error(f"❌ OpenAI client error: {e}")
        return None

def detect_brand_from_filename(filename):
    """Detect brand from filename"""
    filename_lower = filename.lower()
    
    luxury_brands = {
        'prada': 2500,
        'gucci': 2000,
        'chanel': 3000,
        'louis': 2800,  # Louis Vuitton
        'hermes': 8000,
        'dior': 2200,
        'versace': 1800,
        'rolex': 12000,
        'omega': 4000
    }
    
    for brand, price in luxury_brands.items():
        if brand in filename_lower:
            logger.info(f"🎯 BRAND DETECTED FROM FILENAME: {brand} → ${price}")
            return brand, price
    
    return None, None

def detect_item_type(filename):
    """Detect item type from filename"""
    filename_lower = filename.lower()
    
    if any(word in filename_lower for word in ['bag', 'handbag', 'purse', 'clutch', 'tote']):
        return 'handbag', 'fashion_beauty'
    elif any(word in filename_lower for word in ['watch', 'rolex', 'omega']):
        return 'watch', 'fashion_beauty'
    elif any(word in filename_lower for word in ['phone', 'iphone', 'samsung']):
        return 'smartphone', 'electronics'
    elif any(word in filename_lower for word in ['laptop', 'macbook', 'computer']):
        return 'laptop', 'electronics'
    else:
        return 'item', 'electronics'

# Ultimate pricing engine with manual brand detection
class UltimatePricingEngine:
    def __init__(self):
        self.luxury_brands = {
            'prada': {'handbag': 2500, 'wallet': 800, 'shoes': 1200},
            'gucci': {'handbag': 2000, 'wallet': 600, 'shoes': 1000},
            'chanel': {'handbag': 3000, 'wallet': 1200, 'shoes': 1500},
            'louis vuitton': {'handbag': 2800, 'wallet': 900, 'shoes': 1300},
            'hermes': {'handbag': 8000, 'wallet': 2000, 'shoes': 3000},
            'dior': {'handbag': 2200, 'wallet': 700, 'shoes': 1100},
            'versace': {'handbag': 1800, 'wallet': 600, 'shoes': 900},
            'rolex': {'watch': 12000},
            'omega': {'watch': 4000}
        }
        
        self.premium_brands = {
            'apple': {'phone': 1200, 'laptop': 2000, 'tablet': 800},
            'samsung': {'phone': 900, 'laptop': 1200, 'tablet': 600},
            'sony': {'camera': 1500, 'headphones': 300, 'tv': 1200},
            'nike': {'shoes': 180, 'clothing': 80},
            'adidas': {'shoes': 160, 'clothing': 70}
        }
        
        self.category_bases = {
            'electronics': 200,
            'fashion_beauty': 150,
            'vehicles': 25000,
            'home_garden': 180,
            'baby_kids': 80
        }
    
    def analyze_comprehensive_pricing(self, item_info, filename=None):
        brand = item_info.get('brand', 'unknown').lower()
        category = item_info.get('category', 'electronics')
        condition = item_info.get('condition', 'good')
        description = item_info.get('description', 'item').lower()
        
        # Manual brand detection from filename
        if filename:
            detected_brand, detected_price = detect_brand_from_filename(filename)
            if detected_brand:
                brand = detected_brand
                item_info['brand'] = detected_brand
        
        # Determine item type
        item_type = 'item'
        if 'handbag' in description or 'bag' in description:
            item_type = 'handbag'
        elif 'watch' in description:
            item_type = 'watch'
        elif 'phone' in description:
            item_type = 'phone'
        elif 'laptop' in description:
            item_type = 'laptop'
        elif 'shoes' in description:
            item_type = 'shoes'
        
        # Check luxury brands first
        if brand in self.luxury_brands:
            brand_data = self.luxury_brands[brand]
            base_price = brand_data.get(item_type, brand_data.get('handbag', 2000))
            logger.info(f"💎 LUXURY BRAND: {brand} {item_type} → ${base_price}")
        elif brand in self.premium_brands:
            brand_data = self.premium_brands[brand]
            base_price = brand_data.get(item_type, brand_data.get('phone', 500))
            logger.info(f"⭐ PREMIUM BRAND: {brand} {item_type} → ${base_price}")
        else:
            base_price = self.category_bases.get(category, 150)
            logger.info(f"📊 CATEGORY BASE: {category} → ${base_price}")
        
        # Condition adjustments
        condition_multipliers = {
            'excellent': 1.2,
            'very_good': 1.0,
            'good': 0.85,
            'fair': 0.65,
            'poor': 0.45
        }
        
        multiplier = condition_multipliers.get(condition, 0.85)
        final_price = base_price * multiplier
        
        logger.info(f"💰 FINAL PRICING: ${base_price} × {multiplier} = ${final_price}")
        
        return {
            'pricing_analysis': {
                'quick_sale': round(final_price * 0.85, 0),
                'market_value': round(final_price, 0),
                'premium_price': round(final_price * 1.15, 0),
                'range_min': round(final_price * 0.85, 0),
                'range_max': round(final_price * 1.15, 0),
                'average': round(final_price, 0),
                'confidence': 'high',
                'pricing_source': 'ultimate_engine'
            },
            'sources': [{'source': 'Ultimate Pricing Engine', 'confidence': 'high'}]
        }

pricing_engine = UltimatePricingEngine()

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
        
        logger.info(f"=== NEW ANALYSIS SESSION {session_id} ===")
        logger.info(f"📁 Filename: {filename}")
        
        # Detect brand and item type from filename
        detected_brand, detected_price = detect_brand_from_filename(filename)
        item_type, category = detect_item_type(filename)
        
        image = Image.open(image_file)
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        client = get_openai_client()
        
        # Try OpenAI analysis
        if client:
            try:
                # Handle both old and new OpenAI versions
                if hasattr(client, 'chat'):
                    # New version
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": f"Analyze this image. What brand and item is this? Return JSON: {{\"brand\": \"brand name\", \"item\": \"item type\", \"category\": \"fashion_beauty/electronics/vehicles/home_garden/baby_kids\", \"condition\": \"excellent/very_good/good/fair/poor\", \"estimated_value\": \"XXX AUD\"}}"
                                    },
                                    {
                                        "type": "image_url", 
                                        "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
                                    }
                                ]
                            }
                        ],
                        max_tokens=300,
                        temperature=0.1
                    )
                    
                    analysis_text = response.choices[0].message.content
                    
                else:
                    # Old version
                    response = client.ChatCompletion.create(
                        model="gpt-4-vision-preview",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": f"Analyze this image. What brand and item is this? Return JSON: {{\"brand\": \"brand name\", \"item\": \"item type\", \"category\": \"fashion_beauty/electronics/vehicles/home_garden/baby_kids\", \"condition\": \"excellent/very_good/good/fair/poor\", \"estimated_value\": \"XXX AUD\"}}"
                                    },
                                    {
                                        "type": "image_url", 
                                        "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
                                    }
                                ]
                            }
                        ],
                        max_tokens=300,
                        temperature=0.1
                    )
                    
                    analysis_text = response.choices[0].message.content
                
                # Parse AI response
                try:
                    analysis_json = json.loads(analysis_text)
                    brand = analysis_json.get('brand', detected_brand or 'unknown')
                    specific_item = analysis_json.get('item', item_type)
                    ai_category = analysis_json.get('category', category)
                    condition = analysis_json.get('condition', 'good')
                    ai_estimated_value = analysis_json.get('estimated_value', 'unknown')
                    
                    logger.info(f"🎯 AI SUCCESS: {brand} {specific_item} → {ai_estimated_value}")
                    
                except Exception as e:
                    logger.error(f"AI parsing error: {e}")
                    brand = detected_brand or 'unknown'
                    specific_item = item_type
                    ai_category = category
                    condition = 'good'
                    ai_estimated_value = 'unknown'
                    analysis_text = f"AI analysis failed: {e}"
                
            except Exception as e:
                logger.error(f"❌ OpenAI API call failed: {e}")
                client = None
        
        # Fallback to manual detection
        if not client:
            logger.info("🔧 Using manual detection")
            brand = detected_brand or 'unknown'
            specific_item = item_type
            ai_category = category
            condition = 'good'
            ai_estimated_value = 'unknown'
            analysis_text = f"Manual detection: {brand} {specific_item}"
        
        # Create item info
        item_info = {
            'brand': brand,
            'model': 'unknown',
            'category': ai_category,
            'description': specific_item,
            'condition': condition,
            'session_id': session_id,
            'image_hash': image_hash
        }
        
        # Get pricing
        pricing_data = pricing_engine.analyze_comprehensive_pricing(item_info, filename)
        
        # Check if AI gave us a price
        if ai_estimated_value and ai_estimated_value != 'unknown':
            try:
                ai_price = float(re.findall(r'(\d+)', ai_estimated_value)[0])
                if ai_price > 0:
                    pricing_data['pricing_analysis']['market_value'] = ai_price
                    pricing_data['pricing_analysis']['quick_sale'] = round(ai_price * 0.85, 0)
                    pricing_data['pricing_analysis']['premium_price'] = round(ai_price * 1.15, 0)
                    logger.info(f"🎯 USING AI PRICE: ${ai_price}")
            except:
                pass
        
        category_info = MARKETPLACE_CATEGORIES.get(ai_category, MARKETPLACE_CATEGORIES['electronics'])
        
        return {
            'category': ai_category,
            'category_info': category_info,
            'analysis': analysis_text,
            'analysis_json': item_info,
            'pricing_data': pricing_data,
            'image_hash': image_hash,
            'session_id': session_id,
            'specific_item': specific_item,
            'ai_suggested_category': ai_category,
            'corrected_category': ai_category,
            'ai_estimated_value': ai_estimated_value
        }
        
    except Exception as e:
        logger.error(f"Error analyzing photo: {e}")
        return None

def generate_category_listing(analysis_data):
    analysis_json = analysis_data.get('analysis_json', {})
    pricing_analysis = analysis_data.get('pricing_data', {}).get('pricing_analysis', {})
    
    brand = analysis_json.get('brand', 'Unknown')
    model = analysis_json.get('model', 'Unknown')
    specific_item = analysis_data.get('specific_item', 'item')
    condition = analysis_json.get('condition', 'good')
    market_value = pricing_analysis.get('market_value', 100)
    
    logger.info(f"📝 GENERATING LISTING FOR: {brand} {model} {specific_item} - ${market_value}")
    
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
        logger.error(f"Error: {e}")
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
        
        logger.info(f"💰 PRICE ADJUSTED: ${original_price} → ${new_market_value}")
        
        return render_template('results.html', analysis_data=updated_analysis, listing=updated_listing, updated=True)
        
    except Exception as e:
        logger.error(f"Error in refine-analysis: {e}")
        return redirect(url_for('index'))

@app.route('/categories')
def categories():
    return jsonify(MARKETPLACE_CATEGORIES)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
