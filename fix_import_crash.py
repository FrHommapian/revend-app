with open('app.py', 'r') as f:
    content = f.read()

# Fix the import statement
content = content.replace(
    'from timing_insights import timing_insights',
    'from timing_insights import get_timing_insights'
)

# Fix the function call
content = content.replace(
    'timing_data = timing_insights.get_timing_insights(',
    'timing_data = get_timing_insights('
)

with open('app.py', 'w') as f:
    f.write(content)

print("✅ Import crash fixed!")
