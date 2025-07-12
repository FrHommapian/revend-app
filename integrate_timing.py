with open('app.py', 'r') as f:
    content = f.read()

# Add import at the top
import_line = "from timing_insights import timing_insights"
if import_line not in content:
    # Add after other imports
    content = content.replace(
        "from pricing_engine import RealPricingEngine",
        "from pricing_engine import RealPricingEngine\nfrom timing_insights import timing_insights"
    )

# Add timing insights to the analyze_item_photo function
old_return = '''return {
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
        }'''

new_return = '''# Generate timing insights
        timing_data = timing_insights.get_timing_insights(
            category=corrected_category,
            brand=brand,
            item_type=specific_item
        )

        return {
            'category': corrected_category,
            'category_info': category_info,
            'analysis': analysis_text,
            'analysis_json': item_info,
            'pricing_data': final_pricing_data,
            'timing_insights': timing_data,
            'image_hash': image_hash,
            'session_id': session_id,
            'specific_item': specific_item,
            'ai_suggested_category': ai_suggested_category,
            'corrected_category': corrected_category,
            'ai_estimated_value': ai_estimated_value
        }'''

content = content.replace(old_return, new_return)

with open('app.py', 'w') as f:
    f.write(content)

print("✅ Timing insights integrated into app.py!")
