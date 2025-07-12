with open('templates/results.html', 'r') as f:
    content = f.read()

# Debug: Check if listings variable exists
if 'listings.items()' in content:
    print("✅ Template has listings.items()")
else:
    print("❌ Template missing listings.items()")

# Debug: Check platform tabs
if 'platform-tab' in content:
    print("✅ Template has platform-tab class")
else:
    print("❌ Template missing platform-tab class")

# Debug: Check JavaScript
if 'showPlatform' in content:
    print("✅ Template has showPlatform function")
else:
    print("❌ Template missing showPlatform function")

# Show the actual listings section
print("\n=== LISTINGS SECTION ===")
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'Your listing' in line or 'listings' in line:
        print(f"Line {i}: {line.strip()}")
