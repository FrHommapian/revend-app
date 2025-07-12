with open('templates/results.html', 'r') as f:
    content = f.read()

# Find where the listing section should be and add it back
# Look for the item details section and add listing before it
item_details_start = '''        <div class="card">
            <div class="card-header">
                <div class="card-title">Item details</div>'''

# Add the listing section before item details
listing_section = '''        <div class="card">
            <div class="card-header">
                <div class="card-title">Your listing</div>
            </div>
            <div style="padding: 32px;">
                <div class="listing-container">
                    <textarea id="listing-content" class="simple-textarea">{{ listing }}</textarea>
                </div>
                <div class="button-container">
                    <button class="copy-btn" onclick="copyListing()" id="copyBtn">Copy listing</button>
                </div>
            </div>
        </div>
        
        ''' + item_details_start

content = content.replace(item_details_start, listing_section)

# Remove any remaining refinement sections
import re
refinement_patterns = [
    r'<div class="card">\s*<div class="card-header">\s*<div class="card-title">Refine your estimate</div>.*?</div>\s*</div>',
    r'<div class="card">\s*<div class="card-header">\s*<div class="card-title">Need to adjust details\?</div>.*?</div>\s*</div>',
    r'<form[^>]*refinementForm[^>]*>.*?</form>',
    r'<button[^>]*toggleRefinement[^>]*>.*?</button>',
]

for pattern in refinement_patterns:
    content = re.sub(pattern, '', content, flags=re.DOTALL)

# Remove refinement JavaScript
js_patterns = [
    r'function toggleRefinement\(\)[^}]*\{[^}]*\}',
    r'document\.getElementById\(\'refinementForm\'\)[^;]*;',
]

for pattern in js_patterns:
    content = re.sub(pattern, '', content, flags=re.DOTALL)

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ EMERGENCY FIX: Listing section restored!")
