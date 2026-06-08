# Phishing-Website-Detection System
Phishing is a cyberattack where fake websites mimic trusted platforms to steal sensitive data like passwords and banking details. This system uses machine learning to analyze URL patterns and detect suspicious features, helping users identify potentially harmful websites before sharing personal information.





---

## Overview

The Phishing Website Detection System is a full-stack machine learning web application that analyzes URLs in real time and predicts whether a website is **safe or a phishing threat**. It combines a trained ML model with live external threat intelligence from the **VirusTotal API** and an additional **clickjacking vulnerability check** — giving a three-layer verdict on every URL submitted.

Users enter a URL into a clean web interface, click Submit, and instantly receive a prediction: phishing or safe.

---

## What It Does

- Accepts a URL input through a browser-based web form
- Decodes Base64-encoded URLs before analysis (a common obfuscation trick used by phishing links)
- Runs the URL through a trained **Logistic Regression ML model** that was built on 549,346 real URLs
- Cross-checks the URL against **VirusTotal's** database of known malicious URLs via their API
- Checks the live website's HTTP headers for **missing clickjacking protections** (`X-Frame-Options`, `Content-Security-Policy`)
- Returns a final verdict: **Phishing** (if any single check flags it) or **Safe** (if all three checks pass)

---

## Features

- **Three-layer detection** — ML model + VirusTotal API + clickjacking header check
- **Base64 URL decoding** — catches obfuscated phishing links before analysis
- **Live VirusTotal integration** — cross-references URLs against a real threat intelligence database
- **Clickjacking detection** — checks whether the target site is missing `X-Frame-Options` or `frame-ancestors` CSP headers
- **Two trained models** — Logistic Regression (96% accuracy, deployed) and Multinomial Naive Bayes (saved as backup)
- **Persistent model storage** — trained models saved as `.pkl` files with Pickle, no retraining needed on startup
- **Responsive web UI** — built with Tailwind CSS and Bootstrap 5, mobile-friendly
- **Flask web server** — lightweight Python backend, easy to run locally

---

## How It Works — Detection Pipeline

```
User submits URL
       │
       ▼
Step 1 — Base64 Decode
       Detects and decodes base64-encoded URLs (common phishing obfuscation)
       │
       ▼
Step 2 — ML Model Prediction
       URL is cleaned → vectorized via CountVectorizer → passed to Logistic Regression
       Returns: 'good' or 'bad'
       │
       ▼
Step 3 — VirusTotal API Check
       URL submitted to VirusTotal v3 API → malicious engine count checked
       Returns: True (malicious) or False (clean)
       │
       ▼
Step 4 — Clickjacking Header Check
       Live GET request to the URL → checks X-Frame-Options and Content-Security-Policy headers
       Returns: True (vulnerable) or False (protected)
       │
       ▼
Final Verdict
       ANY check = bad → "This is a Phishing Website"
       ALL checks = good → "This is a healthy and Safe Website !!"
```

---

## Machine Learning Pipeline (Notebook)

The model was built in a Jupyter Notebook (`Phishing_Website_detection_system.ipynb`) through the following steps:

### 1. Data Loading
Loaded `phishing_site_urls.csv` containing 549,346 URLs labeled `good` or `bad`.

### 2. Exploratory Data Analysis
- Checked dataset shape, null values, and label distribution
- Dataset breakdown: **392,924 good** URLs, **156,422 bad** URLs
- Generated Word Cloud visualizations separately for good and bad URLs to identify common patterns

### 3. Text Preprocessing
URLs are text data and must be converted to a numeric form the model can process:

| Step | What it does | Library |
|---|---|---|
| **Tokenization** | Extracts only alphabetical words from the URL, strips numbers and special characters | `nltk.RegexpTokenizer` |
| **Stemming** | Reduces words to their root form (e.g. "login" → "login", "logging" → "log") | `SnowballStemmer` |
| **Join** | Rejoins stemmed tokens into a single string per URL | Python string join |

### 4. Vectorization
`CountVectorizer` converts the processed text into a bag-of-words numerical matrix — a format ML algorithms can read.

### 5. Train/Test Split
80% training / 20% test split using `train_test_split`.

### 6. Model Training & Evaluation

| Model | Test Accuracy | Train Accuracy | Notes |
|---|---|---|---|
| **Logistic Regression** | **96%** | **97%** | Deployed in Flask app (`phishing.pkl`) |
| **Multinomial Naive Bayes** | Trained | Trained | Saved as backup (`phishing_mnb.pkl`) |

- Minimal gap between train and test accuracy confirms **no overfitting**
- Full classification report and confusion matrix heatmap generated with seaborn

### 7. Model Saving
Both models and the CountVectorizer saved via Pickle for use in the Flask app:
```
phishing.pkl       ← Logistic Regression model
phishing_mnb.pkl   ← Naive Bayes model
Vectorizer.pkl     ← CountVectorizer (must match the model)
```

---

## Architecture

```
phishing-detection/
│
├── app.py                              # Flask backend — routes, ML inference, API calls
├── templates/
│   └── index.html                      # Frontend — Tailwind CSS + Bootstrap 5 UI
│
├── Phishing_Website_detection_system.ipynb  # ML training notebook
│
├── phishing.pkl                        # Trained Logistic Regression model
├── phishing_mnb.pkl                    # Trained Multinomial Naive Bayes model
├── Vectorizer.pkl                      # Fitted CountVectorizer
│
└── phishing_site_urls.csv              # Training dataset (549,346 URLs)
```

### Backend — `app.py`

| Function | Purpose |
|---|---|
| `decode_base64_url(url)` | Detects base64 data URIs in the URL and decodes them before analysis |
| `check_virustotal(url, api_key)` | Submits URL to VirusTotal v3 API, retrieves malicious engine count |
| `check_clickjacking(url)` | Makes a GET request to the URL and inspects security headers |
| `index()` route | Handles GET (render form) and POST (run full detection pipeline) |

---

## Tech Stack

| Component | Technology |
|---|---|
| **Backend framework** | Flask (Python) |
| **ML library** | scikit-learn |
| **NLP / text processing** | NLTK (RegexpTokenizer, SnowballStemmer) |
| **Vectorization** | scikit-learn CountVectorizer |
| **Model persistence** | Pickle |
| **HTTP requests** | requests |
| **Frontend** | HTML5, Tailwind CSS, Bootstrap 5 |
| **Data analysis** | pandas, numpy |
| **Visualization** | matplotlib, seaborn, WordCloud |
| **Threat intelligence** | VirusTotal API v3 |

---

## Dataset

**File:** `phishing_site_urls.csv`

| Property | Value |
|---|---|
| Total URLs | 549,346 |
| Good (legitimate) URLs | 392,924 |
| Bad (phishing) URLs | 156,422 |
| Columns | `URL`, `Label` |
| Label values | `good`, `bad` |

Sample rows:
```
URL                                                  Label
nobell.it/70ffb52d079109dca5664cce6f317373782/...   bad
youtube.com/watch?v=qI0TQJI3vdU                     good
serviciosbys.com/paypal.cgi.bin.get-into.herf...    bad
```

The dataset contains a mix of real phishing URLs and legitimate website URLs, with a roughly 70/30 split in favor of legitimate sites.

---

## Installation

**Requirements:** Python 3.8+

### 1. Clone the repository

```bash
git clone https://github.com/yourname/phishing-detection.git
cd phishing-detection
```

### 2. Install dependencies

```bash
pip install flask scikit-learn nltk requests pandas numpy matplotlib seaborn wordcloud
```

### 3. Set up your VirusTotal API key

Get a free API key from [virustotal.com](https://www.virustotal.com) → Profile → API Key.

Open `app.py` and replace the placeholder:

```python
VT_API_KEY = "your_actual_api_key_here"
```


### 4. Ensure model files are present

The following files must be in the same directory as `app.py`:

```
phishing.pkl
Vectorizer.pkl
phishing_mnb.pkl   (optional backup)
```

These are pre-trained — no need to retrain unless you want to update the model.

### 5. Place the HTML template

The `index.html` file must be inside a `templates/` folder (Flask convention):

```bash
mkdir templates
mv index.html templates/
```

---

## Usage

### Run the web app

```bash
python3 app.py
```

Then open your browser and go to:
```
http://127.0.0.1:5000
```

### Using the interface

1. Enter any URL in the input field (e.g. `http://suspicious-login.com/paypal`)
2. Click **Submit**
3. The result appears on the page:
<<<<<<< HEAD
   - ✅ `This is a healthy and Safe Website !!`
   - 🚨 `This is a Phishing Website`
=======
   -  `This is a healthy and Safe Website !!`
   -  `This is a Phishing Website`


### Retrain the model (optional)

Open and run `Phishing_Website_detection_system.ipynb` in Jupyter Notebook. Ensure `phishing_site_urls.csv` is in the same directory. The notebook will re-generate `phishing.pkl`, `phishing_mnb.pkl`, and `Vectorizer.pkl`.

```bash
jupyter notebook Phishing_Website_detection_system.ipynb
```

---

## Detection Logic

The final verdict is determined by combining all three checks:

```python
if predict == 'bad' or vt_malicious or clickjack_risk:
    result = "This is a Phishing Website"
elif predict == 'good' and not vt_malicious and not clickjack_risk:
    result = "This is a healthy and Safe Website !!"
```

A URL is flagged as phishing if **any one** of the three signals is triggered — making the system conservative and erring on the side of user safety.

---

## What Vulnerabilities / Threats It Detects

| Threat | Detection Method |
|---|---|
| **Phishing URLs** | ML model trained on 549K labeled URLs (96% accuracy) |
| **Known malicious URLs** | VirusTotal API — checks against 70+ antivirus/security engines |
| **Base64 obfuscated links** | Decoded before analysis — catches disguised phishing URLs |
| **Clickjacking risk** | Missing `X-Frame-Options` or `Content-Security-Policy: frame-ancestors` headers |

---

=======


## thank you

