import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

def send_email(to_email:str,subject:str,html:str):
    try:
        sender_email=os.getenv("SENDER_EMAIL","")
        sender_password=os.getenv("SENDER_PASSWORD","")

        message =MIMEText(html,"html")
        message["Subject"]=subject
        message["From"]=sender_email
        message["To"]=to_email

        server=smtplib.SMTP("smtp.gmail.com",587)

        server.starttls()

        server.login(sender_email,sender_password)

        server.sendmail(
            sender_email,
            to_email,
            message.as_string()
        )

        server.quit()

        return True
    except Exception as e:
        print("Email sending error:",e)
        return False

