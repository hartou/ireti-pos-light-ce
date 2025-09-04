#! /usr/bin/env python3.6

# Python 3.6 or newer required.

import json
import os
import stripe

# This is your test secret API key.
stripe.api_key = 'sk_test_YOUR_TEST_SECRET_KEY_HERE'

from flask import Flask, jsonify, request, render_template


app = Flask(__name__, static_folder='public',
            static_url_path='', template_folder='public')

@app.route('/')
def index():
  return render_template('index.html')

def create_location():
  location = stripe.terminal.Location.create(
    display_name='HQ',
    address={
      'line1': '1272 Valencia Street',
      'city': 'San Francisco',
      'state': 'CA',
      'country': 'US',
      'postal_code': '94110',
    },
  )

  return location



@app.route('/create_payment_intent', methods=['POST'])
def secret():
  data = json.loads(request.data)

  # For Terminal payments, the 'payment_method_types' parameter must include
  # 'card_present'.
  # To automatically capture funds when a charge is authorized,
  # set `capture_method` to `automatic`.
  intent = stripe.PaymentIntent.create(
    amount=data['amount'],
    currency='usd',
    payment_method_types=[
      'card_present',
    ],
    capture_method='automatic',
    payment_method_options={
      "card_present": {
        "capture_method": "manual_preferred"
      }
    }
  )
  return intent



# The ConnectionToken's secret lets you connect to any Stripe Terminal reader
# and take payments with your Stripe account.
# Be sure to authenticate the endpoint for creating connection tokens.
@app.route('/connection_token', methods=['POST'])
def token():
  connection_token = stripe.terminal.ConnectionToken.create()
  return jsonify(secret=connection_token.secret)

@app.route('/capture_payment_intent', methods=['POST'])
def capture():
  data = json.loads(request.data)

  intent = stripe.PaymentIntent.capture(
    data['payment_intent_id']
  )

  return intent

if __name__ == '__main__':
    app.run()