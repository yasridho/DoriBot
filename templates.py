import requests, json
import calendar
import io
import urllib
import pyrebase
from colorthief import ColorThief
from linebot.models import *
from acc import line_bot_api, db

def dori_id(args):
    try:
        user_id = db.child("users").child(args).get().val()["user_id"]
    except:
        user_id = args
    return user_id

def exit_confirm_button(args,roomtype):
    msg = TemplateSendMessage(
        alt_text='WARNING!',
        template=ButtonsTemplate(
            title='Are you sure?',
            text='All data in this '+roomtype+' will be deleted.',
            thumbnail_image_url='https://i.postimg.cc/44h5z8pM/warning-sign.png',
            actions=[
                PostbackAction(
                    label="NO! DON'T DO THAT!",
                    text='Cancel',
                    data='quit: no '+args
                ),
                PostbackAction(
                    label='JUST DO IT!',
                    text='Get out',
                    data='quit: yes '+args
                )
            ]
        )
    )
    return msg

def anilist_search(args,page):
    query = '''
    query ($id: Int, $page: Int, $perPage: Int, $search: String) {
        Page (page: $page, perPage: $perPage) {
            pageInfo {
                total
                currentPage
                lastPage
                hasNextPage
                perPage
            }
            media (id: $id, search: $search) {
                id
                status
                title {
                    romaji
                    english
                    native
                    userPreferred
                }
                type
                bannerImage
            }
        }
    }
    '''
    variables = {
        'search': args,
        'page': page,
        'perPage': 9
    }
    url = 'https://graphql.anilist.co'
    response = requests.post(url, json={'query': query, 'variables': variables})
    results = response.text
    data = json.loads(results)["data"]["Page"]["media"]
    has_next_page = json.loads(results)["data"]["Page"]["pageInfo"]["hasNextPage"]
    if len(data) != 0:
        res = list()
        for ani in data:
            bannerImage = ani["bannerImage"]
            if bannerImage == None:
                bannerImage = 'https://i.postimg.cc/W47ZfhC9/no-image.png'
            anitype = ani["type"]
            title_romaji = ani["title"]["romaji"]
            title_native = ani["title"]["native"]
            if title_native == None:
                title_native = title_romaji
            status = ani["status"]
            ani_id = ani["id"]
        
            res.append(
                BubbleContainer(
                    direction='ltr',
                    header=BoxComponent(
                        layout='vertical',
                        contents=[
                            TextComponent(
                                text=args,
                                align='center',
                                color='#9AA6B4'
                            )
                        ]
                    ),
                    hero=ImageComponent(
                        url=bannerImage,
                        size='full',
                        aspect_ratio='3:1',
                        aspect_mode='cover'
                    ),
                    body=BoxComponent(
                        layout='vertical',
                        contents=[
                            TextComponent(
                                text=title_native,
                                align='center',
                                color='#9AA6B4'
                            ),
                            BoxComponent(
                                layout='baseline',
                                margin='sm',
                                contents=[
                                    TextComponent(
                                        text='Title',
                                        size='sm',
                                        align='start',
                                        weight='bold',
                                        color='#9AA6B4'
                                    ),
                                    TextComponent(
                                        text=title_romaji,
                                        flex=3,
                                        size='sm',
                                        align='start',
                                        color='#9AA6B4'
                                    )
                                ]
                            ),
                            BoxComponent(
                                layout='baseline',
                                margin='sm',
                                contents=[
                                    TextComponent(
                                        text='Type',
                                        size='sm',
                                        align='start',
                                        weight='bold',
                                        color='#9AA6B4'
                                    ),
                                    TextComponent(
                                        text=anitype.capitalize(),
                                        flex=3,
                                        size='sm',
                                        align='start',
                                        color='#9AA6B4'
                                    )
                                ]
                            ),
                            BoxComponent(
                                layout='baseline',
                                margin='sm',
                                contents=[
                                    TextComponent(
                                        text='Status',
                                        size='sm',
                                        align='start',
                                        weight='bold',
                                        color='#9AA6B4'
                                    ),
                                    TextComponent(
                                        text=status.capitalize(),
                                        flex=3,
                                        size='sm',
                                        align='start',
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
                                    label='Details',
                                    text=title_romaji,
                                    data="ani: "+str(ani_id)+" "+anitype
                                ),
                                color='#9AA6B4'
                            )
                        ]
                    ),
                    styles=BubbleStyle(
                        header=BlockStyle(
                            background_color='#1E222C',
                        ),
                        body=BlockStyle(
                            background_color='#262B37'
                        ),
                        footer=BlockStyle(
                            background_color='#262B37'
                        )
                    )
                )
            )
            if has_next_page:
                res.append(
                    BubbleContainer(
                        direction='ltr',
                        body=BoxComponent(
                            contents=[
                                ButtonComponent(
                                    color='#9AA6B4',
                                    action=PostbackAction(
                                        label='NEXT PAGE',
                                        text='next',
                                        data='anires: '+str(int(page)+1)+' '+args
                                    )
                                )
                            ]
                        ),
                        styles=BubbleStyle(
                            body=BlockStyle(
                                background_color='#262B37'
                            )
                        )
                    )
                )
        send = FlexSendMessage(
            alt_text=args,
            contents=CarouselContainer(
                contents=res
            )
        )
    else:
        send = TextSendMessage(
            text="Dori can't found "+args+" in anilist :("
        )
    return send

def anilist_info(anid,anitype):
    query = '''
    query ($id: Int) {
        Media (id: $id, type: '''+anitype.upper()+''') {
            id
            genres
            type
            format
            season
            trailer {
                id
            }
            averageScore
            coverImage {
                extraLarge
                large
                medium
                color
            }
            title {
                romaji
                english
                native
                userPreferred
            }
            description
            siteUrl
            countryOfOrigin
            source
            status
            startDate {
                year
                month
                day
            }
            endDate {
                year
                month
                day
            }
            synonyms
            updatedAt
            isAdult
            duration
            episodes
            chapters
            volumes
            rankings {
                rank
                type
                season
            }
        }
    }
    '''
    variables = {
        'id': anid
    }
    url = 'https://graphql.anilist.co'
    response = requests.post(url, json={'query': query, 'variables': variables})
    results = response.text
    data = json.loads(results)["data"]["Media"]

    trailer = data["trailer"]
    genres = data["genres"]
    if len(genres) == 0:
        genres = 'Unknown'
    else:
        genres = ", ".join(genres)
    aniformat = data["format"]
    try:
        season = data["season"]+" "+str(data["startDate"]["year"])
    except:
        season = 'Unknown'
    score = data["averageScore"]
    if score == None:
        score = 0
    image = data["coverImage"]["large"]
    judul = data["title"]["romaji"]
    source = data["source"]
    status = data["status"]
    try:
        startDate = str(data["startDate"]["day"])+" "+calendar.month_name[data["startDate"]["month"]]+" "+str(data["startDate"]["year"])
    except:
        startDate = 'Unknown'
    try:
        endDate = str(data["endDate"]["day"])+" "+calendar.month_name[data["endDate"]["month"]]+" "+str(data["endDate"]["year"])
    except:
        endDate = 'Unknown'
    
    if anitype == 'ANIME':
        ani_1 = "Duration"
        ani_12 = str(data["duration"])+" minutes"
        if ani_12 == None:
            ani_12 = 0
        ani_2 = "Episodes"
        ani_22 = str(data["episodes"])+" episodes"
        if ani_22 == None:
            ani_22 = 0
    else:
        ani_1 = "Chapters"
        ani_12 = str(data["chapters"])+" chapters"
        if ani_12 == None:
            ani_12 = 0
        ani_2 = "Volumes"
        ani_22 = str(data["volumes"])+" volumes"
        if ani_22 == None:
            ani_22 = 0
    
    desc = data["description"]
    synopsis = desc.replace('<br>','\n').replace('<i>','').replace('</i>','').replace('<b>','').replace('</b>','')

    fd = urllib.request.urlopen(urllib.request.Request(image, headers={'User-Agent': "Mozilla/4.0 (compatible; MSIE 5.01; Windows NT 5.0)"}))
    f = io.BytesIO(fd.read())
    color_thief = ColorThief(f)
    colorbg = "#%02x%02x%02x" % color_thief.get_palette(quality=1)[1]
    colortxt = "#%02x%02x%02x" % color_thief.get_palette(quality=1)[0]

    tr_post = list()
    if source == None:
        source = 'Unknown'

    if trailer != None:
        tr_post.append(
            ButtonComponent(
                action=URIAction(
                    label='Watch Trailer',
                    uri='https://youtu.be/'+trailer["id"]
                ),
                color=colortxt,
                height='sm'
            )
        )
    else:
        tr_post.append(
            TextComponent(
                text='No Trailer',
                align='center',
                color=colortxt
            )
        )
    msg = FlexSendMessage(
        alt_text=judul,
        contents=CarouselContainer(
            contents=[
                BubbleContainer(
                    direction='ltr',
                    header=BoxComponent(
                        layout='vertical',
                        contents=[
                            TextComponent(
                                text=judul,
                                align='center',
                                weight='bold',
                                color=colortxt
                            )
                        ]
                    ),
                    hero=ImageComponent(
                        url=image,
                        size='full',
                        aspect_ratio='3:4',
                        aspect_mode='cover'
                    ),
                    body=BoxComponent(
                        layout='vertical',
                        contents=[
                            TextComponent(
                                text='Average Score: '+str(score)+'%',
                                size='sm',
                                align='center',
                                color=colortxt
                            )
                        ]
                    ),
                    styles=BubbleStyle(
                        header=BlockStyle(
                            background_color=colorbg
                        ),
                        body=BlockStyle(
                            background_color=colorbg
                        )
                    )
                ),
                BubbleContainer(
                    direction='ltr',
                    header=BoxComponent(
                        layout='vertical',
                        contents=[
                            TextComponent(
                                text='INFO',
                                align='center',
                                weight='bold',
                                color=colortxt
                            )
                        ]
                    ),
                    body=BoxComponent(
                        layout='vertical',
                        contents=[
                            BoxComponent(
                                layout='baseline',
                                contents=[
                                    TextComponent(
                                        text='Genres',
                                        size='sm',
                                        align='start',
                                        color=colortxt
                                    ),
                                    TextComponent(
                                        text=genres,
                                        flex=3,
                                        size='sm',
                                        align='start',
                                        color=colortxt,
                                        wrap=True
                                    )
                                ]
                            ),
                            BoxComponent(
                                layout='baseline',
                                contents=[
                                    TextComponent(
                                        text='Type',
                                        size='sm',
                                        align='start',
                                        color=colortxt
                                    ),
                                    TextComponent(
                                        text=anitype.capitalize(),
                                        flex=3,
                                        size='sm',
                                        color=colortxt
                                    )
                                ]
                            ),
                            BoxComponent(
                                layout='baseline',
                                contents=[
                                    TextComponent(
                                        text='Season',
                                        size='sm',
                                        align='start',
                                        color=colortxt
                                    ),
                                    TextComponent(
                                        text=season,
                                        flex=3,
                                        size='sm',
                                        color=colortxt
                                    )
                                ]
                            ),
                            BoxComponent(
                                layout='baseline',
                                contents=[
                                    TextComponent(
                                        text='Source',
                                        size='sm',
                                        align='start',
                                        color=colortxt
                                    ),
                                    TextComponent(
                                        text=source.capitalize(),
                                        flex=3,
                                        size='sm',
                                        color=colortxt
                                    )
                                ]
                            ),
                            BoxComponent(
                                layout='baseline',
                                contents=[
                                    TextComponent(
                                        text='Status',
                                        size='sm',
                                        align='start',
                                        color=colortxt
                                    ),
                                    TextComponent(
                                        text=status.capitalize(),
                                        flex=3,
                                        size='sm',
                                        color=colortxt
                                    )
                                ]
                            ),
                            BoxComponent(
                                layout='vertical',
                                spacing='none',
                                margin='md',
                                contents=[
                                    TextComponent(
                                        text='Start Date',
                                        size='sm',
                                        align='start',
                                        weight='bold',
                                        color=colortxt
                                    ),
                                    TextComponent(
                                        text=startDate,
                                        size='sm',
                                        color=colortxt
                                    )
                                ]
                            ),
                            BoxComponent(
                                layout='vertical',
                                spacing='none',
                                margin='md',
                                contents=[
                                    TextComponent(
                                        text='End Date',
                                        size='sm',
                                        align='start',
                                        weight='bold',
                                        color=colortxt
                                    ),
                                    TextComponent(
                                        text=endDate,
                                        size='sm',
                                        color=colortxt
                                    )
                                ]
                            ),
                            BoxComponent(
                                layout='vertical',
                                spacing='none',
                                margin='md',
                                contents=[
                                    TextComponent(
                                        text=ani_1,
                                        size='sm',
                                        align='start',
                                        weight='bold',
                                        color=colortxt
                                    ),
                                    TextComponent(
                                        text=ani_12,
                                        size='sm',
                                        color=colortxt
                                    )
                                ]
                            ),
                            BoxComponent(
                                layout='vertical',
                                spacing='none',
                                margin='md',
                                contents=[
                                    TextComponent(
                                        text=ani_2,
                                        size='sm',
                                        align='start',
                                        weight='bold',
                                        color=colortxt
                                    ),
                                    TextComponent(
                                        text=ani_22,
                                        size='sm',
                                        color=colortxt
                                    )
                                ]
                            )
                        ]
                    ),
                    footer=BoxComponent(
                        layout='horizontal',
                        contents=tr_post
                    ),
                    styles=BubbleStyle(
                        header=BlockStyle(
                            background_color=colorbg
                        ),
                        body=BlockStyle(
                            background_color=colorbg
                        ),
                        footer=BlockStyle(
                            background_color=colorbg
                        )
                    )
                ),
                BubbleContainer(
                    direction='ltr',
                    header=BoxComponent(
                        layout='vertical',
                        contents=[
                            TextComponent(
                                text='SYNOPSIS',
                                align='center',
                                weight='bold',
                                color=colortxt
                            )
                        ]
                    ),
                    body=BoxComponent(
                        layout='vertical',
                        contents=[
                            TextComponent(
                                text=synopsis,
                                size='sm',
                                align='center',
                                color=colortxt,
                                wrap=True
                            )
                        ]
                    ),
                    styles=BubbleStyle(
                        header=BlockStyle(
                            background_color=colorbg
                        ),
                        body=BlockStyle(
                            background_color=colorbg
                        )
                    )
                )
            ]
        )
    )
    return msg