Certainly! Here's a complete, updated bootstrap script incorporating all the changes and improvements we discussed:

```bash
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
pip install flask gunicorn requests pymysql cryptography boto3
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
from flask import Flask, render_template, request, current_app, jsonify, redirect, url_for, flash, session
import requests
import os
import pymysql
import json
from datetime import datetime, date
import re
import logging
import boto3
from botocore.exceptions import NoCredentialsError


app = Flask(__name__, static_url_path='/static')
app.secret_key = os.urandom(24)  # Required for flashing messages
logging.basicConfig(filename='app.log', level=logging.DEBUG)

@app.errorhandler(Exception)
def handle_exception(e):
    return render_template('error.html', error_message=str(e)), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_message="Page not found"), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', error_message="Access forbidden"), 403

s3 = boto3.client('s3')

hospitals = [
    {'name': 'Hospital A', 'image': 'https://mcit-capstone-hospital-queue-app-test.s3.amazonaws.com/hospital-index-page-images/hospital_a.jpg'},
    {'name': 'Hospital B', 'image': 'https://mcit-capstone-hospital-queue-app-test.s3.amazonaws.com/hospital-index-page-images/hospital_b.jpg'},
    {'name': 'Hospital C', 'image': 'https://mcit-capstone-hospital-queue-app-test.s3.amazonaws.com/hospital-index-page-images/hospital_c.jpg'}
]

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

# Function to get or reset the counter
def get_daily_counter():
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            # Check if we need to reset the counter
            cursor.execute("SELECT value, date FROM daily_counter WHERE id = 1")
            result = cursor.fetchone()
            today = date.today()
            
            if result is None or result['date'] != today:
                # Reset or initialize the counter
                cursor.execute(
                    "INSERT INTO daily_counter (id, value, date) VALUES (1, 1, %s) "
                    "ON DUPLICATE KEY UPDATE value = 1, date = %s",
                    (today, today)
                )
                connection.commit()
                return 1
            else:
                # Increment the counter
                new_value = result['value'] + 1
                cursor.execute(
                    "UPDATE daily_counter SET value = %s WHERE id = 1",
                    (new_value,)
                )
                connection.commit()
                return new_value

# Insert the calculate_estimated_waiting_time function
def calculate_estimated_waiting_time(queue_number):
    # Simple estimation: 15 minutes per person in queue
    return queue_number * 15

@app.route('/check_session')
def check_session():
    return jsonify(dict(session))

@app.route('/')
def index():
    return render_template('index.html', hospitals=hospitals)

@app.route('/form/<hospital>')
def form(hospital):
    available_slots = get_available_slots(hospital)
    return render_template('form.html', hospital=hospital, available_slots=available_slots)

def get_available_slots(hospital):
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, slot_time 
                FROM time_slots 
                WHERE date = CURDATE() AND hospital = %s AND booked < 10
                AND slot_time BETWEEN '18:00' AND '22:00'
            """, (hospital,))
            return cursor.fetchall()

def validate_phone_number(phone_number):
    pattern = re.compile(r'^\+?1?\d{9,15}$')
    return pattern.match(phone_number) is not None

def validate_date(date_string):
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

@app.route('/submit', methods=['POST'])
def submit():
    logging.debug("Submit route accessed")
    data = request.form.to_dict()
    logging.debug(f"Received form data: {data}")
    
    try:
        logging.debug("Attempting to get daily counter")
        queue_number = get_daily_counter()
        logging.debug(f"Queue number assigned: {queue_number}")
        
        logging.debug("Checking if queue is full")
        if queue_number > 20:
            logging.debug("Queue is full, redirecting to index")
            flash('We are full, please check back later.', 'error')
            return redirect(url_for('index'))
        
        logging.debug("Attempting to book time slot")
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE time_slots SET booked = booked + 1 WHERE id = %s", (data['time_slot'],))
                if cursor.rowcount == 0:
                    logging.debug("Time slot no longer available")
                    flash('The selected time slot is no longer available. Please try again.', 'error')
                    return redirect(url_for('form', hospital=data['hospital']))
            
            logging.debug("Inserting patient data")
            with connection.cursor() as cursor:
                sql = """INSERT INTO patients 
                         (name, last_name, dob, hospital, symptoms, queue_number, time_slot_id, status,
                          emergency_contact_name, emergency_contact_phone, insurance_provider,
                          insurance_policy_number, payment_method, appointment_type, estimated_waiting_time) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, 'in_queue', %s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (
                    data['name'], data['lastName'], data['dob'], data['hospital'], data['symptoms'],
                    queue_number, data['time_slot'], data['emergency_contact_name'],
                    data['emergency_contact_phone'], data.get('insurance_provider', ''),
                    data.get('insurance_policy_number', ''), data['payment_method'],
                    data['appointment_type'], calculate_estimated_waiting_time(queue_number)
                ))
            connection.commit()
        logging.debug(f"Patient data inserted successfully. Queue number: {queue_number}")

        logging.debug("Storing queue number in session")
        session['queue_number'] = queue_number
        session['hospital'] = data['hospital']
        
        logging.debug("Redirecting to patients")
        return redirect(url_for('patients'))
    
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        logging.error(error_message)
        logging.error(f"Exception details: {str(e)}")
        logging.error(f"Exception type: {type(e).__name__}")
        logging.error(f"Exception args: {e.args}")
        flash(error_message, 'error')
    
    logging.debug("Rendering form template")
    return render_template('form.html', hospital=data['hospital'])

@app.route('/queue_info')
def queue_info():
    queue_number = session.get('queue_number')
    hospital = session.get('hospital')
    if queue_number and hospital:
        estimated_time = calculate_estimated_waiting_time(queue_number)
        return render_template('queue_info.html', queue_number=queue_number, hospital=hospital, estimated_time=estimated_time)
    else:
        return redirect(url_for('index'))
    
@app.route('/update_status/<int:patient_id>', methods=['POST'])
def update_status(patient_id):
    new_status = request.form.get('status')
    if new_status not in ['checked_in', 'in_progress', 'checked_out']:
        return jsonify({'error': 'Invalid status'}), 400

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                if new_status == 'checked_in':
                    cursor.execute("UPDATE patients SET status = %s, check_in_time = NOW() WHERE id = %s", (new_status, patient_id))
                else:
                    cursor.execute("UPDATE patients SET status = %s WHERE id = %s", (new_status, patient_id))
                connection.commit()

        if new_status == 'checked_out':
            # Decrement queue numbers and update estimated waiting times for patients still in queue
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE patients 
                        SET queue_number = queue_number - 1,
                            estimated_waiting_time = GREATEST(estimated_waiting_time - 15, 0)
                        WHERE status = 'in_queue' AND queue_number > (
                            SELECT queue_number FROM (
                                SELECT queue_number FROM patients WHERE id = %s
                            ) AS subquery
                        )
                    """, (patient_id,))
                    connection.commit()

        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/check_queues')
def check_queues():
    try:
        # Make API call to Lambda function to get queue status from DynamoDB
        response = requests.get(f"{API_ENDPOINT}/check_queues")
        queues = response.json()
        return jsonify(queues)
    except Exception as e:
        error_message = f"Error checking queues: {e}"
        app.logger.error(error_message)
        return jsonify({'error': error_message}), 500

@app.route('/update_payment_status/<int:patient_id>', methods=['POST'])
def update_payment_status(patient_id):
    new_payment_status = request.form.get('payment_status')
    if new_payment_status not in ['pending', 'completed', 'not_required']:
        return jsonify({'error': 'Invalid payment status'}), 400

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE patients SET payment_status = %s WHERE id = %s", (new_payment_status, patient_id))
                connection.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test_db')
def test_db():
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
        return "Database connection successful"
    except Exception as e:
        return f"Database connection failed: {str(e)}"

@app.route('/patients')
def patients():
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, queue_number, name, last_name, hospital, status, 
                           appointment_type, payment_method, payment_status, estimated_waiting_time
                    FROM patients 
                    ORDER BY queue_number
                """)
                patients = cursor.fetchall()
        return render_template('patients.html', patients=patients)
    except Exception as e:
        flash(f"Error retrieving patients: {e}", 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
EOF

# Create database and user
sudo mysql -e "CREATE DATABASE IF NOT EXISTS hospital_queue;"
sudo mysql -e "CREATE USER IF NOT EXISTS 'hospital_user'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';"
sudo mysql -e "GRANT ALL PRIVILEGES ON hospital_queue.* TO 'hospital_user'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"

# Create and modify tables with index addition
sudo mysql hospital_queue << EOF
-- Create patients table if not exists
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    dob DATE NOT NULL,
    hospital VARCHAR(100) NOT NULL,
    symptoms TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    queue_number INT,
    time_slot_id INT,
    status ENUM('in_queue', 'checked_in', 'in_progress', 'checked_out') DEFAULT 'in_queue',
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(15),
    insurance_provider VARCHAR(100),
    insurance_policy_number VARCHAR(50),
    payment_method ENUM('cash', 'credit_card', 'insurance') DEFAULT 'insurance',
    payment_status ENUM('pending', 'completed', 'not_required') DEFAULT 'pending',
    appointment_type ENUM('consultation', 'follow-up', 'emergency') DEFAULT 'consultation',
    check_in_time TIMESTAMP NULL,
    estimated_waiting_time INT  -- in minutes
);

-- Create daily_counter table if not exists
CREATE TABLE IF NOT EXISTS daily_counter (
    id INT PRIMARY KEY,
    value INT,
    date DATE
);

-- Create time_slots table if not exists
CREATE TABLE IF NOT EXISTS time_slots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    slot_time TIME,
    date DATE,
    hospital VARCHAR(100),
    booked INT DEFAULT 0
);

-- Initialize time slots (you may want to adjust this based on your needs)
INSERT IGNORE INTO time_slots (slot_time, date, hospital)
SELECT time_slot, CURDATE() + INTERVAL day DAY, hospital
FROM (
    SELECT 0 AS day UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6
) AS days
CROSS JOIN (
    SELECT '18:00' AS time_slot UNION SELECT '18:30' UNION SELECT '19:00' UNION
    SELECT '19:30' UNION SELECT '20:00' UNION SELECT '20:30' UNION
    SELECT '21:00' UNION SELECT '21:30' UNION SELECT '22:00'
) AS times
CROSS JOIN (
    SELECT 'Hospital A' AS hospital UNION SELECT 'Hospital B' UNION SELECT 'Hospital C'
) AS hospitals;

-- Add an index to the queue_number column in the patients table
ALTER TABLE patients ADD INDEX idx_queue_number (queue_number);

-- Show the index for verification
SHOW INDEX FROM patients;
EOF

if [ $? -ne 0 ]; then
    echo "Error occurred during MySQL setup. Exiting."
    exit 1
fi

# Create templates directory and HTML files
mkdir templates
cat << EOF > templates/index.html
<!DOCTYPE html>
<html>
<head>
    <title>Hospital Queue System</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
</head>
<body>
    <div class="hero">
        <div class="header">
            <h1>Welcome to the Hospital Queue System</h1>
        </div>
        <h2>Select a Hospital:</h2>
        <div class="dropdown">
            <button class="dropbtn" onclick="toggleDropdown()">Choose Hospital</button>
            <div id="hospitalDropdown" class="dropdown-content">
                {% for hospital in hospitals %}
                    <a href="{{ url_for('form', hospital=hospital.name) }}">
                        <img src="{{ hospital.image }}" alt="{{ hospital.name }}" class="hospital-image">
                        {{ hospital.name }}
                    </a>
                {% endfor %}
            </div>
        </div>
        <p><a href="{{ url_for('patients') }}">View All Patients</a></p>
    </div>
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>
EOF

cat << EOF > templates/form.html
<!DOCTYPE html>
<html>
<head>
    <title>Patient Information Form</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
</head>
<body>
    <div class="container">
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
            <label for="emergency_contact_name">Emergency Contact Name:</label>
            <input type="text" id="emergency_contact_name" name="emergency_contact_name" required><br><br>
            <label for="emergency_contact_phone">Emergency Contact Phone:</label>
            <input type="tel" id="emergency_contact_phone" name="emergency_contact_phone" required><br><br>
            <label for="insurance_provider">Insurance Provider:</label>
            <input type="text" id="insurance_provider" name="insurance_provider"><br><br>
            <label for="insurance_policy_number">Insurance Policy Number:</label>
            <input type="text" id="insurance_policy_number" name="insurance_policy_number"><br><br>
            <label for="payment_method">Payment Method:</label>
            <select id="payment_method" name="payment_method" required>
                <option value="insurance">Insurance</option>
                <option value="cash">Cash</option>
                <option value="credit_card">Credit Card</option>
            </select><br><br>
            <label for="appointment_type">Appointment Type:</label>
            <select id="appointment_type" name="appointment_type" required>
                <option value="consultation">Consultation</option>
                <option value="follow-up">Follow-up</option>
                <option value="emergency">Emergency</option>
            </select><br><br>
            <label for="time_slot">Preferred Time Slot:</label>
            <select id="time_slot" name="time_slot" required>
                {% for slot in available_slots %}
                    <option value="{{ slot.id }}">{{ slot.slot_time }}</option>
                {% endfor %}
            </select><br><br>
            <input type="submit" value="Submit">
        </form>
    </div>
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>
EOF

cat << EOF > templates/queue_info.html
<!DOCTYPE html>
<html>
<head>
    <title>Queue Information</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
</head>
<body>
    <div class="container">
        <h1>Thank you for coming to {{ hospital }}</h1>
        <p>You are currently number {{ queue_number }} in the queue.</p>
        <p>Your estimated waiting time is approximately {{ estimated_time }} minutes.</p>
        <p>Please wait for your number to be called.</p>
        <a href="{{ url_for('index') }}">Back to Home</a>
    </div>
</body>
</html>
EOF

cat << EOF > templates/patients.html
<!DOCTYPE html>
<html>
<head>
    <title>Patient List</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
</head>
<body>
    <div class="container">
        <h1>Patient List</h1>
        <table>
            <tr>
                <th>Queue Number</th>
                <th>Name</th>
                <th>Last Name</th>
                <th>Hospital</th>
                <th>Status</th>
                <th>Appointment Type</th>
                <th>Payment Method</th>
                <th>Payment Status</th>
                <th>Estimated Waiting Time</th>
                <th>Actions</th>
            </tr>
            {% for patient in patients %}
            <tr>
                <td>{{ patient.queue_number }}</td>
                <td>{{ patient.name }}</td>
                <td>{{ patient.last_name }}</td>
                <td>{{ patient.hospital }}</td>
                <td>{{ patient.status }}</td>
                <td>{{ patient.appointment_type }}</td>
                <td>{{ patient.payment_method }}</td>
                <td>
                    <select class="payment-status-select" data-patient-id="{{ patient.id }}">
                        <option value="pending" {% if patient.payment_status == 'pending' %}selected{% endif %}>Pending</option>
                        <option value="completed" {% if patient.payment_status == 'completed' %}selected{% endif %}>Completed</option>
                        <option value="not_required" {% if patient.payment_status == 'not_required' %}selected{% endif %}>Not Required</option>
                    </select>
                </td>
                <td>{{ patient.estimated_waiting_time }} minutes</td>
                <td>
                    <select class="status-select" data-patient-id="{{ patient.id }}">
                        <option value="in_queue" {% if patient.status == 'in_queue' %}selected{% endif %}>In Queue</option>
                        <option value="checked_in" {% if patient.status == 'checked_in' %}selected{% endif %}>Checked In</option>
                        <option value="in_progress" {% if patient.status == 'in_progress' %}selected{% endif %}>In Progress</option>
                        <option value="checked_out" {% if patient.status == 'checked_out' %}selected{% endif %}>Checked Out</option>
                    </select>
                </td>
            </tr>
            {% endfor %}
        </table>
        <a href="{{ url_for('index') }}">Back to Home</a>
    </div>
    <script src="{{ url_for('static', filename='js/patients.js') }}"></script>
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>
EOF

EOF

cat << EOF > /home/ubuntu/hospital_queue/templates/error.html
<!DOCTYPE html>
<html>
<head>
    <title>Error</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <h1>An error occurred</h1>
    <p>{{ error_message }}</p>
    <a href="{{ url_for('index') }}">Back to Home</a>
</body>
</html>
EOF

# Create static directory and files
mkdir -p static/css static/js
touch static/css/style.css

# Create and populate script.js
cat << 'EOF' > static/js/script.js
function toggleDropdown() {
    document.getElementById("hospitalDropdown").classList.toggle("show");
}

window.onclick = function(event) {
    if (!event.target.matches('.dropbtn')) {
        var dropdowns = document.getElementsByClassName("dropdown-content");
        for (var i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
}

// Add more JavaScript functions as needed
EOF

# Create and populate patients.js
cat << EOF > static/js/patients.js
$(document).ready(function() {
    $('.status-select, .payment-status-select').change(function() {
        var $this = $(this);
        var patientId = $this.data('patient-id');
        var url = $this.hasClass('status-select') ? '/update_status/' : '/update_payment_status/';
        var dataKey = $this.hasClass('status-select') ? 'status' : 'payment_status';
        var postData = {};
        postData[dataKey] = $this.val();

        $.post(url + patientId, postData, function(response) {
            if (response.success) {
                alert(dataKey.charAt(0).toUpperCase() + dataKey.slice(1) + ' updated successfully');
                if (dataKey === 'status' && postData.status === 'checked_out') {
                    location.reload(); // Reload the page to update queue numbers and estimated waiting times
                }
            } else {
                alert('Error updating ' + dataKey + ': ' + response.error);
            }
        });
    });
});
EOF

# Create and populate style.css with the new styles
cat << EOF > static/css/style.css
/* Existing styles */
body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 20px;
}

h1 {
    color: #333;
}

.container {
    max-width: 800px;
    margin: auto;
}

/* New styles */
.alert {
    padding: 10px;
    margin-bottom: 15px;
    border: 1px solid transparent;
    border-radius: 4px;
}

.alert-success {
    color: #3c763d;
    background-color: #dff0d8;
    border-color: #d6e9c6;
}

.alert-error {
    color: #a94442;
    background-color: #f2dede;
    border-color: #ebccd1;
}

.header {
    background-position-x: left;
    color: black;
    font-size: 15px;
    border-radius: 20px;
}

.hero {
    width: 100%;
    min-height: 100vh;
    background-image: url(/static/images/image-hospital.avif);
    background-position: center;
    background-size: cover;
    padding: 10px 10%;
    overflow: hidden;
}

/* Dropdown Button */
.dropbtn {
    background-color: #3498DB;
    color: white;
    padding: 16px;
    font-size: 16px;
    border: none;
    cursor: pointer;
}

/* Dropdown button on hover & focus */
.dropbtn:hover, .dropbtn:focus {
    background-color: #2980B9;
}

/* The container <div> - needed to position the dropdown content */
.dropdown {
    position: relative;
    display: inline-block;
}

/* Dropdown Content (Hidden by Default) */
.dropdown-content a {
    color: black;
    padding: 12px 16px;
    text-decoration: none;
    display: block;
}

/* Links inside the dropdown */
.dropdown-content a {
    color: black;
    padding: 12px 16px;
    text-decoration: none;
    display: block;
}

/* Change color of dropdown links on hover */
.dropdown-content a:hover {
    background-color: #ddd;
}

/* Show the dropdown menu */
.show {
    display:block;
}

.dropdown-content a {
    display: flex;
    align-items: center;
    padding: 10px;
}
.hospital-image {
    width: 50px;
    height: 50px;
    margin-right: 10px;
    object-fit: cover;
    border-radius: 5px;
}
.dropdown-content {
    display: none;
    position: absolute;
    background-color: #f1f1f1;
    box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
    z-index: 1;
}
.dropbtn:hover .dropdown-content {
    display: block;
}
EOF

# Create static directory and js subdirectory
mkdir -p /home/ubuntu/hospital_queue/static/js

# Create and populate script.js
cat << EOF > /home/ubuntu/hospital_queue/static/js/script.js
console.log('Script loaded');

// Add more JavaScript functions as needed
EOF

# Set correct permissions for script.js
chmod 644 /home/ubuntu/hospital_queue/static/js/script.js

# Ensure the ubuntu user owns the file
chown ubuntu:ubuntu /home/ubuntu/hospital_queue/static/js/script.js

# Log the creation of the file
echo "script.js has been created and populated in /home/ubuntu/hospital_queue/static/js/"

# Configure Nginx
sudo tee /etc/nginx/sites-available/hospital_queue << 'EOF'
server {
    listen 80;
    server_name _;

    # Updated Content Security Policy
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://code.jquery.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' https://mcit-capstone-hospital-queue-app-test.s3.amazonaws.com;";

    location / {
        try_files \$uri @proxy_to_app;
    }

    location @proxy_to_app {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location /static {
        alias /home/ubuntu/hospital_queue/static;
        autoindex off;
        expires max;
        add_header Cache-Control public;
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
ExecStart=/home/ubuntu/hospital_queue/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 --timeout 120 app:app


[Install]
WantedBy=multi-user.target
EOF

# After creating the service file, reload the systemd daemon
sudo systemctl daemon-reload

# Create database and user
sudo mysql -e "CREATE DATABASE IF NOT EXISTS hospital_queue;"
sudo mysql -e "CREATE USER IF NOT EXISTS 'hospital_user'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';"
sudo mysql -e "GRANT ALL PRIVILEGES ON hospital_queue.* TO 'hospital_user'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"

# Bootstrap script to set up MySQL database tables
sudo mysql hospital_queue << EOF
-- Create patients table if not exists
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    dob DATE NOT NULL,
    hospital VARCHAR(100) NOT NULL,
    symptoms TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    queue_number INT,
    time_slot_id INT,
    status ENUM('in_queue', 'checked_in', 'in_progress', 'checked_out') DEFAULT 'in_queue',
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(15),
    insurance_provider VARCHAR(100),
    insurance_policy_number VARCHAR(50),
    payment_method ENUM('cash', 'credit_card', 'insurance') DEFAULT 'insurance',
    payment_status ENUM('pending', 'completed', 'not_required') DEFAULT 'pending',
    appointment_type ENUM('consultation', 'follow-up', 'emergency') DEFAULT 'consultation',
    check_in_time TIMESTAMP,
    estimated_waiting_time INT  -- in minutes
);

-- Create daily_counter table if not exists
CREATE TABLE IF NOT EXISTS daily_counter (
    id INT PRIMARY KEY,
    value INT,
    date DATE
);

-- Create time_slots table if not exists
CREATE TABLE IF NOT EXISTS time_slots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    slot_time TIME,
    date DATE,
    hospital VARCHAR(100),
    booked INT DEFAULT 0
);

-- Initialize time slots
INSERT IGNORE INTO time_slots (slot_time, date, hospital)
SELECT time_slot, date, hospital
FROM (
    SELECT '18:00' AS time_slot UNION SELECT '18:30' UNION SELECT '19:00' UNION
    SELECT '19:30' UNION SELECT '20:00' UNION SELECT '20:30' UNION
    SELECT '21:00' UNION SELECT '21:30' UNION SELECT '22:00'
) AS times
CROSS JOIN (
    SELECT 'Hospital A' AS hospital UNION SELECT 'Hospital B' UNION SELECT 'Hospital C'
) AS hospitals
CROSS JOIN (
    SELECT CURDATE() + INTERVAL a DAY AS date
    FROM (SELECT 0 a UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6) AS days
) AS dates;

EOF

# Check for errors in the execution of the MySQL commands
if [ $? -ne 0 ]; then
    echo "Warning: An error occurred during MySQL setup. This may be due to existing database or tables."
    echo "Continuing with the script execution..."
fi

# Create directory for hospital images
mkdir -p /home/ubuntu/hospital_queue/static/images/hospitals
chmod 755 /home/ubuntu/hospital_queue/static/images/hospitals

# Set correct permissions
chown -R ubuntu:ubuntu /home/ubuntu/hospital_queue/static/images

# Set correct permissions
sudo chown -R ubuntu:ubuntu /home/ubuntu/hospital_queue
sudo chmod -R 755 /home/ubuntu/hospital_queue/static
sudo chown -R ubuntu:www-data /home/ubuntu/hospital_queue/static
sudo chmod -R +x /home/ubuntu /home/ubuntu/hospital_queue

# Create log file with correct permissions
sudo touch /home/ubuntu/hospital_queue/app.log
sudo chown ubuntu:ubuntu /home/ubuntu/hospital_queue/app.log
sudo chmod 666 /home/ubuntu/hospital_queue/app.log

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

# Ensure the Gunicorn service is started and enabled
sudo systemctl start hospital_queue
sudo systemctl enable hospital_queue
if [ $? -ne 0 ]; then
    echo "Warning: An issue occurred while starting Gunicorn service, but continuing..." >&2
fi

# Enable the Nginx configuration
sudo ln -sf /etc/nginx/sites-available/hospital_queue /etc/nginx/sites-enabled/

# Final check and restart of Nginx
sudo nginx -t && sudo systemctl restart nginx
if [ $? -ne 0 ]; then
    echo "Warning: An issue occurred with Nginx configuration or restart, but continuing..." >&2
fi

echo "Setup completed. Please check the logs for any warnings or errors."
```

Before using this script:

1. Replace `your_strong_password_here` with an actual strong password for your database.
2. Replace `https://your-api-gateway-url` with your actual API Gateway URL.

To use this script:

1. Save it as a file, e.g., `bootstrap_hospital_queue.sh`
2. Make it executable: `chmod +x bootstrap_hospital_queue.sh`
3. Run it with sudo: `sudo ./bootstrap_hospital_queue.sh`

This script includes error checking and logging, which will help you identify any issues if they occur. The log file will be created at `/var/log/bootstrap.log`.

After running the script, your application should be accessible via your EC2 instance's public IP address. If you encounter any issues, check the log file and the status of your services (Nginx, MySQL, and the Gunicorn service) for more information.