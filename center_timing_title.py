with open('templates/results.html', 'r') as f:
    content = f.read()

# Find the timing insights header and center it
old_header = '''            <div class="card-header">
                <div class="card-title">⏰ Premium Timing Insights</div>
            </div>'''

new_header = '''            <div class="card-header" style="text-align: center;">
                <div class="card-title">⏰ Premium Timing Insights</div>
            </div>'''

content = content.replace(old_header, new_header)

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ Premium Timing Insights title centered!")
