with open('templates/results.html', 'r') as f:
    content = f.read()

# Remove all the complex JavaScript and keep only simple copy function
old_js_section = '''function showPlatform(platformKey) {
            console.log('🔥 showPlatform called with:', platformKey);
            
            // Hide all platform content
            const allContent = document.querySelectorAll('.platform-content');
            console.log('📦 Found platform content elements:', allContent.length);
            allContent.forEach(content => {
                content.classList.add('hidden');
                console.log('🔒 Hidden:', content.id);
            });
            
            // Remove active class from all tabs
            const allTabs = document.querySelectorAll('.platform-tab');
            allTabs.forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected platform content
            const targetContent = document.getElementById('content-' + platformKey);
            if (targetContent) {
                targetContent.classList.remove('hidden');
                console.log('🔓 Showing:', targetContent.id);
            } else {
                console.error('❌ Target content not found:', 'content-' + platformKey);
            }
            
            // Add active class to selected tab
            const targetTab = document.getElementById('tab-' + platformKey);
            if (targetTab) {
                targetTab.classList.add('active');
                console.log('✅ Activated tab:', targetTab.id);
            }
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

simple_js = '''function copyListing() {
            const listingText = document.getElementById('listing-content').value;
            const btn = document.getElementById('copyBtn');
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

content = content.replace(old_js_section, simple_js)

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ JavaScript cleaned up!")
