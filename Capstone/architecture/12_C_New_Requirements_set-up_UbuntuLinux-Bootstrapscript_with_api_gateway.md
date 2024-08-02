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
pip install flask gunicorn requests pymysql cryptography
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
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import requests
import os
import pymysql
import json
from datetime import datetime, date
import re
import logging


app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for flashing messages
logging.basicConfig(filename='app.log', level=logging.DEBUG)

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

@app.route('/')
def index():
    hospitals = ['Hospital A', 'Hospital B', 'Hospital C']
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
    required_fields = ['name', 'lastName', 'dob', 'hospital', 'symptoms', 'emergency_contact_name', 
                       'emergency_contact_phone', 'payment_method', 'appointment_type', 'time_slot']
    
    # Check if all required fields are present
    for field in required_fields:
        if field not in data:
            flash(f'Missing required field: {field}', 'error')
            return redirect(url_for('form', hospital=data.get('hospital', '')))
    
    # Validate input
    if not validate_date(data['dob']):
        flash('Invalid date of birth format. Please use YYYY-MM-DD.', 'error')
        return redirect(url_for('form', hospital=data['hospital']))
    
    if not validate_phone_number(data['emergency_contact_phone']):
        flash('Invalid phone number format.', 'error')
        return redirect(url_for('form', hospital=data['hospital']))
    
    try:
        queue_number = get_daily_counter()
        
        # Check if queue is full
        if queue_number > 20:
            flash('We are full, please check back later.', 'error')
            return redirect(url_for('index'))
        
        # Book the time slot
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE time_slots SET booked = booked + 1 WHERE id = %s", (data['time_slot'],))
                if cursor.rowcount == 0:
                    flash('The selected time slot is no longer available. Please try again.', 'error')
                    return redirect(url_for('form', hospital=data['hospital']))
            
            # Store patient data
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

        # Store queue number in session
        session['queue_number'] = queue_number
        session['hospital'] = data['hospital']
        
        # Redirect to a new page showing the queue number
        return redirect(url_for('queue_info'))
    
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        logging.error(error_message)
        logging.error(f"Exception details: {str(e)}")
        logging.error(f"Exception type: {type(e).__name__}")
        logging.error(f"Exception args: {e.args}")
        flash(error_message, 'error')
    
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

# Create and modify tables
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
    <script>
        $(document).ready(function() {
            $('.status-select').change(function() {
                var patientId = $(this).data('patient-id');
                var newStatus = $(this).val();
                $.post('/update_status/' + patientId, {status: newStatus}, function(response) {
                    if (response.success) {
                        alert('Status updated successfully');
                        if (newStatus === 'checked_out') {
                            location.reload(); // Reload the page to update queue numbers and estimated waiting times
                        }
                    } else {
                        alert('Error updating status: ' + response.error);
                    }
                });
            });

            $('.payment-status-select').change(function() {
                var patientId = $(this).data('patient-id');
                var newPaymentStatus = $(this).val();
                $.post('/update_payment_status/' + patientId, {payment_status: newPaymentStatus}, function(response) {
                    if (response.success) {
                        alert('Payment status updated successfully');
                    } else {
                        alert('Error updating payment status: ' + response.error);
                    }
                });
            });
        });
    </script>
</body>
</html>
EOF

# Create static directory and files
mkdir -p static/css static/js
touch static/css/style.css

# Create and populate script.js
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

# Create and populate style.css with the new styles
cat << EOF > static/css/style.css
/* Reset and base styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Roboto', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f5f7fa;
}

.container {
    width: 90%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

/* Typography */
h1, h2, h3 {
    margin-bottom: 0.5em;
    color: #2c3e50;
}

h1 {
    font-size: 2.5em;
    font-weight: 700;
}

h2 {
    font-size: 2em;
    font-weight: 600;
}

a {
    color: #3498db;
    text-decoration: none;
    transition: color 0.3s ease;
}

a:hover {
    color: #2980b9;
    text-decoration: underline;
}

/* Header */
header {
    background: linear-gradient(135deg, #3498db, #2c3e50);
    color: #fff;
    padding: 1em 0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

header h1 {
    text-align: center;
    margin: 0;
}

/* Navigation */
nav {
    background-color: #34495e;
    padding: 0.5em 0;
}

nav ul {
    list-style-type: none;
    display: flex;
    justify-content: center;
}

nav ul li {
    margin: 0 1em;
}

nav ul li a {
    color: #ecf0f1;
    font-weight: 500;
}

/* Forms */
form {
    background: #fff;
    padding: 2em;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-bottom: 2em;
}

form label {
    display: block;
    margin-bottom: 0.5em;
    font-weight: 500;
    color: #2c3e50;
}

form input[type="text"],
form input[type="date"],
form textarea {
    width: 100%;
    padding: 0.8em;
    margin-bottom: 1em;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    font-size: 1em;
    transition: border-color 0.3s ease;
}

form input[type="text"]:focus,
form input[type="date"]:focus,
form textarea:focus {
    border-color: #3498db;
    outline: none;
}

form textarea {
    height: 150px;
    resize: vertical;
}

form input[type="submit"] {
    background: #3498db;
    color: #fff;
    border: none;
    padding: 0.8em 1.5em;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1em;
    font-weight: 500;
    transition: background-color 0.3s ease;
}

form input[type="submit"]:hover {
    background: #2980b9;
}

/* Lists */
ul {
    list-style-type: none;
}

ul li {
    background: #fff;
    margin-bottom: 1em;
    padding: 1em;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: box-shadow 0.3s ease;
}

ul li:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

/* Buttons */
button {
    background: #3498db;
    color: #fff;
    border: none;
    padding: 0.8em 1.5em;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1em;
    font-weight: 500;
    transition: background-color 0.3s ease;
}

button:hover {
    background: #2980b9;
}

/* Result Section */
#alternatives {
    background: #fff;
    padding: 1.5em;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    margin-top: 1.5em;
}

#alternatives h2 {
    margin-top: 0;
    color: #2c3e50;
}

#alternatives p {
    margin: 0.5em 0;
    font-size: 1em;
    color: #34495e;
}

/* Alerts */
.alert {
    padding: 1em;
    margin-bottom: 1em;
    border: 1px solid transparent;
    border-radius: 4px;
    font-weight: 500;
}

.alert-success {
    color: #155724;
    background-color: #d4edda;
    border-color: #c3e6cb;
}

.alert-error {
    color: #721c24;
    background-color: #f8d7da;
    border-color: #f5c6cb;
}

/* Responsive Design */
@media (max-width: 768px) {
    .container {
        width: 95%;
    }

    form {
        padding: 1.5em;
    }

    nav ul {
        flex-direction: column;
        align-items: center;
    }

    nav ul li {
        margin: 0.5em 0;
    }
}

/* Accessibility */
:focus {
    outline: 3px solid #3498db;
    outline-offset: 2px;
}

/* Print styles */
@media print {
    body {
        font-size: 12pt;
    }

    header, nav, form input[type="submit"], button {
        display: none;
    }

    a {
        text-decoration: underline;
    }
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

# Ensure the Gunicorn service is started and enabled
sudo systemctl start hospital_queue
sudo systemctl enable hospital_queue
if [ $? -ne 0 ]; then
    echo "Warning: An issue occurred while starting Gunicorn service, but continuing..." >&2
fi

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