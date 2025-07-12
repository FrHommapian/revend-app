with open('templates/results.html', 'r') as f:
    content = f.read()

# Replace the entire listings section (lines 766-770)
old_section = '''            <div style="padding: 32px;">
                <div class="listing-content" id="listing-content">{{ listing }}</div>
                <button class="copy-btn" onclick="copyListing()" id="copyBtn">Copy listing</button>
            </div>'''

new_section = '''            <div style="padding: 32px;">
                <!-- Platform Tabs -->
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
                {% endfor %}
            </div>'''

content = content.replace(old_section, new_section)

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ Precise fix applied!")
