I understand the issue you're experiencing. Let's troubleshoot this step by step:

1. First, let's add more logging to the `/submit` route to see what's happening:

```python
@app.route('/submit', methods=['POST'])
def submit():
    logging.debug("Submit route accessed")
    data = request.form.to_dict()
    logging.debug(f"Received form data: {data}")
    
    # ... (existing code)
    
    try:
        queue_number = get_daily_counter()
        logging.debug(f"Queue number assigned: {queue_number}")
        
        # ... (existing code)
        
        logging.debug("About to insert patient data")
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
        
        logging.debug("Redirecting to queue_info")
        return redirect(url_for('queue_info'))
    
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        logging.error(error_message)
        logging.error(f"Exception details: {str(e)}")
        logging.error(f"Exception type: {type(e).__name__}")
        logging.error(f"Exception args: {e.args}")
        flash(error_message, 'error')
    
    logging.debug("Rendering form template")
    return render_template('form.html', hospital=data['hospital'])
```

2. Check your `form.html` template to ensure the form is set up correctly:

```html
<form action="{{ url_for('submit') }}" method="post">
    <!-- Make sure all your form fields are here and named correctly -->
</form>
```

3. Verify that your `queue_info.html` template exists and is correctly formatted.

4. Check your database connection and make sure the patients table is created correctly:

```python
@app.route('/test_db')
def test_db():
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM patients LIMIT 1")
                result = cursor.fetchone()
                return f"Database connection successful. Sample data: {result}"
    except Exception as e:
        return f"Database connection failed: {str(e)}"
```

5. Add this route to check the session data:

```python
@app.route('/check_session')
def check_session():
    return jsonify(dict(session))
```

6. Modify your `patients` route to include more logging:

```python
@app.route('/patients')
def patients():
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                logging.debug("Fetching patients from database")
                cursor.execute("""
                    SELECT id, queue_number, name, last_name, hospital, status, 
                           appointment_type, payment_method, payment_status, estimated_waiting_time
                    FROM patients 
                    ORDER BY queue_number
                """)
                patients = cursor.fetchall()
                logging.debug(f"Fetched {len(patients)} patients")
        return render_template('patients.html', patients=patients)
    except Exception as e:
        error_message = f"Error retrieving patients: {e}"
        logging.error(error_message)
        flash(error_message, 'error')
        return redirect(url_for('index'))
```

After making these changes:

1. Restart your Flask application.
2. Try submitting the form again.
3. Check your `app.log` file for any error messages or unexpected behavior.
4. Visit the `/test_db` route to ensure your database connection is working.
5. Visit the `/check_session` route after submitting the form to see if the session data is being stored correctly.
6. Check the patients page to see if any entries are displayed.

If you're still having issues, please provide the contents of your `app.log` file and any error messages you see in the browser console (you can open this with F12 in most browsers). This will help identify where the problem is occurring.
==========================================
==========================================
==========================================
To provide me with the information from these steps, you can follow this process:

1. Restart your Flask application:
   - If you're running it directly, stop it (usually with Ctrl+C) and start it again.
   - If it's running as a service, use: `sudo systemctl restart hospital_queue`

2. Try submitting the form again:
   - Go to your application's URL and fill out the form.
   - Click submit and note what happens.

3. Check your `app.log` file:
   - Use this command: `cat /home/ubuntu/hospital_queue/app.log`
   - Copy the output, especially any lines related to the form submission.

4. Visit the `/test_db` route:
   - Go to `http://your-server-ip/test_db` in your browser.
   - Copy the text that appears on the page.

5. Visit the `/check_session` route:
   - Go to `http://your-server-ip/check_session` in your browser.
   - Copy the JSON data that appears.

6. Check the patients page:
   - Go to `http://your-server-ip/patients` in your browser.
   - Describe what you see (e.g., "No patients displayed", or "I see a list of patients").

7. Check the browser console:
   - Open your browser's developer tools (usually F12 or right-click and select "Inspect").
   - Go to the "Console" tab.
   - Copy any error messages you see there.

After collecting all this information, you can paste it into your next message to me. Format it like this:

```
app.log contents:
[Paste the relevant parts of app.log here]

/test_db output:
[Paste the output from the /test_db route here]

/check_session output:
[Paste the JSON data from the /check_session route here]

Patients page description:
[Describe what you see on the patients page]

Browser console errors:
[Paste any error messages from the browser console here]
```

This information will help me understand exactly what's happening in your application and where the problem might be occurring.