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
    if isinstance(event.source, SourceRoom):
        room = event.source.room_id
    else:
        room = event.source.group_id
    db.child(event.source.type).child(room).set({"joined_at":time.time()})
    try:
        total = db.child(event.source.type).get().val()["total"]
        db.child(event.source.type).child("total").update(total+1)
    except:
        db.child(event.source.type).child("total").set(1)
    line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(
                text="Hi! I'm DoriBot\nI'm glad to be here ;D"
            ),
            TextSendMessage(
                text="I'll not respond before you add me first."
            )
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

@handler.add(LeaveEvent)
def handle_leave(event):
    if isinstance(event.source,SourceRoom):
        db.child(event.source.type).child(event.source.room_id).remove()
    else:
        db.child(event.source.type).child(event.source.group_id).remove()
    total = db.child(event.source.type).get().val()["total"]
    db.child(event.source.type).update({"total":total - 1})

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

@handler.add(UnfollowEvent)
def handle_unfollow(event):
    db.child("users").child(event.source.user_id).remove()
    total = db.child("users").get().val()["total"]
    db.child("users").update({"total":total - 1})

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
        
        elif cmd == "anires":
            page, keyword = args.split(" ",1)
            line_bot_api.reply_message(
                event.reply_token,
                anilist_search(keyword,page)
            )

        elif cmd == "quit":
            answer, room = args.split(" ")
            if room in notes:
                command, timestamp = notes[room]
                if command == "exit":
                    if time.time() - timestamp > 60:
                        del notes[room]
                    else:
                        if answer == "no":
                            line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage(text="Okay, I'm not going anywhere ;D")
                            )
                            del notes[room]
                        else:
                            line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage(text='Goodbye cruel world :(')
                            )
                            if isinstance(event.source, SourceGroup):
                                line_bot_api.leave_group(event.source.group_id)
                            else:
                                line_bot_api.leave_room(event.source.room_id)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    sender = event.source.user_id
    text = event.message.text
    if isinstance(event.source,SourceGroup):
        db.child(event.source.type).child(event.source.group_id).child("members").child(sender).set(line_bot_api.get_profile(sender).display_name)
    elif isinstance(event.source,SourceRoom):
        db.child(event.source.type).child(event.source.room_id).child("members").child(sender).set(line_bot_api.get_profile(sender).display_name)
    
    if text.lower() in namaBot:
        reply_with = [
            "What can I do for you?",
            "Is there something you need?",
            "Yesh? O.o",
            "Dori here! ><>",
            "Dori is typing...",
            "What do you want today?"]
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(
                text=random.choice(reply_with),
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(
                                label='Doribot: help',
                                text='Doribot: help'
                            )
                        )
                    ]
                )
            )
        )

    elif ":" in text:
        data = text.split(":",1)
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

        elif cmd in namaBot:
            if args == "help":
                line_bot_api.reply_message(event.reply_token,
                    TextSendMessage(
                        text="Here's some command:\nAni: This will search and get anime/manga info from anilist (Usage: 'Ani: <keyword>')"
                    )
                )
            elif args == "id":
                line_bot_api.reply_message(event.reply_token,
                    TextSendMessage(
                        text='Your id is: '+dori_id(event.source.user_id)+'\nType "id: <your_new_id>" to change.'
                    )
                )
            elif args == "bye":
                if isinstance(event.source, SourceUser):
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage('Where should I go?')
                    )
                    return
                if isinstance(event.source, SourceRoom):
                    room = event.source.room_id
                elif isinstance(event.source, SourceGroup):
                    room = event.source.group_id
                notes.update({room:["exit",time.time()]})
                line_bot_api.reply_message(
                    event.reply_token,
                    exit_confirm_button(room,event.source.type)
                )

        elif cmd == "ani":
            line_bot_api.reply_message(
                event.reply_token,
                anilist_search(args,1)
            )

        elif cmd == "id":
            if " " in args:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="It's prohibited to change id with space included.")
                )
            else:
                for user in db.child("users").get().val():
                    if args == db.child("users").child(user).child("user_id").get().val():
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text='Id is not available :(')
                        )
                        return
                try:
                    user_id = db.child("users").child(event.source.user_id).get().val()["user_id"]
                    db.child("users").child(event.source.user_id).child("user_id").update(args)
                except:
                    db.child("users").child(event.source.user_id).child("user_id").set(args)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text='Changed successfully!\nType "Dori: id" to check your current id ;D')
                )

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)