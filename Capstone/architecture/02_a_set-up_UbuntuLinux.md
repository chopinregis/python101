Certainly! Here's a detailed setup guide for deploying your Flask application on an Ubuntu EC2 instance:

1. Launch an EC2 Instance:
   - Choose Ubuntu Server 20.04 LTS (or the latest LTS version) as the AMI
   - Select t2.micro (or your preferred instance type)
   - Configure security group:
     - Allow SSH (port 22) from your IP
     - Allow HTTP (port 80) from anywhere
     - Allow HTTPS (port 443) from anywhere
   - Launch the instance with a key pair

2. Connect to your EC2 Instance:
   ```
   ssh -i /path/to/your-key-pair.pem ubuntu@your-instance-public-ip
   ```

3. Update the system:
   ```
   sudo apt update
   sudo apt upgrade -y
   ```

4. Install Python and required packages:
   ```
   sudo apt install python3 python3-pip python3-venv -y
   ```

5. Create a directory for your project:
   ```
   mkdir ~/hospital_queue
   cd ~/hospital_queue
   ```

6. Create and activate a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

7. Install Flask and Gunicorn:
   ```
   pip install flask gunicorn
   ```

8. Create your Flask application:
   ```
   nano app.py
   ```
   Paste the Flask application code we created earlier into this file.

9. Create the templates and static directories:
   ```
   mkdir templates static
   mkdir static/css static/js
   ```

10. Create the HTML templates:
    ```
    nano templates/index.html
    nano templates/form.html
    nano templates/result.html
    ```
    Paste the respective HTML content into each file.

11. Create the CSS and JS files:
    ```
    nano static/css/style.css
    nano static/js/script.js
    ```
    Add your CSS and JavaScript code to these files.

12. Test your Flask application:
    ```
    python3 app.py
    ```
    You should see output indicating that the Flask development server is running.

13. Install Nginx:
    ```
    sudo apt install nginx -y
    ```

14. Start Nginx:
    ```
    sudo systemctl start nginx
    sudo systemctl enable nginx
    ```

15. Configure Nginx:
    ```
    sudo nano /etc/nginx/sites-available/hospital_queue
    ```
    Add the following content:
    ```
    server {
        listen 80;
        server_name _;

        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
    ```

16. Create a symbolic link to enable the site:
    ```
    sudo ln -s /etc/nginx/sites-available/hospital_queue /etc/nginx/sites-enabled
    ```

17. Remove the default Nginx configuration:
    ```
    sudo rm /etc/nginx/sites-enabled/default
    ```

18. Test Nginx configuration:
    ```
    sudo nginx -t
    ```

19. If the test is successful, reload Nginx:
    ```
    sudo systemctl reload nginx
    ```

20. Create a systemd service file for Gunicorn:
    ```
    sudo nano /etc/systemd/system/hospital_queue.service
    ```
    Add the following content:
    ```
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
    ```

21. Start and enable the Gunicorn service:
    ```
    sudo systemctl start hospital_queue
    sudo systemctl enable hospital_queue
    ```

22. Check the status of the Gunicorn service:
    ```
    sudo systemctl status hospital_queue
    ```

23. Set up environment variables:
    ```
    sudo nano /etc/environment
    ```
    Add the following line:
    ```
    API_ENDPOINT="https://your-api-gateway-url"
    ```
    Save and exit. Then, reload the environment:
    ```
    source /etc/environment
    ```

24. Restart the Gunicorn service to pick up the new environment variable:
    ```
    sudo systemctl restart hospital_queue
    ```

Now, your Flask application should be running with Gunicorn, and Nginx should be set up to proxy requests to Gunicorn. You should be able to access your application by navigating to your EC2 instance's public IP address in a web browser.

Additional steps for security and maintenance:

25. Set up a firewall (optional but recommended):
    ```
    sudo apt install ufw
    sudo ufw allow 22
    sudo ufw allow 80
    sudo ufw allow 443
    sudo ufw enable
    ```

26. Set up automatic security updates:
    ```
    sudo apt install unattended-upgrades
    sudo dpkg-reconfigure --priority=low unattended-upgrades
    ```

27. Install and configure Fail2Ban to protect against brute-force attacks:
    ```
    sudo apt install fail2ban
    sudo systemctl start fail2ban
    sudo systemctl enable fail2ban
    ```

Remember to replace "your-instance-public-ip" with your actual EC2 instance's public IP address when connecting via SSH, and replace "https://your-api-gateway-url" with your actual API Gateway endpoint.

This setup provides a basic working environment on an Ubuntu EC2 instance. For a production deployment, you'd want to consider additional security measures, HTTPS configuration with Let's Encrypt, and possibly using a domain name instead of the raw IP address.