from flask import Flask, render_template
from flask import request, jsonify
from werkzeug.utils import secure_filename
import os
from db_controller import session, Event


app = Flask(__name__)

@app.route('/save_event', methods=['POST'])
def save_event():
    place = request.form.get('place')
    date = request.form.get('date')
    webpage = request.form.get('webpage')
    description = request.form.get('description')
    topic = request.form.get('topic')
    price = request.form.get('price')
    lat = request.form.get('lat')
    lng = request.form.get('lng')
    image = request.files.get('image')

    image_path = None
    if image:
        filename = secure_filename(image.filename)
        upload_folder = os.path.join('static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        image_path = os.path.join(upload_folder, filename)
        image.save(image_path)

    new_event = Event(
        Description=description,
        Location=place,
        Link=webpage,
        Topic=topic,
        Price=price,
        Image=image_path,
        Latitude=lat,
        Longitude=lng,
        User_ID=1  # temporary
    )
    session.add(new_event)
    session.commit()

    return jsonify({'status': 'ok'})

@app.route('/get_events')
def get_events():
    events = session.query(Event).all()
    return jsonify([
        {
            "description": e.Description,
            "topic": e.Topic,
            "price": e.Price,
            "webpage": e.Link,
            "image": e.Image,
            "lat": e.Latitude,
            "lng": e.Longitude
        }
        for e in events if e.Latitude and e.Longitude
    ])


@app.route('/')
def home():
    return render_template('mainuser.html')

@app.route('/organizer')
def organizer():
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