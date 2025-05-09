from flask import Flask, render_template, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import qrcode
from io import BytesIO
import base64
import uuid
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.uuid}>'

# Create the database and tables
with app.app_context():
    db.create_all()

def generate_qr_code(data):
    """Generate a QR code for the given data and return as base64 string"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

@app.route('/')
def index():
    """Render the main page with the button to generate QR code"""
    return render_template('qrcode.html')

@app.route('/generate_qr')
def generate_qr():
    """Generate a unique QR code and add the user to the database"""
    # Generate a unique identifier
    unique_id = str(uuid.uuid4())
    
    # Create new user in database
    new_user = User(uuid=unique_id)
    db.session.add(new_user)
    db.session.commit()
    
    # Generate QR code with the UUID
    qr_data = f"user:{unique_id}"
    qr_code_base64 = generate_qr_code(qr_data)
    
    return jsonify({
        'uuid': unique_id, 
        'qr_code': qr_code_base64
    })

@app.route('/users')
def users_list():
    """Render the page showing all users in the database"""
    users = User.query.order_by(User.timestamp.desc()).all()
    return render_template('users.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)