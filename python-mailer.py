import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from constants import sender_email, password
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

# Port and SMTP server details
port = 465  # SSL Port
smtp_server = "smtp.gmail.com"

def send_email(receiver_email, role):
    """Send email based on the selected role."""
    
    # Create message container - ensure proper encoding
    msg = MIMEMultipart()
    msg['From'] = Header(sender_email, 'utf-8').encode()
    msg['To'] = Header(receiver_email, 'utf-8').encode()
    
    # Set message content based on role
    if role == "organizer":
        msg['Subject'] = Header("You are now an Organizer", 'utf-8').encode()
        body = """\
Hello,

You have been registered as an Organizer.
Thank you for taking on this important role!

Best regards,
The Team
"""
    else:  # role == "user"
        msg['Subject'] = Header("You are now a User", 'utf-8').encode()
        body = """\
Hello,

You have been registered as a User.
Welcome to our platform!

Best regards,
The Team
"""
    
    # Attach body to email with proper encoding
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # Send email
    try:
        with smtplib.SMTP_SSL(smtp_server, port) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print(f"Email sent successfully to {receiver_email} with role {role}")
            return True, "Email sent successfully!"
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"Authentication error: {e}"
        print(error_msg)
        print("Make sure you are using an App Password or have enabled less secure apps.")
        return False, error_msg
    except Exception as e:
        error_msg = f"An error occurred: {e}"
        print(error_msg)
        return False, error_msg

class EmailRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="application/json"):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')  # For CORS
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        # Handle preflight requests for CORS
        self._set_headers()
    
    def do_GET(self):
        # Serve static files
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/' or path == '/email.html':
            with open('email.html', 'rb') as file:
                self._set_headers("text/html")
                self.wfile.write(file.read())
        elif path == '/verify.html':
            with open('verify.html', 'rb') as file:
                self._set_headers("text/html")
                self.wfile.write(file.read())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'File not found')
    
    def do_POST(self):
        if self.path == '/send-email':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            email = data.get('email', '')
            role = data.get('role', '')
            
            if not email or not role:
                self._set_headers()
                response = {'success': False, 'message': 'Email and role are required'}
                self.wfile.write(json.dumps(response).encode())
                return
            
            success, message = send_email(email, role)
            
            self._set_headers()
            response = {'success': success, 'message': message}
            self.wfile.write(json.dumps(response).encode())

def run_server(server_class=HTTPServer, handler_class=EmailRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()