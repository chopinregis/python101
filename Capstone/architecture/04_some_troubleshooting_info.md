I understand the issue. Let's modify the `/submit` route to handle errors properly and redirect to the patients page on success. We'll also display any error messages on the web screen. Here's how we can update the `app.py` file:

```python
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import requests
import os
import pymysql
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for flashing messages

# ... (keep the existing imports and configuration)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.to_dict()
    
    try:
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
        
        # If everything is successful, redirect to patients page
        flash('Patient information submitted successfully!', 'success')
        return redirect(url_for('patients'))
    
    except pymysql.Error as e:
        # Database error
        error_message = f"Database error: {e}"
        app.logger.error(error_message)
        flash(error_message, 'error')
    except requests.RequestException as e:
        # API call error
        error_message = f"API error: {e}"
        app.logger.error(error_message)
        flash(error_message, 'error')
    except Exception as e:
        # Any other error
        error_message = f"An unexpected error occurred: {e}"
        app.logger.error(error_message)
        flash(error_message, 'error')
    
    # If there was an error, re-render the form
    return render_template('form.html', hospital=data['hospital'])

@app.route('/patients')
def patients():
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM patients")
                patients = cursor.fetchall()
        return render_template('patients.html', patients=patients)
    except Exception as e:
        flash(f"Error retrieving patients: {e}", 'error')
        return redirect(url_for('index'))

# ... (keep the rest of your routes)
```

Now, let's update the `form.html` and `patients.html` templates to display flash messages:

In `templates/form.html`, add this just after the `<body>` tag:

```html
{% with messages = get_flashed_messages(with_categories=true) %}
  {% if messages %}
    {% for category, message in messages %}
      <div class="alert alert-{{ category }}">{{ message }}</div>
    {% endfor %}
  {% endif %}
{% endwith %}
```

Do the same for `templates/patients.html`.

Finally, let's add some basic styling for these alerts. In your `static/css/style.css` file, add:

```css
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
```

These changes will:

1. Handle errors gracefully in the `/submit` route.
2. Display success or error messages using Flask's flash functionality.
3. Redirect to the patients page on successful submission.
4. Re-render the form with an error message if something goes wrong.
5. Add basic styling for the alert messages.

After making these changes:

1. Save the updated `app.py` file.
2. Update the HTML templates and CSS file.
3. Restart your Gunicorn service:
   ```
   sudo systemctl restart hospital_queue
   ```

Now, when you submit the form:
- If successful, you'll be redirected to the patients page with a success message.
- If there's an error, you'll stay on the form page and see an error message explaining what went wrong.

This should resolve the "Internal Server Error" issue and provide more informative feedback to the user.








I apologize for the oversight. The error you're encountering is due to a missing Python package that's required for newer MySQL authentication methods. Let's resolve this issue step by step:

1. First, we need to install the 'cryptography' package. SSH into your EC2 instance and run the following commands:

   ```
   cd /home/ubuntu/hospital_queue
   source venv/bin/activate
   pip install cryptography
   ```

2. After installing the package, restart your Gunicorn service:

   ```
   sudo systemctl restart hospital_queue
   ```

3. If you're still encountering issues, it's possible that your MySQL user is configured to use a newer authentication method that your current setup doesn't support. Let's modify the MySQL user to use the older, compatible authentication method. Run these MySQL commands:

   ```
   sudo mysql
   ```

   Once in the MySQL prompt, run:

   ```sql
   ALTER USER 'hospital_user'@'localhost' IDENTIFIED WITH mysql_native_password BY 'your_password_here';
   FLUSH PRIVILEGES;
   EXIT;
   ```

   Replace 'your_password_here' with the actual password you set for the hospital_user.

4. Now, let's modify the database connection in your `app.py` file to explicitly specify the authentication plugin. Update the `db_config` dictionary in your `app.py`:

   ```python
   db_config = {
       'host': 'localhost',
       'user': 'hospital_user',
       'password': os.environ.get('DB_PASSWORD'),
       'db': 'hospital_queue',
       'charset': 'utf8mb4',
       'cursorclass': pymysql.cursors.DictCursor,
       'auth_plugin': 'mysql_native_password'
   }
   ```

5. After making these changes, save the `app.py` file and restart your Gunicorn service again:

   ```
   sudo systemctl restart hospital_queue
   ```

These steps should resolve the authentication issue and allow you to view the entries in your database again.

If you're still encountering issues, please check the Gunicorn error log for more detailed error messages:

```
sudo journalctl -u hospital_queue
```

This will show you the logs for the Gunicorn service, which might provide more insight into what's going wrong.

Also, ensure that your environment variables (particularly `DB_PASSWORD`) are set correctly in the `/etc/systemd/system/hospital_queue.service` file.

If you continue to face issues, please provide the output of the Gunicorn error log, and I'll be happy to help you troubleshoot further.









The error you're seeing is due to the API Gateway URL not being correctly set or resolved. This error occurs because the script is trying to connect to a URL that's literally 'your-api-gateway-url' instead of an actual API Gateway endpoint. Let's fix this:

1. First, make sure you've replaced the placeholder API Gateway URL in your bootstrap script or environment variables. In your `app.py`, you should have a line like this:

   ```python
   API_ENDPOINT = os.environ.get('API_ENDPOINT')
   ```

2. The `API_ENDPOINT` environment variable should be set to your actual API Gateway URL. You can set this in the `/etc/systemd/system/hospital_queue.service` file. Edit this file:

   ```
   sudo nano /etc/systemd/system/hospital_queue.service
   ```

   Find the line that sets the `API_ENDPOINT` environment variable and update it with your actual API Gateway URL:

   ```
   Environment="API_ENDPOINT=https://your-actual-api-gateway-url.execute-api.region.amazonaws.com/stage"
   ```

   Replace `your-actual-api-gateway-url.execute-api.region.amazonaws.com/stage` with your actual API Gateway URL.

3. After updating the service file, reload the systemd daemon and restart the service:

   ```
   sudo systemctl daemon-reload
   sudo systemctl restart hospital_queue
   ```

4. If you don't actually have an API Gateway set up yet, or if you want to test your application without making API calls, you can modify your `submit` function in `app.py` to skip the API call temporarily:

   ```python
   @app.route('/submit', methods=['POST'])
   def submit():
       data = request.form.to_dict()
       
       try:
           # Store data in MySQL
           with get_db_connection() as connection:
               with connection.cursor() as cursor:
                   sql = """INSERT INTO patients 
                            (name, last_name, dob, hospital, symptoms) 
                            VALUES (%s, %s, %s, %s, %s)"""
                   cursor.execute(sql, (data['name'], data['lastName'], data['dob'], 
                                        data['hospital'], data['symptoms']))
               connection.commit()
           
           # Temporarily skip API call
           # response = requests.post(f"{API_ENDPOINT}/submit", json=data)
           # result = response.json()
           
           # Mock result for testing
           result = {"userId": "mock-user-id", "queuePosition": 1}
           
           flash('Patient information submitted successfully!', 'success')
           return redirect(url_for('patients'))
       
       except Exception as e:
           error_message = f"An unexpected error occurred: {e}"
           app.logger.error(error_message)
           flash(error_message, 'error')
       
       return render_template('form.html', hospital=data['hospital'])
   ```

5. If you do have an API Gateway set up, ensure that the URL is correct and that your EC2 instance has proper network access to reach it. Check your security groups and network ACLs to make sure outbound HTTPS traffic (port 443) is allowed.

6. You can also add some debugging to your `app.py` to print out the API_ENDPOINT:

   ```python
   print(f"API_ENDPOINT: {API_ENDPOINT}")
   ```

   Then check the Gunicorn logs to see what URL it's trying to use:

   ```
   sudo journalctl -u hospital_queue
   ```

By following these steps, you should be able to resolve the API Gateway connection issue. If you're still having problems, please provide more details about your API Gateway setup (if you have one) and the contents of your Gunicorn log file.