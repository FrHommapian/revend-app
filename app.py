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
from pricing_engine import RealPricingEngine

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = f'revend-secret-key-{int(time.time())}'

def get_openai_client():
    return OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

pricing_engine = RealPricingEngine()

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

def bulletproof_category_detection(ai_category, specific_item, brand, model, analysis_notes):
    all_text = f"{specific_item} {brand} {model} {analysis_notes}".lower()
    brand_lower = brand.lower().strip()
    
    logger.info(f"🔍 BULLETPROOF CATEGORIZATION")
    logger.info(f"   Brand: '{brand}' | Item: '{specific_item}'")
    
    electronics_brands = [
        'apple', 'samsung', 'google', 'huawei', 'xiaomi', 'dell', 'hp', 'lenovo', 'asus', 'sony', 'bose', 'beats', 'canon', 'nikon', 'nintendo', 'playstation', 'xbox'
    ]
    
    fashion_brands = [
        'chanel', 'dior', 'gucci', 'prada', 'louis vuitton', 'hermes', 'versace', 'armani', 'tom ford', 'le labo', 'creed', 'coach', 'kate spade', 'michael kors', 'zara', 'h&m', 'nike', 'adidas', 'rolex', 'omega'
    ]
    
    vehicle_brands = [
        'ford', 'toyota', 'honda', 'bmw', 'mercedes', 'audi', 'volkswagen', 'nissan', 'mazda', 'tesla', 'holden'
    ]
    
    home_brands = [
        'ikea', 'dyson', 'shark vacuum', 'kitchenaid', 'cuisinart', 'dewalt', 'makita', 'weber'
    ]
    
    baby_brands = [
        'fisher-price', 'little tikes', 'lego', 'graco', 'chicco', 'britax', 'uppababy'
    ]
    
    if any(brand_lower == electronics_brand or electronics_brand in brand_lower for electronics_brand in electronics_brands):
        logger.info(f"📱 ELECTRONICS BRAND: {brand} → electronics")
        return 'electronics'
    
    if any(brand_lower == fashion_brand or fashion_brand in brand_lower for fashion_brand in fashion_brands):
        logger.info(f"👗 FASHION BRAND: {brand} → fashion_beauty")
        return 'fashion_beauty'
    
    if any(brand_lower == vehicle_brand or vehicle_brand in brand_lower for vehicle_brand in vehicle_brands):
        vehicle_context = any(keyword in all_text for keyword in ['car', 'truck', 'van', 'vehicle', 'motor'])
        if vehicle_context:
            logger.info(f"🚗 VEHICLE BRAND: {brand} → vehicles")
            return 'vehicles'
    
    if any(brand_lower == home_brand or home_brand in brand_lower for home_brand in home_brands):
        logger.info(f"🏠 HOME BRAND: {brand} → home_garden")
        return 'home_garden'
    
    if any(brand_lower == baby_brand or baby_brand in brand_lower for baby_brand in baby_brands):
        logger.info(f"👶 BABY BRAND: {brand} → baby_kids")
        return 'baby_kids'
    
    if any(keyword in all_text for keyword in ['phone', 'laptop', 'computer', 'tablet', 'camera', 'headphones', 'speaker', 'console', 'hard drive', 'ssd']):
        logger.info(f"📱 ELECTRONICS ITEM: {specific_item} → electronics")
        return 'electronics'
    
    if any(keyword in all_text for keyword in ['dress', 'bag', 'handbag', 'shoes', 'jewelry', 'watch', 'perfume', 'cologne', 'fragrance']):
        logger.info(f"👗 FASHION ITEM: {specific_item} → fashion_beauty")
        return 'fashion_beauty'
    
    logger.info(f"✅ USING AI SUGGESTION: {ai_category}")
    return ai_category

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
        logger.warning(f"⚠️ USING FALLBACK PRICING")
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
        timestamp = datetime.now().isoformat()
        
        category_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""Analyze this image. Focus on the main item.

Categories: electronics, vehicles, fashion_beauty, home_garden, baby_kids

Return JSON: {{"primary_category": "category", "specific_item": "item", "confidence": 10}}"""
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
        
        # THIS IS THE LINE THAT WAS BROKEN - I'm fixing the parenthesis issue here
        try:
            category_data = json.loads(category_text)
            ai_suggested_category = category_data.get('primary_category', 'electronics')
            specific_item = category_data.get('specific_item', 'item')
        except:
            ai_suggested_category = 'electronics'
            specific_item = 'item'
        
        analysis_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""Analyze this {specific_item} for Australian pricing.

Return JSON: {{"brand": "exact brand", "model": "exact model", "condition": "excellent/very_good/good/fair/poor", "estimated_value": "XXX AUD", "analysis_notes": "description"}}"""
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
            brand = analysis_json.get('brand', 'Unknown')
            model = analysis_json.get('model', 'Unknown')
            analysis_notes = analysis_json.get('analysis_notes', '')
            ai_estimated_value = analysis_json.get('estimated_value', 'Unknown')
            
            corrected_category = bulletproof_category_detection(
                ai_suggested_category, specific_item, brand, model, analysis_notes
            )
            
            logger.info(f"🎯 FINAL: {ai_suggested_category} → {corrected_category}")
            
            item_info = {
                'brand': brand,
                'model': model,
                'category': corrected_category,
                'description': specific_item,
                'condition': analysis_json.get('condition', 'good'),
                'session_id': session_id,
                'image_hash': image_hash
            }
            
        except Exception as e:
            logger.error(f"Parse error: {e}")
            item_info = {
                'brand': 'Unknown', 'model': 'Unknown', 'category': 'fashion_beauty',
                'description': specific_item, 'condition': 'good', 'session_id': session_id, 'image_hash': image_hash
            }
            ai_estimated_value = 'Unknown'
        
        fallback_pricing_data = pricing_engine.analyze_comprehensive_pricing(item_info)
        final_pricing_data = create_ai_priority_pricing(ai_estimated_value, brand, model, item_info['condition'], fallback_pricing_data)
        
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
    try:
        analysis_json = analysis_data.get('analysis_json', {})
        pricing_analysis = analysis_data.get('pricing_data', {}).get('pricing_analysis', {})
        
        brand = analysis_json.get('brand', 'Unknown')
        model = analysis_json.get('model', 'Unknown')
        specific_item = analysis_data.get('specific_item', 'item')
        condition = analysis_json.get('condition', 'good')
        category = analysis_json.get('category', 'electronics')
        market_value = pricing_analysis.get('market_value', 100)
        
        analysis_text = analysis_data.get('analysis', '')
        
        logger.info(f"📝 GENERATING MULTI-PLATFORM LISTINGS FOR: {specific_item}")
        
        client = get_openai_client()
        
        platforms = {
            'general': {
                'name': 'General',
                'prompt': f"""Create an Australian marketplace listing for this {brand} {model} {specific_item} in {condition} condition for . Write 150-250 words as an Australian seller with personal story. No emojis."""
            },
            'ebay': {
                'name': 'eBay',
                'prompt': f"""Create professional eBay listing for {brand} {model} {specific_item} - {condition} condition. Include specifications, shipping info. 180-220 words. End with 'Buy with confidence!'"""
            },
            'facebook': {
                'name': 'Facebook Marketplace',
                'prompt': f"""Create casual Facebook Marketplace listing for {brand} {model} {specific_item}. Local pickup focus, personal touch. 120-160 words. Start with 'Selling my...' End with 'Message me if interested!'"""
            },
            'gumtree': {
                'name': 'Gumtree',
                'prompt': f"""Create straightforward Gumtree listing for {brand} {model} {specific_item} for sale. Price . Pickup/delivery options. 140-180 words. End with 'Serious buyers only'."""
            },
            'mercari': {
                'name': 'Mercari',
                'prompt': f"""Create mobile-friendly Mercari listing for {brand} {model} {specific_item}. Condition: {condition}. Quick sale focus. 100-140 words. End with 'Fast shipping!'"""
            }
        }
        
        listings = {}
        
        for platform_key, platform_info in platforms.items():
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": platform_info['prompt']}],
                    max_tokens=400,
                    temperature=0.3
                )
                
                generated_listing = response.choices[0].message.content
                listings[platform_key] = {
                    'name': platform_info['name'],
                    'content': generated_listing
                }
                
                logger.info(f"✅ Generated {platform_info['name']} listing")
                
            except Exception as e:
                logger.error(f"Error generating {platform_info['name']} listing: {e}")
                listings[platform_key] = {
                    'name': platform_info['name'],
                    'content': f"I'm selling my {brand} {model} {specific_item} in {condition} condition for . Please contact me for more details."
                }
        
        return listings.get('general', {}).get('content', f"I'm selling my {brand} {model} {specific_item} in {condition} condition for ${market_value}. Please contact me for more details.")
        
    except Exception as e:
        logger.error(f"Error generating listings: {e}")
        return {
            'general': {
                'name': 'General',
                'content': f"I'm selling my {brand} {model} {specific_item} in {condition} condition for . Please contact me for more details."
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating listing: {e}")
        return f"I'm selling my {brand} {model} {specific_item} in {condition} condition for ${market_value}. Please contact me for more details."

# ALL YOUR ROUTES ARE PRESERVED EXACTLY AS THEY WERE
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
