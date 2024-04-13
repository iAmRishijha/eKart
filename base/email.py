from django.conf import settings
from django.core.mail import send_mail

def send_activation_email(email, email_token):
    subject = "Your accounts needs to be verified"
    email_from = settings.EMAIL_HOST_USER
    message = f'Hi, Click on this link to verify your account http://127.0.0.1:8000/accounts/activate/{email_token}'

    send_mail(subject, message, email_from, [email])
