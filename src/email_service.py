import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.config import Config

class EmailService:
    def __init__(self):
        self.config = Config.EMAIL_CONFIG
    
    def send_email(self, to_email, subject, body):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['email']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.starttls()
            server.login(self.config['email'], self.config['password'])
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Email error: {e}")
            return False
    
    def send_booking_confirmation(self, user_email, user_name, booking_id, vehicle_model, pickup_date, return_date, total_amount):
        subject = "Booking Confirmation - Vehicle Rental"
        body = f"""
        <h2>Booking Confirmation</h2>
        <p>Dear {user_name},</p>
        <p>Your vehicle booking has been confirmed:</p>
        <ul>
            <li>Booking ID: {booking_id}</li>
            <li>Vehicle: {vehicle_model}</li>
            <li>Pickup Date: {pickup_date}</li>
            <li>Return Date: {return_date}</li>
            <li>Total Amount: ${total_amount}</li>
        </ul>
        <p>Thank you for choosing our service!</p>
        """
        return self.send_email(user_email, subject, body)
    
    def send_invoice(self, user_email, user_name, booking_id, vehicle_model, pickup_date, return_date, total_amount, invoice_number):
        subject = f"Invoice #{invoice_number} - Vehicle Rental"
        body = f"""
        <h2>Invoice #{invoice_number}</h2>
        <p>Dear {user_name},</p>
        <p>Thank you for your booking. Here are your invoice details:</p>
        <ul>
            <li>Booking ID: {booking_id}</li>
            <li>Vehicle: {vehicle_model}</li>
            <li>Pickup Date: {pickup_date}</li>
            <li>Return Date: {return_date}</li>
            <li>Total Amount: ${total_amount}</li>
        </ul>
        <p>Payment has been processed successfully.</p>
        <p>Thank you for choosing our service!</p>
        """
        return self.send_email(user_email, subject, body)