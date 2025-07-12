with open('templates/results.html', 'r') as f:
    content = f.read()

# Find where to insert the CSS (before closing </style>)
css_to_add = '''
        .simple-textarea {
            width: 100%;
            height: 400px;
            padding: 20px;
            border: none;
            background: linear-gradient(135deg, #e53e3e 0%, #c53030 100%);
            color: white;
            font-size: 16px;
            line-height: 1.6;
            font-family: -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
            resize: none;
            outline: none;
            overflow-y: auto;
            -webkit-appearance: none;
            border-radius: 16px;
            text-align: left;
            box-sizing: border-box;
        }
        
        .simple-textarea:focus {
            background: linear-gradient(135deg, #e53e3e 0%, #c53030 100%);
            outline: none;
        }
        
        .listing-container {
            margin: 20px 0;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(229, 62, 62, 0.3);
        }
        
        .platform-content.hidden {
            display: none;
        }
        
        @media (max-width: 768px) {
            .simple-textarea {
                font-size: 14px;
                height: 350px;
                padding: 16px;
                -webkit-overflow-scrolling: touch;
            }
        }
'''

# Insert CSS before </style>
if '</style>' in content:
    content = content.replace('</style>', css_to_add + '\n        </style>')
else:
    print("❌ No </style> tag found!")

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ Missing CSS added!")
