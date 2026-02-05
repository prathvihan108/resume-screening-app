import re
from pypdf import PdfReader

class ResumeParser:
    def __init__(self):
        # Keywords to identify major resume sections
        self.patterns = {
            "skills": r"(?i)\b(skills|technical skills|technologies|tools|competencies)\b",
            "experience": r"(?i)\b(experience|work history|employment|professional experience)\b",
            "education": r"(?i)\b(education|academic background|qualifications)\b"
        }

    def extract_context_summary(self, text):
        """Extracts a dense summary for better semantic search."""
        # Regex for 'X years of experience'
        exp_match = re.search(r"(\d+)\+?\s*(years?|yrs?)", text, re.IGNORECASE)
        experience = exp_match.group(0) if exp_match else "Experience not specified"
        
        # Look for common Indian tech hubs 
        cities = ["Bengaluru", "Bangalore", "Pune", "Mumbai", "Hyderabad", "Delhi", "Chennai", "Gurgaon"]
        found_city = "Remote/Unknown"
        for city in cities:
            if city.lower() in text.lower():
                found_city = city
                break
                
        return {"location": found_city, "experience_years": experience}

    def extract_raw_text(self, pdf_file):
        """Extracts text from PDF pages and joins them."""
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text

    def segment_resume(self, text):
        """Simple sectioning logic based on header detection."""
        lines = text.split('\n')
        extracted_sections = {"skills": [], "experience": [], "education": [], "other": []}
        current_section = "other"

        for line in lines:
            clean_line = line.strip()
            if not clean_line: continue
            
            # Check if this line is a section header
            header_found = False
            for section, pattern in self.patterns.items():
                if re.search(pattern, clean_line) and len(clean_line) < 30:
                    current_section = section
                    header_found = True
                    break
            
            if not header_found:
                extracted_sections[current_section].append(clean_line)

        # Join lines back into strings
        return {k: " ".join(v) for k, v in extracted_sections.items()}