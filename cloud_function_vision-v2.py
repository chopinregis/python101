from google.cloud import storage
import uuid

def create_bucket_and_file(request):
    # Initialize the client
    storage_client = storage.Client()

    # Generate a unique bucket name
    bucket_name = f"my-new-bucket-{uuid.uuid4()}"

    try:
        # Create the new bucket
        bucket = storage_client.create_bucket(bucket_name)
        print(f"Bucket {bucket.name} created.")

        # Create a new blob (file) in the bucket
        blob = bucket.blob("hello.txt")

        # Write content to the file
        blob.upload_from_string("Hello, World! This is a test file.")
        print(f"File hello.txt created and written to {bucket.name}.")

        return f"Bucket {bucket.name} created with file hello.txt", 200
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"Error: {str(e)}", 500
    

"""
Above is a Python script for a Google Cloud Function that creates a new bucket, creates a file within that bucket, and writes some content to the file. Here's the code:

```python
from google.cloud import storage
import uuid

def create_bucket_and_file(request):
    # Initialize the client
    storage_client = storage.Client()

    # Generate a unique bucket name
    bucket_name = f"my-new-bucket-{uuid.uuid4()}"

    try:
        # Create the new bucket
        bucket = storage_client.create_bucket(bucket_name)
        print(f"Bucket {bucket.name} created.")

        # Create a new blob (file) in the bucket
        blob = bucket.blob("hello.txt")

        # Write content to the file
        blob.upload_from_string("Hello, World! This is a test file.")
        print(f"File hello.txt created and written to {bucket.name}.")

        return f"Bucket {bucket.name} created with file hello.txt", 200
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"Error: {str(e)}", 500

```

Here's an explanation of what this code does:

1. We import the necessary libraries: `google.cloud.storage` for interacting with Google Cloud Storage, and `uuid` for generating a unique bucket name.

2. We define a function `create_bucket_and_file` that will be our Cloud Function's entry point.

3. Inside the function:
   - We initialize a Storage client.
   - We generate a unique bucket name using UUID to avoid naming conflicts.
   - We create a new bucket with this name.
   - We create a new blob (file) named "hello.txt" in this bucket.
   - We write the content "Hello, World! This is a test file." to this file.

4. If everything is successful, we return a success message with a 200 status code.

5. If an error occurs at any point, we catch the exception, print it, and return an error message with a 500 status code.

To deploy this Cloud Function:

1. Save this code in a file, for example, `main.py`.

2. Create a `requirements.txt` file in the same directory with the following content:
   ```
   google-cloud-storage
   ```

3. Deploy the function using the gcloud CLI:
   ```
   gcloud functions deploy create_bucket_and_file \
     --runtime python39 \
     --trigger-http \
     --allow-unauthenticated
   ```

This creates an HTTP-triggered function. When called, it will create a new bucket with a unique name, create a file named "hello.txt" in that bucket, and write a simple message to it.

Note: Ensure that the service account running this function has the necessary permissions to create buckets and write to them in your Google Cloud project.
"""