with open('requirements.txt', 'r') as f:
    content = f.read()

if 'pytz' not in content:
    content += '\npytz==2023.3\n'
    
    with open('requirements.txt', 'w') as f:
        f.write(content)
    
    print("✅ Added pytz timezone dependency!")
else:
    print("✅ pytz already in requirements!")
