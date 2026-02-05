import requests
import time

class OnlineEmbedder:
    def __init__(self, token):
       
        self.api_url = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"
        self.headers = {"Authorization": f"Bearer {token}"}

    def generate_vector(self, text):
        if not text:
           
            return [0.0] * 384
            
        payload = {
            "inputs": text, 
            "options": {"wait_for_model": True}
        }
        
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            # Feature extraction returns a nested list: [[0.1, 0.2, ...]]
            
            if isinstance(result, list) and len(result) > 0:
                return result[0] if isinstance(result[0], list) else result
            return result
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return [0.0] * 384