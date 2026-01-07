# ATS_ANALYZER // SYSTEM_ACTIVE

> **Industrial-grade resume analysis.** Upload your resume, paste a job description, and get an instant ATS compatibility score with actionable optimization protocols.

---

## ⚡ Features

- **PDF Resume Parsing** — Extracts text from uploaded PDF resumes
- **AI-Powered Analysis** — Uses Google Gemini to compare resume vs job description
- **Match Score** — Get a percentage-based compatibility index
- **Keyword Detection** — Identifies matching and missing skills
- **Improvement Suggestions** — Actionable recommendations to optimize your resume
- **Retry Logic** — Handles API rate limits and overload gracefully

---

## 🛠 Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Backend    | Python 3.x, Flask                 |
| AI Engine  | Google Gemini API (`gemini-2.5-flash`) |
| Frontend   | HTML, CSS (Industrial Terminal UI), Vanilla JS |
| PDF Parser | PyPDF2                            |

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
2. **Paste** — Enter the target job description
3. **Analyze** — Click `[ INITIATE ANALYSIS ]`
4. **Review** — Check your match score, matching/missing keywords, and optimization suggestions

---

## 📁 Project Structure

```
Ats-Analyzer/
├── main.py              # Flask backend with Gemini integration
├── requirements.txt     # Python dependencies
├── .env                 # API key (not committed)
├── .gitignore
├── uploads/             # Temporary PDF storage
└── templates/
    └── index.html       # Industrial terminal-style UI
```

---

## ⚠️ Troubleshooting

| Error | Solution |
|-------|----------|
| `503 UNAVAILABLE` | Gemini API overloaded — retry automatically handled, or wait 30s |
| `429 RESOURCE_EXHAUSTED` | API quota exceeded — wait or upgrade plan |
| `405 Method Not Allowed` | Ensure you're using POST to `/analyze` |

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👤 Author

**Kaligotla Sri Datta Sai**  
GitHub: [@Sridattasai18](https://github.com/Sridattasai18)
