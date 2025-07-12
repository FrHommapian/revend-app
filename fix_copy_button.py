with open('templates/results.html', 'r') as f:
    content = f.read()

# Remove existing copy function
import re
content = re.sub(r'function copyListing\(\).*?(?=function|\</script\>)', '', content, flags=re.DOTALL)

# Add working copy function
working_copy_js = '''
function copyListing() {
    const textarea = document.getElementById('listing-content');
    const btn = document.getElementById('copyBtn');
    
    if (!textarea || !btn) {
        console.error('Copy elements not found');
        return;
    }
    
    const listingText = textarea.value;
    const originalText = btn.textContent;
    
    // Try modern clipboard API first
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(listingText).then(() => {
            btn.textContent = '✓ Copied!';
            btn.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
            
            setTimeout(() => {
                btn.textContent = originalText;
                btn.style.background = 'linear-gradient(135deg, #dc3545 0%, #c82333 100%)';
            }, 2000);
        }).catch(() => {
            // Fallback for older browsers
            fallbackCopy(listingText, btn, originalText);
        });
    } else {
        // Fallback for browsers without clipboard API
        fallbackCopy(listingText, btn, originalText);
    }
}

function fallbackCopy(text, btn, originalText) {
    // Create temporary textarea
    const tempTextarea = document.createElement('textarea');
    tempTextarea.value = text;
    tempTextarea.style.position = 'fixed';
    tempTextarea.style.left = '-9999px';
    tempTextarea.style.top = '-9999px';
    document.body.appendChild(tempTextarea);
    
    // Select and copy
    tempTextarea.focus();
    tempTextarea.select();
    tempTextarea.setSelectionRange(0, 99999); // For mobile devices
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            btn.textContent = '✓ Copied!';
            btn.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
            
            setTimeout(() => {
                btn.textContent = originalText;
                btn.style.background = 'linear-gradient(135deg, #dc3545 0%, #c82333 100%)';
            }, 2000);
        } else {
            btn.textContent = 'Copy failed';
            setTimeout(() => {
                btn.textContent = originalText;
            }, 2000);
        }
    } catch (err) {
        console.error('Copy failed:', err);
        btn.textContent = 'Copy failed';
        setTimeout(() => {
            btn.textContent = originalText;
        }, 2000);
    }
    
    // Clean up
    document.body.removeChild(tempTextarea);
}
'''

# Add the new copy function before closing script tag
if '</script>' in content:
    content = content.replace('</script>', working_copy_js + '</script>')
else:
    content = content.replace('</body>', '<script>' + working_copy_js + '</script></body>')

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ Copy button functionality fixed!")
