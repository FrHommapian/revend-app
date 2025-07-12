with open('templates/results.html', 'r') as f:
    content = f.read()

# Replace all symbols with impactful single words
symbol_replacements = {
    '⏱️': 'TIMING',
    '◉': 'OPTIMAL',
    '📊': 'TRENDS',
    '⚡': 'URGENT',
    '💻': 'DIGITAL',
    '🗓️': 'SCHEDULE',
    '✓': 'VERIFIED',
    '⏱️': 'TIMING',
    '◐': 'EVENING',
    '⚠️': 'ALERT',
    '📈': 'GROWTH',
    '◼': 'STRATEGY',
    '⌂': 'LOCAL',
    '⚈': 'MARKET',
    '●': 'PRIME',
    '◆': 'BOOST',
    '★': 'PREMIUM',
    '◦': 'SEARCH',
}

for symbol, word in symbol_replacements.items():
    content = content.replace(symbol, word)

# Also replace in the timing insights section specifically
content = content.replace('TIMING Premium Timing Insights', 'TIMING Premium Timing Insights')

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ All symbols replaced with professional words!")
