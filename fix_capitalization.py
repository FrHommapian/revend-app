with open('templates/results.html', 'r') as f:
    content = f.read()

# Fix capitalization in timing insights section
content = content.replace(
    '<h4>📅 Next Best Time to List</h4>',
    '<h4>📅 Next best time to list</h4>'
)

# Fix other section titles if needed
content = content.replace('Optimal Timing', 'Optimal timing')
content = content.replace('Seasonal Trends', 'Seasonal trends')
content = content.replace('Market Urgency', 'Market urgency')
content = content.replace('Platform Timing', 'Platform timing')

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ Capitalization fixed!")
