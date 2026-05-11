import base64

from flask import Flask, render_template , request
import pickle
import re
import requests
app = Flask(__name__)

vector = pickle.load(open('Vectorizer.pkl', 'rb'))
model = pickle.load(open('phishing.pkl', 'rb'))


#Go to virustotal.com → your profile → API Key → regenerate a new one
VT_API_KEY = "API_KEY_HERE" # Replace with your VirusTotal API key

#Base64 URL decoding

def decode_base64_url(url):
    # Match base64 data URIs
    match = re.search(r'base64,([A-Za-z0-9+/=]+)', url)
    if match:
        try:
            decoded = base64.b64decode(match.group(1)).decode('utf-8', errors='ignore')
            return decoded  # Analyze this instead
        except:
            pass
    return url  # Return original if no encoding found


#VirusTotal API (4 requests/min)

def check_virustotal(url, api_key):
    headers = {"x-apikey": api_key}
    # Submit URL
    resp = requests.post(
        "https://www.virustotal.com/api/v3/urls",
        headers=headers,
        data={"url": url}
    )
    url_id = resp.json()["data"]["id"]
    # Get analysis
    result = requests.get(
        f"https://www.virustotal.com/api/v3/analyses/{url_id}",
        headers=headers
    ).json()
    stats = result["data"]["attributes"]["stats"]
    return stats["malicious"] > 0  # True = phishing


# Clickjacking detection


def check_clickjacking(url):
    try:
        resp = requests.get(url, timeout=5)
        headers = resp.headers
        xfo = headers.get("X-Frame-Options", "").upper()
        csp = headers.get("Content-Security-Policy", "")
        safe = xfo in ("DENY", "SAMEORIGIN") or "frame-ancestors" in csp
        return not safe  # True = potentially vulnerable
    except:
        return None  # Couldn't reach site


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        #print(url)

# 1. Decode base64 first
        url = decode_base64_url(url)

        cleaned_url = re.sub(r'^https?://(www\.)?', '', url)    # print(cleaned_url)

 # 2. Your existing ML model prediction
        predict =model.predict(vector.transform([url]))[0] #print(predict)
 # 3. VirusTotal check       
        vt_malicious = check_virustotal(url, VT_API_KEY)
 # 4. Clickjacking check           
        clickjack_risk = check_clickjacking(url) 


# Final verdict: flag if ANY signal is bad
        if predict == 'bad' or vt_malicious or clickjack_risk:
            predict = "This is a Phishing Website"
        elif predict == 'good' and not vt_malicious and not clickjack_risk:
            predict = "This is a healthy and Safe Website !!"
        else:
            predict = 'something went wrong'

        return render_template('index.html', predict=predict)
    else:
        return render_template('index.html')

    
    
if __name__=="__main__":
    app.run(debug=True)


