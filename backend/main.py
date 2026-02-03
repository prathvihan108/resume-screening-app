from fastapi import FastAPI
from .services.endee_client import EndeeClient

app = FastAPI(title="Resume Screening AI - Backend")
# Initialize the client (connecting to your running Docker engine)
db_client = EndeeClient()

@app.get("/")
def read_root():
    return {"status": "Backend is running"}

@app.get("/test-connection")
def test_connection():
    is_alive = db_client.check_health()
    if is_alive:
        return {
            "database_connection": "Success",
            "message": "Connected to Endee Engine on port 8080"
        }
    return {
        "database_connection": "Failed",
        "message": "Cannot reach the Docker engine. Is 'docker compose up' running?"
    }