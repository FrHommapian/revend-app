with open('templates/results.html', 'r') as f:
    content = f.read()

# Remove the first duplicate listing section (lines 949-964)
first_duplicate = '''        </div>
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
        </div>'''

# Replace with just the timing insights end
clean_end = '''        </div>
        {% endif %}'''

content = content.replace(first_duplicate, clean_end)

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ Duplicate listing section removed!")
