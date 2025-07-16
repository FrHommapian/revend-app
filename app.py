from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os
import uuid
from PIL import Image
import io

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(image_path):
    """
    Process the uploaded image and generate listing information
    This is where you'd integrate with your AI/ML service
    """
    try:
        # Open and process the image
        with Image.open(image_path) as img:
            # Basic image processing
            img.thumbnail((800, 800), Image.Resampling.LANCZOS)
            
            # Here you would integrate with your pricing/listing AI service
            # For now, returning mock data
            listing_data = {
                'title': 'Detected Item',
                'description': 'Item detected from uploaded image',
                'estimated_price': '$25.00',
                'category': 'Electronics',
                'condition': 'Good',
                'confidence': 85
            }
            
            return listing_data
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Check if file is present
        if 'image' not in request.files:
            return jsonify({'error': True, 'message': 'No file uploaded'}), 400
        
        file = request.files['image']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': True, 'message': 'No file selected'}), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({'error': True, 'message': 'File type not allowed. Please upload an image.'}), 400
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Process the image
        listing_data = process_image(file_path)
        
        if listing_data:
            # Store listing data in session or database
            # For now, just return the data
            return jsonify({
                'success': True,
                'message': 'Image processed successfully',
                'listing': listing_data,
                'redirect': f'/listing/{unique_filename}'
            })
        else:
            return jsonify({'error': True, 'message': 'Failed to process image'}), 500
            
    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({'error': True, 'message': 'Server error occurred'}), 500

@app.route('/listing/<filename>')
def show_listing(filename):
    # This would show the listing results page
    # For now, just return success message
    return f"<h1>Listing Results for {filename}</h1><p>Your item has been processed successfully!</p>"

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': True, 'message': 'File is too large. Maximum size is 10MB.'}), 413

if __name__ == '__main__':
    app.run(debug=True)
