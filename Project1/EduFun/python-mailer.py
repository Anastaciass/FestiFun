import smtplib
from Project1.EduFun.constants import sender_email, password

# Port and SMTP server details
port = 465  # SSL Port
smtp_server = "smtp.gmail.com"

# Email details
receiver_email = "" # Replace with the recipient's email address through index.html
# change message to what need be \/
message = """\
Subject: Hi broski! 

email verification?."""

# Establish an SSL connection and send the email
try:
    with smtplib.SMTP_SSL(smtp_server, port) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
        print("Email sent successfully!")
except smtplib.SMTPAuthenticationError as e:
    print("Authentication error:", e)
    print("Make sure you are using an App Password or have enabled less secure apps.")
except Exception as e:
    print("An error occurred:", e)
