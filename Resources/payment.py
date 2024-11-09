from flask import Flask, request, jsonify, make_response
import requests
import base64
from datetime import datetime
from flask_restx import Namespace, Resource, fields

payment_ns = Namespace('payments', description='Payment-related operations')

class PaymentResource(Resource):

    def get_token(self):
        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        consumer_key = "m8JMckxJn0aRtrqnoqD7ey4jH1w2WYbyhGe4tXGqMF9GxOGC"
        consumer_secret = "NfRXzw0qDCzXdu01TZqB8ojBobIknXCQ5E2BUCAKSEezF2dwrrCUmR4mN9GBk4Ze"
        auth = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()

        headers = {
            "Authorization": f"Basic {auth}"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json().get("access_token")
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def post(self):
        short_code = 174379
        passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

        # Get phone and amount from request body
        data = request.json
        phone = data.get("phone")
        amount = data.get("amount")

        if not phone or not amount:
            return make_response(jsonify({"error": "Phone number and amount are required"}), 400)

        # Ensure phone number is correctly formatted
        if phone.startswith("0"):
            phone = phone[1:]  # Remove leading zero
        phone = f"254{phone}"

        token = self.get_token()
        if not token:
            return make_response(jsonify({"error": "Unable to get token"}), 500)

        date = datetime.now()
        timestamp = date.strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(f"{short_code}{passkey}{timestamp}".encode()).decode()

        mpesa_data = {
            "BusinessShortCode": short_code,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": short_code,
            "PhoneNumber": phone,
            "CallBackURL": "https://mydomain.com/path",
            "AccountReference": "Mpesa Test",
            "TransactionDesc": "Testing stk push"
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=mpesa_data, headers=headers)
            response.raise_for_status()
            return jsonify(response.json())
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            print(f"Response content: {response.content}")
            return make_response(jsonify({"error": "Unable to process STK push", "details": response.json()}), 400)

payment_ns.add_resource(PaymentResource, '/sendSTKPush')
