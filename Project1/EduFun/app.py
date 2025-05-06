from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('mainorg.html')

@app.route('/guestlist')
def guestlist():
    return render_template('guestlist.html')

if __name__ == '__main__':
    app.run(debug=True)
