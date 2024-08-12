#!/bin/bash

# Update the system
sudo apt update && sudo apt upgrade -y

# Install Java (Jenkins requires Java to run)
sudo apt install openjdk-11-jdk -y

# Add Jenkins repository key
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo tee \
  /usr/share/keyrings/jenkins-keyring.asc > /dev/null

# Add Jenkins repository
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null

# Update package list
sudo apt update

# Install Jenkins
sudo apt install jenkins -y

# Start Jenkins service
sudo systemctl start jenkins

# Enable Jenkins to start on boot
sudo systemctl enable jenkins

# Print initial admin password
echo "Initial Admin Password:"
sudo cat /var/lib/jenkins/secrets/initialAdminPassword

# Print Jenkins status
sudo systemctl status jenkins

# Print public IP address (assumes AWS EC2 instance)
echo "Your server's public IP address is:"
curl -s http://169.254.169.254/latest/meta-data/public-ipv4

echo "Jenkins installation complete. Access it via http://YOUR_SERVER_PUBLIC_IP:8080"