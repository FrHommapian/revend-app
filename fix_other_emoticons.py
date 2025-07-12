with open('templates/results.html', 'r') as f:
    content = f.read()

# Replace other emoticons throughout the app
other_replacements = {
    '📦': '◼',   # Package
    '🏷️': '◉',   # Tag
    '📱': '💻',  # Phone to computer
    '✅': '✓',   # Check mark
    '💰': '◉',   # Money bag
    '🔍': '◦',   # Magnifying glass
    '⭐': '★',   # Star
    '🚀': '◆',   # Rocket
}

for old, new in other_replacements.items():
    content = content.replace(old, new)

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ Other emoticons replaced throughout the app!")
