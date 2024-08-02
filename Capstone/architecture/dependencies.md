Based on the proof of concept we've discussed, here's a list of dependencies you should include in your `requirements.txt` file:

```
Flask==2.3.2
requests==2.31.0
gunicorn==20.1.0
boto3==1.28.0
```

Let me break down why each of these is necessary:

1. Flask: This is the web framework we're using for the frontend.

2. requests: This library is used to make HTTP requests from your Flask app to the API Gateway.

3. gunicorn: This is the WSGI HTTP server that will run your Flask application in production on EC2.

4. boto3: This is the AWS SDK for Python, which is used in the Lambda functions to interact with DynamoDB.

You might also want to include:

```
python-dotenv==1.0.0
```

This is useful for loading environment variables from a .env file, which is a good practice for managing configuration.

For your Lambda functions, you typically don't need to include boto3 in the requirements as it's already available in the Lambda execution environment. However, if you're testing your Lambda functions locally, you'll need boto3.

Remember to specify the versions of the packages as I've done above. This ensures that your application works with the versions you've tested it with. You can get the latest versions of these packages at the time you're setting up your project.

Also, it's a good practice to create a virtual environment for your project and install these dependencies there. You can do this with:

```
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt
```

This keeps your project dependencies isolated from your global Python installation.