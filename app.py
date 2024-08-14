from flask import Flask, request, render_template_string, send_file, Response, redirect, url_for, flash, jsonify
import firebase_admin
from firebase_admin import credentials, db
import os
import json
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

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
    message = ""
    if request.method == 'POST':
        if 'submit_name' in request.form:
            name = request.form['name']
            db.reference('names').push({'name': name})
            message = 'Name saved successfully!'
        elif 'submit_age' in request.form:
            age = request.form['age']
            db.reference('ages').push({'age': age})
            message = 'Age saved successfully!'
        elif 'submit_date' in request.form:
            date = request.form['date']
            db.reference('dates').push({'date': date})
            message = 'Date saved successfully!'
        elif 'view_name' in request.form:
            return redirect(url_for('view_data', data_type='names'))
        elif 'view_age' in request.form:
            return redirect(url_for('view_data', data_type='ages'))
        elif 'view_date' in request.form:
            return redirect(url_for('view_data', data_type='dates'))
        elif 'upload_image' in request.form:
            name = request.form['name']
            image = request.files['image']
            if image:
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                db.reference('images').push({
                    'name': name,
                    'filename': filename
                })
                message = 'Image uploaded successfully!'
        elif 'download_image' in request.form:
            name = request.form['name']
            images_ref = db.reference('images').order_by_child('name').equal_to(name).get()
            for key, val in images_ref.items():
                filename = val['filename']
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if os.path.exists(image_path):
                    return send_file(image_path, as_attachment=True, download_name=f"{name}.jpg")
            message = "Image not uploaded for this name!"

    return render_template_string(main_template, message=message)

@app.route('/view_data/<data_type>', methods=['GET'])
def view_data(data_type):
    ref = db.reference(data_type)
    data = ref.get()
    rows = [{'id': key, **value} for key, value in data.items()]
    return render_template_string(view_template, rows=rows, table_name=data_type.capitalize())

# Template strings
main_template = '''
    <form method="post">
        <h2>Submit Your Information</h2>
        Name: <input type="text" name="name"><br>
        Age: <input type="number" name="age"><br>
        Date: <input type="date" name="date"><br>
        <input type="submit" name="submit_name" value="Submit Name">
        <input type="submit" name="submit_age" value="Submit Age">
        <input type="submit" name="submit_date" value="Submit Date">
    </form>
    <br>
    <form method="post">
        <input type="submit" name="view_name" value="View All Names">
        <input type="submit" name="view_age" value="View All Ages">
        <input type="submit" name="view_date" value="View All Dates">
    </form>
    <br>
    <form method="post" enctype="multipart/form-data">
        <h2>Upload Your Image</h2>
        Name: <input type="text" name="name"><br>
        Image: <input type="file" name="image"><br>
        <input type="submit" name="upload_image" value="Upload Image">
    </form>
    <br>
    <form method="post">
        <h2>Download Your Image</h2>
        Name: <input type="text" name="name"><br>
        <input type="submit" name="download_image" value="Download Image">
    </form>
    <br>
    <h3>{{ message }}</h3>
'''

view_template = '''
    <h2>{{ table_name }}</h2>
    <table border="1">
        <tr>
            <th>ID</th>
            <th>Content</th>
        </tr>
        {% for row in rows %}
        <tr>
            <td>{{ row.id }}</td>
            <td>{{ row.name or row.age or row.date }}</td>
        </tr>
        {% endfor %}
    </table>
    <br>
    <a href="/">Go Back</a>
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
