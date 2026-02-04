import io
from fastapi import FastAPI, UploadFile, File  
from .services.endee_client import EndeeClient
from .core.parser import ResumeParser
from .core.embedder import OnlineEmbedder

HF_TOKEN = "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"
embedder = OnlineEmbedder(token=HF_TOKEN)

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

# Processing and embedding endpoint

@app.post("/process-and-embed")
async def process_and_embed(file: UploadFile = File(...)):
    # 1. Parse
    content = await file.read()
    raw_text = parser.extract_raw_text(io.BytesIO(content))
    structured_data = parser.segment_resume(raw_text)
    
 
    # We embed the 'skills' section as it is the most important for screening
    text_to_embed = structured_data["skills"] if structured_data["skills"] else raw_text[:500]
    vector = embedder.generate_vector(text_to_embed)
    
    return {
        "filename": file.filename,
        "vector_dimensions": len(vector),
        "vector_sample": vector[:5], 
        "status": "Ready for Endee Database"
    }