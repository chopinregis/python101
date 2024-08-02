Certainly! I'll provide you with an outline for a proof of concept of your hospital queue system using EC2 for hosting a dynamic Python-based website, while still utilizing Lambda for backend processing. We'll use Flask as the web framework for this example.

Step-by-step outline:

1. EC2 Setup:
   - Launch an EC2 instance
   - Install necessary software (Python, Flask, Gunicorn, Nginx)
   - Configure security groups to allow HTTP/HTTPS traffic

2. Frontend Development (Flask):
   - Create a Flask application structure
   - Implement routes for different pages
   - Create templates for dynamic content rendering

3. API Gateway and Lambda:
   - Set up API Gateway endpoints
   - Create Lambda functions for backend processing

4. Database:
   - Set up DynamoDB tables for storing user and queue data

5. Connecting Frontend to Backend:
   - Use requests library in Python to make API calls from Flask to API Gateway

Now, let's dive into a more detailed proof of concept:

1. EC2 Setup:

```bash
# Update and install dependencies
sudo apt-get update
sudo apt-get install python3-pip python3-dev nginx
sudo pip3 install flask gunicorn

# Configure Nginx (basic configuration)
sudo nano /etc/nginx/sites-available/default
# Add proxy pass to Gunicorn
```

2. Frontend Development (Flask):

Create a project structure:

```
hospital_queue/
├── app.py
├── templates/
│   ├── index.html
│   ├── form.html
│   └── result.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── script.js
```

`app.py`:

```python
from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

API_ENDPOINT = os.environ.get('API_ENDPOINT')

@app.route('/')
def index():
    # In a real application, you'd fetch this from your database
    hospitals = ['Hospital A', 'Hospital B', 'Hospital C']
    return render_template('index.html', hospitals=hospitals)

@app.route('/form/<hospital>')
def form(hospital):
    return render_template('form.html', hospital=hospital)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.to_dict()
    
    # Make API call to Lambda function via API Gateway
    response = requests.post(f"{API_ENDPOINT}/submit", json=data)
    result = response.json()
    
    return render_template('result.html', result=result)

@app.route('/check_queues')
def check_queues():
    # Make API call to Lambda function to get queue status
    response = requests.get(f"{API_ENDPOINT}/check_queues")
    queues = response.json()
    return jsonify(queues)

if __name__ == '__main__':
    app.run(debug=True)
```

`templates/index.html`:

```html
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
```

`templates/form.html`:

```html
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
```

`templates/result.html`:

```html
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
```

`static/js/script.js`:

```javascript
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
```

3. API Gateway and Lambda:

Set up API Gateway with the following endpoints:
- POST /submit
- GET /check_queues

Lambda function for user submission:

```python
import json
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('HospitalQueue')

def lambda_handler(event, context):
    body = json.loads(event['body'])
    
    user_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    item = {
        'UserId': user_id,
        'Name': body['name'],
        'LastName': body['lastName'],
        'DoB': body['dob'],
        'Hospital': body['hospital'],
        'Symptoms': body['symptoms'],
        'Timestamp': timestamp,
        'QueuePosition': calculate_queue_position(body['symptoms'])
    }
    
    table.put_item(Item=item)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'userId': user_id,
            'queuePosition': item['QueuePosition']
        })
    }

def calculate_queue_position(symptoms):
    # Implement your queue position logic here
    if 'emergency' in symptoms.lower():
        return 1
    return 10  # Default position
```

Lambda function for checking queues:

```python
import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('HospitalQueue')

def lambda_handler(event, context):
    hospitals = ['Hospital A', 'Hospital B', 'Hospital C']
    queue_lengths = {}
    
    for hospital in hospitals:
        response = table.query(
            IndexName='HospitalIndex',
            KeyConditionExpression=Key('Hospital').eq(hospital)
        )
        queue_lengths[hospital] = len(response['Items'])
    
    return {
        'statusCode': 200,
        'body': json.dumps(queue_lengths)
    }
```

4. Database:

Create a DynamoDB table named 'HospitalQueue' with primary key 'UserId' and a Global Secondary Index on 'Hospital'.

5. Deployment:

Deploy your Flask application on EC2:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

Configure Nginx to proxy requests to Gunicorn.

This proof of concept provides a dynamic website hosted on EC2 using Flask, with Lambda functions handling the backend processing. The front-end flow allows users to select a hospital, fill out a form, submit their information, receive a queue position, and check alternatives if desired.

Remember to implement proper error handling, input validation, and security measures in a production environment. Also, consider using environment variables for sensitive information and implementing proper user authentication and authorization.