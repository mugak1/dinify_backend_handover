import requests
import json
from typing import Optional
from decouple import config
from dataclasses import dataclass
from misc_app.controllers.determine_telecom import determine_telecom


@ dataclass
class Pesapal:
    pesapal_domain = 'https://cybqa.pesapal.com/pesapalv3/api'
    HEADERS = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }

    def authenticate(self):
        URL = f"{self.pesapal_domain}/Auth/RequestToken"
        post_body = {
            'consumer_key': config('PESAPAL_CONSUMER_KEY'),
            'consumer_secret': config('PESAPAL_CONSUMER_SECRET')
        }
        print(URL, post_body)
        response = requests.post(
            URL,
            data=json.dumps(post_body),
            headers=self.HEADERS,
        )
        response = response.json()
        print(f"\nResponse: {response}\n")
        response['status'] = 200
        return response
    



