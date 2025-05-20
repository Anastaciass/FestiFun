from flask import Flask, render_template, request, jsonify, redirect, url_for, session as flask_session
from flask_cors import CORS
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from db_controller import Event, User, Comment, Rating, Session, session
import os
import API_events
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import random
import string
import hashlib
import qrcode
import io
import base64
from PIL import Image

try:
    from constants import sender_email, password
except ImportError:
    # Fallback values if constants.py doesn't exist
    print("Warning: constants.py not found. Email functionality might not work.")
    sender_email = "costindylan@gmail.com"
    password = "cntx rotx iegc azne"

# Inspect the API_events module to understand its structure
try:
    print(f"API_events module functions: {dir(API_events)}")
except Exception as e:
    print(f"Warning: Error inspecting API_events module: {e}")

app = Flask(__name__)
CORS(app)

# Set a secret key for the application
app.secret_key = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

# Define the path to the templates
current_dir = os.path.dirname(os.path.abspath(__file__))
# Don't override template_folder if already set and working
if not hasattr(app, 'template_folder') or not app.template_folder:
    app.template_folder = current_dir

# Email verification code storage
verification_codes = {}

# SMTP configuration
smtp_port = 465  # SSL Port
smtp_server = "smtp.gmail.com"

# Password hashing function
def hash_password(password):
    """Simple password hashing function"""
    return hashlib.sha256(password.encode()).hexdigest()

# QR Code generation function
def generate_qr_code_data():
    """Generate a random string for QR code"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

# Email verification functions
def generate_verification_code():
    """Generate a 6-digit verification code."""
    return ''.join(random.choices(string.digits, k=6))

def send_email(receiver_email, role):
    """Send email with verification code based on the selected role."""
    
    # Generate a verification code
    verification_code = generate_verification_code()
    
    # Store the verification code for later validation
    verification_codes[receiver_email] = {
        'code': verification_code,
        'role': role,
        'verified': False
    }
    
    # Create message container - ensure proper encoding
    msg = MIMEMultipart()
    msg['From'] = Header(sender_email, 'utf-8').encode()
    msg['To'] = Header(receiver_email, 'utf-8').encode()
    
    # Set message content based on role with verification code
    if role == "organizer":
        msg['Subject'] = Header("Verify your Organizer Registration", 'utf-8').encode()
        body = f"""\
Hello,

You have requested to register as an Organizer.

Please use the following verification code to complete your registration:

Verification Code: {verification_code}

If you did not request this, please ignore this email.

Best regards,
The Team"""
    else:  # role == "user"
        msg['Subject'] = Header("Verify your User Registration", 'utf-8').encode()
        body = f"""\
Hello,

You have requested to register as a User.

Please use the following verification code to complete your registration:

Verification Code: {verification_code}

If you did not request this, please ignore this email.

Best regards,
The Team"""
    
    # Attach body to email with proper encoding
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # Send email
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print(f"Email with verification code sent successfully to {receiver_email} with role {role}")
            return True, "Email with verification code sent successfully!"
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"Authentication error: {e}"
        print(error_msg)
        print("Make sure you are using an App Password or have enabled less secure apps.")
        return False, error_msg
    except Exception as e:
        error_msg = f"An error occurred: {e}"
        print(error_msg)
        return False, error_msg

# Database seeding function
def seed_database():
    # Create and add user if not exists
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

    # Create and add events if not exist
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

    # Create and add comments if not exist
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

    # Create and add ratings if not exist
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

def debug_data():
    comments = session.query(Comment, User, Rating).join(User, Comment.User_ID == User.User_ID).join(
        Rating, Rating.User_ID == User.User_ID
    ).all()
    for comment, user, rating in comments:
        print(f"Username: {user.Gmail.split('@')[0]}, Rating: {rating.Rating_value}, Comment: {comment.Comment_text}")

# Routes for the application
@app.route('/')
def index():
    # Redirect to login as the first page
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

# Added from first app.py - AJAX login authentication
@app.route('/login', methods=['POST'])
def login_post():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400
        
        # Query user by email (Gmail field in your database)
        user = session.query(User).filter(User.Gmail == email).first()
        
        if user is None:
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401
        
        # Check password (direct comparison - not secure for production)
        if user.Password != password:
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401
        
        # Store user information in session
        flask_session['user_id'] = user.User_ID
        flask_session['user_type'] = user.User_Type
        
        # Login successful - return user type for redirection
        return jsonify({
            'success': True,
            'user_type': user.User_Type,
            'user_id': user.User_ID,
            'message': 'Login successful'
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An internal error occurred'
        }), 500

@app.route('/signup')
def signup():
    return render_template('signup.html')

# Legacy route - keeping the form-based login for backward compatibility
@app.route('/process_login', methods=['POST'])
def process_login():
    # Process login credentials
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Check credentials against database
    user = session.query(User).filter_by(Gmail=email, Password=password).first()
    
    if user:
        # Store user information in session
        flask_session['user_id'] = user.User_ID
        flask_session['user_type'] = user.User_Type
        
        # If user is regular user, go to mainuser.html
        if user.User_Type == "User":
            return redirect(url_for('mainuser'))
        # If user is organizer, go to mainorg.html
        elif user.User_Type == "Organisor":
            return redirect(url_for('mainorg'))
    
    # If login fails, return to login page with error
    return render_template('login.html', error="Invalid credentials")

# Email verification routes - part of signup flow
@app.route('/email')
def email_verification():
    """Serve the email verification page with role selection buttons."""
    return render_template('email.html')

@app.route('/verify.html')
def verify():
    """Serve the verification page."""
    return render_template('verify.html')

@app.route('/send-email', methods=['POST'])
def process_email():
    """Process the email request and send verification email."""
    data = request.json
    
    email = data.get('email', '')
    role = data.get('role', '')
    
    if not email or not role:
        return jsonify({'success': False, 'message': 'Email and role are required'})
    
    success, message = send_email(email, role)
    
    return jsonify({'success': success, 'message': message})

@app.route('/check-verification', methods=['POST'])
def check_verification():
    """Check if the provided verification code is correct."""
    data = request.json
    
    email = data.get('email', '')
    code = data.get('code', '')
    
    if not email or not code:
        return jsonify({'success': False, 'message': 'Email and verification code are required'})
    
    # Check if the verification code matches
    if email in verification_codes and verification_codes[email]['code'] == code:
        verification_codes[email]['verified'] = True
        role = verification_codes[email]['role']
        
        return jsonify({
            'success': True, 
            'message': 'Verification successful!',
            'role': role
        })
    else:
        return jsonify({
            'success': False, 
            'message': 'Invalid verification code. Please try again.'
        })

@app.route('/confirmation.html')
def confirmation():
    """Serve the confirmation page after successful verification."""
    return render_template('confirmation.html')

@app.route('/complete_registration', methods=['POST'])
def complete_registration():
    """Complete the registration process after confirmation and redirect to mainorg.html"""
    # Process registration data
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')
    
    # Create a new user in the database
    user_type = "Organisor" if role == "organizer" else "User"
    new_user = User(
        Gmail=email,
        Password=password,
        User_Type=user_type,
        Location="Not specified"  # Default location
    )
    
    session.add(new_user)
    session.commit()
    
    # Store user info in session
    flask_session['user_id'] = new_user.User_ID
    flask_session['user_type'] = new_user.User_Type
    
    # Redirect based on role
    if user_type == "Organisor":
        return redirect(url_for('mainorg'))
    else:
        return redirect(url_for('mainuser'))

# Main pages routes
@app.route('/mainuser')
def mainuser():
    return render_template('mainuser.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/mainorg')
def mainorg():
    return render_template('mainorg.html')

@app.route('/guestlist')
def guestlist():
    return render_template('guestlist.html')

# QR Code routes
@app.route('/qrcode')
def qrcode():
    """Serve the QR code page."""
    return render_template('qrcode.html')

@app.route('/generate-qr', methods=['POST'])
def generate_qr():
    """Generate a QR code with random data and add user to database."""
    try:
        # Generate random QR code data
        qr_data = generate_qr_code_data()
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert image to base64 string
        img_buffer = io.BytesIO()
        qr_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        # Get current user ID or create a new user entry
        user_id = flask_session.get('user_id')
        
        if not user_id:
            # Create a guest user entry if no user is logged in
            guest_user = User(
                Gmail=f"guest_{qr_data}@temp.com",
                Password="temp_password",
                User_Type="Guest",
                Location="QR Generated"
            )
            session.add(guest_user)
            session.commit()
            user_id = guest_user.User_ID
        
        # Return success response with QR code image
        return jsonify({
            'success': True,
            'qr_code': f"data:image/png;base64,{img_base64}",
            'qr_data': qr_data,
            'user_id': user_id,
            'message': 'QR code generated successfully and user added to database!'
        })
        
    except Exception as e:
        print(f"QR generation error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error generating QR code: {str(e)}'
        }), 500

@app.route('/users')
def users():
    """Serve the users page."""
    return render_template('users.html')

@app.route('/get-users', methods=['GET'])
def get_users():
    """Get all users from the database."""
    try:
        users = session.query(User).all()
        user_list = [
            {
                'id': user.User_ID,
                'email': user.Gmail,
                'type': user.User_Type,
                'location': user.Location
            }
            for user in users
        ]
        return jsonify({
            'success': True,
            'users': user_list
        })
    except Exception as e:
        print(f"Error fetching users: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error fetching users: {str(e)}'
        }), 500

# Legacy route - keeping for backward compatibility
@app.route('/organizer')
def organizer():
    return redirect(url_for('mainorg'))

# Legacy route - keeping for backward compatibility
@app.route('/home')
def home():
    return redirect(url_for('mainuser'))

# Event management routes
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

    # Use the logged-in user's ID if available
    user_id = flask_session.get('user_id', 1)  # Default to 1 if not logged in

    new_event = Event(
        Description=description,
        Location=place,
        Link=webpage,
        Topic=topic,
        Price=price,
        Image=image_path,
        Latitude=lat,
        Longitude=lng,
        User_ID=user_id
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
    
    @app.route('/comments.html')
def comments_page():
    """Serve the comments HTML page."""
    return render_template('comments.html')

# Keep the existing API endpoint for getting comments data
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

# Comment management routes
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

    # Use the logged-in user's ID if available
    user_id = flask_session.get('user_id', 1)  # Default to 1 if not logged in
    
    comment = Comment(Event_ID=1, User_ID=user_id, Comment_text=comment_text)
    rating = Rating(Event_ID=1, User_ID=user_id, Rating_value=int(rating_value))

    session.add(comment)
    session.add(rating)
    session.commit()

    return jsonify({"status": "success"})

# Logout route
@app.route('/logout')
def logout():
    # Clear session
    flask_session.clear()
    return redirect(url_for('login'))

# Function to create test users (from first app.py)
def create_test_users():
    try:
        # Check if users already exist
        existing_users = session.query(User).count()
        if existing_users > 0:
            print("Users already exist in database")
            return
        
        # Create test organizer
        organizer = User(
            Gmail="organizer@test.com",
            Password="password123",  # In production, hash this password
            User_Type="Organisor",
            Location="Test City"
        )
        
        # Create test user
        regular_user = User(
            Gmail="user@test.com",
            Password="password123",  # In production, hash this password
            User_Type="User",
            Location="Test City"
        )
        
        session.add(organizer)
        session.add(regular_user)
        session.commit()
        print("Test users created successfully")
        
    except Exception as e:
        session.rollback()
        print(f"Error creating test users: {str(e)}")

def run_app():
    # Safely try to execute API_events functionality
    try:
        # Check if main function exists
        if hasattr(API_events, 'main'):
            API_events.main()
        # If the module itself is callable
        elif callable(API_events):
            API_events()
        # Otherwise, just import it for its side effects
        else:
            print("Note: API_events module imported but no main function found to execute")
    except Exception as e:
        print(f"Warning: Error executing API_events module: {e}")
        print("Continuing with Flask application...")

if __name__ == '__main__':
    # Print template folder for debugging
    print(f"Template folder set to: {app.template_folder}")
    print("Starting Flask server on http://127.0.0.1:5000")
    
    # Initialize the database with sample data
    seed_database()
    debug_data()
    
    # Create test users for authentication testing
    create_test_users()
    
    # Try to run API_events functionality, but don't stop if it fails
    run_app()
    
    # Start the Flask application
    app.run(debug=True)
