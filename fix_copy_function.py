with open('templates/results.html', 'r') as f:
    content = f.read()

# Check if copyListing function exists
if 'function copyListing()' not in content:
    # Add the copy function
    copy_js = '''
        function copyListing() {
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
        }
        '''
    
    # Add before closing </script>
    content = content.replace('</script>', copy_js + '\n    </script>')
    
    with open('templates/results.html', 'w') as f:
        f.write(content)
    
    print("✅ Copy function added!")
else:
    print("✅ Copy function already exists!")
