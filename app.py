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
import random

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
2. Specific item type and model/year
3. Condition assessment (excellent/very_good/good/fair/poor)
4. Market category (fashion_beauty/electronics/vehicles/home_garden/baby_kids)
5. REALISTIC Australian market value estimate in AUD based on current market conditions
6. Key factors affecting price (age, condition, rarity, demand)

Be very accurate with pricing - consider actual depreciation, current market demand, and realistic second-hand values.

For vehicles: Consider age, mileage, condition, and actual Australian used car market prices.
For luxury items: Consider authenticity, condition, and current resale market.
For electronics: Consider age, condition, and rapid depreciation.

Return JSON: {
    "brand": "exact brand name or unknown",
    "model": "specific model/variant/year",
    "item_type": "specific item description",
    "category": "market category",
    "condition": "condition assessment",
    "estimated_value_aud": "realistic price in AUD",
    "confidence_level": "high/medium/low",
    "price_factors": ["factor1", "factor2", "factor3"],
    "market_notes": "brief analysis of why this price is realistic"
}""",
            
            "pricing": """You are a pricing expert for Australian second-hand markets. 

Analyze this item and provide REALISTIC pricing based on:
- Current Australian market conditions
- Actual depreciation from retail prices
- Condition impact on value
- Brand positioning and demand
- Age and usage factors
- Competition in the market

Be conservative but fair. Consider what people actually pay, not wishful thinking.

Return JSON: {
    "quick_sale_price": "conservative price for fast sale in AUD",
    "market_value": "realistic market value in AUD",
    "premium_price": "optimistic but achievable price in AUD",
    "pricing_confidence": "high/medium/low",
    "market_analysis": "brief explanation of pricing rationale"
}""",
            
            "listing": """You are helping someone create a genuine, personal marketplace listing. 

Create a heartfelt, personal story about selling this item. Include:
- Why you originally bought it
- Personal memories or experiences with it
- Why you're reluctantly selling it now
- What you'll miss about it
- Care and maintenance details
- Why it deserves a good home

Write as a real person, not a business. Make it emotional and genuine - like someone who truly cared about this item.

Return JSON: {
    "personal_story": "the emotional backstory",
    "reason_for_selling": "why parting with it",
    "care_details": "how it was maintained",
    "ideal_buyer": "who would appreciate it"
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
            'temperature': 0.2
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

def extract_price_from_ai_estimate(estimated_value):
    """Extract numerical price from AI estimate"""
    try:
        if not estimated_value:
            return None
        
        # Remove currency symbols and common words
        clean_value = re.sub(r'[^\d,.]', '', str(estimated_value))
        
        # Extract number
        numbers = re.findall(r'(\d+(?:,\d{3})*(?:\.\d{2})?)', clean_value)
        
        if numbers:
            price = float(numbers[0].replace(',', ''))
            # Reasonable bounds check
            if 10 <= price <= 1000000:
                return price
        
        return None
    except:
        return None

def format_condition_display(condition):
    """Format condition for professional display"""
    condition_map = {
        'excellent': 'Excellent',
        'very_good': 'Very Good',
        'good': 'Good',
        'fair': 'Fair',
        'poor': 'Poor'
    }
    return condition_map.get(condition, condition.title())

class PureAIDynamicPricingEngine:
    def __init__(self):
        # Only condition multipliers for adjustments - NO FIXED PRICES
        self.condition_multipliers = {
            'excellent': 1.0,
            'very_good': 0.90,
            'good': 0.75,
            'fair': 0.55,
            'poor': 0.35
        }
        
        # Emergency fallback values ONLY if AI completely fails
        self.emergency_fallbacks = {
            'vehicles': 25000,
            'fashion_beauty': 150,
            'electronics': 300,
            'home_garden': 200,
            'baby_kids': 80
        }
    
    def generate_ai_dynamic_pricing(self, analysis_data, img_base64):
        """Generate purely AI-driven dynamic pricing"""
        try:
            # Extract AI pricing estimate
            ai_price = extract_price_from_ai_estimate(analysis_data.get('estimated_value_aud', ''))
            
            if ai_price and ai_price > 0:
                logger.info(f"🎯 AI PROVIDED PRICE: ${ai_price}")
                
                # Apply condition adjustment to AI price
                condition = analysis_data.get('condition', 'good')
                condition_multiplier = self.condition_multipliers.get(condition, 0.75)
                
                adjusted_price = ai_price * condition_multiplier
                
                logger.info(f"💰 AI DYNAMIC PRICING:")
                logger.info(f"   AI Estimate: ${ai_price}")
                logger.info(f"   Condition: {condition} (×{condition_multiplier})")
                logger.info(f"   Final: ${adjusted_price}")
                
                return self._create_pricing_structure(adjusted_price, 'high', 'ai_visual_analysis')
            
            # If no AI price, try secondary pricing analysis
            logger.info("🔍 No AI price found, trying secondary analysis...")
            secondary_analysis = call_openai_api(img_base64, "pricing")
            
            if secondary_analysis:
                try:
                    clean_text = re.sub(r'```json\s*', '', secondary_analysis)
                    clean_text = re.sub(r'```\s*', '', clean_text)
                    pricing_data = json.loads(clean_text)
                    
                    market_value = extract_price_from_ai_estimate(pricing_data.get('market_value', ''))
                    
                    if market_value and market_value > 0:
                        logger.info(f"🎯 SECONDARY AI PRICING: ${market_value}")
                        return self._create_pricing_structure(market_value, 'medium', 'ai_secondary_analysis')
                    
                except Exception as e:
                    logger.error(f"Secondary pricing parsing failed: {e}")
            
            # Last resort - intelligent fallback based on category
            logger.warning("⚠️ Using intelligent fallback pricing")
            return self._intelligent_fallback(analysis_data)
            
        except Exception as e:
            logger.error(f"AI Dynamic pricing failed: {e}")
            return self._intelligent_fallback(analysis_data)
    
    def _create_pricing_structure(self, base_price, confidence, source):
        """Create pricing structure from base price"""
        market_value = round(base_price)
        quick_sale = round(base_price * 0.80)
        premium_price = round(base_price * 1.20)
        
        return {
            'pricing_analysis': {
                'quick_sale': quick_sale,
                'market_value': market_value,
                'premium_price': premium_price,
                'range_min': quick_sale,
                'range_max': premium_price,
                'average': market_value,
                'confidence': confidence,
                'pricing_source': source
            },
            'sources': [
                {'source': 'AI Visual Analysis', 'confidence': confidence}
            ]
        }
    
    def _intelligent_fallback(self, analysis_data):
        """Intelligent fallback when AI fails"""
        category = analysis_data.get('category', 'electronics')
        brand = analysis_data.get('brand', 'unknown').lower()
        item_type = analysis_data.get('item_type', 'item').lower()
        
        # Use emergency fallback but try to be smart about it
        base_price = self.emergency_fallbacks.get(category, 150)
        
        # Simple brand boost for known luxury brands
        if any(luxury in brand for luxury in ['prada', 'gucci', 'chanel', 'louis vuitton', 'hermes']):
            base_price *= 10  # Luxury boost
        elif any(premium in brand for premium in ['bmw', 'mercedes', 'audi', 'lexus', 'tesla']):
            base_price *= 2   # Premium boost
        
        logger.warning(f"🚨 FALLBACK PRICING: {category} → ${base_price}")
        
        return self._create_pricing_structure(base_price, 'low', 'intelligent_fallback')

pricing_engine = PureAIDynamicPricingEngine()

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
    """Pure AI-powered item analysis with dynamic pricing"""
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
        
        # AI Analysis
        analysis_results = {}
        
        logger.info("🤖 AI Visual Analysis...")
        primary_analysis = call_openai_api(img_base64, "analysis")
        
        if primary_analysis:
            try:
                # Clean and parse JSON
                clean_text = re.sub(r'```json\s*', '', primary_analysis)
                clean_text = re.sub(r'```\s*', '', clean_text)
                
                analysis_results = json.loads(clean_text)
                logger.info(f"✅ AI Analysis successful")
                logger.info(f"🏷️ Brand: {analysis_results.get('brand', 'unknown')}")
                logger.info(f"📱 Item: {analysis_results.get('item_type', 'unknown')}")
                logger.info(f"💎 Condition: {analysis_results.get('condition', 'unknown')}")
                logger.info(f"💰 AI Price: {analysis_results.get('estimated_value_aud', 'unknown')}")
                
            except Exception as e:
                logger.error(f"AI analysis parsing failed: {e}")
                # Manual extraction fallback
                analysis_results = extract_analysis_manually(primary_analysis)
        
        # Pure AI Dynamic Pricing
        logger.info("💰 AI Dynamic Pricing...")
        pricing_data = pricing_engine.generate_ai_dynamic_pricing(analysis_results, img_base64)
        
        # Personal listing generation
        logger.info("📝 Personal listing generation...")
        personal_listing = call_openai_api(img_base64, "listing")
        
        # Build comprehensive result
        item_info = {
            'brand': analysis_results.get('brand', 'unknown'),
            'model': analysis_results.get('model', 'unknown'),
            'category': analysis_results.get('category', 'electronics'),
            'description': analysis_results.get('item_type', 'item'),
            'condition': analysis_results.get('condition', 'good'),
            'condition_display': format_condition_display(analysis_results.get('condition', 'good')),
            'session_id': session_id,
            'image_hash': image_hash
        }
        
        category_info = MARKETPLACE_CATEGORIES.get(item_info['category'], MARKETPLACE_CATEGORIES['electronics'])
        
        logger.info(f"🎯 FINAL RESULT:")
        logger.info(f"   Brand: {item_info['brand']}")
        logger.info(f"   Item: {item_info['description']}")
        logger.info(f"   Category: {item_info['category']}")
        logger.info(f"   Condition: {item_info['condition_display']}")
        logger.info(f"   AI Price: ${pricing_data['pricing_analysis']['market_value']}")
        logger.info(f"   Source: {pricing_data['pricing_analysis']['pricing_source']}")
        
        return {
            'category': item_info['category'],
            'category_info': category_info,
            'analysis': primary_analysis or 'AI analysis completed',
            'analysis_json': item_info,
            'pricing_data': pricing_data,
            'ai_analysis_data': analysis_results,
            'personal_listing_data': personal_listing,
            'image_hash': image_hash,
            'session_id': session_id,
            'specific_item': item_info['description'],
            'ai_suggested_category': item_info['category'],
            'corrected_category': item_info['category'],
            'ai_estimated_value': f"${pricing_data['pricing_analysis']['market_value']}"
        }
        
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        return None

def extract_analysis_manually(text):
    """Manual extraction when JSON parsing fails"""
    try:
        result = {
            'brand': 'unknown',
            'item_type': 'item',
            'category': 'electronics',
            'condition': 'good',
            'confidence_level': 'low',
            'estimated_value_aud': 'unknown'
        }
        
        text_lower = text.lower()
        
        # Brand detection
        luxury_brands = ['hermes', 'chanel', 'louis vuitton', 'prada', 'gucci', 'dior', 'rolex', 'cartier']
        premium_brands = ['coach', 'michael kors', 'apple', 'samsung', 'sony', 'canon', 'nike', 'adidas']
        vehicle_brands = ['bmw', 'mercedes', 'audi', 'toyota', 'honda', 'ford', 'hyundai', 'tesla']
        
        for brand in luxury_brands + premium_brands + vehicle_brands:
            if brand in text_lower:
                result['brand'] = brand
                break
        
        # Item type detection
        if any(word in text_lower for word in ['handbag', 'bag', 'purse']):
            result['item_type'] = 'handbag'
            result['category'] = 'fashion_beauty'
        elif any(word in text_lower for word in ['car', 'suv', 'vehicle']):
            result['item_type'] = 'suv'
            result['category'] = 'vehicles'
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
        
        # Try to extract price
        price_matches = re.findall(r'(\d+(?:,\d{3})*(?:\.\d{2})?)', text)
        if price_matches:
            result['estimated_value_aud'] = price_matches[0]
        
        return result
        
    except Exception as e:
        logger.error(f"Manual extraction failed: {e}")
        return {
            'brand': 'unknown',
            'item_type': 'item',
            'category': 'electronics',
            'condition': 'good',
            'confidence_level': 'low',
            'estimated_value_aud': 'unknown'
        }

def generate_personal_listing(analysis_data):
    """Generate highly personal, emotional listing"""
    try:
        analysis_json = analysis_data.get('analysis_json', {})
        pricing_analysis = analysis_data.get('pricing_data', {}).get('pricing_analysis', {})
        personal_listing_data = analysis_data.get('personal_listing_data', '')
        
        brand = analysis_json.get('brand', 'Unknown')
        model = analysis_json.get('model', 'Unknown')
        specific_item = analysis_data.get('specific_item', 'item')
        condition = analysis_json.get('condition_display', 'Good')
        market_value = pricing_analysis.get('market_value', 100)
        
        # Try to parse AI-generated personal story
        personal_story = None
        if personal_listing_data:
            try:
                clean_text = re.sub(r'```json\s*', '', personal_listing_data)
                clean_text = re.sub(r'```\s*', '', clean_text)
                personal_data = json.loads(clean_text)
                personal_story = personal_data.get('personal_story', '')
            except:
                pass
        
        # Generate personal listing templates
        personal_templates = [
            f"I'm reluctantly selling my beloved {brand} {specific_item} that has been with me through so many special moments. I originally bought this beautiful piece because I fell in love with its craftsmanship and elegance. It's been my go-to companion for important meetings, special dinners, and memorable occasions. The {condition.lower()} condition reflects how much I've treasured and cared for it. I'm only parting with it because I'm moving overseas and need to downsize my collection. This deserves to go to someone who will appreciate its quality and beauty as much as I have. Asking ${market_value} for this treasured piece.",
            
            f"After much thought, I've decided to part with my stunning {brand} {specific_item}. This isn't just any ordinary {specific_item} - it's been my trusted companion for over two years. I remember the day I bought it; I had been saving up for months because I knew this was 'the one'. The quality is exceptional, and despite regular use, it's maintained its {condition.lower()} condition because I've always treated it with care. Life changes are forcing me to simplify, and while it breaks my heart to let this go, I hope it finds a new home with someone who will love it as much as I do. ${market_value} for this beauty.",
            
            f"This {brand} {specific_item} has been more than just an accessory to me - it's been part of my identity. I bought it during a particularly meaningful time in my life, and it's accompanied me through promotions, celebrations, and countless everyday moments. The {condition.lower()} condition speaks to how well I've maintained it, always storing it properly and treating it with the respect it deserves. I'm selling because I'm decluttering before a big move, but honestly, this is one of the hardest pieces to let go. Looking for someone who understands quality and will give this the love it deserves. ${market_value} firm."
        ]
        
        # Use AI-generated story if available, otherwise use template
        if personal_story and len(personal_story) > 50:
            # Clean up AI story and add pricing
            clean_story = re.sub(r'[^\w\s\.,!?;:()\'-]', '', personal_story)
            listing = f"{clean_story} I'm asking ${market_value} for this special piece."
        else:
            listing = random.choice(personal_templates)
        
        # Clean up any formatting issues
        listing = re.sub(r'\s+', ' ', listing)  # Remove extra spaces
        listing = re.sub(r'[^\w\s\.,!?;:()\'-]', '', listing)  # Remove weird characters
        listing = listing.strip()
        
        # Ensure proper ending
        if not listing.endswith('.'):
            listing += '.'
        
        logger.info(f"📝 PERSONAL LISTING GENERATED: {len(listing)} characters")
        
        return listing
        
    except Exception as e:
        logger.error(f"Personal listing generation failed: {e}")
        # Simple fallback
        return f"I'm selling my {brand} {specific_item} in {condition.lower()} condition for ${market_value}. This has been a cherished piece in my collection, and I'm only parting with it due to changing circumstances. It's been well-maintained and deserves a new home with someone who will appreciate its quality. Please contact me if you're interested."

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
        listing = generate_personal_listing(analysis_data)
        
        return render_template('results.html', analysis_data=analysis_data, listing=listing)
        
    except Exception as e:
        logger.error(f"Route error: {e}")
        flash('Error processing request')
        return redirect(url_for('index'))

@app.route('/categories')
def categories():
    return jsonify(MARKETPLACE_CATEGORIES)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
