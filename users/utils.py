import requests
from django.conf import settings

def send_brevo_email(subject, html_content, to_email):
    url = "https://api.brevo.com/v3/smtp/email"

    payload = {
        "sender": {
            "name": "Dev journal",
            "email": settings.BREVO_SENDER_EMAIL,
        },
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html_content,
    }

    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json",
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print("Brevo error:", e)
        return False