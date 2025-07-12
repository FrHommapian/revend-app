# Find the loading template (could be index.html or separate loading.html)
import os

template_files = ['templates/index.html', 'templates/loading.html']

for template_file in template_files:
    if os.path.exists(template_file):
        with open(template_file, 'r') as f:
            content = f.read()
        
        if 'Analyzing your item' in content or 'loading-progress' in content:
            # Remove ALL existing loading JavaScript
            import re
            content = re.sub(r'function startLoadingProgress.*?(?=function|\</script\>|\</body\>)', '', content, flags=re.DOTALL)
            content = re.sub(r'startLoadingProgress\(\);', '', content)
            content = re.sub(r'document\.addEventListener.*?startLoadingProgress.*?;', '', content, flags=re.DOTALL)
            
            # Add completely new working loading animation
            new_loading_js = '''
<script>
document.addEventListener('DOMContentLoaded', function() {
    const progressBar = document.querySelector('.loading-progress-bar');
    if (!progressBar) return;
    
    let progress = 0;
    
    function updateProgress() {
        if (progress < 20) {
            progress += Math.random() * 3 + 1; // 1-4% increments
        } else if (progress < 50) {
            progress += Math.random() * 2 + 0.5; // 0.5-2.5% increments
        } else if (progress < 80) {
            progress += Math.random() * 1.5 + 0.3; // 0.3-1.8% increments
        } else if (progress < 95) {
            progress += Math.random() * 0.8 + 0.1; // 0.1-0.9% increments
        }
        
        if (progress > 95) progress = 95; // Cap at 95%
        
        progressBar.style.width = progress + '%';
        
        if (progress < 95) {
            setTimeout(updateProgress, 600 + Math.random() * 400); // 600-1000ms intervals
        }
    }
    
    // Start the animation
    updateProgress();
});
</script>'''
            
            # Add the new JavaScript before closing body
            if '</body>' in content:
                content = content.replace('</body>', new_loading_js + '</body>')
            else:
                content += new_loading_js
            
            # Ensure the loading bar starts at 0%
            content = re.sub(r'width:\s*\d+%', 'width: 0%', content)
            
            with open(template_file, 'w') as f:
                f.write(content)
            
            print(f"✅ Loading bar animation fixed in {template_file}!")

print("✅ All loading animations updated!")
