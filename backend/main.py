import io
from fastapi import FastAPI, UploadFile, File  
from .services.endee_client import EndeeClient
from .core.parser import ResumeParser

app = FastAPI(title="Resume Screening AI - Backend")
parser = ResumeParser()

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

@app.post("/parse")
async def parse_resume(file: UploadFile = File(...)):
    # Read the file into memory
    content = await file.read()
    pdf_stream = io.BytesIO(content)
    
    # Extract and Segment
    raw_text = parser.extract_raw_text(pdf_stream)
    structured_data = parser.segment_resume(raw_text)
    
    return {
        "filename": file.filename,
        "segments": {
            "skills_preview": structured_data["skills"][:200],
            "experience_preview": structured_data["experience"][:200]
        },
        "full_text_length": len(raw_text)
    }