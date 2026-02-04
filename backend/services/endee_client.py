import requests
import uuid

class EndeeClient:
    def __init__(self, host="localhost", port=8080):
        self.base_url = f"http://{host}:{port}/api/v1"

    
    def initialize_collection(self):
        """Checks if the 'resumes' collection exists; creates it if not."""
        collection_url = f"{self.base_url}/collections/resumes"
        
        # 1. Check if collection exists
        response = requests.get(collection_url)
        
        if response.status_code == 200:
            print("--- Collection 'resumes' already exists. ---")
            return
        
        # 2. Create collection if it's missing (404)
        print("--- Creating 'resumes' collection (384 dimensions)... ---")
        create_payload = {
            "vectors": {
                "size": 384,          # Must match your Hugging Face model
                "distance": "Cosine"  # Best for resume similarity
            }
        }
        
        create_res = requests.put(collection_url, json=create_payload)
        if create_res.status_code == 200:
            print("--- Collection created successfully! ---")
        else:
            print(f"--- Error creating collection: {create_res.text} ---")

    def check_health(self):
        """Checks if the Dockerized Endee Engine is responding."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            return False

    def get_version(self):
        """Retrieves engine details to confirm connection."""
        try:
            response = requests.get(f"{self.base_url}/version")
            return response.json() if response.status_code == 200 else None
        except:
            return None

    def insert_resume(self, filename, vector, metadata):
        # In Endee-09, we 'PUT' points into a collection
        url = f"{self.base_url}/collections/resumes/points"
        
        payload = {
            "points": [
                {
                    "id": str(uuid.uuid4()), # Generates a unique ID for each resume
                    "vector": vector,
                    "payload": {
                        "filename": filename,
                        **metadata # Unpacks skills and experience
                    }
                }
            ]
        }

        response = requests.put(url, json=payload)
        return response.status_code == 200

