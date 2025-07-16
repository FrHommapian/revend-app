with open('templates/index.html', 'r') as f:
    content = f.read()

import re

# Fix the main container and centering
# Replace any broken container classes
content = re.sub(r'<div class="container[^"]*"[^>]*>', '<div class="container-fluid px-3">', content)

# Ensure proper viewport and responsive meta tag
if '<meta name="viewport"' not in content:
    content = content.replace('<head>', '<head>\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">')

# Fix the main layout structure - ensure everything is centered
main_layout_css = '''
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
            min-height: 100vh;
            padding: 20px 0;
            margin: 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .container-fluid {
            max-width: 500px;
            width: 100%;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        .upload-card {
            background: rgba(255,255,255,0.95);
            border-radius: 28px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 16px 48px rgba(0,0,0,0.15);
            backdrop-filter: blur(20px);
            border: 2px solid rgba(255,255,255,0.2);
            margin: 0 auto;
            position: relative;
            overflow: hidden;
        }
        
        .logo {
            font-size: 3.5rem;
            font-weight: 900;
            color: #dc3545;
            margin-bottom: 20px;
            letter-spacing: -0.03em;
            text-align: center;
        }
        
        .upload-section {
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            color: white;
            padding: 30px;
            border-radius: 20px;
            margin: 20px 0;
            text-align: center;
        }
        
        .upload-icon {
            font-size: 3rem;
            margin-bottom: 16px;
            display: block;
        }
        
        .upload-title {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 12px;
        }
        
        .upload-subtitle {
            font-size: 1rem;
            opacity: 0.9;
            margin-bottom: 24px;
            line-height: 1.4;
        }
        
        .file-input-wrapper {
            position: relative;
            display: inline-block;
            width: 100%;
            margin-bottom: 16px;
        }
        
        .file-input {
            position: absolute;
            opacity: 0;
            width: 100%;
            height: 100%;
            cursor: pointer;
        }
        
        .file-input-button {
            background: rgba(255,255,255,0.2);
            border: 2px solid rgba(255,255,255,0.3);
            color: white;
            padding: 16px 32px;
            border-radius: 25px;
            font-weight: 700;
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            display: block;
            width: 100%;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        
        .file-input-button:hover {
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.2);
        }
        
        .submit-button {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            border: none;
            color: white;
            padding: 16px 32px;
            border-radius: 25px;
            font-weight: 700;
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            box-shadow: 0 8px 24px rgba(40,167,69,0.3);
        }
        
        .submit-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 32px rgba(40,167,69,0.4);
        }
        
        .submit-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        @media (max-width: 768px) {
            .container-fluid {
                padding: 0 16px;
                max-width: 100%;
            }
            
            .upload-card {
                padding: 30px 20px;
                margin: 20px 0;
            }
            
            .logo {
                font-size: 2.8rem;
            }
        }
'''

# Replace existing CSS with fixed layout
if '<style>' in content and '</style>' in content:
    # Replace everything between style tags
    content = re.sub(r'<style>.*?</style>', f'<style>{main_layout_css}</style>', content, flags=re.DOTALL)
else:
    # Add style section
    content = content.replace('</head>', f'<style>{main_layout_css}</style></head>')

# Fix the HTML structure
html_structure = '''<div class="container-fluid">
        <div class="upload-card">
            <div class="logo">Revend</div>
            
            <div class="upload-section">
                <div class="upload-icon">📷</div>
                <div class="upload-title">Upload your photo</div>
                <div class="upload-subtitle">Any item works • Get instant pricing</div>
                
                <form action="/analyze" method="post" enctype="multipart/form-data" id="uploadForm">
                    <div class="file-input-wrapper">
                        <input type="file" name="photo" accept="image/*" capture="environment" class="file-input" id="photoInput" required>
                        <label for="photoInput" class="file-input-button" id="fileLabel">
                            Choose photo
                        </label>
                    </div>
                    
                    <button type="submit" class="submit-button" id="submitBtn" disabled>
                        Get my listing
                    </button>
                </form>
            </div>
        </div>
    </div>'''

# Replace the body content
body_pattern = r'<body[^>]*>.*?</body>'
new_body = f'<body>{html_structure}</body>'
content = re.sub(body_pattern, new_body, content, flags=re.DOTALL)

with open('templates/index.html', 'w') as f:
    f.write(content)

print("✅ Emergency layout fix applied!")
