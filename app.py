from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify
import firebase_admin
from firebase_admin import credentials, db
import os
import json

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for flashing messages

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
        # Check if the post request has the file part
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                # Save file to the uploads folder
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                flash(f'File {file.filename} uploaded successfully.')
            else:
                flash('No file selected for uploading.')
            return redirect(url_for('index'))

        # Get the text and age from the form
        name = request.form.get('name')
        age = request.form.get('age')
        
        if name and age:
            # Write data to Firebase Realtime Database
            ref = db.reference('users')
            ref.child(name).set({'age': age})

            return redirect(url_for('index'))
        
    # Get all users stored in Firebase
    ref = db.reference('users')
    users = ref.get()

    # Provide a default empty dictionary if no users are found
    if users is None:
        users = {}

    # List of uploaded files
    uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])

    return render_template('index.html', users=users, uploaded_files=uploaded_files)

@app.route('/view_data', methods=['GET'])
def view_data():
    # Get all users stored in Firebase
    ref = db.reference('users')
    users = ref.get()
    return jsonify(users)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
