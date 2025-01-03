from django.shortcuts import redirect
from .sms_senders import otp_sender
import random
from datetime import datetime

def create_otp():
    return random.randint(100000, 999999)

def send_otp(request):
    if "otp" in request.session:
        del request.session["otp"]
    otp = create_otp()
    request.session["otp"] = {
        "otp": otp,
        "timestamp": datetime.now().isoformat()
    }
    otp_sender(otp=otp, number=request.session["phone"])
    return redirect("accounts:input_otp")
