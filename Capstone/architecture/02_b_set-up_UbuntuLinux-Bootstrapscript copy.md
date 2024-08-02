Certainly! Here's a bootstrap script that automates the setup process for your Flask application on an Ubuntu EC2 instance. You can use this script as a user data script when launching your EC2 instance, or run it manually after connecting to your instance.

```bash
#!/bin/bash

# Update and upgrade the system
sudo apt update
sudo apt upgrade -y

# Install required packages
sudo apt install python3 python3-pip python3-venv nginx -y

# Create project directory
mkdir -p /home/ubuntu/hospital_queue
cd /home/ubuntu/hospital_queue

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Flask and Gunicorn
pip install flask gunicorn requests

# Create Flask application
cat << EOF > app.py
from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

API_ENDPOINT = os.environ.get('API_ENDPOINT')

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
    response = requests.post(f"{API_ENDPOINT}/submit", json=data)
    result = response.json()
    return render_template('result.html', result=result)

@app.route('/check_queues')
def check_queues():
    response = requests.get(f"{API_ENDPOINT}/check_queues")
    queues = response.json()
    return jsonify(queues)

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
ExecStart=/home/ubuntu/hospital_queue/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 app:app

[Install]
WantedBy=multi-user.target
EOF

# Start and enable Gunicorn service
sudo systemctl start hospital_queue
sudo systemctl enable hospital_queue

# Set up environment variables
echo "API_ENDPOINT=https://your-api-gateway-url" | sudo tee -a /etc/environment
source /etc/environment

# Restart Gunicorn service to pick up new environment variable
sudo systemctl restart hospital_queue

# Set up firewall
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
echo "y" | sudo ufw enable

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

echo "Setup completed successfully!"
```

To use this script:

1. Save it as a file, e.g., `setup_hospital_queue.sh`

2. Make it executable:
   ```
   chmod +x setup_hospital_queue.sh
   ```

3. Run it with sudo:
   ```
   sudo ./setup_hospital_queue.sh
   ```

Alternatively, you can use this script as user data when launching your EC2 instance:

1. In the EC2 launch wizard, expand the "Advanced Details" section.
2. In the "User data" field, paste the entire script.
3. Make sure to select "As text" instead of "As file".

Important notes:

- Replace `https://your-api-gateway-url` with your actual API Gateway endpoint in the script.
- This script assumes you're using the default Ubuntu user. If you're using a different user, you'll need to modify the paths and user references accordingly.
- The script sets up basic firewall rules. Ensure these align with your security requirements.
- After running the script, your application should be accessible via your EC2 instance's public IP address.
- For a production environment, you should set up HTTPS using a tool like Certbot for Let's Encrypt certificates.

Remember to review and understand the script before running it, especially in a production environment. You may need to customize it further based on your specific requirements.