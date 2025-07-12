with open('app.py', 'r') as f:
    content = f.read()

# Find the generate_category_listing function and simplify it
old_function_pattern = r'def generate_category_listing\(analysis_data\):.*?return listings\.get\(\'general\', \{\}\)\.get\(\'content\'.*?\)'

new_function = '''def generate_category_listing(analysis_data):
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
        
        logger.info(f"📝 GENERATING SINGLE LISTING FOR: {specific_item}")
        
        client = get_openai_client()
        
        # Generate single general listing
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": f"""Create an Australian marketplace listing for this {brand} {model} {specific_item} in {condition} condition for ${market_value}. 

Write 150-250 words as an Australian seller with personal story about why you're selling. Include care details and condition. No emojis. Sound authentic and trustworthy.

Make sure the listing is about the {specific_item}, not anything else."""
            }],
            max_tokens=400,
            temperature=0.3
        )
        
        generated_listing = response.choices[0].message.content
        
        logger.info(f"✅ Generated single listing")
        return generated_listing
        
    except Exception as e:
        logger.error(f"Error generating listing: {e}")
        return f"I'm selling my {brand} {model} {specific_item} in {condition} condition for ${market_value}. Please contact me for more details."'''

import re
content = re.sub(old_function_pattern, new_function, content, flags=re.DOTALL)

with open('app.py', 'w') as f:
    f.write(content)

print("✅ Backend fixed to generate single listing!")
