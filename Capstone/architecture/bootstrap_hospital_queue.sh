#!/bin/bash

# Logging
exec > >(tee -i /var/log/bootstrap.log)
exec 2>&1

echo "Starting bootstrap script..."

# Update and upgrade the system
sudo apt update && sudo apt upgrade -y
if [ $? -ne 0 ]; then
    echo "Error occurred during system update. Exiting."
    exit 1
fi

# Install required packages
sudo apt install python3 python3-pip python3-venv nginx mysql-server python3-dev default-libmysqlclient-dev build-essential -y
if [ $? -ne 0 ]; then
    echo "Error occurred during package installation. Exiting."
    exit 1
fi

# Create project directory
mkdir -p /home/ubuntu/hospital_queue
cd /home/ubuntu/hospital_queue

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install flask gunicorn requests pymysql
if [ $? -ne 0 ]; then
    echo "Error occurred during Python package installation. Exiting."
    exit 1
fi

# Set environment variables
DB_PASSWORD="your_strong_password_here"
API_ENDPOINT="https://your-api-gateway-url"

echo "DB_PASSWORD=${DB_PASSWORD}" | sudo tee -a /etc/environment
echo "API_ENDPOINT=${API_ENDPOINT}" | sudo tee -a /etc/environment
source /etc/environment

# Create Flask application
cat << EOF > app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import os
import pymysql

app = Flask(__name__)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'hospital_user',
    'password': os.environ.get('DB_PASSWORD'),
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
EOF

# Create templates directory and HTML files
mkdir templates
cat << EOF > templates/index.html
<!DOCTYPE html>
<html>
<head>
    <title>Hospital Queue System</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <h1>Welcome to the Hospital Queue System</h1>
    <h2>Select a Hospital:</h2>
    <ul>
    {% for hospital in hospitals %}
        <li><a href="{{ url_for('form', hospital=hospital) }}">{{ hospital }}</a></li>
    {% endfor %}
    </ul>
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
    <p><a href="{{ url_for('patients') }}">View All Patients</a></p>
</body>
</html>
EOF

cat << EOF > templates/form.html
<!DOCTYPE html>
<html>
<head>
    <title>Patient Information Form</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <h1>Patient Information for {{ hospital }}</h1>
    <form action="{{ url_for('submit') }}" method="post">
        <input type="hidden" name="hospital" value="{{ hospital }}">
        <label for="name">Name:</label>
        <input type="text" id="name" name="name" required><br><br>
        <label for="lastName">Last Name:</label>
        <input type="text" id="lastName" name="lastName" required><br><br>
        <label for="dob">Date of Birth:</label>
        <input type="date" id="dob" name="dob" required><br><br>
        <label for="symptoms">Symptoms:</label>
        <textarea id="symptoms" name="symptoms" required></textarea><br><br>
        <input type="submit" value="Submit">
    </form>
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>
EOF

cat << EOF > templates/result.html
<!DOCTYPE html>
<html>
<head>
    <title>Queue Position</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <h1>Your Queue Information</h1>
    <p>Your unique ID: {{ result.userId }}</p>
    <p>Your queue position: {{ result.queuePosition }}</p>
    <button onclick="checkAlternatives()">Check Other Hospitals</button>
    <div id="alternatives"></div>
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>
EOF

cat << EOF > templates/patients.html
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
EOF

# Create static directory and files
mkdir -p static/css static/js
touch static/css/style.css
cat << EOF > static/js/script.js
function checkAlternatives() {
    fetch('/check_queues')
        .then(response => response.json())
        .then(data => {
            let alternativesDiv = document.getElementById('alternatives');
            alternativesDiv.innerHTML = '<h2>Alternative Hospitals:</h2>';
            for (let hospital in data) {
                alternativesDiv.innerHTML += `<p>${hospital}: ${data[hospital]} in queue</p>`;
            }
        });
}
EOF

# Configure Nginx
sudo tee /etc/nginx/sites-available/hospital_queue << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/hospital_queue /etc/nginx/sites-enabled
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
if [ $? -ne 0 ]; then
    echo "Error occurred during Nginx configuration. Exiting."
    exit 1
fi

# Create systemd service for Gunicorn
sudo tee /etc/systemd/system/hospital_queue.service << EOF
[Unit]
Description=Gunicorn instance to serve hospital queue application
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/hospital_queue
Environment="PATH=/home/ubuntu/hospital_queue/venv/bin"
Environment="DB_PASSWORD=${DB_PASSWORD}"
Environment="API_ENDPOINT=${API_ENDPOINT}"
ExecStart=/home/ubuntu/hospital_queue/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 app:app

[Install]
WantedBy=multi-user.target
EOF

# Create database and user
sudo mysql -e "CREATE DATABASE hospital_queue;"
sudo mysql -e "CREATE USER 'hospital_user'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';"
sudo mysql -e "GRANT ALL PRIVILEGES ON hospital_queue.* TO 'hospital_user'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"
if [ $? -ne 0 ]; then
    echo "Error occurred during database setup. Exiting."
    exit 1
fi

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
if [ $? -ne 0 ]; then
    echo "Error occurred during table creation. Exiting."
    exit 1
fi

# Set correct permissions
sudo chown -R ubuntu:ubuntu /home/ubuntu/hospital_queue

# Start and enable Gunicorn service
sudo systemctl start hospital_queue
sudo systemctl enable hospital_queue
if [ $? -ne 0 ]; then
    echo "Error occurred while starting Gunicorn service. Exiting."
    exit 1
fi

# Set up firewall
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable
if [ $? -ne 0 ]; then
    echo "Error occurred during firewall setup. Exiting."
    exit 1
fi

# Set up automatic security updates
sudo apt install unattended-upgrades -y
echo "Unattended-Upgrade::Allowed-Origins {
    \"\${distro_id}:\${distro_codename}\";
    \"\${distro_id}:\${distro_codename}-security\";
    \"\${distro_id}ESM:\${distro_codename}\";
};
Unattended-Upgrade::AutoFixInterruptedDpkg \"true\";
Unattended-Upgrade::MinimalSteps \"true\";
Unattended-Upgrade::InstallOnShutdown \"false\";
Unattended-Upgrade::Remove-Unused-Dependencies \"true\";
Unattended-Upgrade::Automatic-Reboot \"false\";" | sudo tee /etc/apt/apt.conf.d/50unattended-upgrades

# Install and configure Fail2Ban
sudo apt install fail2ban -y
sudo systemctl start fail2ban
sudo systemctl enable fail2ban
if [ $? -ne 0 ]; then
    echo "Error occurred during Fail2Ban setup. Exiting."
    exit 1
fi

echo "Setup completed successfully!"