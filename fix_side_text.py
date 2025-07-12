with open('templates/results.html', 'r') as f:
    content = f.read()

# Find and fix the side text styling (likely in card::before or similar)
import re

# Look for any vertical text or side text styling
side_text_patterns = [
    r'\.card::before[^}]*\{[^}]*content:[^}]*color:[^}]*\}',
    r'\.card-header::before[^}]*\{[^}]*content:[^}]*color:[^}]*\}',
    r'\.detail-item::before[^}]*\{[^}]*content:[^}]*color:[^}]*\}',
]

# Replace with more subtle styling
subtle_side_text = '''            content: '';
            position: absolute;
            left: -20px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: linear-gradient(135deg, rgba(220, 53, 69, 0.1) 0%, rgba(220, 53, 69, 0.05) 100%);
            opacity: 0.3;
            transition: opacity 0.3s ease;'''

for pattern in side_text_patterns:
    content = re.sub(pattern, subtle_side_text, content, flags=re.DOTALL)

# Also fix any transform: rotate text
content = re.sub(r'transform:\s*rotate\([^)]*\)', 'transform: rotate(0deg)', content)

# Make any red text more transparent
content = re.sub(r'color:\s*#dc3545', 'color: rgba(220, 53, 69, 0.2)', content)
content = re.sub(r'color:\s*#c82333', 'color: rgba(200, 35, 51, 0.2)', content)

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ Side text made more subtle and readable!")
