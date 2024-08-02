Certainly! I'll guide you through the process of setting up your EC2 instance, installing the necessary software, and getting your Flask application running with Gunicorn and Nginx. Here's a step-by-step guide:

1. Launch an EC2 Instance:
   - Log into AWS Console
   - Navigate to EC2 Dashboard
   - Click "Launch Instance"
   - Choose an Amazon Linux 2 AMI
   - Select t2.micro (or your preferred instance type)
   - Configure instance details as needed
   - Add storage (default is usually fine)
   - Add tags if desired
   - Configure security group:
     - Allow SSH (port 22) from your IP
     - Allow HTTP (port 80) from anywhere
     - Allow HTTPS (port 443) from anywhere
   - Review and launch
   - Select or create a key pair

2. Connect to your EC2 Instance:
   ```
   ssh -i /path/to/your-key-pair.pem ec2-user@your-instance-public-ip
   ```

3. Update the system:
   ```
   sudo yum update -y
   ```

4. Install Python 3 and development tools:
   ```
   sudo yum install python3 python3-devel -y
   ```

5. Install pip:
   ```
   curl -O https://bootstrap.pypa.io/get-pip.py
   python3 get-pip.py --user
   ```

6. Add pip to your path:
   ```
   echo "export PATH=~/.local/bin:$PATH" >> ~/.bashrc
   source ~/.bashrc
   ```

7. Install virtualenv:
   ```
   pip install --user virtualenv
   ```

8. Create a directory for your project:
   ```
   mkdir ~/hospital_queue
   cd ~/hospital_queue
   ```

9. Create and activate a virtual environment:
   ```
   virtualenv venv
   source venv/bin/activate
   ```

10. Install Flask and Gunicorn:
    ```
    pip install flask gunicorn
    ```

11. Create your Flask application:
    ```
    nano app.py
    ```
    Paste the Flask application code we created earlier into this file.

12. Create the templates and static directories:
    ```
    mkdir templates static
    mkdir static/css static/js
    ```

13. Create the HTML templates:
    ```
    nano templates/index.html
    nano templates/form.html
    nano templates/result.html
    ```
    Paste the respective HTML content into each file.

14. Create the CSS and JS files:
    ```
    nano static/css/style.css
    nano static/js/script.js
    ```
    Add your CSS and JavaScript code to these files.

15. Test your Flask application:
    ```
    python3 app.py
    ```
    You should see output indicating that the Flask development server is running.

16. Install Nginx:
    ```
    sudo amazon-linux-extras install nginx1
    ```

17. Start Nginx:
    ```
    sudo systemctl start nginx
    sudo systemctl enable nginx
    ```

18. Configure Nginx:
    ```
    sudo nano /etc/nginx/nginx.conf
    ```
    Add the following server block inside the http block:
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

19. Test Nginx configuration:
    ```
    sudo nginx -t
    ```

20. If the test is successful, reload Nginx:
    ```
    sudo systemctl reload nginx
    ```

21. Create a systemd service file for Gunicorn:
    ```
    sudo nano /etc/systemd/system/hospital_queue.service
    ```
    Add the following content:
    ```
    [Unit]
    Description=Gunicorn instance to serve hospital queue application
    After=network.target

    [Service]
    User=ec2-user
    Group=ec2-user
    WorkingDirectory=/home/ec2-user/hospital_queue
    Environment="PATH=/home/ec2-user/hospital_queue/venv/bin"
    ExecStart=/home/ec2-user/hospital_queue/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 app:app

    [Install]
    WantedBy=multi-user.target
    ```

22. Start and enable the Gunicorn service:
    ```
    sudo systemctl start hospital_queue
    sudo systemctl enable hospital_queue
    ```

23. Check the status of the Gunicorn service:
    ```
    sudo systemctl status hospital_queue
    ```

Now, your Flask application should be running with Gunicorn, and Nginx should be set up to proxy requests to Gunicorn. You should be able to access your application by navigating to your EC2 instance's public IP address in a web browser.

Remember to replace "your-instance-public-ip" with your actual EC2 instance's public IP address when connecting via SSH.

Also, don't forget to set up your environment variables for sensitive information like API endpoints:

```
export API_ENDPOINT="https://your-api-gateway-url"
```

You may want to add this to your `.bashrc` file or the systemd service file for persistence.

This setup provides a basic working environment. For a production deployment, you'd want to consider additional security measures, HTTPS configuration, and possibly using a domain name instead of the raw IP address.