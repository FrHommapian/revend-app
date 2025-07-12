with open('templates/results.html', 'r') as f:
    content = f.read()

# Add CSS to style the professional words
word_styling = '''
        .timing-icon {
            font-size: 0.9rem;
            font-weight: 800;
            color: #dc3545;
            background: rgba(220, 53, 69, 0.1);
            padding: 6px 12px;
            border-radius: 20px;
            text-align: center;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
            display: inline-block;
            border: 2px solid rgba(220, 53, 69, 0.2);
        }
'''

# Add CSS before closing </style>
content = content.replace('</style>', word_styling + '</style>')

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ Professional word styling added!")
