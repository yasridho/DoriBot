from flask import Flask, request, abort

from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)

from argparse import ArgumentParser
from linebot.models import *
from templates import *

import requests, json
import os
import acc
import errno
import sys, random, datetime, time, re 
import tempfile
import urllib

from acc import *

app = Flask(__name__)
sleep = False

notes = {}

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
    line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(
                text="Hi! I'm DoriBot\nI'm glad to be here ;D"
            ),
            TextSendMessage(
                text='Type "Doribot: help" without quote to see my commands ;)',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(
                                label="Doribot: help",
                                text="Doribot: help"
                            )
                        )
                    ]
                )
            )
        ]
    )

@handler.add(FollowEvent)
def handle_follow(event):
    data = {'display_name':line_bot_api.get_profile(event.source.user_id).display_name,
            'picture_url':line_bot_api.get_profile(event.source.user_id).picture_url,
            'status_message':line_bot_api.get_profile(event.source.user_id).status_message,
            'follow_time':time.time()}
    db.child("users").child(event.source.user_id).set(data)
    try:
        total = db.child("users").get().val()["total"]
    except:
        total = 0
    db.child("users").child("total").set(total + 1)
    line_bot_api.reply_message(event.reply_token,
        [
            TextSendMessage(
                text='Hello '+line_bot_api.get_profile(event.source.user_id).display_name+'! My name is DoriBot, you can call me Dori ;)'
            ),
            TextSendMessage(
                text='Type "Doribot: help" without quote to see my commands ;)',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(
                                label="Doribot: help",
                                text="Doribot: help"
                            )
                        )
                    ]
                )
            )
        ]
    )

@handler.add(PostbackEvent)
def handle_postback(event):
    if ": " in event.postback.data:
        data = event.postback.data.split(": ",1)
        if len(data) > 1:
            cmd, args = data[0], data[1]
        else:
            cmd, args = data[0], ""

        if cmd == "ani":
            aniid, anitype = args.split(" ")
            line_bot_api.reply_message(
                event.reply_token,
                anilist_info(aniid, anitype)
            )

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    sender = event.source.user_id
    text = event.message.text
    
    if text.lower() in namaBot:
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(
                text="What can I do for you?"
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

        elif cmd in namaBot.lower():
            if args == "help":
                line_bot_api.reply_message(event.reply_token,
                    TextSendMessage(
                        text="Here's some command:\nAni: This will search and get anime/manga info from anilist (Usage: 'Ani: <keyword>')"
                    )
                )

        elif cmd == "ani":
            line_bot_api.reply_message(
                event.reply_token,
                anilist_search(args,1)
            )

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)