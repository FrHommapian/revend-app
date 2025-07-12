# First, let's check if we have a loading template
import os
if os.path.exists('templates/loading.html'):
    with open('templates/loading.html', 'r') as f:
        content = f.read()
    template_file = 'templates/loading.html'
else:
    # Check if loading is embedded in index.html
    with open('templates/index.html', 'r') as f:
        content = f.read()
    template_file = 'templates/index.html'

# Add animated loading bar CSS and JavaScript
loading_bar_css = '''
        .loading-progress {
            width: 100%;
            height: 8px;
            background-color: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
            margin: 20px 0;
        }
        
        .loading-progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #dc3545, #c82333);
            width: 0%;
            border-radius: 4px;
            transition: width 0.8s ease-in-out;
            animation: progressPulse 2s infinite;
        }
        
        @keyframes progressPulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }
'''

loading_bar_js = '''
        // Animated loading bar
        function startLoadingProgress() {
            const progressBar = document.querySelector('.loading-progress-bar');
            if (!progressBar) return;
            
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 12 + 3; // Random increment 3-15%
                if (progress > 95) progress = 95; // Cap at 95%
                progressBar.style.width = progress + '%';
                
                if (progress >= 95) {
                    clearInterval(interval);
                    // Complete when page actually loads
                    window.addEventListener('beforeunload', () => {
                        progressBar.style.width = '100%';
                    });
                }
            }, 600); // Update every 600ms for smooth animation
        }
        
        // Start progress when analysis begins
        document.addEventListener('DOMContentLoaded', startLoadingProgress);
'''

# Add CSS before closing </style>
if '</style>' in content:
    content = content.replace('</style>', loading_bar_css + '</style>')

# Add JavaScript before closing </script> or </body>
if '</script>' in content:
    content = content.replace('</script>', loading_bar_js + '</script>')
elif '</body>' in content:
    content = content.replace('</body>', '<script>' + loading_bar_js + '</script></body>')

# Add the loading bar HTML (look for existing progress bar or red section)
if 'progress-bar' in content or 'loading-bar' in content:
    # Replace existing progress bar
    import re
    content = re.sub(
        r'<div[^>]*progress[^>]*>.*?</div>',
        '<div class="loading-progress"><div class="loading-progress-bar"></div></div>',
        content,
        flags=re.DOTALL
    )
else:
    # Add new loading bar after "This usually takes 30-60 seconds"
    content = content.replace(
        'This usually takes 30-60 seconds',
        'This usually takes 30-60 seconds</p><div class="loading-progress"><div class="loading-progress-bar"></div></div><p style="margin-top: 15px;"'
    )

with open(template_file, 'w') as f:
    f.write(content)

print(f"✅ Animated loading bar added to {template_file}!")
