import requests

class EndeeClient:
    def __init__(self, host="localhost", port=8080):
        self.base_url = f"http://{host}:{port}/api/v1"

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