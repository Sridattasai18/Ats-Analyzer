# ATS Resume Analyzer

> **Industrial-grade ATS resume analysis powered by Google Gemini AI.** Upload your resume for an instant ATS compatibility audit — optionally add a job description for detailed match scoring.

---

## ⚡ Features

- **PDF Resume Parsing** — Extracts text from uploaded PDF resumes
- **Standalone ATS Audit** — Resume quality check that runs with or without a job description
- **AI-Powered Job Matching** — Uses Google Gemini to compare resume vs job description
- **Dual Scoring System**:
  - **ATS Compatibility Score** — How well your resume parses through ATS systems
  - **Job Match Score** — How well your resume matches a specific job (when JD provided)
- **Keyword Detection** — Identifies matching and missing skills
- **Actionable Recommendations** — Specific fixes to optimize your resume
- **Graceful Error Handling** — Handles API limits, overload, and missing inputs

---

## 📊 How It Works

### Architecture
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  User Uploads   │────▶│  Flask Backend  │────▶│   Gemini AI     │
│  Resume (+JD)   │     │  (main.py)      │     │  (Analysis)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │  ATS Scores +   │
                        │  Recommendations│
                        └─────────────────┘
```

### Scoring Methodology (100 Points)

#### 🔹 Job Match Score (When JD Provided)
| Category | Max Points | What It Measures |
|----------|------------|------------------|
| Keyword Match | 40 | Overlap between resume and JD keywords |
| Skills Alignment | 25 | Required & preferred skills coverage |
| Experience Relevance | 20 | Role, years, and industry match |
| Qualifications | 15 | Education and certifications |

| Score | Verdict |
|-------|---------|
| 80–100 | **STRONG MATCH** |
| 70–79 | **GOOD MATCH** |
| 50–69 | **NEEDS IMPROVEMENT** |
| 0–49 | **POOR MATCH** |

#### 🔎 Standalone ATS Audit (Always Active)
| Category | Max Points | Checks |
|----------|------------|--------|
| Format & Structure | 30 | ATS-friendly layout, no tables |
| Contact Info | 15 | Name, email, phone, LinkedIn |
| Content Quality | 30 | Action verbs, measurable results |
| Section Completeness | 25 | Experience, Education, Skills |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.x, Flask |
| AI Engine | Google Gemini API (`gemini-2.5-flash`) |
| Frontend | HTML, CSS (Industrial Terminal UI), Vanilla JS |
| PDF Parser | PyPDF2 |

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Sridattasai18/Ats-Analyzer.git
cd Ats-Analyzer
```

### 2. Create & Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Key
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_api_key_here
```
> 🔑 Get your free API key from [Google AI Studio](https://aistudio.google.com/)

### 5. Run the Application
```bash
python main.py
```

### 6. Open in Browser
Navigate to: **`http://127.0.0.1:5000`**

---

## 📖 How to Use

1. **Upload** — Drop or select your PDF resume
2. **Paste (Optional)** — Enter a job description for match analysis
3. **Analyze** — Click `[ INITIATE ANALYSIS ]`
4. **Review** — Check your scores:
   - **With JD**: Get match percentage + keyword analysis
   - **Without JD**: Get standalone ATS compatibility audit

---

## 📁 Project Structure

```
Ats-Analyzer/
├── main.py              # Flask backend with Gemini integration
├── requirements.txt     # Python dependencies
├── Procfile             # Render/Heroku start command
├── render.yaml          # Render deployment config
├── vercel.json          # Vercel deployment config
├── .env                 # API key (not committed)
├── .gitignore
├── uploads/             # Temporary PDF storage
└── templates/
    └── index.html       # Industrial terminal-style UI
```

---

## 🚀 Deploy to Render

1. Push your code to GitHub
2. Go to [render.com](https://render.com) and create a new **Web Service**
3. Connect your GitHub repo
4. Render will auto-detect `render.yaml` or use these settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn main:app`
5. Add environment variable: `GEMINI_API_KEY` = your API key
6. Deploy!

---

## ⚠️ Troubleshooting

| Error | Solution |
|-------|----------|
| `503 UNAVAILABLE` | Gemini API overloaded — retry automatically handled, or wait 30s |
| `429 RESOURCE_EXHAUSTED` | API quota exceeded — wait or upgrade plan |
| `API key not configured` | Add GEMINI_API_KEY to .env file and restart |
| `Could not extract text` | PDF may be scanned/image-based — use text-based PDF |

---

## 🎯 Summary

**This ATS Resume Analyzer evaluates resumes using real ATS-style logic, provides standalone ATS compatibility scores, and optionally compares resumes against job descriptions to deliver clear, actionable feedback for job seekers.**

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👤 Author

**Kaligotla Sri Datta Sai**  
GitHub: [@Sridattasai18](https://github.com/Sridattasai18)
