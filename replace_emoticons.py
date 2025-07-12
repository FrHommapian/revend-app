with open('templates/results.html', 'r') as f:
    content = f.read()

# Replace timing insights emoticons with professional symbols
replacements = {
    '⏰': '⏱️',  # Clock
    '🎯': '◉',   # Target
    '📈': '📊',  # Chart
    '⚡': '⚡',   # Lightning (keep)
    '📱': '💻',  # Device
    '📅': '🗓️',  # Calendar
    '🔥': '●',   # Fire to dot
    '✅': '✓',   # Check mark
    '⏳': '⏱️',  # Hourglass to clock
    '🌙': '◐',   # Moon to half circle
    '🚨': '⚠️',  # Warning
    '📊': '📈',  # Keep chart
    '💡': '◉',   # Light bulb to dot
    '📋': '◼',   # Clipboard to square
    '🏠': '⌂',   # House
    '🛒': '⚈',   # Shopping cart
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ Emoticons replaced with professional symbols!")
