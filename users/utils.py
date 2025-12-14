import requests
from django.conf import settings


def send_otp_msg91(mobile, otp):
    url = "https://api.msg91.com/api/v5/flow/"

    payload = {
        "flow_id": settings.MSG91_FLOW_ID,
        "sender": settings.MSG91_SENDER_ID,
        "mobiles": f"91{mobile}",
        "otp": otp
    }

    headers = {
        "authkey": settings.MSG91_AUTH_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.status_code == 200
