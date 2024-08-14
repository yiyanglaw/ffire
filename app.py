from flask import Flask, request, jsonify, send_from_directory
import firebase_admin
from firebase_admin import credentials, db
import os
import json
from flask_cors import CORS  # Import CORS

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
    'databaseURL': 'https://flask-bae57-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                return jsonify({'message': 'File uploaded successfully'}), 200
            return jsonify({'error': 'No file selected'}), 400

        name = request.form.get('name')
        age = request.form.get('age')
        if name and age:
            ref = db.reference('users')
            ref.child(name).set({'age': age})
            return jsonify({'message': 'User data added successfully'}), 200
        return jsonify({'error': 'Name and age are required'}), 400

    return jsonify({'error': 'Invalid request method'}), 405

@app.route('/view_data', methods=['GET'])
def view_data():
    ref = db.reference('users')
    users = ref.get() or {}
    return jsonify(users)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
