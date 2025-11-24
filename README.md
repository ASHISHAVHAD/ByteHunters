# ByteHunters - Automated Fact Verification System

## Project Overview

ByteHunters is a web-based automated fact verification system designed to combat digital misinformation. The application allows users to input web URLs or raw text, from which it extracts factual claims, cross-references them against trusted internet sources using Large Language Models (Google Gemini), and provides a detailed credibility assessment. The system includes features for user authentication, historical data tracking, statistical insights, and downloadable PDF reporting.

## Features

*   **Multi-Modal Input:** Accepts both direct website URLs and raw text blocks for analysis.
*   **Automated Web Scraping:** Intelligent extraction of relevant text from web pages, stripping away navigation, scripts, and non-essential content.
*   **LLM-Powered Verification:** Utilizes Google Gemini 2.5 Flash to extract claims, perform semantic reasoning, and assign validity verdicts (True, False, Uncertain).
*   **Source Citations:** Provides direct links to the web sources used to verify each claim along with a credibility score.
*   **User Dashboard:** A personal dashboard for users to view, manage, and delete their verification history.
*   **Global Insights:** An analytics page visualizing data trends, including misinformation statistics and confidence/credibility correlations using Chart.js.
*   **PDF Reporting:** Generation of professional-grade PDF reports containing validity distribution charts and detailed claim analysis.
*   **Secure Authentication:** User signup and login system with password hashing.

## Technology Stack

*   **Backend Framework:** Python Flask
*   **Database:** MySQL
*   **AI/LLM Provider:** Google GenAI (Gemini 2.5 Flash)
*   **Frontend:** HTML5, CSS3, JavaScript
*   **Visualization:** Chart.js, Matplotlib (server-side for PDFs)
*   **PDF Generation:** ReportLab
*   **Web Scraping:** BeautifulSoup4, Requests

## Project Structure and File Organization

The project follows a modular architecture to separate concerns between routing, utility logic, and frontend presentation.

```text
/project-root
├── app.py                  # Main application entry point and route controller
├── .env                    # Environment variables (API keys, DB credentials)
├── requirements.txt        # Python dependencies list
│
├── utils/                  # Backend utility modules
│   ├── __init__.py         # Package initializer
│   ├── scraper.py          # Logic for fetching and cleaning text from URLs
│   ├── llm_api.py          # Interface for Google Gemini API communication
│   └── report_gen.py       # Logic for generating PDF reports with ReportLab
│
├── static/                 # Static assets
│   ├── css/
│   │   ├── style.css       # Global styles and layout
│   │   ├── auth.css        # Specific styles for Login/Signup pages
│   │   └── about.css       # Specific styles for the About page
│   └── images/             # Team photos and assets
│
└── templates/              # Jinja2 HTML Templates
    ├── base.html           # Base layout (Navbar, Footer, Scroll Scripts)
    ├── index.html          # Home page (Hero, Features, Ticker)
    ├── about.html          # Team information page
    ├── signup.html         # User registration form
    ├── login.html          # User authentication form
    ├── input.html          # Main interface for URL/Text submission
    ├── results.html        # Display of verification analysis
    ├── dashboard.html      # User history management
    └── insights.html       # Data visualizations and statistics
```

### Detailed File Roles

*   **app.py:** Initializes the Flask app, connects to the MySQL database, manages user sessions (Flask-Login), and defines all URL routes. It coordinates data flow between the frontend and the utility modules.
*   **utils/scraper.py:** Contains the `extract_text_from_url` function. It handles HTTP requests, parses HTML, removes script/style tags, and truncates text to fit LLM context limits.
*   **utils/llm_api.py:** Manages the connection to Google Gemini. It constructs the prompt instructions, sends the payload, and parses the returned JSON structure containing claims, verdicts, and reasoning.
*   **utils/report_gen.py:** Uses `ReportLab` and `Matplotlib` to programmatically draw a PDF document. It generates pie charts for validity distribution and formats the claim data into a readable table layout.
*   **templates/base.html:** Acts as the master template. All other pages extend this file to ensure consistent navigation bars, footers, and script loading.

## Installation and Setup

### Prerequisites

*   Python 3.8 or higher
*   MySQL Server installed and running

### Step 1: Clone the Repository

```bash
git clone https://github.com/ASHISHAVHAD/ByteHunters
cd bytehunters
```

### Step 2: Install Dependencies

It is recommended to use a virtual environment.

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

*If requirements.txt is not provided, install the following packages manually:*
`flask flask-mysqldb flask-login werkzeug python-dotenv google-genai beautifulsoup4 requests reportlab matplotlib`

### Step 3: Database Configuration

Open your MySQL client and execute the following SQL commands to set up the database schema:

```sql
CREATE DATABASE bytehunters_db;
USE bytehunters_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE verification_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    input_type ENUM('text', 'url'),
    input_content TEXT,
    json_result JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Step 4: Environment Variables

Create a file named `.env` in the root directory and add the following configuration keys:

```ini
GEMINI_API_KEY=your_google_gemini_api_key
MYSQL_PASSWORD=your_mysql_root_password
FLASK_SECRET_KEY=your_random_secret_string
```

### Step 5: Run the Application

```bash
python app.py
```

The application will start on `http://127.0.0.1:5000/`.

## System Workflow

1.  **Ingestion:** The user logs in and submits a URL or text via the Input Page.
2.  **Processing:**
    *   If a URL is provided, `scraper.py` fetches the HTML and strips it down to clean text.
    *   The clean text is passed to `llm_api.py`.
3.  **Analysis:** The Google Gemini API processes the text. It identifies claims, searches the internal knowledge base (and internet via the model's capabilities), and returns a JSON object containing verdicts, confidence scores, and reasoning.
4.  **Presentation:** The JSON data is rendered on the Results Page using Jinja2 templates.
5.  **Persistence:** If the user clicks "Save," the raw input and the JSON result are serialized and stored in the MySQL `verification_history` table.
6.  **Reporting:** If the user requests a PDF, `report_gen.py` reads the JSON data, generates a chart in memory, draws the PDF layout, and serves the file as a download.

## Contributors

**ByteHunters Team** (IIT Bombay)

*   **Backend Developer:** Ashish Avhad
*   **Frontend Developer:** Avirup Chakraborty
*   **Python Developer:** Shivam Singh