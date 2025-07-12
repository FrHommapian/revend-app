with open('templates/results.html', 'r') as f:
    content = f.read()

# Check if showPlatform function exists
if 'function showPlatform' not in content:
    js_to_add = '''
        function showPlatform(platformKey) {
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
        '''
    
    # Add before closing </script>
    content = content.replace('</script>', js_to_add + '\n    </script>')
    
    with open('templates/results.html', 'w') as f:
        f.write(content)
    
    print("✅ Missing JavaScript added!")
else:
    print("✅ JavaScript already exists!")
