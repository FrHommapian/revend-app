with open('timing_insights.py', 'r') as f:
    content = f.read()

# Replace emoticons in the Python file
replacements = {
    '🔥': '●',   # Fire to dot
    '✅': '✓',   # Check mark
    '⏳': '⏱️',  # Hourglass to clock
    '🌙': '◐',   # Moon to half circle
    '📈': '📊',  # Chart
    '📅': '🗓️',  # Calendar
    '🚨': '⚠️',  # Warning
    '📊': '📈',  # Keep chart
    '📱': '💻',  # Device
    '🏠': '⌂',   # House
    '🛒': '⚈',   # Shopping cart
    '🎯': '◉',   # Target
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open('timing_insights.py', 'w') as f:
    f.write(content)

print("✅ Timing insights Python file emoticons updated!")
