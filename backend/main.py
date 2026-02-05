import io
import os
from fastapi import FastAPI, UploadFile, File  
from .services.endee_client import EndeeClient
from .core.parser import ResumeParser
from .core.embedder import OnlineEmbedder
from typing import List
from dotenv import load_dotenv

load_dotenv()

# 2. Get the token from the environment
HF_TOKEN = os.getenv("HF_TOKEN")



embedder = OnlineEmbedder(token=HF_TOKEN)

app = FastAPI(title="Resume Screening AI - Backend")
parser = ResumeParser()

db_client = EndeeClient()

# This runs the moment 'uvicorn' starts the app
@app.on_event("startup")
async def startup_event():
    
    db_client.initialize_collection()

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

#Getting the no of resumes in the database

@app.get("/db-stats")
async def get_db_stats():
    # Asks Endee-09 how many vectors are in the 'resumes' collection
    url = "http://localhost:8080/collections/resumes"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return {"error": "Could not connect to Endee engine"}

# multiple files upload and process

@app.post("/upload-batch")
async def upload_batch(files: List[UploadFile] = File(...)):
    report = []
    
    for file in files:
        try:
            # 1. Read and Parse
            content = await file.read()
            raw_text = parser.extract_raw_text(io.BytesIO(content))
            structured_data = parser.segment_resume(raw_text)
            
            # --- NEW: Extract Contextual Data ---
            # We scan the raw text for city names and years of experience
            cities = ["Bengaluru", "Bangalore", "Pune", "Mumbai", "Hyderabad", "Delhi", "Chennai"]
            detected_city = "Not Specified"
            for city in cities:
                if city.lower() in raw_text.lower():
                    detected_city = city
                    break
            
            # Simple regex to find experience (e.g., "5 years", "3+ yrs")
            import re
            exp_match = re.search(r"(\d+)\+?\s*(years?|yrs?)", raw_text, re.IGNORECASE)
            exp_years = exp_match.group(0) if exp_match else "Not Specified"

            # 2. Vectorize (Using "Rich Text" for Context)
            # We combine skills, city, and experience into one sentence.
            # This allows the AI to "map" the resume to multi-part queries.
            text_to_embed = (
                f"Candidate Skills: {structured_data['skills']}. "
                f"Location: {detected_city}. "
                f"Experience: {exp_years}."
            )
            vector = embedder.generate_vector(text_to_embed)
            
            # 3. Store in Endee
            success = db_client.insert_resume(
                filename=file.filename,
                vector=vector,
                metadata={
                    "skills": structured_data["skills"],
                    "experience_text": structured_data["experience"], # Full segment
                    "detected_location": detected_city,               # Searchable meta
                    "years_of_experience": exp_years                  # Searchable meta
                }
            )

            if success:
                report.append({"file": file.filename, "status": "Success"})
            else:
                report.append({"file": file.filename, "status": "Database Push Failed"})
        
        except Exception as e:
            report.append({"file": file.filename, "status": f"Error: {str(e)}"})
            
    return {"summary": report, "total_processed": len(report)}
@app.get("/search")
async def search_resumes(query: str, top_k: int = 5):
    # 1. Generate vector from user search string
    query_vector = embedder.generate_vector(query)
    
    # 2. Get results from SDK
    results = db_client.search_resumes(query_vector, top_k=top_k)
    
    # 3. Format exactly as the docs suggest
    formatted_results = []
    for item in results:
        formatted_results.append({
            "id": item['id'],               
            "score": item['similarity'],   
            "metadata": item.get('meta'),  
            "vector_returned": "True" if 'vector' in item else "False"
        })
        
    return {"results": formatted_results}