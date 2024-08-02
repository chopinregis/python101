Certainly! I'll guide you through implementing these new requirements step by step. We'll need to modify both the backend (Flask application) and the frontend (HTML templates and JavaScript).

1. Add a counter column to the database:

First, let's add a new column to your MySQL database:

```sql
ALTER TABLE patients ADD COLUMN queue_number INT;
```

2. Modify the Flask application (`app.py`):

```python
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import pymysql
import os
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ... (keep existing configurations)

# Add this function to get or reset the counter
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

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.to_dict()
    
    try:
        queue_number = get_daily_counter()
        
        # Check if queue is full
        if queue_number > 20:
            flash('We are full, please check back later.', 'error')
            return redirect(url_for('index'))
        
        # Store data in MySQL
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                sql = """INSERT INTO patients 
                         (name, last_name, dob, hospital, symptoms, queue_number) 
                         VALUES (%s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (data['name'], data['lastName'], data['dob'], 
                                     data['hospital'], data['symptoms'], queue_number))
            connection.commit()
        
        # Store queue number in session
        session['queue_number'] = queue_number
        session['hospital'] = data['hospital']
        
        # Redirect to a new page showing the queue number
        return redirect(url_for('queue_info'))
    
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        app.logger.error(error_message)
        flash(error_message, 'error')
    
    return render_template('form.html', hospital=data['hospital'])

@app.route('/queue_info')
def queue_info():
    queue_number = session.get('queue_number')
    hospital = session.get('hospital')
    if queue_number and hospital:
        return render_template('queue_info.html', queue_number=queue_number, hospital=hospital)
    else:
        return redirect(url_for('index'))

# ... (keep other routes and configurations)
```

3. Create a new template `queue_info.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Queue Information</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <h1>Thank you for coming to {{ hospital }}</h1>
        <p>You are currently number {{ queue_number }} in the queue.</p>
        <a href="{{ url_for('index') }}">Back to Home</a>
    </div>
</body>
</html>
```

4. Modify the `patients.html` template to hide the queue number column:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Patient List</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <style>
        .hidden {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Patient List</h1>
        <table>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Last Name</th>
                <th>Date of Birth</th>
                <th>Hospital</th>
                <th>Symptoms</th>
                <th class="hidden">Queue Number</th>
            </tr>
            {% for patient in patients %}
            <tr>
                <td>{{ patient.id }}</td>
                <td>{{ patient.name }}</td>
                <td>{{ patient.last_name }}</td>
                <td>{{ patient.dob }}</td>
                <td>{{ patient.hospital }}</td>
                <td>{{ patient.symptoms }}</td>
                <td class="hidden">{{ patient.queue_number }}</td>
            </tr>
            {% endfor %}
        </table>
        <a href="{{ url_for('index') }}">Back to Home</a>
    </div>
</body>
</html>
```

5. Create a new table for the daily counter:

```sql
CREATE TABLE daily_counter (
    id INT PRIMARY KEY,
    value INT,
    date DATE
);
```

6. To implement the time slot booking feature, you'll need to add another table and modify the form:

```sql
CREATE TABLE time_slots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    slot_time TIME,
    date DATE,
    hospital VARCHAR(100),
    booked INT DEFAULT 0
);
```

Modify the `form.html` template to include time slot selection:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Patient Information Form</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
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
```

Update the Flask application to handle time slots:

```python
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

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.to_dict()
    
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
                         (name, last_name, dob, hospital, symptoms, queue_number, time_slot_id) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (data['name'], data['lastName'], data['dob'], 
                                     data['hospital'], data['symptoms'], queue_number, data['time_slot']))
            connection.commit()
        
        # Store queue number in session
        session['queue_number'] = queue_number
        session['hospital'] = data['hospital']
        
        # Redirect to a new page showing the queue number
        return redirect(url_for('queue_info'))
    
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        app.logger.error(error_message)
        flash(error_message, 'error')
    
    return render_template('form.html', hospital=data['hospital'])
```

These changes will implement the new requirements:

1. A daily counter that resets each day
2. A queue number assigned to each patient
3. A maximum queue size of 20
4. A "thank you" page showing the queue number
5. Hidden queue number column in the patient list
6. Time slot booking for 6 PM to 10 PM with a maximum of 10 bookings per slot

Remember to initialize the time slots table with the desired time slots for each hospital. You may want to create a script to do this automatically each day or week, depending on your needs.
==========================================================
==========================================================
==========================================================
==========================================================
You're absolutely right. We should include all database schema modifications in the bootstrap script to ensure a smooth, automated deployment. I apologize for the oversight. Let's update the bootstrap script to include all the necessary database changes.

Here's an updated section of the bootstrap script that includes all the required database modifications:

```bash
# ... (previous parts of the bootstrap script)

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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add queue_number column if not exists
ALTER TABLE patients ADD COLUMN IF NOT EXISTS queue_number INT;

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
SELECT time_slot, CURDATE(), hospital
FROM (
    SELECT '18:00' AS time_slot UNION SELECT '18:30' UNION SELECT '19:00' UNION
    SELECT '19:30' UNION SELECT '20:00' UNION SELECT '20:30' UNION
    SELECT '21:00' UNION SELECT '21:30' UNION SELECT '22:00'
) AS times
CROSS JOIN (
    SELECT 'Hospital A' AS hospital UNION SELECT 'Hospital B' UNION SELECT 'Hospital C'
) AS hospitals;

EOF

# ... (rest of the bootstrap script)
```

This updated section of the bootstrap script does the following:

1. Creates the `hospital_queue` database if it doesn't exist.
2. Creates the `hospital_user` if it doesn't exist.
3. Grants necessary privileges to the `hospital_user`.
4. Creates the `patients` table if it doesn't exist.
5. Adds the `queue_number` column to the `patients` table if it doesn't exist.
6. Creates the `daily_counter` table if it doesn't exist.
7. Creates the `time_slots` table if it doesn't exist.
8. Initializes the `time_slots` table with default slots for each hospital.

By using `IF NOT EXISTS` and `IGNORE` clauses, this script can be run multiple times without causing errors, making it idempotent and safe for re-runs.

Make sure to integrate this section into your main bootstrap script, replacing any existing database setup commands. This will ensure that when you deploy your application, all necessary database structures are in place.

Also, remember to update your application code (Flask app) to work with these new table structures, as outlined in the previous response. This includes modifying the patient submission process, handling the daily counter, and managing time slot bookings.