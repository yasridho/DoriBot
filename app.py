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
from games import *

app = Flask(__name__)
sleep = False

notes = {}
players = {}

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
        db.child(event.source.type).update({"total":total+1})
    except:
        db.child(event.source.type).child("total").set(1)
    line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(
                text="Hi! I'm DoriBot\nGlad to be here ;D"
            ),
            TextSendMessage(
                text="I'll not respond until you add me first."
            ),
            TextSendMessage(
                text='Type "Doribot: help" without quote to see my commands ;)',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(
                                label="Help",
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
    try:
        gambar = line_bot_api.get_profile(event.source.user_id).picture_url
    except:
        gambar = ''
    try:
        status = line_bot_api.get_profile(event.source.user_id).status_message
    except:
        status = ''
    data = {'display_name':line_bot_api.get_profile(event.source.user_id).display_name,
            'picture_url':gambar,
            'status_message':status,
            'follow_time':time.time()}
    db.child("users").child(event.source.user_id).set(data)
    try:
        total = db.child("users").get().val()["total"]
    except:
        db.child("users").child("total").set(0)
    db.child("users").update({"total":total+1})
    line_bot_api.reply_message(event.reply_token,
        [
            TextSendMessage(
                text='Hello '+line_bot_api.get_profile(event.source.user_id).display_name+'! My name is DoriBot, you can call me Dori ;)'
            ),
            warning_message(
                "You need to change your default id!",
                "id:",
                "your_new_user_id",
                "human_being"
            ),
            TextSendMessage(
                text='Just call me when you need me ;)',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(
                                label='Help',
                                text='Doribot: help'
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

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    sender = event.source.user_id
    if sender in notes:
        command, timestamp = notes[sender]
        if (time.time() - timestamp) > 60:
            del notes[sender]
        else:
            if command == "location":
                try:
                    msg = nearest_theater(event.message.latitude, event.message.longitude)
                    del notes[sender]
                except:
                    msg = TextSendMessage(
                        text="Can't find nearest theater in your area.\nMake sure you drop the pin in the right area.",
                        quick_reply=QuickReply(
                            items=[
                                QuickReplyButton(
                                    action=LocationAction(
                                        label='Share location'
                                    )
                                )
                            ]
                        )
                    )
                data = {'address':event.message.address,
						'latitude':event.message.latitude,
						'longitude':event.message.longitude}
                db.child("users").child(sender).child("location").set(data)
                line_bot_api.reply_message(event.reply_token,msg)

@handler.add(PostbackEvent)
def handle_postback(event):
    sender = event.source.user_id
    if isinstance(event.source, SourceRoom):
        room = event.source.room_id
    elif isinstance(event.source, SourceGroup):
        room = event.source.group_id

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

        elif cmd == "theater":
            line_bot_api.reply_message(
                event.reply_token,
                xxi_playing(args)
            )
        
        elif cmd == "img":
            link, preview = args.split()
            if link[:14] == "http://bit.ly/":
                link = bitly_expander(link)
            if preview[:14] == "http://bit.ly/":
                preview = bitly_expander(preview)
            line_bot_api.reply_message(
                event.reply_token,
                ImageSendMessage(
                    original_content_url=link,
                    preview_image_url=preview
                )
            )

        elif cmd == "img_page":
            startIndex, keyword = args.split(" ",1)
            line_bot_api.reply_message(
                event.reply_token,
                gis(keyword,startIndex)
            )

        elif cmd == "tod":
            if args == "join":
                players[room]["players"].append(sender)
                players[room]["lastActive"] = time.time()
                msg = []
                msg.append(TextSendMessage(
                        text=line_bot_api.get_profile(sender).display_name+" telah bergabung.",
                        quick_reply=QuickReply(
                            items=[
                                QuickReplyButton(
                                    action=PostbackAction(
                                        label='Gabung',
                                        text='Aing ikut',
                                        data='tod: join'
                                    )
                                )
                            ]
                        )
                    )
                )
                if len(players[room]["players"]) > 1:
                    msg.append(TODPlayerNotif())
            elif args == "start":
                if sender in players[room]["players"]:
                    try:
                        current_target = players[room]["chosen"]
                    except:
                        current_target = None
                    if current_target == None:
                        target = random.choice(players[room]["players"])
                        target_name = line_bot_api.get_profile(target).display_name
                        send = "Botol berputar... menunjuk ke "+target_name
                        players[room].update({"chosen":target})
                        msg = TODPlayerChoose(target_name)
                    else:
                        msg = TextSendMessage(
                            text='Permainan sudah dimulai'
                        )
                else:
                    msg = TextSendMessage(
                        text="Kamu bukan pemain, silahkan gabung dulu sebelum permainan dimulai"
                    )
            elif args == "done":
                if sender == players[room]["chosen"]:
                    lucky_guy = players[room]["chosen"]
                    name = line_bot_api.get_profile(lucky_guy).display_name
                    send = name+' memutar botol... botol menunjuk ke '+target_name
                    players[room]["chosen"] = target
                    msg = TODPlayerChoose(target_name)
                else:
                    msg = TextSendMessage(
                        text='Bukan giliran lau'
                    )
            else:
                chosen = players[room]["chosen"]
                chosen_name = line_bot_api.get_profile(chosen).display_name
                msg = TODPlayerQuestion(chosen_name, args)
            line_bot_api.reply_message(event.reply_token, msg)

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
    if isinstance(event.source, SourceRoom):
        room = event.source.room_id
    elif isinstance(event.source, SourceGroup):
        room = event.source.group_id
    
    if event.source.type in ["room","group"]:
        try:
            members = db.child(event.source.type).child(room).get().val()["members"]
            if sender not in members:
                db.child(event.source.type).child(room).child("members").child(sender).set(line_bot_api.get_profile(sender).display_name)
        except:
            db.child(event.source.type).child(room).child("members").child(sender).set(line_bot_api.get_profile(sender).display_name)
    
    if line_bot_api.get_profile(sender).display_name != db.child("users").child(sender).child('display_name').get().val():
        try:
            for room in db.child("room").get().val():
                for person in db.child("room").child(room).child("members").get().val():
                    if person == sender:
                        db.child("room").child(room).child("members").update({person:line_bot_api.get_profile(person).display_name})
        except:pass
        try:
            for group in db.child("group").get().val():
                for person in db.child("group").child(group).child("members").get().val():
                    if person == sender:
                        db.child("group").child(group).child("members").update({person:line_bot_api.get_profile(person).display_name})
        except:pass
        db.child("users").child(sender).update({'display_name':line_bot_api.get_profile(sender).display_name})
    
    try:
        if line_bot_api.get_profile(sender).picture_url != db.child("users").child(sender).child('picture_url').get().val():
            db.child("users").child(sender).update({'picture_url':line_bot_api.get_profile(sender).picture_url})
    except:pass

    if line_bot_api.get_profile(sender).status_message != db.child("users").child(sender).child('status_message').get().val():
        db.child("users").child(sender).update({'status_message':line_bot_api.get_profile(sender).status_message})
    
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
                        ),
                        QuickReplyButton(
                            action=MessageAction(
                                label='Check TP',
                                text='TP: List'
                            )
                        )
                    ]
                )
            )
        )

    elif text.lower() == "udahan":
        if sender in players[room]["players"]:
            players[room]["players"].remove(sender)
            name = line_bot_api.get_profile(sender).display_name
            if len(players[room]["players"]) > 1:
                if players[room]["chosen"] == sender:
                    lucky_guy = players[room]["chosen"]
                    send = name+' berhenti bermain dan memutar botol untuk terakhir kalinya...\nbotol menunjuk ke '+target_name
                    players[room]["chosen"] = target
                    msg = TextSendMessage(
                        text=send,
                        quick_reply=QuickReply(
                            items=[
                                QuickReplyButton(
                                    action=PostbackAction(
                                        label='Truth',
                                        text='Jujur',
                                        data='tod:truth'
                                    )
                                ),
                                QuickReplyButton(
                                    action=PostbackAction(
                                        label='Dare',
                                        text='Berani',
                                        data='tod:dare'
                                    )
                                )
                            ]
                        )
                    )
                else:
                    msg = TextSendMessage(text=name+' berhenti bermain')
            else:
                msg = TextSendMessage(text=name+' berhenti bermain\nKarena kekurangan pemain, permainan diberhentikan')
                players.pop(room)
            line_bot_api.reply_message(event.reply_token,msg)

    elif ":" in text:
        data = text.split(":",1)
        if len(data) > 1:
            cmd, args = data[0].lower(), data[1]
        else:
            cmd, args = data[0].lower(), ""
        if args[0] == " ":
            args = args[1:]
        cmd = cmd.replace(" ","")

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
                        text="""Here's some command:
                        \nAni: This will search and get anime/manga info from anilist (Usage: 'Ani: anime/manga')
                        \nTP: Weekend? MITOS, coba cek ada TP gak? (Usage: 'TP: List' or 'TP: matkul')
                        \nBitly: Shorten your link with bitly (Usage: 'Bitly: long_url')
                        """
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

        elif cmd == "tp":
            matkul = {
                "strukdat":"struktur-data",
                "dap":"dasar-algoritma-dan-pemrograman",
                "std":"struktur-data",
                "pbo":"pemrograman-berorientasi-objek-a",
                "pbd":"pemodelan-basis-data",
                "jarkom":"jaringan-komputer",
                "sod":"sistem-operasi-dasar",
                "bd":"basis-data",
                "pw":"pemrograman-web"
            }
            args = args.lower()
            try:
                short = list(matkul.keys())[list(matkul.values()).index(args.replace(" ","-"))]
                args = short
            except:
                short = None
            
            if args == "list":
                msg = listTP()
            elif args in matkul:
                msg = cekTP(args)
            else:
                msg = TextSendMessage(text=args.capitalize()+' tidak ada TP :/')

            line_bot_api.reply_message(event.reply_token, msg)

        elif cmd == "bitly":
            try:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=bitly_shortener(args))
                )
            except:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="Link is invalid, make sure you type it correctly")
                )

        elif cmd == "gis":
            line_bot_api.reply_message(
                event.reply_token,
                gis(args,1)
            )

        elif cmd == "xxi":
            try:
                location = db.child("users").child(sender).get().val()["location"]
                msg = nearest_theater(location["latitude"],location["longitude"])
            except:
                notes.update({sender:["location",time.time()]})
                msg = TextSendMessage(
                    text='Where are you?\nPlease share your location first.',
                    quick_reply=QuickReply(
                        items=[
                            QuickReplyButton(
                                action=LocationAction(
                                    label='Share Location'
                                )
                            )
                        ]
                    )
                )
            line_bot_api.reply_message(event.reply_token,msg)

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

        elif cmd == "game":
            if args == "tod" or args == "truth or dare":
                players.update({room:{"game":"tod","players":[],"lastActive":time.time()}})
                msg = TODRules()
            line_bot_api.reply_message(event.reply_token,msg)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)