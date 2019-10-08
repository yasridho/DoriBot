from linebot.models import *
import pyrebase
import random
from acc import tod_db

tod_question = {}

def getRandomTOD(choose):
    if len(tod_question) == 0:
        tod_question.update(tod_db.get().val())
    question = random.choice(tod_question[choose.capitalize()])
    return question

def TODQuestionUpdate(tod, question):
    try:
        total = tod_db.child("Pending").child(tod.capitalize()).child("total").get().val()
        num = total+1
        tod_db.child("Pending").update(tod.capitalize()).update({"Question"+str(total):question})
        tod_db.child("Pending").child(tod.capitalize()).update({"total":num})
    except:
        tod_db.child("Pending").child(tod.capitalize()).child("Question0").set(question)
        tod_db.child("Pending").child(tod.capitalize()).child("total").set(1)
    tod_question.update(tod_db.get().val())

def TODRemovePending(tod, index):
    tod_question.update(tod_db.get().val())
    tod_question["Pending"][tod.capitalize()].pop(index)
    tod_db.child("Pending").update(tod_question["Pending"])

def TODAdd(tod, question):
    try:
        tod_question[tod.capitalize()].append(question)
    except:
        tod_question.update(tod_db.get().val())
        tod_question[tod.capitalize()].append(question)
    tod_db.update(tod_question)

def TODReview(tod):
    database = tod_db.child("Pending").child(tod.capitalize()).get().val()
    bubble = []
    num = 0
    for r in database:
        for question in database[r]:
            bubble.append(
                BubbleContainer(
                    direction='ltr',
                    body=BoxComponent(
                        layout='vertical',
                        contents=[
                            BoxComponent(
                                layout='vertical',
                                spacing='md',
                                contents=[
                                    ImageComponent(
                                        url='https://img.icons8.com/flat_round/64/000000/question-mark.png',
                                        size='xxs'
                                    ),
                                    TextComponent(
                                        text=tod.capitalize(),
                                        align='center',
                                        weight='bold',
                                        color='#9AA6B4'
                                    )
                                ]
                            ),
                            TextComponent(
                                text=question,
                                margin='md',
                                size='sm',
                                align='center',
                                color='#9AA6B4',
                                wrap=True
                            )
                        ]
                    ),
                    footer=BoxComponent(
                        layout='horizontal',
                        contents=[
                            ButtonComponent(
                                action=PostbackAction(
                                    label='Accept',
                                    data=tod+': accept '+r
                                ),
                                color='#DFF536'
                            ),
                            SeparatorComponent(
                                color='#6E6E6E'
                            ),
                            ButtonComponent(
                                action=PostbackAction(
                                    label='Decline',
                                    data=tod+': decline '+r
                                ),
                                color='#F53636'
                            )
                        ]
                    ),
                    styles=BubbleStyle(
                        body=BlockStyle(
                            background_color='#1F2129'
                        ),
                        footer=BlockStyle(
                            background_color='#1F2129'
                        )
                    )
                )
            )
    msg = FlexSendMessage(
        alt_text='You\'re reviewing',
        contents=CarouselContainer(
            contents=bubble
        )
    )
    return msg

def TODRules():
    bubble = BubbleContainer(
        direction='ltr',
        body=BoxComponent(
            layout='vertical',
            contents=[
                BoxComponent(
                    layout='vertical',
                    spacing='md',
                    contents=[
                        ImageComponent(
                            url='https://img.icons8.com/flat_round/64/000000/question-mark.png',
                            size='xxs'
                        ),
                        TextComponent(
                            text='Truth or Dare',
                            align='center',
                            weight='bold',
                            color='#9AA6B4'
                        )
                    ]
                ),
                SeparatorComponent(
                    margin='md'
                ),
                BoxComponent(
                    layout='vertical',
                    margin='md',
                    contents=[
                        TextComponent(
                            text='Cara Bermain',
                            align='center',
                            color='#6EB1FF'
                        ),
                        BoxComponent(
                            layout='baseline',
                            spacing='sm',
                            margin='md',
                            contents=[
                                TextComponent(
                                    text='1.',
                                    flex=0,
                                    size='sm',
                                    color='#9AA6B4'
                                ),
                                TextComponent(
                                    text='Pemain lebih dari 1',
                                    size='sm',
                                    color='#9AA6B4',
                                    wrap=True
                                )
                            ]
                        ),
                        BoxComponent(
                            layout='baseline',
                            spacing='sm',
                            margin='md',
                            contents=[
                                TextComponent(
                                    text='2.',
                                    flex=0,
                                    size='sm',
                                    color='#9AA6B4'
                                ),
                                TextComponent(
                                    text='Pemain akan dipilih secara acak',
                                    size='sm',
                                    color='#9AA6B4',
                                    wrap=True
                                )
                            ]
                        ),
                        BoxComponent(
                            layout='baseline',
                            spacing='sm',
                            margin='md',
                            contents=[
                                TextComponent(
                                    text='3.',
                                    flex=0,
                                    size='sm',
                                    color='#9AA6B4'
                                ),
                                TextComponent(
                                    text='Pemain yang terpilih memilih antara Truth atau Dare',
                                    size='sm',
                                    color='#9AA6B4',
                                    wrap=True
                                )
                            ]
                        ),
                        BoxComponent(
                            layout='baseline',
                            spacing='sm',
                            margin='md',
                            contents=[
                                TextComponent(
                                    text='4.',
                                    flex=0,
                                    size='sm',
                                    color='#9AA6B4'
                                ),
                                TextComponent(
                                    text='Pemain melakukan/menjawab apa sesuai dengan pertanyaan/suruhan yang diberikan',
                                    size='sm',
                                    color='#9AA6B4',
                                    wrap=True
                                )
                            ]
                        ),
                        BoxComponent(
                            layout='baseline',
                            spacing='sm',
                            margin='md',
                            contents=[
                                TextComponent(
                                    text='5.',
                                    flex=0,
                                    size='sm',
                                    color='#9AA6B4'
                                ),
                                TextComponent(
                                    text='Jika pemain ingin berhenti ditengah permainan, ketik "udahan". Pemain akan dikeluarkan dari permainan',
                                    size='sm',
                                    color='#9AA6B4',
                                    wrap=True
                                )
                            ]
                        )
                    ]
                )
            ]
        ),
        footer=BoxComponent(
            layout='horizontal',
            contents=[
                ButtonComponent(
                    action=PostbackAction(
                        label='Gabung',
                        text='Aing ikut',
                        data='tod: join'
                    ),
                    color='#DFF536'
                )
            ]
        ),
        styles=BubbleStyle(
            body=BlockStyle(
                background_color='#1F2129'
            ),
            footer=BlockStyle(
                background_color='#1F2129'
            )
        )
    )
    msg = FlexSendMessage(
        alt_text='Truth or Dare',
        contents=bubble
    )
    return msg

def TODPlayerNotif():
    bubble = BubbleContainer(
        direction='ltr',
        body=BoxComponent(
            layout='vertical',
            contents=[
                BoxComponent(
                    layout='vertical',
                    spacing='md',
                    contents=[
                        ImageComponent(
                            url='https://img.icons8.com/flat_round/64/000000/question-mark.png',
                            size='xxs'
                        ),
                        TextComponent(
                            text='Truth or Dare',
                            align='center',
                            weight='bold',
                            color='#9AA6B4'
                        )
                    ]
                ),
                SeparatorComponent(
                    margin='md'
                ),
                TextComponent(
                    text='Pemain sudah cukup',
                    margin='md',
                    align='center',
                    color='#9AA6B4'
                ),
                TextComponent(
                    text='Silahkan klik tombol dibawah jika sudah siap mulai',
                    size='sm',
                    align='center',
                    color='#9AA6B4',
                    wrap=True
                )
            ]
        ),
        footer=BoxComponent(
            layout='horizontal',
            contents=[
                ButtonComponent(
                    action=PostbackAction(
                        label='Aku Siap!',
                        text='Ashiaapp',
                        data='tod: start'
                    ),
                    color='#DFF536'
                )
            ]
        ),
        styles=BubbleStyle(
            body=BlockStyle(
                background_color='#1F2129'
            ),
            footer=BlockStyle(
                background_color='#1F2129'
            )
        )
    )
    msg = FlexSendMessage(
        alt_text='Pemain cukup',
        contents=bubble
    )
    return msg

def TODPlayerChoose(user_name):
    bubble = BubbleContainer(
        direction='ltr',
        header=BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(
                    text=user_name,
                    size='lg',
                    align='center',
                    weight='bold',
                    color='#71C0D8'
                )
            ]
        ),
        body=BoxComponent(
            layout='vertical',
            contents=[
                BoxComponent(
                    layout='vertical',
                    spacing='md',
                    contents=[
                        ImageComponent(
                            url='https://img.icons8.com/flat_round/64/000000/question-mark.png',
                            size='xxs'
                        ),
                        TextComponent(
                            text='Truth or Dare',
                            align='center',
                            weight='bold',
                            color='#9AA6B4'
                        )
                    ]
                )
            ]
        ),
        footer=BoxComponent(
            layout='horizontal',
            contents=[
                ButtonComponent(
                    action=PostbackAction(
                        label='Truth',
                        text='Truth',
                        data='tod: truth'
                    ),
                    color='#38F536'
                ),
                SeparatorComponent(
                    color='#6E6E6E'
                ),
                ButtonComponent(
                    action=PostbackAction(
                        label='Dare',
                        text='Dare',
                        data='tod: dare'
                    ),
                    color='#FFC27D'
                )
            ]
        ),
        styles=BubbleStyle(
            header=BlockStyle(
                background_color='#25272B'
            ),
            body=BlockStyle(
                background_color='#1F2129'
            ),
            footer=BlockStyle(
                background_color='#1F2129'
            )
        )
    )
    msg = FlexSendMessage(
        alt_text=user_name+" memilih",
        contents=bubble
    )
    return msg

def TODPlayerQuestion(user_name, choose):
    question = getRandomTOD(choose)
    bubble = BubbleContainer(
        direction='ltr',
        header=BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(
                    text=user_name,
                    size='lg',
                    align='center',
                    weight='bold',
                    color='#71C0D8'
                )
            ]
        ),
        body=BoxComponent(
            layout='vertical',
            contents=[
                BoxComponent(
                    layout='vertical',
                    spacing='md',
                    contents=[
                        ImageComponent(
                            url='https://img.icons8.com/flat_round/64/000000/question-mark.png',
                            size='xxs'
                        ),
                        TextComponent(
                            text=choose.capitalize(),
                            align='center',
                            weight='bold',
                            color='#9AA6B4'
                        )
                    ]
                ),
                TextComponent(
                    text=question,
                    margin='md',
                    size='sm',
                    align='center',
                    color='#9AA6B4',
                    wrap=True
                ),
                TextComponent(
                    text='Klik tombol dibawah jika sudah menjawab',
                    margin='lg',
                    size='xs',
                    gravity='bottom',
                    color='#809F77',
                    wrap=True
                )
            ]
        ),
        footer=BoxComponent(
            layout='horizontal',
            contents=[
                ButtonComponent(
                    action=PostbackAction(
                        label='Done',
                        text='Udah',
                        data='tod: done'
                    ),
                    color='#DFF536'
                )
            ]
        ),
        styles=BubbleStyle(
            header=BlockStyle(
                background_color='#25272B'
            ),
            body=BlockStyle(
                background_color='#1F2129'
            ),
            footer=BlockStyle(
                background_color='#1F2129'
            )
        )
    )
    msg = FlexSendMessage(
        alt_text=user_name+' memilih '+choose.capitalize(),
        contents=bubble
    )
    return msg

def TODAddQuestion():
    bubble = BubbleContainer(
        direction='ltr',
        body=BoxComponent(
            layout='vertical',
            contents=[
                BoxComponent(
                    layout='vertical',
                    spacing='md',
                    contents=[
                        ImageComponent(
                            url='https://img.icons8.com/flat_round/64/000000/question-mark.png',
                            size='xxs'
                        ),
                        TextComponent(
                            text='Truth or Dare',
                            align='center',
                            weight='bold',
                            color='#9AA6B4'
                        )
                    ]
                ),
                TextComponent(
                    text='Kamu punya pertanyaan/tantangan yang unik?',
                    margin='md',
                    size='sm',
                    align='center',
                    color='#9AA6B4',
                    wrap=True
                ),
                TextComponent(
                    text='Kamu bisa menambah sendiri perintah/pertanyaan kamu dengan cara ketik:',
                    margin='md',
                    size='xs',
                    color='#9AA6B4',
                    wrap=True
                ),
                BoxComponent(
                    layout='baseline',
                    flex=0,
                    spacing='sm',
                    margin='md',
                    contents=[
                        TextComponent(
                            text='Truth: ',
                            flex=0,
                            margin='lg',
                            size='xs',
                            gravity='bottom',
                            color='#38F536'
                        ),
                        TextComponent(
                            text='Pertanyaan kamu',
                            size='xs',
                            color='#DFF536'
                        )
                    ]
                ),
                BoxComponent(
                    layout='baseline',
                    flex=0,
                    spacing='sm',
                    margin='md',
                    contents=[
                        TextComponent(
                            text='Dare: ',
                            flex=0,
                            margin='lg',
                            size='xs',
                            gravity='bottom',
                            color='#38F536'
                        ),
                        TextComponent(
                            text='Perintah kamu',
                            size='xs',
                            color='#DFF536'
                        )
                    ]
                )
            ]
        ),
        footer=BoxComponent(
            layout='horizontal',
            contents=[
                ButtonComponent(
                    action=PostbackAction(
                        label='Truth',
                        text='Truth',
                        data='tod: truth'
                    ),
                    color='#38F536'
                ),
                SeparatorComponent(
                    color='#6E6E6E'
                ),
                ButtonComponent(
                    action=PostbackAction(
                        label='Dare',
                        text='Dare',
                        data='tod: dare'
                    ),
                    color='#FFC27D'
                )
            ]
        ),
        styles=BubbleStyle(
            body=BlockStyle(
                background_color='#1F2129'
            )
        )
    )
    msg = FlexSendMessage(
        alt_text="Kamu punya pertanyaan/tantangan yang unik?",
        contents=bubble
    )
    return msg