# ATS Resume Analyzer

A simple web application that acts as an Applicant Tracking System (ATS). It analyzes a resume against a job description and provides a match score and suggestions for improvement.

## Features

- Upload a resume in PDF format.
- Paste a job description.
- Get an ATS score based on the match between the resume and the job description.
- Identify matching and missing keywords.
- Receive suggestions to improve your resume for the specific job.

## Tech Stack

- **Backend:** Python, Flask
- **AI:** Google Gemini API
- **Frontend:** HTML, CSS, JavaScript
- **PDF Parsing:** PyPDF2

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd ATS-proj
    ```

2.  **Install dependencies:**
    Make sure you have Python 3.6+ installed.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Create a file named `.env` in the root of the project and add your Google Gemini API key:
    ```
    GEMINI_API_KEY="your_api_key_here"
    ```
    You can get your API key from [Google AI Studio](https://aistudio.google.com/).

4.  **Run the application:**
    ```bash
    python main.py
    ```

5.  **Access the application:**
    Open your web browser and navigate to `http://127.0.0.1:5000`.

## How to Use

1.  Open the web application in your browser.
2.  Click on "Browse" or "Choose PDF resume" to upload your resume in PDF format.
3.  Paste the job description into the text area.
4.  Click the "Analyze" button.
5.  The application will process the documents and display the ATS score, insights, and suggestions.
