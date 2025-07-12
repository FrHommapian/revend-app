with open('templates/results.html', 'r') as f:
    content = f.read()

# Find the old copyListing function and replace with both functions
old_js_pattern = r'function copyListing\(\) \{[^}]*\}'

new_js = '''function showPlatform(platformKey) {
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

import re
content = re.sub(old_js_pattern, new_js, content, flags=re.DOTALL)

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ JavaScript tab switching fixed!")
