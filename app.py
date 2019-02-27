from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)

from acc import (
    namaBot, line_bot_api, handler
)

from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)

from argparse import ArgumentParser
from linebot.models import *

import requests, json
import os
import errno
import sys, random, datetime, time, re 
import tempfile
import urllib

app = Flask(__name__)
sleep = False

#Post Request
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: "+body)
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(event.reply_token,
        TextSendMessage(
            text="Hai, saya DoriBot! Salam kenal dan senang berada disini :)"
        ),
        TextSendMessage(
            text='DoriBot bisa apa saja? Silahkan ketik ".help" tanpa tanda kutip untuk mengetahui cara kerja DoriBot ;D',
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(
                        action=MessageAction(
                            label=".help",
                            text=".help"
                        )
                    )
                ]
            )
        )
    )

@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(event.reply_token,
        [
            TextSendMessage(
                text='Salam kenal '+line_bot_api.get_profile(event.source.user_id).display_name+'! Saya DoriBot, bisa dipanggil Dori ;)'
            ),
            TextSendMessage(
                text='DoriBot bisa apa saja? Silahkan ketik ".help" untuk mengetahui cara kerja DoriBot ;D',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(
                                label=".help",
                                text=".help"
                            )
                        )
                    ]
                )
            )
        ]
    )

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    sender = event.source.user_id
    text = event.message.text
    
    if text.lower() in ["dori","doribot"]:
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(
                text="Ada yang bisa dibantu?"
            )
        )

    elif text.lower() == ".help":
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(
                text='Berikut adalah command yang dapat kakak pakai:'
            )
        )

    elif ": " in text:
        data = text.split(": ",1)
        if len(data) > 1:
            cmd, args = data[0].lower(), data[1]
        else:
            cmd, args = data[0].lower(), ""

        if cmd == "say":
            line_bot_api.reply_message(event.reply_token,
                TextSendMessage(
                    text=args
                )
            )

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)