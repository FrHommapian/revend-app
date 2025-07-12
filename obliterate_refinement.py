with open('templates/results.html', 'r') as f:
    content = f.read()

# NUCLEAR REMOVAL: Remove the entire refinement section (lines 980-987)
refinement_section = '''        <div class="refinement-section">
            <div style="text-align: center; margin-bottom: 24px; position: relative; z-index: 1;">
                <h4 style="font-size: 1.3rem; font-weight: 800; margin-bottom: 12px;">Need to adjust details?</h4>
                
            </div>
            <div class="refinement-form" id="refinementForm" style="display: none;">
                <form id="refineForm">
                    
        
        <!-- Timing Insights Section -->'''

# Replace with just the timing insights section
clean_section = '''        
        <!-- Timing Insights Section -->'''

content = content.replace(refinement_section, clean_section)

# Remove ALL refinement CSS
import re
css_patterns = [
    r'\.refinement-section[^}]*\{[^}]*\}',
    r'\.refinement-section::before[^}]*\{[^}]*\}',
    r'\.refinement-form[^}]*\{[^}]*\}',
    r'\.refine-btn[^}]*\{[^}]*\}',
    r'\.refine-btn::before[^}]*\{[^}]*\}',
    r'\.refine-btn:hover[^}]*\{[^}]*\}',
    r'\.refine-btn:hover::before[^}]*\{[^}]*\}',
    r'\.toggle-btn[^}]*\{[^}]*\}',
    r'\.toggle-btn::before[^}]*\{[^}]*\}',
    r'\.toggle-btn:hover[^}]*\{[^}]*\}',
    r'\.toggle-btn:hover::before[^}]*\{[^}]*\}',
]

for pattern in css_patterns:
    content = re.sub(pattern, '', content, flags=re.DOTALL)

# Remove refinement JavaScript
js_patterns = [
    r'function toggleRefinement\(\)[^}]*\{[^}]*\}',
    r'document\.getElementById\(\'refineForm\'\)[^}]*addEventListener[^}]*\{[^}]*\}',
    r'fetch\(\'\/refine-analysis\'[^}]*\{[^}]*\}[^}]*\)',
]

for pattern in js_patterns:
    content = re.sub(pattern, '', content, flags=re.DOTALL)

# Remove mobile refinement CSS
content = re.sub(r'\.refinement-section \{ margin: 0 16px 32px; \}', '', content)

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ REFINEMENT SECTION OBLITERATED!")
