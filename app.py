from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, db
import os
import json

# Initialize Flask app
app = Flask(__name__)

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
        # Get the text and age from the form
        name = request.form['name']
        age = request.form['age']

        # Write data to Firebase Realtime Database
        ref = db.reference('users')
        ref.child(name).set({'age': age})

        return redirect(url_for('index'))

    # Get all ages stored in Firebase
    ref = db.reference('users')
    users = ref.get()

    return render_template('index.html', users=users)

@app.route('/view_ages')
def view_ages():
    # Get all ages stored in Firebase
    ref = db.reference('users')
    users = ref.get()
    return render_template('view_ages.html', users=users)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
