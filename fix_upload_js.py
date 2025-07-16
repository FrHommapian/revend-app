with open('templates/index.html', 'r') as f:
    content = f.read()

# Add proper JavaScript for file upload functionality
upload_js = '''
<script>
document.addEventListener('DOMContentLoaded', function() {
    const photoInput = document.getElementById('photoInput');
    const fileLabel = document.getElementById('fileLabel');
    const submitBtn = document.getElementById('submitBtn');
    const uploadForm = document.getElementById('uploadForm');
    
    if (photoInput && fileLabel && submitBtn) {
        photoInput.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                fileLabel.textContent = 'Photo selected ✓';
                fileLabel.style.background = 'rgba(40,167,69,0.3)';
                submitBtn.disabled = false;
                submitBtn.style.opacity = '1';
            } else {
                fileLabel.textContent = 'Choose photo';
                fileLabel.style.background = 'rgba(255,255,255,0.2)';
                submitBtn.disabled = true;
                submitBtn.style.opacity = '0.6';
            }
        });
        
        uploadForm.addEventListener('submit', function(e) {
            if (!photoInput.files.length) {
                e.preventDefault();
                alert('Please select a photo first');
                return;
            }
            
            submitBtn.textContent = 'Analyzing...';
            submitBtn.disabled = true;
        });
    }
});
</script>'''

# Add JavaScript before closing body tag
content = content.replace('</body>', upload_js + '</body>')

with open('templates/index.html', 'w') as f:
    f.write(content)

print("✅ Upload functionality JavaScript added!")
