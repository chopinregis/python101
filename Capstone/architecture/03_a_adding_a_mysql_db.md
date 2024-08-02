Certainly! I'll provide you with the detailed code to set up a MySQL database on your EC2 instance, modify your Flask application to store and retrieve data from the database, and create a new page to display all patient information. Here's a step-by-step guide with the necessary code:

1. First, let's update our bootstrap script to install MySQL and the required Python packages:

Add these lines to your bootstrap script after the initial package installation:

```bash
# Install MySQL and required packages
sudo apt install mysql-server python3-dev default-libmysqlclient-dev build-essential -y

# Secure MySQL installation
sudo mysql_secure_installation

# Install PyMySQL
pip install pymysql
```

2. Next, let's create the MySQL database and user. Add these lines to your bootstrap script:

```bash
# Create database and user
sudo mysql -e "CREATE DATABASE hospital_queue;"
sudo mysql -e "CREATE USER 'hospital_user'@'localhost' IDENTIFIED BY 'your_password';"
sudo mysql -e "GRANT ALL PRIVILEGES ON hospital_queue.* TO 'hospital_user'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"
```

Replace 'your_password' with a strong password.

3. Now, let's update our Flask application to use MySQL. Replace the content of `app.py` with the following:

```python
from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import os
import pymysql

app = Flask(__name__)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'hospital_user',
    'password': 'your_password',
    'db': 'hospital_queue',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

API_ENDPOINT = os.environ.get('API_ENDPOINT')

def get_db_connection():
    return pymysql.connect(**db_config)

@app.route('/')
def index():
    hospitals = ['Hospital A', 'Hospital B', 'Hospital C']
    return render_template('index.html', hospitals=hospitals)

@app.route('/form/<hospital>')
def form(hospital):
    return render_template('form.html', hospital=hospital)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.to_dict()
    
    # Store data in MySQL
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            sql = """INSERT INTO patients 
                     (name, last_name, dob, hospital, symptoms) 
                     VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(sql, (data['name'], data['lastName'], data['dob'], 
                                 data['hospital'], data['symptoms']))
        connection.commit()
    
    # Make API call to Lambda function via API Gateway
    response = requests.post(f"{API_ENDPOINT}/submit", json=data)
    result = response.json()
    
    return render_template('result.html', result=result)

@app.route('/check_queues')
def check_queues():
    # Make API call to Lambda function to get queue status
    response = requests.get(f"{API_ENDPOINT}/check_queues")
    queues = response.json()
    return jsonify(queues)

@app.route('/patients')
def patients():
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM patients")
            patients = cursor.fetchall()
    return render_template('patients.html', patients=patients)

if __name__ == '__main__':
    app.run(debug=True)
```

4. Create a new template file `patients.html` in the `templates` directory:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Patient List</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <h1>Patient List</h1>
    <table>
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Last Name</th>
            <th>Date of Birth</th>
            <th>Hospital</th>
            <th>Symptoms</th>
        </tr>
        {% for patient in patients %}
        <tr>
            <td>{{ patient.id }}</td>
            <td>{{ patient.name }}</td>
            <td>{{ patient.last_name }}</td>
            <td>{{ patient.dob }}</td>
            <td>{{ patient.hospital }}</td>
            <td>{{ patient.symptoms }}</td>
        </tr>
        {% endfor %}
    </table>
    <a href="{{ url_for('index') }}">Back to Home</a>
</body>
</html>
```

5. Update the `index.html` file to include a link to the patients page:

Add this line just before the closing `</body>` tag:

```html
<p><a href="{{ url_for('patients') }}">View All Patients</a></p>
```

6. Create the MySQL table for storing patient information. Add these lines to your bootstrap script:

```bash
# Create patients table
sudo mysql hospital_queue -e "
CREATE TABLE patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    dob DATE NOT NULL,
    hospital VARCHAR(100) NOT NULL,
    symptoms TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);"
```

7. Update the Gunicorn service file to include the database password as an environment variable. Replace the content of `/etc/systemd/system/hospital_queue.service` with:

```
[Unit]
Description=Gunicorn instance to serve hospital queue application
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/hospital_queue
Environment="PATH=/home/ubuntu/hospital_queue/venv/bin"
Environment="DB_PASSWORD=your_password"
ExecStart=/home/ubuntu/hospital_queue/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 app:app

[Install]
WantedBy=multi-user.target
```

Replace 'your_password' with the actual password you set for the MySQL user.

8. Finally, update the `app.py` file to use the environment variable for the database password:

Replace the `db_config` dictionary with:

```python
db_config = {
    'host': 'localhost',
    'user': 'hospital_user',
    'password': os.environ.get('DB_PASSWORD'),
    'db': 'hospital_queue',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}
```

After making these changes:

1. Restart the Gunicorn service:
   ```
   sudo systemctl restart hospital_queue
   ```

2. Reload Nginx:
   ```
   sudo systemctl reload nginx
   ```

Now your application will store patient information in the MySQL database and display it on the `/patients` page. The main page will have a link to view all patients, and you can navigate back to the home page from the patients list.

Remember to replace 'your_password' with a strong, unique password in all the places it appears in the code.

This setup provides a basic working environment. For a production deployment, you'd want to consider additional security measures, such as:

- Using environment variables for all sensitive information
- Implementing user authentication for the patients list page
- Using HTTPS
- Implementing proper input validation and sanitization
- Regular database backups