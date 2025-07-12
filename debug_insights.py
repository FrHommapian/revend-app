with open('app.py', 'r') as f:
    content = f.read()

# Check if timing_insights import exists
if 'from timing_insights import timing_insights' in content:
    print("✅ Import exists")
else:
    print("❌ Import missing")

# Check if timing_data is being generated
if 'timing_data = timing_insights.get_timing_insights' in content:
    print("✅ Timing data generation exists")
else:
    print("❌ Timing data generation missing")

# Check if timing_insights is in return statement
if "'timing_insights': timing_data" in content:
    print("✅ Timing insights in return statement")
else:
    print("❌ Timing insights not in return statement")

# Check template
with open('templates/results.html', 'r') as f:
    template_content = f.read()

if 'timing_insights' in template_content:
    print("✅ Template has timing_insights reference")
else:
    print("❌ Template missing timing_insights reference")

if 'Premium Timing Insights' in template_content:
    print("✅ Template has Premium Timing Insights section")
else:
    print("❌ Template missing Premium Timing Insights section")
