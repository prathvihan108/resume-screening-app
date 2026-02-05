from endee import Endee, Precision #
import uuid

class EndeeClient:



    def __init__(self):
        # Connects to your Docker container at localhost:8080
        self.client = Endee()
        self.index_name = "resumes"

    def initialize_collection(self):
        """Official production method to check and create indices."""
        try:
            # Step 1: Check if index exists by trying to 'get' it
            try:
                self.client.get_index(name=self.index_name)
                print(f"--- Index '{self.index_name}' verified in Production DB! ---")
                return # Index exists, we are done
            except Exception:
                # Step 2: If 'get_index' fails, it likely doesn't exist yet
                print(f"--- Index not found. Creating {self.index_name}... ---")
                self.client.create_index(
                    name=self.index_name,
                    dimension=384,
                    space_type="cosine",
                    precision=Precision.INT8D
                )
                print(f"--- SUCCESS: Production index created! ---")

        except Exception as e:
            # If even the creation fails, we need to know why
            print(f"--- Critical SDK Error: {e} ---")
    

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

    import uuid

    def insert_resume(self, filename, vector, metadata):
        """
        Matches official Endee SDK 'upsert' pattern.
        """
        try:
            # 1. Get the index object first, as shown in the docs
            index = self.client.get_index(name=self.index_name)
            

            data_to_upsert = [
                {
                    "id": str(uuid.uuid4()),  
                    "vector": vector,         
                    "meta": {                 
                        "filename": filename,
                        **metadata            
                    }
                }
            ]
            
        
            index.upsert(data_to_upsert)
            
            print(f"--- Success: {filename} uploaded to Endee Production! ---")
            return True

        except Exception as e:
            print(f"--- SDK Upsert Error for {filename}: {e} ---")
            return False


    def search_resumes(self, query_vector, top_k=5):
        """
        Matches official docs for high-precision querying.
        """
        try:
            index = self.client.get_index(name=self.index_name)
            
            # Passing ef=128 for better accuracy and including vectors
            results = index.query(
                vector=query_vector,
                top_k=top_k,
                ef=128,
                include_vectors=True
            )
            
            return results
        except Exception as e:
            print(f"--- Search Error: {e} ---")
            return []