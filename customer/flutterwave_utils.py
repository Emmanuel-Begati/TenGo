# customer/flutterwave_utils.py

from rave_python import Rave
from django.conf import settings

rave = Rave(settings.FLUTTERWAVE_PUBLIC_KEY, settings.FLUTTERWAVE_SECRET_KEY, usingEnv=False)

def initialize_payment(amount, email, reference):
    payload = {
        "tx_ref": reference,
        "amount": amount,
        "currency": "NGN",  # Update currency based on your requirements
        "redirect_url": "http://localhost:8000/payment/callback/",  # Update with your actual callback URL
        "payment_options": "card,account,ussd",
        "meta": {
            "consumer_id": 23,
            "consumer_mac": "92a3-912ba-1192a"
        },
        "customer": {
            "email": email,
            "phonenumber": "080****4528",
            "name": "Yemi Desola"  # Update with actual customer details
        },
        "customizations": {
            "title": "Your Food Order",
            "description": "Payment for items in cart",
            "logo": "http://www.piedpiper.com/app/themes/joystick-v27/images/logo.svg"  # Update with your logo URL
        }
    }
    
    try:
        response = rave.Card.charge(payload)
        if response["status"] == "success":
            return {
                "status": "success",
                "message": "Payment initialized",
                "data": {
                    "link": response["data"]["link"]
                }
            }
        else:
            return {
                "status": "error",
                "message": response["message"]
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

def verify_payment(transaction_id):
    try:
        response = rave.Card.verify(transaction_id)
        if response["status"] == "success":
            return {
                "status": "success",
                "message": "Payment verified",
                "data": response["data"]
            }
        else:
            return {
                "status": "error",
                "message": response["message"]
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
