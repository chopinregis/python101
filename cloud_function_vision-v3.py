from google.cloud import storage
import uuid

def create_bucket_and_file(request):
    storage_client = storage.Client()
    
    unique_id = uuid.uuid4()
    bucket_name = "my-new-bucket-" + str(unique_id)
    
    try:
        new_bucket = storage_client.create_bucket(bucket_name)
        print("I made a new bucket called: " + new_bucket.name)
        
        new_file = new_bucket.blob("hello.txt")
        
        new_file.upload_from_string("Hello, World! This is a test file.")
        print("I made a file called hello.txt in the bucket: " + new_bucket.name)
        
        return "I made a bucket called " + new_bucket.name + " with a file called hello.txt", 200
    
    except:
        print("Oops, something went wrong!")
        return "Error occurred", 500

if __name__ == "__main__":
    create_bucket_and_file(None)
    

