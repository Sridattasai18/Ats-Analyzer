import os
import json
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
else:
    print("API Key loaded: NO")
    raise RuntimeError("API key not found. Set GEMINI_API_KEY or GOOGLE_API_KEY in .env")

client = genai.Client(api_key=GEMINI_API_KEY)


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


import time

def gemini_json(prompt, max_retries=3):
    """Call Gemini API with automatic retry on overload/rate-limit errors."""
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


def ats_match(parsed_resume, parsed_jd):
    prompt = f"""
You are a professional Applicant Tracking System (ATS).

Return ONLY valid JSON.

Schema:
{{
  "match_percentage": 0,
  "matching_skills": [],
  "missing_skills": [],
  "strengths": [],
  "improvement_suggestions": []
}}

Resume:
{json.dumps(parsed_resume, indent=2)}

Job Description:
{json.dumps(parsed_jd, indent=2)}
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
        jd_text = request.form.get("job_description")

        if not jd_text:
            return jsonify({"error": "Job description is required"}), 400

        if resume_file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(resume_file.filename):
            return jsonify({"error": "Only PDF files are allowed"}), 400

        filename = secure_filename(resume_file.filename)
        pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        resume_file.save(pdf_path)

        resume_text = extract_text_from_pdf(pdf_path)
        if not resume_text:
            return jsonify({"error": "Could not extract text from PDF"}), 400

        parsed_resume = parse_resume(resume_text)
        parsed_jd = parse_job_description(jd_text)
        ats_result = ats_match(parsed_resume, parsed_jd)

        # Optional cleanup
        os.remove(pdf_path)

        return jsonify({
            "parsed_resume": parsed_resume,
            "parsed_job_description": parsed_jd,
            "ats_result": ats_result
        })

    except Exception as e:
        # Specific handling for Gemini quota exhaustion
        error_str = str(e)
        if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
            return jsonify({
                "error": "Gemini API quota exceeded. Please wait a few minutes and try again, or upgrade your plan."
            }), 429
        return jsonify({"error": error_str}), 500


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
