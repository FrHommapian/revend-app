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
from pricing_engine import RealPricingEngine

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = f'revend-secret-key-{int(time.time())}'

def get_openai_client():
    """Nuclear OpenAI client fix - handles all versions"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.error("❌ OPENAI_API_KEY not found")
            return None
        
        logger.info(f"🔑 API Key found: {api_key[:12]}...")
        
        # Import OpenAI inside function to avoid import issues
        try:
            from openai import OpenAI
            
            # Try different initialization methods
            initialization_methods = [
                lambda: OpenAI(api_key=api_key),
                lambda: OpenAI(api_key=api_key, base_url="https://api.openai.com/v1"),
                lambda: OpenAI(api_key=api_key, timeout=30),
            ]
            
            for method in initialization_methods:
                try:
                    client = method()
                    logger.info("✅ OpenAI client initialized successfully!")
                    return client
                except Exception as e:
                    logger.warning(f"Initialization method failed: {e}")
                    continue
            
            logger.error("❌ All OpenAI initialization methods failed")
            return None
            
        except ImportError:
            logger.error("❌ OpenAI library not available")
            return None
        
    except Exception as e:
        logger.error(f"❌ OpenAI client error: {e}")
        return None

# Enhanced pricing engine with better fallback
class EnhancedPricingEngine:
    def __init__(self):
        self.luxury_brands = {
            'prada': {'base': 2500, 'multiplier': 1.8},
            'gucci': {'base': 2000, 'multiplier': 1.6},
            'chanel': {'base': 3000, 'multiplier': 2.0},
            'louis vuitton': {'base': 2800, 'multiplier': 1.9},
            'hermes': {'base': 8000, 'multiplier': 3.0},
            'rolex': {'base': 12000, 'multiplier': 4.0},
            'omega': {'base': 4000, 'multiplier': 2.5}
        }
        
        self.premium_brands = {
            'apple': {'base': 800, 'multiplier': 1.4},
            'samsung': {'base': 600, 'multiplier': 1.2},
            'sony': {'base': 400, 'multiplier': 1.1},
            'nike': {'base': 150, 'multiplier': 1.2},
            'adidas': {'base': 130, 'multiplier': 1.1}
        }
        
        self.category_bases = {
            'electronics': 200,
            'fashion_beauty': 120,
            'vehicles': 25000,
            'home_garden': 180,
            'baby_kids': 80
        }
    
    def analyze_comprehensive_pricing(self, item_info):
        brand = item_info.get('brand', 'unknown').lower()
        category = item_info.get('category', 'electronics')
        condition = item_info.get('condition', 'good')
        
        # Check luxury brands first
        if brand in self.luxury_brands:
            base_price = self.luxury_brands[brand]['base']
            logger.info(f"💎 LUXURY BRAND DETECTED: {brand} → ${base_price}")
        elif brand in self.premium_brands:
            base_price = self.premium_brands[brand]['base']
            logger.info(f"⭐ PREMIUM BRAND DETECTED: {brand} → ${base_price}")
        else:
            base_price = self.category_bases.get(category, 100)
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
        
        logger.info(f"💰 ENHANCED PRICING: ${base_price} × {multiplier} = ${final_price}")
        
        return {
            'pricing_analysis': {
                'quick_sale': round(final_price * 0.85, 0),
                'market_value': round(final_price, 0),
                'premium_price': round(final_price * 1.15, 0),
                'range_min': round(final_price * 0.85, 0),
                'range_max': round(final_price * 1.15, 0),
                'average': round(final_price, 0),
                'confidence': 'high',
                'pricing_source': 'enhanced_engine'
            },
            'sources': [{'source': 'Enhanced Pricing Engine', 'confidence': 'high'}]
        }

pricing_engine = EnhancedPricingEngine()

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

def detect_brand_from_image_data(image_data):
    """Detect brand from image data without OpenAI"""
    # Simple brand detection based on filename or basic analysis
    luxury_brands = ['prada', 'gucci', 'chanel', 'louis vuitton', 'hermes', 'rolex', 'omega']
    premium_brands = ['apple', 'samsung', 'sony', 'nike', 'adidas']
    
    # This is a placeholder - in real implementation you'd use computer vision
    # For now, return unknown but the enhanced pricing engine will handle it
    return 'unknown'

def bulletproof_category_detection(specific_item, brand, analysis_notes):
    all_text = f"{specific_item} {brand} {analysis_notes}".lower()
    
    if any(keyword in all_text for keyword in ['phone', 'laptop', 'computer', 'tablet', 'camera', 'headphones', 'speaker', 'console']):
        return 'electronics'
    
    if any(keyword in all_text for keyword in ['dress', 'bag', 'handbag', 'shoes', 'jewelry', 'watch', 'perfume', 'cologne', 'fragrance']):
        return 'fashion_beauty'
    
    if any(keyword in all_text for keyword in ['car', 'truck', 'van', 'vehicle', 'motorcycle', 'bike', 'boat']):
        return 'vehicles'
    
    if any(keyword in all_text for keyword in ['furniture', 'sofa', 'table', 'chair', 'appliance', 'tool']):
        return 'home_garden'
    
    if any(keyword in all_text for keyword in ['toy', 'baby', 'kids', 'children', 'stroller', 'crib']):
        return 'baby_kids'
    
    return 'electronics'

def extract_price_from_ai_estimate(estimated_value):
    try:
        if not estimated_value:
            return None
        
        patterns = [
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:AUD|USD|\$)',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, estimated_value, re.IGNORECASE)
            for match in matches:
                try:
                    price = float(match.replace(',', ''))
                    if 10 <= price <= 500000:
                        return price
                except:
                    continue
        return None
    except:
        return None

def create_ai_priority_pricing(ai_estimated_value, brand, model, condition, fallback_pricing):
    ai_price = extract_price_from_ai_estimate(ai_estimated_value)
    
    if ai_price and ai_price > 0:
        logger.info(f"🎯 USING AI ESTIMATE: ${ai_price}")
        
        return {
            'pricing_analysis': {
                'quick_sale': round(ai_price * 0.85, 0),
                'market_value': ai_price,
                'premium_price': round(ai_price * 1.15, 0),
                'range_min': round(ai_price * 0.85, 0),
                'range_max': round(ai_price * 1.15, 0),
                'average': ai_price,
                'confidence': 'high',
                'pricing_source': 'ai_visual_estimate'
            },
            'sources': [{'source': f'AI Analysis ({brand} {model})', 'confidence': 'high'}],
            'ai_estimate_used': True
        }
    else:
        logger.warning(f"⚠️ USING ENHANCED FALLBACK PRICING")
        return fallback_pricing

def clean_json_response(response_text):
    cleaned = re.sub(r'```json\s*', '', response_text)
    cleaned = re.sub(r'```\s*', '', cleaned)
    return cleaned.strip()

def analyze_item_photo(image_file):
    try:
        session_id = f"{int(time.time())}-{os.urandom(4).hex()}"
        
        image_file.seek(0)
        image_content = image_file.read()
        image_hash = hashlib.sha256(image_content + session_id.encode()).hexdigest()[:12]
        image_file.seek(0)
        
        logger.info(f"=== NEW ANALYSIS SESSION {session_id} ===")
        
        image = Image.open(image_file)
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        client = get_openai_client()
        
        if client:
            try:
                # Category analysis
                category_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Analyze this image. What is the main item? Return JSON: {\"primary_category\": \"electronics/fashion_beauty/vehicles/home_garden/baby_kids\", \"specific_item\": \"item name\", \"brand\": \"brand name\"}"
                                },
                                {
                                    "type": "image_url", 
                                    "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
                                }
                            ]
                        }
                    ],
                    max_tokens=200,
                    temperature=0.1
                )
                
                category_text = clean_json_response(category_response.choices[0].message.content)
                
                try:
                    category_data = json.loads(category_text)
                    ai_suggested_category = category_data.get('primary_category', 'electronics')
                    specific_item = category_data.get('specific_item', 'item')
                    brand = category_data.get('brand', 'unknown')
                except:
                    ai_suggested_category = 'electronics'
                    specific_item = 'item'
                    brand = 'unknown'
                
                # Detailed analysis
                analysis_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Analyze this {specific_item} for Australian pricing. Return JSON: {{\"brand\": \"exact brand\", \"model\": \"exact model\", \"condition\": \"excellent/very_good/good/fair/poor\", \"estimated_value\": \"XXX AUD\", \"analysis_notes\": \"description\"}}"
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
                
                analysis_text = clean_json_response(analysis_response.choices[0].message.content)
                
                try:
                    analysis_json = json.loads(analysis_text)
                    brand = analysis_json.get('brand', brand)
                    model = analysis_json.get('model', 'unknown')
                    condition = analysis_json.get('condition', 'good')
                    ai_estimated_value = analysis_json.get('estimated_value', 'unknown')
                    analysis_notes = analysis_json.get('analysis_notes', '')
                except:
                    model = 'unknown'
                    condition = 'good'
                    ai_estimated_value = 'unknown'
                    analysis_notes = ''
                
                logger.info(f"🎯 AI ANALYSIS SUCCESS: {brand} {model} {specific_item}")
                
            except Exception as e:
                logger.error(f"❌ OpenAI API call failed: {e}")
                client = None
                
        if not client:
            logger.error("❌ OpenAI client unavailable - using enhanced fallback")
            
            # Enhanced fallback analysis
            brand = detect_brand_from_image_data(image_content)
            specific_item = 'item'
            ai_suggested_category = 'electronics'
            model = 'unknown'
            condition = 'good'
            ai_estimated_value = 'unknown'
            analysis_notes = 'OpenAI unavailable - using enhanced fallback'
            analysis_text = analysis_notes
        
        corrected_category = bulletproof_category_detection(specific_item, brand, analysis_notes)
        
        item_info = {
            'brand': brand,
            'model': model,
            'category': corrected_category,
            'description': specific_item,
            'condition': condition,
            'session_id': session_id,
            'image_hash': image_hash
        }
        
        fallback_pricing_data = pricing_engine.analyze_comprehensive_pricing(item_info)
        final_pricing_data = create_ai_priority_pricing(ai_estimated_value, brand, model, condition, fallback_pricing_data)
        
        category_info = MARKETPLACE_CATEGORIES.get(corrected_category, MARKETPLACE_CATEGORIES['electronics'])
        
        return {
            'category': corrected_category,
            'category_info': category_info,
            'analysis': analysis_text,
            'analysis_json': item_info,
            'pricing_data': final_pricing_data,
            'image_hash': image_hash,
            'session_id': session_id,
            'specific_item': specific_item,
            'ai_suggested_category': ai_suggested_category,
            'corrected_category': corrected_category,
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
