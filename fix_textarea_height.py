with open('templates/results.html', 'r') as f:
    content = f.read()

# Find and update the textarea height in CSS
old_height = 'height: 250px;'
new_height = 'height: 400px;'

content = content.replace(old_height, new_height)

# Also add minimum height for mobile
mobile_fix = '''        @media (max-width: 768px) {
            .simple-textarea {
                font-size: 14px;
                height: 300px;
                -webkit-overflow-scrolling: touch;
            }
        }'''

# Find mobile section and update
content = content.replace(
    '            .simple-textarea {\n                font-size: 14px;\n                height: 200px;\n                -webkit-overflow-scrolling: touch;\n            }',
    '            .simple-textarea {\n                font-size: 14px;\n                height: 300px;\n                -webkit-overflow-scrolling: touch;\n            }'
)

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ Textarea height fixed!")
