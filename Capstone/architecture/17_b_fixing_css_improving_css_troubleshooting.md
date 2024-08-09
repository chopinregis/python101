Thank you for providing the complete bootstrap script. I've reviewed it and have some suggestions for improvements and corrections. I'll go through the script section by section and provide specific recommendations:

1. AWS Credentials:
   Instead of hardcoding AWS credentials, use IAM roles for EC2 instances. Remove these lines:

   ```bash
   # Configure AWS credentials
   cat << EOF > /home/ubuntu/.aws/credentials
   [default]
   aws_access_key_id = YOUR_AWS_ACCESS_KEY_ID
   aws_secret_access_key = YOUR_AWS_SECRET_ACCESS_KEY
   EOF

   # Set correct permissions for AWS credentials
   chmod 600 /home/ubuntu/.aws/credentials
   chown ubuntu:ubuntu /home/ubuntu/.aws/credentials
   ```

   Instead, attach an IAM role to your EC2 instance with the necessary permissions.

2. Flask Application (`app.py`):
   - Remove the `S3_BUCKET` variable as it's not being used.
   - Update the `boto3` client initialization:

   ```python
   s3 = boto3.client('s3')
   ```

3. HTML Templates:
   - In `index.html`, move the inline styles to the `style.css` file.
   - In `patients.html`, move the JavaScript to a separate file.

4. Static Files:
   - Update the `script.js` file to include the dropdown functionality:

   ```javascript
   console.log('Script loaded');

   function toggleDropdown() {
       document.querySelector('.dropdown-content').classList.toggle('show');
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
   ```

5. Nginx Configuration:
   Add a `try_files` directive to handle Flask routes:

   ```nginx
   location / {
       try_files $uri @proxy_to_app;
   }

   location @proxy_to_app {
       proxy_pass http://127.0.0.1:8000;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
   }
   ```

6. Gunicorn Service:
   Remove the AWS credential environment variables and add a `--timeout` option:

   ```bash
   ExecStart=/home/ubuntu/hospital_queue/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 --timeout 120 app:app
   ```

7. Database Setup:
   Add an index to the `patients` table for faster queries:

   ```sql
   ALTER TABLE patients ADD INDEX idx_queue_number (queue_number);
   ```

8. Security:
   Add a Content Security Policy header in Nginx:

   ```nginx
   add_header Content-Security-Policy "default-src 'self'; script-src 'self' https://code.jquery.com; style-src 'self' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com;";
   ```

9. Error Handling:
   Add a custom error page:

   ```bash
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
   ```

   Then add an error handler in `app.py`:

   ```python
   @app.errorhandler(Exception)
   def handle_exception(e):
       return render_template('error.html', error_message=str(e)), 500
   ```

These changes will improve security, performance, and error handling in your application. Remember to test thoroughly after making these changes to ensure everything works as expected.
=============================================
=============================================
=============================================
=============================================
Certainly! I'll provide detailed steps on how to move the inline styles from `index.html` to `style.css` and the JavaScript from `patients.html` to a separate file.

1. Moving inline styles from `index.html` to `style.css`:

a. Open your `static/css/style.css` file and add the following styles at the end:

```css
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
    background-color: #f9f9f9;
    box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
    z-index: 1;
}
.dropbtn:hover .dropdown-content {
    display: block;
}
```

b. Open your `templates/index.html` file and remove the `<style>` tag and its contents. The beginning of your file should now look like this:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Hospital Queue System</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
</head>
<body>
    <div class="hero">
        <!-- Rest of your HTML content -->
    </div>
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>
```

2. Moving JavaScript from `patients.html` to a separate file:

a. Create a new file named `patients.js` in your `static/js/` directory:

```bash
touch /home/ubuntu/hospital_queue/static/js/patients.js
```

b. Open this new `patients.js` file and add the following content:

```javascript
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
```

c. Open your `templates/patients.html` file and replace the existing `<script>` tag (containing the JavaScript code) with a reference to the new file:

```html
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
        <!-- Your existing HTML content -->
    </div>
    <script src="{{ url_for('static', filename='js/patients.js') }}"></script>
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>
```

After making these changes:

1. The inline styles from `index.html` are now in the `style.css` file, making your HTML cleaner and your styles more maintainable.
2. The JavaScript code from `patients.html` is now in a separate `patients.js` file, improving code organization and making it easier to manage.

Remember to test your application after making these changes to ensure everything still works as expected. If you encounter any issues, double-check that the file paths in your HTML files are correct and that all the necessary files are in the right locations.