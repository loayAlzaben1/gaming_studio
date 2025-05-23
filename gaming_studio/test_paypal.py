import paypalrestsdk
from dotenv import load_dotenv
import os

load_dotenv()
paypalrestsdk.configure({
    "mode": "live",
    "client_id": os.getenv("PAYPAL_CLIENT_ID"),
    "client_secret": os.getenv("PAYPAL_CLIENT_SECRET")
})

payment = paypalrestsdk.Payment({
    "intent": "sale",
    "payer": {"payment_method": "paypal"},
 "redirect_urls": {
    "return_url": "https://4cab-91-186-251-209.ngrok-free.app/donate/success/",
    "cancel_url": "https://4cab-91-186-251-209.ngrok-free.app/donate/"
},
    "transactions": [{
        "item_list": {
            "items": [{
                "name": "Test Game Item",
                "sku": "item1",
                "price": "1.00",
                "currency": "USD",
                "quantity": 1
            }]
        },
        "amount": {"total": "1.00", "currency": "USD"},
        "description": "Test transaction for Gaming Studio"
    }]
})

if payment.create():
    print("Payment created successfully")
    for link in payment.links:
        if link.rel == "approval_url":
            print(f"Redirect user to: {link.href}")
else:
    print(f"Error: {payment.error}")
    