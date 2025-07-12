with open('app.py', 'r') as f:
    content = f.read()

# Change the analyze route back to single listing
old_route = '''listings = generate_category_listing(analysis_data)
        return render_template('results.html', analysis_data=analysis_data, listings=listings)'''

new_route = '''listing = generate_category_listing(analysis_data)
        return render_template('results.html', analysis_data=analysis_data, listing=listing)'''

content = content.replace(old_route, new_route)

# Update the function to return just the general listing
old_function_end = '''        return listings'''
new_function_end = '''        return listings.get('general', {}).get('content', f"I'm selling my {brand} {model} {specific_item} in {condition} condition for ${market_value}. Please contact me for more details.")'''

content = content.replace(old_function_end, new_function_end)

with open('app.py', 'w') as f:
    f.write(content)

print("✅ App.py reverted to single listing!")
