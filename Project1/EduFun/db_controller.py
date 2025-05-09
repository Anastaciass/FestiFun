from sqlalchemy import Column, Integer, String, ForeignKey, Sequence, create_engine, Enum
import enum
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
import os

# db_url = os.getenv('DATABASE_URL', 'sqlite:///orm.db')
db_url = os.getenv('DATABASE_URL', 'sqlite:///orm_stacy.db')
if db_url == 'sqlite:///orm.db':
    print("Warning: DATABASE_URL environment variable not set. Using fallback SQLite database.")
else:
    print(f"Using database URL: {db_url}")
engine = create_engine(db_url)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class UserType(enum.Enum):
    Organisor = "Organisor"
    User = "User"

class User(Base):
    __tablename__ = 'Users'
    User_Type = Column(Enum(UserType, native_enum=True, create_constraint=True), nullable=False)
    User_ID = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    Gmail = Column(String, unique=True, nullable=False)
    Password = Column(String(50))
    Location = Column(String(255))
    events = relationship(
        "Event",
        back_populates="user",
        cascade="all, delete-orphan"
    )

class Event(Base):
    __tablename__ = 'Event'
    Event_ID = Column(Integer, Sequence('event_id_seq'), primary_key=True)
    Description = Column(String())
    Location = Column(String())
    Link = Column(String())  
    Topic = Column(String())
    Price = Column(String())  
    Image = Column(String())  
    Latitude = Column(String())  
    Longitude = Column(String())  
    User_ID = Column(Integer, ForeignKey('Users.User_ID'), nullable=False)  
    user = relationship("User", back_populates="events")

class Comment(Base):
    __tablename__ = 'Comment'
    Comment_ID = Column(Integer, Sequence('comment_id_seq'), primary_key=True)
    Event_ID = Column(Integer, ForeignKey('Event.Event_ID'))
    User_ID = Column(Integer, ForeignKey('Users.User_ID')) 
    Comment_text = Column(String())

class Rating(Base):
    __tablename__ = 'Rating'
    Rating_ID = Column(Integer, Sequence('rating_id_seq'), primary_key=True)
    Event_ID = Column(Integer, ForeignKey('Event.Event_ID'))
    User_ID = Column(Integer, ForeignKey('Users.User_ID')) 
    Rating_value = Column(Integer)

class Attendence(Base):
    __tablename__ = 'Attendence'
    Attendence_ID = Column(Integer, Sequence('attendence_id_seq'), primary_key=True)
    Event_ID = Column(Integer, ForeignKey('Event.Event_ID'))
    User_ID = Column(Integer, ForeignKey('Users.User_ID')) 



Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
session.commit()