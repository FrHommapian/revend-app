with open('templates/results.html', 'r') as f:
    content = f.read()

# Fix 1: Make textarea taller
content = content.replace('height: 250px;', 'height: 400px;')

# Fix 2: Center textarea content and improve styling
textarea_improvements = '''        .simple-textarea {
            width: 100%;
            height: 400px;
            padding: 20px;
            border: none;
            background: linear-gradient(135deg, #e53e3e 0%, #c53030 100%);
            color: white;
            font-size: 16px;
            line-height: 1.6;
            font-family: -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
            resize: none;
            outline: none;
            overflow-y: auto;
            -webkit-appearance: none;
            border-radius: 16px;
            text-align: left;
            vertical-align: top;
        }'''

# Replace the existing simple-textarea CSS
import re
old_textarea_css = r'\.simple-textarea \{[^}]*\}'
content = re.sub(old_textarea_css, textarea_improvements, content, flags=re.DOTALL)

# Fix 3: Improve button container spacing
button_container_fix = '''        .button-container {
            display: flex;
            justify-content: center;
            margin: 20px 0;
            padding: 0 20px;
        }'''

content = content.replace(
    '        .button-container {\n            display: flex;\n            justify-content: center;\n            margin: 20px 0;\n        }',
    button_container_fix
)

# Fix 4: Mobile responsive improvements
mobile_fix = '''        @media (max-width: 768px) {
            .simple-textarea {
                font-size: 14px;
                height: 350px;
                -webkit-overflow-scrolling: touch;
                padding: 16px;
            }
            
            .platform-tab {
                padding: 8px 16px;
                font-size: 13px;
                flex: 1;
                text-align: center;
                min-width: 70px;
            }
        }'''

# Replace mobile section
content = re.sub(
    r'@media \(max-width: 768px\) \{[^}]*\.simple-textarea[^}]*\}[^}]*\}',
    mobile_fix,
    content,
    flags=re.DOTALL
)

# Fix 5: Fix JavaScript - replace old function completely
old_js_section = r'function copyListing\(\)[^}]*\}[^}]*\}'

new_js_section = '''function showPlatform(platformKey) {
            // Hide all platform content
            document.querySelectorAll('.platform-content').forEach(content => {
                content.classList.add('hidden');
            });
            
            // Remove active class from all tabs
            document.querySelectorAll('.platform-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected platform content
            document.getElementById('content-' + platformKey).classList.remove('hidden');
            
            // Add active class to selected tab
            document.getElementById('tab-' + platformKey).classList.add('active');
        }
        
        function copyListing(platformKey) {
            const listingText = document.getElementById('listing-' + platformKey).value;
            const btn = document.getElementById('copyBtn-' + platformKey);
            const originalText = btn.textContent;
            
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(listingText).then(() => {
                    btn.textContent = '✓ Copied!';
                    btn.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
                    btn.classList.add('success');
                    setTimeout(() => {
                        btn.textContent = originalText;
                        btn.style.background = 'linear-gradient(135deg, #dc3545 0%, #c82333 100%)';
                        btn.classList.remove('success');
                    }, 2000);
                }).catch(() => {
                    fallbackCopy(listingText, btn, originalText);
                });
            } else {
                fallbackCopy(listingText, btn, originalText);
            }
        }'''

content = re.sub(old_js_section, new_js_section, content, flags=re.DOTALL)

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ ALL fixes applied!")
