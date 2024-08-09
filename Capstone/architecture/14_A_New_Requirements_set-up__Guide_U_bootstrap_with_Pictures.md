Certainly! I'd be happy to help you add pictures for each hospital on the welcome screen. We'll start by storing the pictures locally and then provide guidance on how to transition to S3 storage later. Here's how we can achieve this:

1. First, let's modify the bootstrap script to create a folder for hospital images.
2. Then, we'll update the Flask application to serve these images.
3. Finally, we'll modify the HTML template to display the images.

Let's go through these steps:

1. Modify the bootstrap script:

Add the following lines to your bootstrap script, after creating the static directory:

```bash
# Create directory for hospital images
mkdir -p /home/ubuntu/hospital_queue/static/images/hospitals
chmod 755 /home/ubuntu/hospital_queue/static/images/hospitals

# Download sample images (replace these with your actual image URLs later)
wget -O /home/ubuntu/hospital_queue/static/images/hospitals/hospital_a.jpg https://example.com/hospital_a.jpg
wget -O /home/ubuntu/hospital_queue/static/images/hospitals/hospital_b.jpg https://example.com/hospital_b.jpg
wget -O /home/ubuntu/hospital_queue/static/images/hospitals/hospital_c.jpg https://example.com/hospital_c.jpg

# Set correct permissions
chown -R ubuntu:ubuntu /home/ubuntu/hospital_queue/static/images
```

2. Update the Flask application:

Modify your `app.py` file to include information about the hospital images. Add this to your existing hospital data:

```python
hospitals = [
    {'name': 'Hospital A', 'image': 'hospital_a.jpg'},
    {'name': 'Hospital B', 'image': 'hospital_b.jpg'},
    {'name': 'Hospital C', 'image': 'hospital_c.jpg'}
]

@app.route('/')
def index():
    return render_template('index.html', hospitals=hospitals)
```

3. Modify the HTML template:

Update your `index.html` file to display the hospital images:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Hospital Queue System</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        .hospital-list {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-around;
        }
        .hospital-item {
            width: 300px;
            margin: 20px;
            text-align: center;
        }
        .hospital-image {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to the Hospital Queue System</h1>
        <h2>Select a Hospital:</h2>
        <div class="hospital-list">
            {% for hospital in hospitals %}
                <div class="hospital-item">
                    <img src="{{ url_for('static', filename='images/hospitals/' + hospital.image) }}" alt="{{ hospital.name }}" class="hospital-image">
                    <h3><a href="{{ url_for('form', hospital=hospital.name) }}">{{ hospital.name }}</a></h3>
                </div>
            {% endfor %}
        </div>
        <p><a href="{{ url_for('patients') }}">View All Patients</a></p>
    </div>
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>
```

These changes will display the hospital images on the welcome screen, with the hospital names as links below each image.

For transitioning to S3 storage later:

1. You'll need to set up an S3 bucket and configure appropriate permissions.
2. Install the boto3 library in your Flask application: `pip install boto3`
3. Update your Flask application to use S3 for image URLs. Here's a basic example:

```python
import boto3
from botocore.exceptions import NoCredentialsError

s3 = boto3.client('s3')
S3_BUCKET = 'your-s3-bucket-name'

def get_s3_image_url(image_name):
    try:
        url = s3.generate_presigned_url('get_object',
                                        Params={'Bucket': S3_BUCKET,
                                                'Key': f'hospitals/{image_name}'},
                                        ExpiresIn=3600)
        return url
    except NoCredentialsError:
        print("No AWS credentials found")
        return None

hospitals = [
    {'name': 'Hospital A', 'image': get_s3_image_url('hospital_a.jpg')},
    {'name': 'Hospital B', 'image': get_s3_image_url('hospital_b.jpg')},
    {'name': 'Hospital C', 'image': get_s3_image_url('hospital_c.jpg')}
]
```

4. Update your HTML template to use these S3 URLs instead of local file paths.

Remember to handle errors gracefully and ensure your application has the necessary permissions to access the S3 bucket. Also, consider implementing caching to reduce the number of S3 requests and improve performance.

This approach allows you to start with local images and then easily transition to S3-hosted images in the future.
=================================================================================================================
=================================================================================================================
=================================================================================================================
=================================================================================================================
=================================================================================================================
=================================================================================================================
I've reviewed the updated bootstrap script, and I can see that you've made changes to use S3 for image storage. However, there are a few issues that need to be addressed. I'll provide corrections and suggestions, along with specific areas where to insert or modify the code.

1. In the Flask application (`app.py`), update the `hospitals` list:

Replace:

```python
hospitals = [
    {'name': 'Hospital A', 'image': https://mcit-capstone-hospital-queue-app-test.s3.amazonaws.com/hospital-index-page-images/hospital_a.jpg('hospital_a.jpg')},
    {'name': 'Hospital B', 'image': https://mcit-capstone-hospital-queue-app-test.s3.amazonaws.com/hospital-index-page-images/hospital_b.jpg('hospital_b.jpg')},
    {'name': 'Hospital C', 'image': https://mcit-capstone-hospital-queue-app-test.s3.amazonaws.com/hospital-index-page-images/hospital_c.jpg('hospital_c.jpg')}
]
```

With:

```python
hospitals = [
    {'name': 'Hospital A', 'image': 'https://mcit-capstone-hospital-queue-app-test.s3.amazonaws.com/hospital-index-page-images/hospital_a.jpg'},
    {'name': 'Hospital B', 'image': 'https://mcit-capstone-hospital-queue-app-test.s3.amazonaws.com/hospital-index-page-images/hospital_b.jpg'},
    {'name': 'Hospital C', 'image': 'https://mcit-capstone-hospital-queue-app-test.s3.amazonaws.com/hospital-index-page-images/hospital_c.jpg'}
]
```

2. In the `index.html` template, update the image source:

Replace:

```html
<img src="{{ url_for('static', filename='images/hospitals/' + hospital.image) }}" alt="{{ hospital.name }}" class="hospital-image">
```

With:

```html
<img src="{{ hospital.image }}" alt="{{ hospital.name }}" class="hospital-image">
```

3. Remove the local image download section from the bootstrap script:

Delete or comment out these lines:

```bash
# Download sample images (replace these with your actual image URLs later)
# wget -O /home/ubuntu/hospital_queue/static/images/hospitals/hospital_a.jpg https://mcit-capstone-hospital-queue-app-test.s3.amazonaws.com/hospital-index-page-images/hospital_a.jpeg
# wget -O /home/ubuntu/hospital_queue/static/images/hospitals/hospital_b.jpg https://mcit-capstone-hospital-queue-app-test.s3.amazonaws.com/hospital-index-page-images/hospital_b.jpeg
# wget -O /home/ubuntu/hospital_queue/static/images/hospitals/hospital_c.jpg https://mcit-capstone-hospital-queue-app-test.s3.amazonaws.com/hospital-index-page-images/hospital_c.jpeg
```

4. Add AWS credentials configuration:

Add the following lines to the bootstrap script, just before creating the Flask application:

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

Replace `YOUR_AWS_ACCESS_KEY_ID` and `YOUR_AWS_SECRET_ACCESS_KEY` with your actual AWS credentials.

5. Update the Gunicorn service file to include AWS credentials:

In the `hospital_queue.service` file, add the following environment variables:

```bash
Environment="AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_ID"
Environment="AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY"
Environment="AWS_DEFAULT_REGION=YOUR_AWS_REGION"
```

Replace `YOUR_AWS_ACCESS_KEY_ID`, `YOUR_AWS_SECRET_ACCESS_KEY`, and `YOUR_AWS_REGION` with your actual AWS credentials and region.

6. Remove the `get_s3_image_url` function from `app.py` as it's no longer needed:

Delete or comment out this function:

```python
def get_s3_image_url(image_name):
    try:
        url = s3.generate_presigned_url('get_object',
                                        Params={'Bucket': S3_BUCKET,
                                                'Key': f'hospitals/{image_name}'},
                                        ExpiresIn=3600)
        return url
    except NoCredentialsError:
        print("No AWS credentials found")
        return None
```

7. Update the `boto3` configuration in `app.py`:

Replace:

```python
s3 = boto3.client('s3')
S3_BUCKET = 'mcit-capstone-hospital-queue-app-test'
```

With:

```python
s3 = boto3.client('s3', region_name=os.environ.get('AWS_DEFAULT_REGION'))
S3_BUCKET = 'mcit-capstone-hospital-queue-app-test'
```

These changes should allow your application to display images from S3 correctly. Make sure to replace the placeholder AWS credentials with your actual credentials, and ensure that your S3 bucket is properly configured with the correct permissions to allow public read access to the images.

After making these changes, your application should be able to display the images from S3 when you run the bootstrap script.

=================================================================================================================
=================================================================================================================
=================================================================================================================
Trouble shooting
=================================================================================================================
=================================================================================================================
=================================================================================================================
Thank you for providing the screenshot. I can see several issues that need to be addressed:

1. Image Loading: The images for the hospitals are not loading correctly. The alt text is displayed instead of the actual images.

2. Resource Loading Errors: There are 404 (Not Found) errors for 'hospital_b.jpg' and 'hospital_c.jpg', and 403 (Forbidden) errors for 'script.js' and 'style.css'.

Let's address these issues one by one:

1. For the hospital images:
   - Ensure that the image URLs in your `app.py` are correct and accessible.
   - Check if the S3 bucket permissions allow public read access to these specific images.

2. For the CSS and JavaScript files:
   - Make sure that the 'static' folder is set up correctly in your Flask application.
   - Verify that 'script.js' and 'style.css' exist in the correct location within your project structure.

Here are the steps to resolve these issues:

1. Update your `app.py` to use the correct S3 URLs:

```python
hospitals = [
    {'name': 'Hospital A', 'image': 'https://mcit-capstone-hospital-queue-app-test.s3.amazonaws.com/hospital-index-page-images/hospital_a.jpeg'},
    {'name': 'Hospital B', 'image': 'https://mcit-capstone-hospital-queue-app-test.s3.amazonaws.com/hospital-index-page-images/hospital_b.jpeg'},
    {'name': 'Hospital C', 'image': 'https://mcit-capstone-hospital-queue-app-test.s3.amazonaws.com/hospital-index-page-images/hospital_c.jpeg'}
]
```

2. Check your S3 bucket permissions. Make sure the images are set to public read access.

3. Verify your project structure. It should look something like this:

```
/home/ubuntu/hospital_queue/
├── app.py
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
└── templates/
    └── index.html
```

4. Update your `index.html` to correctly reference the static files:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Hospital Queue System</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
</head>
<body>
    <!-- Your existing HTML content -->
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>
```

5. Make sure your Nginx configuration is correct. The location block for static files should look like this:

```nginx
location /static {
    alias /home/ubuntu/hospital_queue/static;
}
```

6. After making these changes, restart your Gunicorn service and Nginx:

```bash
sudo systemctl restart hospital_queue
sudo systemctl restart nginx
```

If you've made these changes and are still experiencing issues, please provide:
1. The contents of your `app.py` file
2. The contents of your `index.html` file
3. Your Nginx configuration file
4. The output of `ls -R /home/ubuntu/hospital_queue/static`

This information will help me provide more specific guidance to resolve the remaining issues.
=================================================================================================================
=================================================================================================================
=================================================================================================================
Trouble shooting 2
=================================================================================================================
=================================================================================================================
=================================================================================================================
Certainly! I'll guide you through each step, showing exactly where to insert or modify the code.

1. Update `app.py`:
   Open the file `/home/ubuntu/hospital_queue/app.py` and find the `hospitals` list. Replace it with:

   ```python
   hospitals = [
       {'name': 'Hospital A', 'image': 'https://mcit-capstone-hospital-queue-app-test.s3.amazonaws.com/hospital-index-page-images/hospital_a.jpeg'},
       {'name': 'Hospital B', 'image': 'https://mcit-capstone-hospital-queue-app-test.s3.amazonaws.com/hospital-index-page-images/hospital_b.jpeg'},
       {'name': 'Hospital C', 'image': 'https://mcit-capstone-hospital-queue-app-test.s3.amazonaws.com/hospital-index-page-images/hospital_c.jpeg'}
   ]
   ```

2. Check S3 bucket permissions:
   Go to your AWS S3 console, select your bucket, and for each image:
   - Select the image
   - Click "Actions" -> "Make public using ACL"

3. Verify project structure:
   In your SSH terminal, run:
   ```
   cd /home/ubuntu/hospital_queue
   ls -R
   ```
   Ensure you see a structure similar to what I described earlier.

4. Update `index.html`:
   Open `/home/ubuntu/hospital_queue/templates/index.html` and replace the entire content with:

   ```html
   <!DOCTYPE html>
   <html>
   <head>
       <title>Hospital Queue System</title>
       <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
       <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
   </head>
   <body>
       <div class="container">
           <h1>Welcome to the Hospital Queue System</h1>
           <h2>Select a Hospital:</h2>
           <div class="hospital-list">
               {% for hospital in hospitals %}
                   <div class="hospital-item">
                       <img src="{{ hospital.image }}" alt="{{ hospital.name }}" class="hospital-image">
                       <h3><a href="{{ url_for('form', hospital=hospital.name) }}">{{ hospital.name }}</a></h3>
                   </div>
               {% endfor %}
           </div>
           <p><a href="{{ url_for('patients') }}">View All Patients</a></p>
       </div>
       <script src="{{ url_for('static', filename='js/script.js') }}"></script>
   </body>
   </html>
   ```

5. Check Nginx configuration:
   Open `/etc/nginx/sites-available/hospital_queue` and ensure it contains:

   ```nginx
   server {
       listen 80;
       server_name _;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }

       location /static {
           alias /home/ubuntu/hospital_queue/static;
       }
   }
   ```

6. Restart services:
   In your terminal, run:
   ```
   sudo systemctl restart hospital_queue
   sudo systemctl restart nginx
   ```

7. Verify static files:
   Run this command to check if static files exist:
   ```
   ls -R /home/ubuntu/hospital_queue/static
   ```
   If `style.css` or `script.js` are missing, create them:
   ```
   mkdir -p /home/ubuntu/hospital_queue/static/css /home/ubuntu/hospital_queue/static/js
   touch /home/ubuntu/hospital_queue/static/css/style.css
   touch /home/ubuntu/hospital_queue/static/js/script.js
   ```

8. Set permissions:
   Ensure correct permissions:
   ```
   sudo chown -R ubuntu:ubuntu /home/ubuntu/hospital_queue
   sudo chmod -R 755 /home/ubuntu/hospital_queue/static
   ```

After completing these steps, try accessing your application again. If you're still having issues, please provide the output of the commands I mentioned, especially the `ls -R` command for the static directory, and any error messages you see in the browser console or server logs.