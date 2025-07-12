with open('templates/results.html', 'r') as f:
    content = f.read()

# Remove the broken duplicate code
broken_section = '''        });
            
            // Remove active class from all tabs
            document.querySelectorAll('.platform-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected platform content
            document.getElementById('content-' + platformKey).classList.remove('hidden');
            
            // Add active class to selected tab
            document.getElementById('tab-' + platformKey).classList.add('active');
        }'''

# Replace with just the closing brace
content = content.replace(broken_section, '        }')

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ JavaScript syntax fixed!")
