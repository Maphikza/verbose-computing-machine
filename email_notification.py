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
