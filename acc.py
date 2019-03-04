import os
import pyrebase
from linebot import (LineBotApi, WebhookHandler)

namaBot = ["dori","doribot"]
line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('SECRET_TOKEN'))

config = {
    "apiKey": os.environ.get('FIREBASE_API_KEY'),
    "authDomain": os.environ.get('FIREBASE_AUTH_DOMAIN'),
    "databaseURL": os.environ.get('FIREBASE_LINK_DATABASE'),
    "storageBucket": os.environ.get('FIREBASE_STORAGE_BUCKET')
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

bitly_username = os.environ.get('BITLY_USERNAME')
bitly_password = os.environ.get('BITLY_PASSWORD')

google_key = os.environ.get('GOOGLE_API_KEY')