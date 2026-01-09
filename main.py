import os
import json
import time
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from google import genai
import PyPDF2
from werkzeug.utils import secure_filename

# ==============================
# LOAD ENV
# ==============================
from pathlib import Path
env_path = Path(__file__).parent / ".env"
if env_path.is_file():
    load_dotenv(dotenv_path=env_path)
    print("Loaded .env from", env_path)
else:
    print("No .env file found at", env_path)

# ==============================
# CONFIG
# ==============================
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Try both possible API key names
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if GEMINI_API_KEY:
    print("API Key loaded: YES (length:", len(GEMINI_API_KEY), ")")
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    print("API Key loaded: NO - App will start but analysis will be unavailable")
    print("To enable analysis, set GEMINI_API_KEY or GOOGLE_API_KEY in .env")
    client = None


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ==============================
# HOME ROUTE (NEW)
# ==============================
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


# ==============================
# UTILS
# ==============================
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(pdf_path):
    extracted_text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text
    return extracted_text.strip()


# Retry logic uses 'time' module imported at top

def gemini_json(prompt, max_retries=3):
    """Call Gemini API with automatic retry on overload/rate-limit errors."""
    if client is None:
        raise ValueError("API key not configured. Please add GEMINI_API_KEY to your .env file.")
    
    last_error = None
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            text = response.text
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            
            # Try direct parse
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                # Fallback: find JSON substring
                start = text.find('{')
                end = text.rfind('}')
                if start != -1 and end != -1:
                    return json.loads(text[start:end+1])
                raise ValueError("Gemini did not return valid JSON: " + text)
                
        except Exception as e:
            last_error = e
            error_str = str(e).lower()
            # Retry on overload (503) or rate limit (429)
            if "503" in error_str or "overloaded" in error_str or "429" in error_str or "resource_exhausted" in error_str:
                wait_time = (2 ** attempt) + 1  # 2s, 3s, 5s backoff
                print(f"[RETRY {attempt+1}/{max_retries}] Gemini overloaded. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                raise  # Non-retryable error
    
    # All retries exhausted
    raise last_error


# ==============================
# PARSERS
# ==============================
def parse_resume(resume_text):
    prompt = f"""
You are a resume parser.

Return ONLY valid JSON.

Schema:
{{
  "skills": [],
  "experience_summary": "",
  "education": [],
  "tools_and_technologies": []
}}

Resume:
\"\"\"{resume_text}\"\"\"
"""
    return gemini_json(prompt)


def parse_job_description(jd_text):
    prompt = f"""
You are a job description parser.

Return ONLY valid JSON.

Schema:
{{
  "required_skills": [],
  "responsibilities": [],
  "preferred_qualifications": []
}}

Job Description:
\"\"\"{jd_text}\"\"\"
"""
    return gemini_json(prompt)


def resume_ats_audit(resume_text):
    """Standalone ATS audit of resume quality - independent of job description."""
    prompt = f"""
You are an expert ATS (Applicant Tracking System) auditor.

Analyze this resume for ATS COMPATIBILITY issues. This is NOT about job matching - this is about whether the resume will PARSE CORRECTLY through ATS software.

## AUDIT CRITERIA (100 points total):

### 1. FORMAT & STRUCTURE (30 points)
- Clean section headers (Experience, Education, Skills, etc.): 0-10
- Consistent date formatting: 0-5
- No tables, columns, or complex layouts that break ATS: 0-10
- Standard fonts/no graphics mentioned: 0-5

### 2. CONTACT INFORMATION (15 points)
- Full name present: 0-5
- Email present: 0-5
- Phone present: 0-3
- LinkedIn/Portfolio (bonus): 0-2

### 3. CONTENT QUALITY (30 points)
- Action verbs used: 0-10
- Quantifiable achievements: 0-10
- Keyword density (industry terms): 0-10

### 4. SECTION COMPLETENESS (25 points)
- Work experience section: 0-10
- Education section: 0-5
- Skills section: 0-5
- Summary/objective: 0-5

## IMPORTANT:
- Be STRICT. Point out every flaw.
- Common issues: missing sections, vague descriptions, no metrics, poor formatting

Return ONLY valid JSON:
{{
  "ats_compatibility_score": <0-100>,
  "audit_breakdown": {{
    "format_structure": <0-30>,
    "contact_info": <0-15>,
    "content_quality": <0-30>,
    "section_completeness": <0-25>
  }},
  "detected_sections": ["section1", "section2", ...],
  "missing_sections": ["section1", ...],
  "formatting_issues": ["issue1", "issue2", ...],
  "content_issues": ["issue1", "issue2", ...],
  "strengths": ["strength1", ...],
  "critical_flaws": ["flaw1", "flaw2", ...],
  "recommendations": ["specific fix 1", "specific fix 2", ...],
  "ats_parse_risk": "<LOW | MEDIUM | HIGH>"
}}

## RESUME TO AUDIT:
\"\"\"{resume_text}\"\"\"

Perform thorough audit and return JSON.
"""
    return gemini_json(prompt)


def ats_match(parsed_resume, parsed_jd):
    prompt = f"""
You are a professional Applicant Tracking System (ATS) used by Fortune 500 companies.

Your task is to score a resume against a job description using STRICT ATS criteria.

## SCORING METHODOLOGY (100 points total):

### 1. KEYWORD MATCH (40 points)
- Count exact keyword matches between resume and job description
- Include: technical skills, tools, certifications, industry terms
- Score = (matched keywords / total required keywords) × 40

### 2. SKILLS ALIGNMENT (25 points)  
- Required skills present: +5 points each (max 15)
- Preferred/bonus skills present: +2 points each (max 10)
- Deduct 3 points for each CRITICAL missing skill

### 3. EXPERIENCE RELEVANCE (20 points)
- Relevant job titles/roles: 0-8 points
- Years of experience alignment: 0-6 points
- Industry experience match: 0-6 points

### 4. QUALIFICATIONS MATCH (15 points)
- Education level match: 0-8 points
- Certifications match: 0-7 points

## IMPORTANT RULES:
- Be STRICT. Real ATS systems reject 75% of resumes.
- A score of 70+ is considered a GOOD match.
- A score below 50 means the resume needs significant work.
- Do NOT inflate scores to be nice.

Return ONLY valid JSON with this exact schema:
{{
  "match_percentage": <0-100 integer based on above methodology>,
  "score_breakdown": {{
    "keyword_match": <0-40>,
    "skills_alignment": <0-25>,
    "experience_relevance": <0-20>,
    "qualifications_match": <0-15>
  }},
  "matching_skills": ["skill1", "skill2", ...],
  "missing_skills": ["critical_skill1", "critical_skill2", ...],
  "keyword_analysis": {{
    "found": ["keyword1", "keyword2", ...],
    "missing": ["keyword1", "keyword2", ...]
  }},
  "strengths": ["strength1", "strength2", ...],
  "weaknesses": ["weakness1", "weakness2", ...],
  "improvement_suggestions": [
    "Specific actionable suggestion 1",
    "Specific actionable suggestion 2",
    ...
  ],
  "ats_verdict": "<STRONG MATCH | GOOD MATCH | NEEDS IMPROVEMENT | POOR MATCH>"
}}

## INPUT DATA:

### RESUME:
{json.dumps(parsed_resume, indent=2)}

### JOB DESCRIPTION:
{json.dumps(parsed_jd, indent=2)}

Analyze thoroughly and return the JSON score.
"""
    return gemini_json(prompt)


# ==============================
# ANALYZE ROUTE (POST ONLY)
# ==============================
@app.route("/analyze", methods=["POST"], strict_slashes=False)
def analyze():
    try:
        if "resume" not in request.files:
            return jsonify({"error": "Resume PDF is required"}), 400

        resume_file = request.files["resume"]
        jd_text = request.form.get("job_description", "").strip()  # Optional now

        if resume_file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(resume_file.filename):
            return jsonify({"error": "Only PDF files are allowed"}), 400

        filename = secure_filename(resume_file.filename)
        pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        resume_file.save(pdf_path)

        try:
            resume_text = extract_text_from_pdf(pdf_path)
            if not resume_text:
                return jsonify({"error": "Could not extract text from PDF. The file may be scanned or image-based."}), 400

            # Parse resume (always required)
            parsed_resume = parse_resume(resume_text)
            
            # Resume ATS Audit (ALWAYS runs - standalone quality check)
            resume_audit = resume_ats_audit(resume_text)
            
            # Job Description matching (OPTIONAL - only if JD provided)
            if jd_text:
                parsed_jd = parse_job_description(jd_text)
                ats_result = ats_match(parsed_resume, parsed_jd)
                jd_provided = True
            else:
                parsed_jd = None
                ats_result = None
                jd_provided = False

            return jsonify({
                "jd_provided": jd_provided,
                "parsed_resume": parsed_resume,
                "parsed_job_description": parsed_jd,
                "resume_audit": resume_audit,  # Always present - standalone ATS quality
                "ats_result": ats_result        # Only present if JD was provided
            })
        finally:
            # Always cleanup uploaded file
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

    except ValueError as ve:
        # Handle API key not configured
        error_str = str(ve)
        if "API key not configured" in error_str:
            return jsonify({
                "error": "API key not configured. Please add your GEMINI_API_KEY to the .env file and restart the server."
            }), 503
        return jsonify({"error": error_str}), 400

    except Exception as e:
        # Specific handling for Gemini quota exhaustion
        error_str = str(e)
        if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
            return jsonify({
                "error": "API quota exceeded. Please wait a few minutes and try again."
            }), 429
        elif "503" in error_str or "overloaded" in error_str.lower():
            return jsonify({
                "error": "AI service is temporarily overloaded. Please try again in a moment."
            }), 503
        elif "JSON" in error_str or "parse" in error_str.lower():
            return jsonify({
                "error": "Failed to parse AI response. Please try again."
            }), 500
        return jsonify({"error": f"Analysis failed: {error_str}"}), 500


# ==============================
# GLOBAL ERROR HANDLERS
# ==============================
@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error. Please try again."}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found."}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed. Use POST for /analyze."}), 405

@app.errorhandler(Exception)
def handle_exception(e):
    error_str = str(e)
    if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
        return jsonify({
            "error": "Gemini API quota exceeded. Please wait a few minutes and try again."
        }), 429
    return jsonify({"error": error_str}), 500


# ==============================
# ENTRY POINT
# ==============================
# For Vercel serverless, the 'app' variable is used directly
# For local development, run with: python main.py
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
