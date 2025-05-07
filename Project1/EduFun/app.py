from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('mainorg.html')

@app.route('/guestlist')
def guestlist():
    return render_template('guestlist.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/mainuser')
def mainuser():
    return render_template('mainuser.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

if __name__ == '__main__':
    app.run(debug=True)