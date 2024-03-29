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

tod_config = {
    "apiKey": os.environ.get('TOD_API_KEY'),
    "authDomain": os.environ.get('TOD_AUTH_DOMAIN'),
    "databaseURL": os.environ.get('TOD_LINK_DATABASE'),
    "storageBucket": os.environ.get('TOD_STORAGE_BUCKET')
}

tod_data = pyrebase.initialize_app(tod_config)
tod_db = tod_data.database()

firebase = pyrebase.initialize_app(config)
db = firebase.database()

bitly_access_token = os.environ.get('BITLY_ACCESS_TOKEN')

google_key = os.environ.get('GOOGLE_API_KEY')