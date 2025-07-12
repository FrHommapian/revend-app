with open('templates/results.html', 'r') as f:
    content = f.read()

# Find and remove the refinement section (it's between pricing and item details)
import re

# Look for the refinement form section pattern
patterns_to_remove = [
    r'<div class="card">\s*<div class="card-header">\s*<div class="card-title">Refine your estimate</div>.*?</form>\s*</div>\s*</div>',
    r'<div class="row">\s*<div class="col-md-6">.*?</form>\s*</div>\s*</div>',
    r'function toggleRefinement\(\)[^}]*\{[^}]*\}',
]

for pattern in patterns_to_remove:
    content = re.sub(pattern, '', content, flags=re.DOTALL)

# Remove any remaining refinement-related elements
content = re.sub(r'<button[^>]*toggleRefinement[^>]*>.*?</button>', '', content, flags=re.DOTALL)

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ Refinement section removed!")
