from flask import Flask, jsonify
from flask_cors import CORS
from main import Event, User, Session
import API_events


app = Flask(__name__)


CORS(app)


session = Session()


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


event1 = Event(Description="Tech Conference 2025", Location="San Francisco", Link="https://example.com/tech", Topic="Tech Conferences", User_ID=user.User_ID)
event2 = Event(Description="Art Expo", Location="Los Angeles", Link="https://example.com/art", Topic="Art Exhibitions", User_ID=user.User_ID)
event3 = Event(Description="Music Festival", Location="Chicago", Link="https://example.com/music", Topic="Music Events", User_ID=user.User_ID)


existing_events = session.query(Event).filter_by(User_ID=user.User_ID).all()
if not existing_events:
    session.add_all([event1, event2, event3])
    session.commit()
    print("Sample events successfully added to the database!")
else:
    print("Events already exist in the database.")


@app.route('/api/topics', methods=['GET'])
def get_topics():
    
    topics = session.query(Event.Topic).distinct().all()
    topic_list = [topic[0] for topic in topics if topic[0]]  
    return jsonify(topic_list)
def run_app():
    API_events.main()

if __name__ == '__main__':
    app.run(debug=True)

