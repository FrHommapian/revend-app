with open('templates/results.html', 'r') as f:
    content = f.read()

# Remove any CSS that creates vertical text
import re

# Remove transform rotate styles
content = re.sub(r'transform:\s*rotate\([^)]*\)[^;]*;', '', content)

# Remove any writing-mode vertical text
content = re.sub(r'writing-mode:\s*vertical[^;]*;', '', content)

# Remove any position absolute elements with red text that might be causing side text
patterns_to_remove = [
    r'\.card::before[^}]*\{[^}]*color:\s*#dc3545[^}]*\}',
    r'\.detail-item::before[^}]*\{[^}]*color:\s*#dc3545[^}]*\}',
    r'\.card-header::before[^}]*\{[^}]*color:\s*#dc3545[^}]*\}',
]

for pattern in patterns_to_remove:
    content = re.sub(pattern, '', content, flags=re.DOTALL)

# Make any remaining red text very subtle
content = re.sub(r'color:\s*#dc3545', 'color: rgba(220, 53, 69, 0.1)', content)

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ Vertical red text removed/made subtle!")
