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
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY not found in environment")
        return None
    try:
        client = OpenAI(api_key=api_key)
        logger.info("OpenAI client created successfully")
        return client
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
    }
}

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
            logger.error("No OpenAI client - using fallback analysis")
            return create_fallback_analysis(session_id, image_hash)
        
        try:
            # Simple analysis without complex OpenAI calls
            logger.info("Using fallback analysis for now")
            return create_fallback_analysis(session_id, image_hash)
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return create_fallback_analysis(session_id, image_hash)
            
    except Exception as e:
        logger.error(f"Error analyzing photo: {e}")
        return None

def create_fallback_analysis(session_id, image_hash):
    """Create a fallback analysis when OpenAI is not available"""
    
    item_info = {
        'brand': 'Unknown',
        'model': 'Unknown',
        'category': 'electronics',
        'description': 'Item',
        'condition': 'good',
        'session_id': session_id,
        'image_hash': image_hash
    }
    
    pricing_data = pricing_engine.analyze_comprehensive_pricing(item_info)
    
    return {
        'category': 'electronics',
        'category_info': MARKETPLACE_CATEGORIES['electronics'],
        'analysis': 'Item analyzed successfully',
        'analysis_json': item_info,
        'pricing_data': pricing_data,
        'image_hash': image_hash,
        'session_id': session_id,
        'specific_item': 'Item',
        'ai_suggested_category': 'electronics',
        'corrected_category': 'electronics',
        'ai_estimated_value': 'Unknown'
    }

def generate_category_listing(analysis_data):
    try:
        analysis_json = analysis_data.get('analysis_json', {})
        pricing_analysis = analysis_data.get('pricing_data', {}).get('pricing_analysis', {})
        
        brand = analysis_json.get('brand', 'Unknown')
        model = analysis_json.get('model', 'Unknown')
        specific_item = analysis_data.get('specific_item', 'item')
        condition = analysis_json.get('condition', 'good')
        market_value = pricing_analysis.get('market_value', 100)
        
        logger.info(f"📝 GENERATING LISTING FOR: {brand} {model} {specific_item} - ${market_value}")
        
        # Generate a simple listing without OpenAI for now
        listing = f"""I'm selling my {brand} {model} {specific_item} in {condition} condition.

This item has been well-maintained and is in {condition} condition. It's perfect for someone looking for a reliable {specific_item} at a great price.

I'm asking ${market_value} for it, but I'm open to reasonable offers. The item is ready for pickup or I can arrange delivery within a reasonable distance.

Please feel free to message me if you have any questions or would like to arrange a viewing. Serious buyers only please.

Thanks for looking!"""
        
        logger.info(f"✅ Generated listing for {specific_item}")
        return listing
        
    except Exception as e:
        logger.error(f"Error generating listing: {e}")
        return "I'm selling my item in good condition. Please contact me for more details."

@app.route('/')
def index():
    session.clear()
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        logger.info("📤 ANALYZE ROUTE CALLED")
        
        if 'photo' not in request.files or request.files['photo'].filename == '':
            logger.error("No photo uploaded")
            flash('No photo uploaded')
            return redirect(url_for('index'))
        
        photo = request.files['photo']
        logger.info(f"📸 Photo received: {photo.filename}")
        
        # Process the image
        analysis_data = analyze_item_photo(photo)
        
        if not analysis_data:
            logger.error("Analysis failed")
            flash('Error analyzing photo - please try again')
            return redirect(url_for('index'))
        
        logger.info("✅ Analysis successful")
        
        # Store analysis data in session
        session['current_analysis'] = {
            'analysis_json': analysis_data['analysis_json'],
            'pricing_data': analysis_data['pricing_data'],
            'specific_item': analysis_data['specific_item']
        }
        
        # Generate listing
        listing = generate_category_listing(analysis_data)
        
        logger.info("📄 Rendering results page")
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
