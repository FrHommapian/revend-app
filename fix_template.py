with open('templates/results.html', 'r') as f:
    content = f.read()

# Fix: Change title from "Your listing" to "Your listings"
content = content.replace('<div class="card-title">Your listing</div>', '<div class="card-title">Your listings</div>')

# Fix: Replace the old listing section with new platform tabs
old_section = r'<div class="listing-container">\s*<textarea id="listing-content" class="simple-textarea">{{ listing }}</textarea>\s*</div>'
new_section = '''<!-- Platform Tabs -->
                <div class="platform-tabs" style="display: flex; gap: 10px; margin-bottom: 24px; flex-wrap: wrap;">
                    {% for platform_key, platform_data in listings.items() %}
                    <button class="platform-tab {% if loop.first %}active{% endif %}" 
                            onclick="showPlatform('{{ platform_key }}')" 
                            id="tab-{{ platform_key }}">
                        {{ platform_data.name }}
                    </button>
                    {% endfor %}
                </div>
                
                <!-- Platform Content -->
                {% for platform_key, platform_data in listings.items() %}
                <div class="platform-content {% if not loop.first %}hidden{% endif %}" id="content-{{ platform_key }}">
                    <div class="listing-container">
                        <textarea id="listing-{{ platform_key }}" class="simple-textarea">{{ platform_data.content }}</textarea>
                    </div>
                    <div class="button-container">
                        <button class="copy-btn" onclick="copyListing('{{ platform_key }}')" id="copyBtn-{{ platform_key }}">
                            Copy {{ platform_data.name }} listing
                        </button>
                    </div>
                </div>
                {% endfor %}'''

import re
content = re.sub(old_section, new_section, content, flags=re.DOTALL)

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ Template fixed!")
