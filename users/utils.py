from django.conf import settings
from django.core.mail import send_mail
from twilio.rest import Client
from .models import OTP


def send_otp_email(otp: OTP):
    """Send OTP to email."""
    send_mail(
        subject='Your CityMate Verification Code',
        message=f'Your OTP for CityMate is: {otp.code}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[otp.contact_info],
        fail_silently=False,
    )
    return otp


def send_otp_phone(otp: OTP):
    """Send OTP via SMS."""
    if not all([
        getattr(settings, 'TWILIO_ACCOUNT_SID', None),
        getattr(settings, 'TWILIO_AUTH_TOKEN', None),
        getattr(settings, 'TWILIO_PHONE_NUMBER', None)
    ]):
        print("Twilio is not configured. Skipping SMS.")
        return None

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    try:
        phone_number = otp.contact_info
        if not phone_number.startswith('+'):
            # Assume Indian numbers if no country code
            if not phone_number.startswith('91'):
                phone_number = f"+91{phone_number}"
            else:
                phone_number = f"+{phone_number}"

        client.messages.create(
            body=f'Your CityMate verification code is: {otp.code}',
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return otp
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return None
