import os
#import pyrebase
from linebot import (LineBotApi, WebhookHandler)

namaBot = "dori"
line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('SECRET_TOKEN'))