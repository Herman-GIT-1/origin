import os
import requests
from dotenv import load_dotenv
from datetime import datetime
from flask_mail import Message
from extensions import db, mail

def save_payout_to_db(payout_batch_id, amount, currency, recipient_email, sent_date):
    from app import PayoutHistory
    existing_payout = PayoutHistory.query.filter_by(batch_id=payout_batch_id).first()
    
    if not existing_payout:
        new_payout = PayoutHistory(
            batch_id=payout_batch_id,
            amount=amount,
            currency=currency,
            recipient_email=recipient_email,
            sent_date=sent_date
        )
        db.session.add(new_payout)
        db.session.commit()

load_dotenv()

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")
PAYPAL_MODE = os.getenv("PAYPAL_MODE", "sandbox")

PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com" if PAYPAL_MODE == "sandbox" else "https://api-m.paypal.com"


def get_access_token():
    """Получаем OAuth 2.0 токен от PayPal"""
    url = f"{PAYPAL_API_BASE}/v1/oauth2/token"
    headers = {"Accept": "application/json", "Accept-Language": "en_US"}
    data = {"grant_type": "client_credentials"}
    
    response = requests.post(url, auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET), headers=headers, data=data)
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"{response.text}")


def create_payout(receiver_email, amount, currency="USD"):
    """Создаёт выплату через PayPal Payouts API"""
    access_token = get_access_token()
    url = f"{PAYPAL_API_BASE}/v1/payments/payouts"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    payload = {
        "sender_batch_header": {
            "sender_batch_id": "batch_" + os.urandom(8).hex(),
            "email_subject": "You have received a payment!"
        },
        "items": [
            {
                "recipient_type": "EMAIL",
                "receiver": receiver_email,
                "amount": {
                    "value": f"{amount:.2f}",
                    "currency": currency
                },
                "note": "Thank you for using our service!",
                "sender_item_id": "item_1"
            }
        ]
    }

    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code in [200, 201]:
        return response.json()
    else:
        raise Exception(f"{response.text}")


def get_payout_status(payout_batch_id):
    """Проверяет статус выплаты и сохраняет её в базу"""
    access_token = get_access_token()
    url = f"{PAYPAL_API_BASE}/v1/payments/payouts/{payout_batch_id}"
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        payout_info = response.json()
        amount = payout_info["items"][0]["payout_item"]["amount"]["value"]
        currency = payout_info["items"][0]["payout_item"]["amount"]["currency"]
        sent_date = payout_info["batch_header"]["time_created"]
        recipient_email = payout_info["items"][0]["payout_item"]["receiver"]

        sent_date = datetime.strptime(sent_date, "%Y-%m-%dT%H:%M:%SZ")

        existing_payout = PayoutHistory.query.filter_by(batch_id=payout_batch_id).first()
        if not existing_payout:
            new_payout = PayoutHistory(
                batch_id=payout_batch_id,
                amount=amount,
                currency=currency,
                recipient_email=recipient_email,
                sent_date=sent_date
            )
            db.session.add(new_payout)
            db.session.commit()
            send_payout_email(recipient_email, amount, currency, sent_date)

        return {
            "batch_id": payout_batch_id,
            "amount": f"{amount} {currency}",
            "sent_date": sent_date.strftime("%d %B %Y, %H:%M"),
            "full_response": payout_info
        }
    else:
        raise Exception(f"Ошибка при проверке статуса: {response.text}")

def send_payout_email(to_email, amount, currency, sent_date):
    msg = Message(
        "Payment has been successfully sent",
        sender="your_email@example.com",
        recipients=[to_email]
    )
    msg.body = f"""
    Hello,

    Payment was sent to your account:{amount} {currency}.
    
    Transaction date: {sent_date.strftime('%d %B %Y, %H:%M')}

    Thank you!
    """
    mail.send(msg)