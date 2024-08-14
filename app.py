from flask import Flask, request, jsonify, send_from_directory
import firebase_admin
from firebase_admin import credentials, db, storage
import os
import json
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set up upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load Firebase credentials from environment variable
firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')
cred_dict = json.loads(firebase_credentials)
cred = credentials.Certificate(cred_dict)

# Initialize Firebase
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://flask-bae57-default-rtdb.asia-southeast1.firebasedatabase.app/',
    'storageBucket': 'your-bucket-name.appspot.com'  # Update with your storage bucket
})

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                try:
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                    file.save(file_path)

                    # Upload file to Firebase Storage
                    bucket = storage.bucket()
                    blob = bucket.blob(file.filename)
                    blob.upload_from_filename(file_path)
                    image_url = blob.generate_signed_url(expiration=3600)

                    name = request.form.get('name')
                    age = request.form.get('age')
                    if name and age:
                        ref = db.reference('users')
                        ref.child(name).set({'age': age, 'imageUrl': image_url})
                        return jsonify({'message': 'User data and file uploaded successfully'}), 200

                except Exception as e:
                    return jsonify({'error': f'File upload failed: {str(e)}'}), 500
            return jsonify({'error': 'No file selected'}), 400

    return jsonify({'error': 'Invalid request method'}), 405

@app.route('/view_data', methods=['GET'])
def view_data():
    try:
        ref = db.reference('users')
        users = ref.get() or {}
        return jsonify(users)
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve data: {str(e)}'}), 500

@app.route('/delete_data/<name>', methods=['DELETE'])
def delete_data(name):
    try:
        ref = db.reference('users')
        if ref.child(name).get() is not None:
            ref.child(name).delete()
            return jsonify({'message': 'User data deleted successfully'}), 200
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to delete data: {str(e)}'}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        return jsonify({'error': f'File retrieval failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
