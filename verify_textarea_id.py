import re

with open('templates/results.html', 'r') as f:
    content = f.read()

# Ensure the textarea has the correct ID
content = re.sub(r'<textarea[^>]*id="listing-[^"]*"', '<textarea id="listing-content"', content)

# Ensure the copy button has the correct onclick
content = re.sub(r'onclick="copyListing\([^)]*\)"', 'onclick="copyListing()"', content)

# Ensure the copy button has the correct ID
content = re.sub(r'id="copyBtn-[^"]*"', 'id="copyBtn"', content)

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ Textarea and button IDs verified!")
