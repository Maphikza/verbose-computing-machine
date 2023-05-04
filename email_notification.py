import os
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailNotify:
    def __init__(self, admin_email_address: str, admin_email_password: str, to_email_address: str, img_path: str):
        self.email_address = admin_email_address
        self.email_password = admin_email_password
        self.destination_email = to_email_address
        self.image_path = img_path

    def send_message(self, detail: str) -> None:
        message = MIMEMultipart()
        message['Subject'] = f'Detected images {detail}'
        message['From'] = self.email_address
        message['To'] = self.destination_email

        with open(self.image_path, 'rb') as f:
            image_data = f.read()

        image = MIMEImage(image_data, name=os.path.basename(self.image_path))
        message.attach(image)

        custom_message = MIMEText(f'Please find attached the image from the detection earlier. '
                                  f'{detail}\n\nRegards\nSiphiwe')
        message.attach(custom_message)

        with smtplib.SMTP("smtpout.secureserver.net", 587) as smtp:
            smtp.starttls()
            smtp.login(self.email_address, self.email_password)
            smtp.sendmail(self.email_address, self.destination_email, message.as_string())

# # 1.
# # Your email account information
# email_address = 'your_email_address'
# email_password = 'your_email_password'
#
# # The recipient's email address
# to_address = 'recipient_email_address'
#
# # 2.
# # The email message
# message = MIMEMultipart()
# message['Subject'] = 'Check out this cool image!'
# message['From'] = email_address
# message['To'] = to_address
#
# # The path to the image file
# image_path = 'runs/detect/exp/image0.jpg'
#
# # Opening and reading the image file
# with open(image_path, 'rb') as f:
#     image_data = f.read()
#
# # Creating the MIME image object and attaching it to the email message
# image = MIMEImage(image_data, name=os.path.basename(image_path))
# message.attach(image)
#
# # Sending the email message using smtplib
# with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
#     smtp.login(email_address, email_password)
#     smtp.sendmail(email_address, to_address, message.as_string())
