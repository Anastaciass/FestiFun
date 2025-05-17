from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from main import Event, User, Comment, Rating, Session
import os

app = Flask(__name__)
CORS(app)

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
        User_ID=1  # временно
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


# --- Подключение базы данных и заполнение ---
db_url = os.getenv('DATABASE_URL', 'sqlite:///orm.db')
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

def seed_database():
    user = User(
        User_ID=1,
        User_Type="Organisor",
        Gmail="organisor@example.com",
        Password="password123",
        Location="New York"
    )

    existing_user = session.query(User).filter_by(Gmail="organisor@example.com").first()
    if not existing_user:
        session.add(user)
        session.commit()
        print("User successfully added to the database:", user.Gmail)
    else:
        print("User already exists in the database:", existing_user.Gmail)

    events = [
        Event(Description="Tech Conference 2025", Location="San Francisco", Link="https://example.com/tech", Topic="Tech Conferences", User_ID=user.User_ID),
        Event(Description="Art Expo", Location="Los Angeles", Link="https://example.com/art", Topic="Art Exhibitions", User_ID=user.User_ID),
        Event(Description="Music Festival", Location="Chicago", Link="https://example.com/music", Topic="Music Events", User_ID=user.User_ID)
    ]
    existing_events = session.query(Event).filter_by(User_ID=user.User_ID).all()
    if not existing_events:
        session.add_all(events)
        session.commit()
        print("Sample events successfully added to the database!")
    else:
        print("Events already exist in the database.")

    comments = [
        Comment(Comment_text="Great event, learned a lot!", Event_ID=1, User_ID=user.User_ID),
        Comment(Comment_text="Amazing atmosphere and organization.", Event_ID=2, User_ID=user.User_ID),
        Comment(Comment_text="Looking forward to next year!", Event_ID=3, User_ID=user.User_ID)
    ]
    existing_comments = session.query(Comment).filter_by(User_ID=user.User_ID).all()
    if not existing_comments:
        session.add_all(comments)
        session.commit()
        print("Sample comments successfully added to the database!")
    else:
        print("Comments already exist in the database.")

    ratings = [
        Rating(Rating_value=5, Event_ID=1, User_ID=user.User_ID),
        Rating(Rating_value=4, Event_ID=2, User_ID=user.User_ID),
        Rating(Rating_value=5, Event_ID=3, User_ID=user.User_ID)
    ]
    existing_ratings = session.query(Rating).filter_by(User_ID=user.User_ID).all()
    if not existing_ratings:
        session.add_all(ratings)
        session.commit()
        print("Sample ratings successfully added to the database!")
    else:
        print("Ratings already exist in the database.")


@app.route('/api/topics', methods=['GET'])
def get_topics():
    topics = session.query(Event.Topic).distinct().all()
    topic_list = [topic[0] for topic in topics if topic[0]]
    return jsonify(topic_list)

@app.route('/api/events', methods=['GET'])
def get_events_by_topic():
    topic = request.args.get('topic', None)
    if not topic:
        return jsonify({"error": "Topic parameter is required"}), 400

    events = session.query(Event).filter_by(Topic=topic).all()
    event_list = [
        {
            "Description": event.Description,
            "Location": event.Location,
            "Link": event.Link,
            "Topic": event.Topic
        }
        for event in events
    ]
    return jsonify(event_list)


@app.route('/comments', methods=['GET'])
def get_comments():
    comments = session.query(Comment, Rating, User).join(
        Rating, Comment.Event_ID == Rating.Event_ID
    ).join(
        User, Comment.User_ID == User.User_ID
    ).all()

    comment_data = [
        {
            "username": user.Gmail.split('@')[0],  
            "rating": rating.Rating_value,
            "comment": comment.Comment_text,
        }
        for comment, rating, user in comments
    ]

    return jsonify({"status": "success", "data": comment_data})

@app.route('/add_comment', methods=['POST'])
def add_comment():
    comment_text = request.form.get('comment')
    rating_value = request.form.get('rating')

    if not comment_text or not rating_value:
        return jsonify({"error": "Both comment and rating are required"}), 400

    comment = Comment(Event_ID=1, User_ID=1, Comment_text=comment_text)
    rating = Rating(Event_ID=1, User_ID=1, Rating_value=int(rating_value))

    session.add(comment)
    session.add(rating)
    session.commit()

    return jsonify({"status": "success"})


def debug_data():
    comments = session.query(Comment, User, Rating).join(User, Comment.User_ID == User.User_ID).join(
        Rating, Rating.User_ID == User.User_ID
    ).all()

    for comment, user, rating in comments:
        print(f"Username: {user.Gmail.split('@')[0]}, Rating: {rating.Rating_value}, Comment: {comment.Comment_text}")


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
    seed_database()
    debug_data()
    app.run(debug=True)
