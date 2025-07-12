with open('templates/results.html', 'r') as f:
    content = f.read()

# Replace the timing card color CSS with app-themed colors
old_css = '''        .timing-optimal {
            border-left-color: #28a745;
            background: linear-gradient(135deg, #d4edda 0%, #ffffff 100%);
        }
        
        .timing-peak {
            border-left-color: #dc3545;
            background: linear-gradient(135deg, #f8d7da 0%, #ffffff 100%);
        }
        
        .timing-high {
            border-left-color: #dc3545;
            background: linear-gradient(135deg, #f8d7da 0%, #ffffff 100%);
        }
        
        .timing-normal {
            border-left-color: #17a2b8;
            background: linear-gradient(135deg, #d1ecf1 0%, #ffffff 100%);
        }'''

new_css = '''        .timing-optimal {
            border-left-color: #dc3545;
            background: linear-gradient(135deg, #ffe6e6 0%, #ffffff 100%);
        }
        
        .timing-peak {
            border-left-color: #dc3545;
            background: linear-gradient(135deg, #ffe6e6 0%, #ffffff 100%);
        }
        
        .timing-high {
            border-left-color: #dc3545;
            background: linear-gradient(135deg, #ffe6e6 0%, #ffffff 100%);
        }
        
        .timing-normal {
            border-left-color: #6c757d;
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        }
        
        .timing-good {
            border-left-color: #6c757d;
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        }
        
        .timing-wait {
            border-left-color: #6c757d;
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        }'''

content = content.replace(old_css, new_css)

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ Timing card colors updated to match app theme!")
