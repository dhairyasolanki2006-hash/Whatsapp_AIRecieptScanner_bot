from dotenv import load_dotenv
import os
import requests
from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request
from scan_parse import *

app = Flask(__name__)
load_dotenv()
account_sid = os.getenv('ACCOUNT_SID')
auth_token = os.getenv('AUTH_TOKEN')

@app.route('/webhook', methods=['POST'])
def webhook():
    numberOfPic = int(request.values.get('NumMedia', ''))
    if numberOfPic > 0:
        media_url = request.values.get('MediaUrl0', '')
        response = requests.get(media_url, auth=(account_sid, auth_token))

        status = store(response.content)
        result = MessagingResponse()
        result.message(status)
        return str(result)
    else:
        resp = MessagingResponse()
        resp.message("Please send a pictures of receipt")
        return str(resp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)

