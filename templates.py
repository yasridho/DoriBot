import requests, json
import cinema21
import calendar
import io
import re
import os
import errno
import urllib
import pyrebase
from colorthief import ColorThief
from linebot.models import *
from acc import *

def dori_id(args):
    try:
        user_id = db.child("users").child(args).get().val()["user_id"]
    except:
        user_id = args
    return user_id

def file_size(args):
    minimal = 2**10
    n = 0
    ukuran = {0:'', 1:'Kilo', 2:'Mega', 3:'Giga', 4:'Tera'}
    while args > minimal:
        args = args/minimal
        n = n + 1
    if args == 1:
        return args, ukuran[n]+'byte'
    else:
        return args, ukuran[n]+'bytes'

def gis(args,startIndex):
    search = args.split()
    url = urllib.request.urlopen('https://www.googleapis.com/customsearch/v1?q='+'+'.join(search)+'&cx=012011408610071646553%3A9m9ecisn3oe&imgColorType=color&num=9&start='+str(startIndex)+'&safe=off&searchType=image&key='+google_key)
    udict = url.read().decode('utf-8')[0]
    datagis = json.loads(udict)
    result = list()
    nextPage = datagis["queries"]["nextPage"]["startIndex"]
    for d in datagis["items"]:
        gambar = d["link"]
        if gambar[:7] == "http://":
            #gambar = shorturl(gambar)
            gambar = "https://proxy.duckduckgo.com/iu/?u="+urllib.parse.quote(gambar)+'&f=1'
            #imgur = os.popen("curl --request POST \
            #            --url https://api.imgur.com/3/image \
            #            --header 'Authorization: Client-ID 802f673008792da' \
            #            --form 'image="+gambar+"'").read()
            #ganti = json.loads(imgur)
            #gambar = ganti["data"]["link"]
        jenis = d["mime"].replace("image/","")
        tinggi = d["image"]["height"]
        lebar = d["image"]["width"]
        judul = d["title"]
        html_snippet = d["htmlSnippet"]
        link = d["image"]["contextLink"]
        display_link = d["displayLink"]
        preview_img = d["image"]["thumbnailLink"]
        size = d["byteSize"]
        size = file_size(size)
        result.append(
            BubbleContainer(
                direction='ltr',
                header=BoxComponent(
                    layout='vertical',
                    contents=[
                        TextComponent(
                            text=args,
                            align='center',
                            weight='bold',
                            color='#9AA6B4'
                        )
                    ]
                ),
                hero=ImageComponent(
                    url=gambar,
                    size='full',
                    aspect_mode='fit',
                    aspect_ratio='20:13'
                ),
                body=BoxComponent(
                    layout='vertical',
                    contents=[
                        TextComponent(
                            text=judul,
                            size='sm',
                            align='center',
                            weight='bold',
                            color='#9AA6B4',
                            wrap=True
                        ),
                        SeparatorComponent(
                            margin='xl'
                        ),
                        BoxComponent(
                            layout='horizontal',
                            spacing='none',
                            margin='md',
                            contents=[
                                TextComponent(
                                    text=str(lebar)+' x '+str(tinggi),
                                    flex=1,
                                    size='sm',
                                    align='center',
                                    color='#9AA6B4'
                                ),
                                SeparatorComponent(
                                    margin='none'
                                ),
                                TextComponent(
                                    text=jenis+' image',
                                    size='sm',
                                    align='center',
                                    color='#9AA6B4'
                                )
                            ]
                        ),
                        SeparatorComponent(
                            margin='md'
                        ),
                        BoxComponent(
                            layout='baseline',
                            margin='md',
                            contents=[
                                IconComponent(
                                    url='https://i.postimg.cc/vB4GrXT5/449px-Media-Viewer-Icon-Link-Hover-svg.png',
                                    size='xs'
                                ),
                                TextComponent(
                                    text=display_link,
                                    margin='md',
                                    size='sm',
                                    color='#9AA6B4'
                                )
                            ]
                        ),
                        BoxComponent(
                            layout='baseline',
                            margin='md',
                            contents=[
                                IconComponent(
                                    url='https://i.postimg.cc/BbJMW7FK/1024px-Folder-4-icon-72a7cf-svg.png',
                                    size='xs'
                                ),
                                TextComponent(
                                    text=size,
                                    margin='md',
                                    size='sm',
                                    color='#9AA6B4'
                                )
                            ]
                        ),
                        SeparatorComponent(
                            margin='md'
                        ),
                        TextComponent(
                            text=html_snippet,
                            margin='md',
                            size='xs',
                            color='#9AA6B4',
                            wrap=True
                        )
                    ]
                ),
                footer=BoxComponent(
                    layout='vertical',
                    contents=[
                        ButtonComponent(
                            action=URIAction(
                                label='To the source',
                                uri=link
                            ),
                            color='#9AA6B4',
                            height='sm'
                        ),
                        ButtonComponent(
                            action=PostbackAction(
                                label='Download image',
                                text='Download image',
                                data='img: '+gambar+' '+preview_img
                            ),
                            color='#9AA6B4',
                            height='sm'
                        )
                    ]
                ),
                styles=BubbleStyle(
                    header=BlockStyle(
                        background_color='#1E222C'
                    ),
                    hero=BlockStyle(
                        background_color='#262B37'
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
    if nextPage < 92:
        result.append(
            BubbleContainer(
                direction='ltr',
                hero=ImageComponent(
                    url='https://i.postimg.cc/9FzFN3Bj/next.png',
                    size='full',
                    aspect_ratio='1:1',
                    aspect_mode='cover'
                ),
                footer=BoxComponent(
                    layout='horizontal',
                    contents=[
                        ButtonComponent(
                            color='#9AA6B4',
                            action=PostbackAction(
                                label='NEXT PAGE',
                                text='next',
                                data='img_page: '+str(nextPage)+' '+args
                            )
                        )
                    ]
                ),
                styles=BubbleStyle(
                    footer=BlockStyle(
                        background_color='#262B37'
                    )
                )
            )
        )
    hasil = FlexSendMessage(
        alt_text='Search Result for: '+args,
        contents=CarouselContainer(
            contents=result
        )
    )
    return hasil

def xxi_playing(kode_bioskop):
    url = urllib.request.urlopen('https://mtix.21cineplex.com/gui.schedule.php?sid=&find_by=1&cinema_id='+kode_bioskop+'&movie_id=')
    udict = url.read().decode('utf-8').replace('\r','').replace('\n','')
    #data = re.findall('<li class="list-group-item" style="border-color: #FFFFFF; padding:0px">(.*?)</p>', udict, re.S)
    
    gambar = re.findall('<img src="(.*?)" border="0" width="125" class="img-responsive pull-left gap-left" style="margin-right:10px;"/>',udict, re.S)
    gambar = gambar[1:]
    
    judul = re.findall('<a >(.*?)</a>',udict, re.S)
    judul = judul[1:]

    tipe = re.findall('<br>                     <span class="btn btn-default btn-outline disabled" style="color: #005350;">(.*?)</span>',udict, re.S)
    tipe = tipe[1:]

    rating = re.findall('</span>                     <span class="btn btn-default btn-outline disabled" style="color: #005350;">(.*?)</span>',udict, re.S)
    rating = rating[1:]

    durasi = re.findall('<span class="glyphicon glyphicon-time"></span> (.*?)</div>',udict, re.S)
    durasi = durasi[2:]

    tanggal = re.findall('<div class="row">                            <div class="col-xs-7" style="text-align:left"><p class="p_date"><p class="p_date">(.*?)</p></div>',udict, re.S)
    bioskop = re.findall('<h4><span><strong>(.*?)</strong></span></h4>',udict, re.S)[0]

    harga = re.findall('</p></div><div class="col-xs-5" style="text-align:right"><span class="p_price">(.*?)</span></div><br><p class="p_time pull-left" style="margin: 10px">',udict, re.S)

    jamku = {}
    main = list()
    waktu = re.findall('<p class="p_time pull-left" style="margin: 10px">(.*?) </p><div class="clearfix"></div>',udict, re.S)
    num = 1
    for i in waktu:
        data = re.findall('<a class="btn btn-outline-primary div_schedule" style="border-color: #337ab7;font-size:14px; margin-left:3px; margin-top:15px" href="#" onClick="(.*?)">(.*?)</a>',i, re.S)
        data1 = re.findall('<a class="btn btn-default btn-outline disabled div_schedule" style="color: #FFFFFF; background-color: #737373;font-size:14px; margin-left:3px; margin-top:15px" >(.*?)</a>',i, re.S)
        puluh = 0
        for jam in data1:
            try:
                if (len(jamku[num]) - 7 == puluh):
                    jamku[num].append(SeparatorComponent())
                    puluh = puluh + 7
                jamku[num].append(
                    TextComponent(
                        text=jam,
                        align='center',
                        color='#A5A5A5',
                        size='xs'
                    )
                )
                jamku[num].append(SeparatorComponent())
            except:
                jamku.update({num:[]})
                jamku[num].append(SeparatorComponent())
                jamku[num].append(
                    TextComponent(
                        text=jam,
                        align='center',
                        color='#A5A5A5',
                        size='xs'
                    )
                )
                jamku[num].append(SeparatorComponent())
        for klik, jam in data:
            if tanggal[0] in klik:
                try:
                    if (len(jamku[num]) - 7 == puluh):
                        jamku[num].append(SeparatorComponent())
                        puluh = puluh + 7
                    jamku[num].append(
                        TextComponent(
                            text=jam,
                            align='center',
                            color='#9AA6B4',
                            size='xs'
                        )
                    )
                    jamku[num].append(SeparatorComponent())
                except:
                    jamku.update({num:[]})
                    jamku[num].append(SeparatorComponent())
                    jamku[num].append(
                        TextComponent(
                            text=jam,
                            align='center',
                            color='#9AA6B4',
                            size='xs'
                        )
                    )
                    jamku[num].append(SeparatorComponent())
        num = len(jamku) + 1
    num = 1
    gabungin = zip(gambar, judul, tipe, rating, durasi, tanggal, harga)
    if gabungin:
        results = list()
        for y in gabungin:
            img, title, tpe, rate, lama, tgl, rupiah = y
            clock = list()
            if len(jamku[num]) < 7:
                clock.append(
                    BoxComponent(
                        layout='horizontal',
                        margin='md',
                        contents=jamku[num]
                    )
                )
            else:
                jwaktu = len(jamku[num])
                batas = 7
                while batas < jwaktu:
                    awal = batas - 7
                    clock.append(
                        BoxComponent(
                            layout='horizontal',
                            margin='md',
                            contents=jamku[num][awal:batas]
                        )
                    )
                    batas = batas + 7
                awal = batas - 7
                if awal < jwaktu:
                    clock.append(
                        BoxComponent(
                            layout='horizontal',
                            margin='md',
                            contents=jamku[num][awal:]
                        )
                    )
            results.append(
                BubbleContainer(
                    header=BoxComponent(
                        layout='vertical',
                        contents=[
                            TextComponent(
                                text=bioskop,
                                align='center',
                                weight='bold',
                                color='#9AA6B4',
                                wrap=True
                            )
                        ]
                    ),
                    hero=ImageComponent(
                        url=img,
                        size='full',
                        aspect_ratio='3:4',
                        aspect_mode='cover'
                    ),
                    body=BoxComponent(
                        layout='vertical',
                        contents=[
                            TextComponent(
                                text=title,
                                size='xl',
                                align='center',
                                weight='bold',
                                color='#9AA6B4',
                                wrap=True
                            ),
                            SeparatorComponent(margin='md'),
                            BoxComponent(
                                layout='horizontal',
                                margin='md',
                                contents=[
                                    TextComponent(
                                        text=tpe,
                                        flex=1,
                                        align='center',
                                        gravity='center',
                                        color='#9AA6B4',
                                        weight='bold'
                                    ),
                                    SeparatorComponent(margin='md'),
                                    TextComponent(
                                        text=rate,
                                        flex=1,
                                        align='center',
                                        gravity='center',
                                        color='#9AA6B4',
                                        weight='bold'
                                    )
                                ]
                            ),
                            SeparatorComponent(margin='md'),
                            BoxComponent(
                                layout='horizontal',
                                margin='lg',
                                contents=[
                                    BoxComponent(
                                        layout='baseline',
                                        spacing='md',
                                        margin='xl',
                                        contents=[
                                            IconComponent(
                                                url='https://www.freeiconspng.com/uploads/clock-png-5.png',
                                                margin='sm',
                                                aspect_ratio='1:1'
                                            ),
                                            TextComponent(
                                                text=lama,
                                                flex=2,
                                                margin='lg',
                                                color='#9AA6B4',
                                                align='start'
                                            )
                                        ]
                                    ),
                                    BoxComponent(
                                        layout='baseline',
                                        spacing='md',
                                        margin='md',
                                        contents=[
                                            IconComponent(
                                                url='https://cdn4.iconfinder.com/data/icons/small-n-flat/24/calendar-512.png',
                                                margin='sm',
                                                aspect_ratio='1:1'
                                            ),
                                            TextComponent(
                                                text=tgl,
                                                color='#9AA6B4',
                                            )
                                        ]
                                    )
                                ]
                            ),
                            SeparatorComponent(margin='md'),
                            TextComponent(
                                text=rupiah,
                                margin='md',
                                size='lg',
                                align='center'
                            ),
                            SeparatorComponent(margin='md'),
                            BoxComponent(
                                layout='vertical',
                                margin='md',
                                contents=clock
                            )
                        ]
                    ),
                    footer=BoxComponent(
                        layout='horizontal',
                        contents=[
                            ButtonComponent(
                                PostbackAction(
                                    label='Details',
                                    data='movie: '+img.replace('https://web3.21cineplex.com/movie-images/','').replace('.jpg',''),
                                    text='Movie details'
                                ),
                                color='#9AA6B4'
                            )
                        ]
                    ),
                    styles=BubbleStyle(
                        header=BlockStyle(
                            background_color='#1E222C'
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
            num = num + 1
        hasil = FlexSendMessage(
            alt_text="Now playing at "+bioskop.capitalize(),
            contents=CarouselContainer(
                contents=results
            )    
        )
        return hasil

def nearest_theater(latitude, longitude):
    cinema = cinema21.Cinema21()
    terdekat = cinema.nearest_cinemas(latitude, longitude)
    premiere = terdekat[0]
    xxi = terdekat[1]
    imax = terdekat[2]
    res = list()
            
    if len(premiere) > 0:
        for film in premiere:
            bioskop = film[4]
            kode = film[0]
            keterangan = film[6].replace('\r','')
            res.append(
                BubbleContainer(
                    header=BoxComponent(
                        layout='vertical',
                        contents=[
                            TextComponent(
                                text=bioskop,
                                size='lg',
                                align='center',
                                weight='bold',
                                color='#9AA6B4',
                                wrap=True
                            )
                        ]
                    ),
                    hero=ImageComponent(
                        url='https://i.postimg.cc/28r8Vsnt/premiere.png',
                        size='full',
                        aspect_ratio='3:1',
                        aspect_mode='cover'
                    ),
                    body=BoxComponent(
                        layout='vertical',
                        contents=[
                            TextComponent(
                                text=keterangan,
                                margin='lg',
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
                                    text='Check theater',
                                    label='Check theater',
                                    data='theater '+kode
                                ),
                                color='#9AA6B4'
                            )
                        ]
                    ),
                    styles=BubbleStyle(
                        header=BlockStyle(
                            background_color='#1E222C'
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

    if len(xxi) > 0:
        for film in xxi:
            bioskop = film[4]
            kode = film[0]
            keterangan = film[6].replace('\r','')
            res.append(
                BubbleContainer(
                    header=BoxComponent(
                        layout='vertical',
                        contents=[
                            TextComponent(
                                text=bioskop,
                                size='lg',
                                align='center',
                                weight='bold',
                                color='#9AA6B4',
                                wrap=True
                            )
                        ]
                    ),
                    hero=ImageComponent(
                        url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTiTQHHaE05tNJ7cNhMbE6DmB0EXBHe0HnbRULKt0YpG9-uc5v5',
                        size='full',
                        aspect_ratio='3:1',
                        aspect_mode='cover'
                    ),
                    body=BoxComponent(
                        layout='vertical',
                        contents=[
                            TextComponent(
                                text=keterangan,
                                margin='lg',
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
                                    text='Check theater',
                                    label='Check theater',
                                    data='theater: '+kode
                                ),
                                color='#9AA6B4'
                            )
                        ]
                    ),
                    styles=BubbleStyle(
                        header=BlockStyle(
                            background_color='#1E222C'
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
            
    if len(imax) > 0:
        for film in imax:
            bioskop = film[4]
            kode = film[0]
            keterangan = film[6].replace('\r','')
            res.append(
                BubbleContainer(
                    header=BoxComponent(
                        layout='vertical',
                        contents=[
                            TextComponent(
                                text=bioskop,
                                size='lg',
                                align='center',
                                weight='bold',
                                color='#9AA6B4',
                                wrap=True
                            )
                        ]
                    ),
                    hero=ImageComponent(
                        url='https://i.postimg.cc/nLY3cQxg/imax.png',
                        size='full',
                        aspect_ratio='3:1',
                        aspect_mode='cover'
                    ),
                    body=BoxComponent(
                        layout='vertical',
                        contents=[
                            TextComponent(
                                text=keterangan,
                                margin='lg',
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
                                    text='Check theater',
                                    label='Check theater',
                                    data='theater: '+kode
                                ),
                                color='#9AA6B4'
                            )
                        ]
                    ),
                    styles=BubbleStyle(
                        header=BlockStyle(
                            background_color='#1E222C'
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
            
    hasil = FlexSendMessage(
        alt_text="Nearest theater from your place",
        contents=CarouselContainer(
            contents=res
        )    
    )
    
    return hasil

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
                    hero=ImageComponent(
                        url='https://i.postimg.cc/9FzFN3Bj/next.png',
                        size='full',
                        aspect_ratio='1:1',
                        aspect_mode='cover'
                    ),
                    footer=BoxComponent(
                        layout='horizontal',
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
                        footer=BlockStyle(
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