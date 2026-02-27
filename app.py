from flask import Flask, render_template , request
import pickle
import re

app = Flask(__name__)

vector = pickle.load(open('Vectorizer.pkl', 'rb'))
model = pickle.load(open('phishing.pkl', 'rb'))

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        #print(url)

        cleaned_url = re.sub(r'^https?://(www\.)?', '', url)
        # print(cleaned_url)

        predict =model.predict(vector.transform([url]))[0]
        #print(predict)
        
        if predict == 'bad':
            predict = "This is a Phishing Website"
        elif predict == 'good':
            predict = "This is a healthy and Safe Website !!"
        else:
            predict = 'something went wrong'

        return render_template('index.html', predict=predict)
    else:
        return render_template('index.html')

    
    
if __name__=="__main__":
    app.run(debug=True)


