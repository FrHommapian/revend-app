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
import tempfile
from pricing_engine import RealPricingEngine

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = f'revend-secret-key-{int(time.time())}'

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY not found in environment")
        return None
    try:
        return OpenAI(api_key=api_key)
    except Exception as e:
        logger.error(f"Error creating OpenAI client: {e}")
        return None

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
    
    if any(brand_lower == electronics_brand or electronics_brand in brand_lower for electronics_brand in electronics_brands):
        logger.info(f"📱 ELECTRONICS BRAND: {brand} → electronics")
        return 'electronics'
    
    if any(brand_lower == fashion_brand or fashion_brand in brand_lower for fashion_brand in fashion_brands):
        logger.info(f"👗 FASHION BRAND: {brand} → fashion_beauty")
        return 'fashion_beauty'
    
    if any(keyword in all_text for keyword in ['phone', 'laptop', 'computer', 'tablet', 'camera', 'headphones', 'speaker', 'console']):
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
        if not client:
            logger.error("Failed to get OpenAI client")
            return None
        
        try:
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
            logger.error(f"OpenAI API error: {e}")
            return None
            
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
        
        logger.info(f"📝 GENERATING LISTING FOR:")
        logger.info(f"   Item: {specific_item}")
        logger.info(f"   Brand: {brand}")
        logger.info(f"   Model: {model}")
        logger.info(f"   Category: {category}")
        logger.info(f"   Price: ${market_value}")
        
        client = get_openai_client()
        if not client:
            logger.error("Failed to get OpenAI client for listing generation")
            return f"I'm selling my {brand} {model} {specific_item} in {condition} condition for ${market_value}. Please contact me for more details."
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": f"""Create an Australian marketplace listing for this SPECIFIC item:

ITEM DETAILS:
- Item: {specific_item}
- Brand: {brand}
- Model: {model}
- Condition: {condition}
- Category: {category}
- Price: ${market_value}

CRITICAL REQUIREMENTS:
1. Write about the EXACT item: {brand} {model} {specific_item}
2. Price: Ask for ${market_value}
3. Write as an Australian seller
4. Personal story about owning this {specific_item}
5. Why selling this {specific_item}
6. Care and usage details
7. 150-250 words
8. No emojis
9. Sound authentic and trustworthy

MAKE SURE THE LISTING IS ABOUT THE {specific_item}, NOT ANYTHING ELSE!"""
                    }
                ],
                max_tokens=400,
                temperature=0.3
            )
            
            generated_listing = response.choices[0].message.content
            
            logger.info(f"✅ Generated listing for {specific_item}")
            return generated_listing
            
        except Exception as e:
            logger.error(f"Error generating listing: {e}")
            return f"I'm selling my {brand} {model} {specific_item} in {condition} condition for ${market_value}. Please contact me for more details."
        
    except Exception as e:
        logger.error(f"Error generating listing: {e}")
        return f"I'm selling my item in good condition. Please contact me for more details."

@app.route('/')
def index():
    session.clear()
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'photo' not in request.files or request.files['photo'].filename == '':
            flash('No photo uploaded')
            return redirect(url_for('index'))
        
        photo = request.files['photo']
        
        # Process the image immediately
        analysis_data = analyze_item_photo(photo)
        
        if not analysis_data:
            flash('Error analyzing photo - please try again')
            return redirect(url_for('index'))
        
        # Store only essential data in session (not the image)
        session['current_analysis'] = {
            'analysis_json': analysis_data['analysis_json'],
            'pricing_data': analysis_data['pricing_data'],
            'specific_item': analysis_data['specific_item']
        }
        
        listing = generate_category_listing(analysis_data)
        
        return render_template('results.html', analysis_data=analysis_data, listing=listing)
        
    except Exception as e:
        logger.error(f"Error in analyze route: {e}")
        flash('Error processing request - please try again')
        return redirect(url_for('index'))

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
