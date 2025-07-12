with open('templates/results.html', 'r') as f:
    content = f.read()

# Find the timing insights section end
timing_end = '''        </div>
        {% endif %}'''

# Find item details start
item_details_start = '''        <div class="card">
            <div class="card-header">
                <div class="card-title">Item details</div>'''

# Insert the listing section between them
listing_section = '''        </div>
        {% endif %}
        
        <div class="card">
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
        
        <div class="card">
            <div class="card-header">
                <div class="card-title">Item details</div>'''

# Replace the section
content = content.replace(timing_end + '\n        ' + item_details_start, listing_section)

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ LISTING SECTION RESTORED!")
