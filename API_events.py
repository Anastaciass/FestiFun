from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import Event
import os  


app = Flask(__name__)


db_url = os.getenv('DATABASE_URL', 'sqlite:///orm.db')
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

@app.route('/api/topics', methods=['GET'])
def get_topics():
    topics = session.query(Event.Topic).distinct().all()
    print(topics)
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

if __name__ == '__main__':
    app.run(debug=True)