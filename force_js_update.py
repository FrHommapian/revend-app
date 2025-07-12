with open('templates/results.html', 'r') as f:
    content = f.read()

# Check current state
if 'console.log' in content:
    print("✅ Debug JS already exists")
else:
    print("❌ Adding debug JS now")
    
    # Find the exact showPlatform function
    import re
    pattern = r'function showPlatform\(platformKey\) \{[^}]*\}'
    
    debug_function = '''function showPlatform(platformKey) {
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
        }'''
    
    # Replace the function
    content = re.sub(pattern, debug_function, content, flags=re.DOTALL)
    
    with open('templates/results.html', 'w') as f:
        f.write(content)
    
    print("✅ Debug JS force updated!")
