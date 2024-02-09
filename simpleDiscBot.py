import random
import discord
import asyncio
import yt_dlp as youtube_dl
import time
from googleapiclient.discovery import build

intents = discord.Intents.all()

client = discord.Client(intents=intents)

key = "your discord bot key"

voice_clients = {}
APIKEY = 'your youtube API key'
youtube = build('youtube', 'v3', developerKey=APIKEY)

ydl_opts = {'format': 'bestaudio/best',
            'quiet': True,
            'simulate': True,
            'noplaylist': False,
            'skip_download': True,
            'youtube_include_dash_manifest': True,
            'extract_flat': True,
            'writeinfojson': True,
            'no_warnings': True,
            'no_color': True,
            'logtostderr': False,
            'verbose': False,
            'default_search': 'auto',
            'ignoreerrors': True,
            'youtube_api_key': APIKEY
            }

ytdl = youtube_dl.YoutubeDL(ydl_opts)
song_links = {}
song_list = {}
firstplay = {"first": False}

# ytdl = youtube_dl.YoutubeDL(yt_dl_opts)

ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                  'options': '-vn -b:a 320k -ac 2'}


# Starta o bot
@client.event
async def on_ready():
    print(f"O BOT agora está online como {client.user}")


# Quando enviam uma msg com o comando
@client.event
async def on_message(msg):
    global voice_client, pega_tempo, url, response100, song_links, firstplay

    # comando -comandos mostra as opcoes de comandos que o usuario pode enviar ao bot e o que fazem cada uma delas
    if msg.author != client.user:
        if msg.content.lower().startswith("-comandos"):
            timenow = time.strftime("%H:%M:%S")
            print(f" <<< DIÁRIO DO BOT >>> {msg.author.display_name} enviou um -comandos às {timenow}")
            await msg.channel.send(f"Fala aí, {msg.author.display_name} meu consagrado!\nOs comandos são:\nTem o "
                                   f"-play ▶ Para tocar uma música ou uma playlist.\n"
                                   f"Tem o -pause ⏸ Para pausar uma música.\nTem o -resume ⏯ Para tirar a "
                                   f"música do pause.\nTem o -skip ⏹ Para parar a música que está tocando.\nTem o "
                                   f"-repeat 🔄 Para que eu repita a música quando ela acabar.\ne tem o "
                                   f"-list 🔊 Para saber quantas músicas ainda existem na fila.\ne tem o "
                                   f"-kickbot 👋 Para que eu saia do canal.")

    if msg.content.startswith("-play") or msg.content.startswith("-p"):
        try:
            voice_client = await msg.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client
            timenow = time.strftime("%H:%M:%S")
            print(f" <<< DIÁRIO DO BOT >>> ENTREI NO CANAL À PEDIDO DE {msg.author.display_name} às {timenow}")
            # await msg.channel.send("Hat jemand nach Musik gefragt? Cheguei! 🔊")
            song_links[msg.guild.id] = []


        except Exception as err:
            print(err)

        try:
            if msg.content.find("https") > 0:
                url = msg.content.split(" ")[1]
                # await msg.author.voice.channel.connect()
                if 'youtu' in url:
                    if 'list=' in url:
                        playlist_id = url.split('list=')[-1]
                        if "&feature=" in playlist_id:
                            playlist_id = playlist_id.split("&feature=")[0]
                        elif "&t=" in playlist_id:
                            playlist_id = playlist_id.split("&t=")[0]

                        response50 = youtube.playlistItems().list(part='snippet', maxResults=50,
                                                                playlistId=playlist_id).execute()
                        next_page_token = ''
                        while next_page_token is not None:
                            print('nhe')
                            song_titles = [item['snippet']['title'] for item in response50['items']]
                            response100 = youtube.playlistItems().list(part='snippet', maxResults=50,
                                                                    playlistId=playlist_id,
                                                                    pageToken=next_page_token).execute()
                            if len(song_titles) < 50:
                                break
                            next_page_token = response100.get('nextPageToken')

                        videos = response50['items']
                        videos.extend(response100['items'])
                        metade = len(videos) // 2
                        videos = videos[:metade]
                        video_ids = [video['snippet']['resourceId']['videoId'] for video in videos]
                        video_names = [video['snippet']['title'] for video in videos]

                        print(f"Adicionadas: {len(video_names)} músicas")
                        await msg.channel.send(f"{len(video_names)} músicas adicionadas à fila, use -clear se quiser limpar a fila ou -shuffle para embaralhar 🔊")
                        n = 1
                        songs = []
                        for item in video_names[:]:
                            songs.append(f"{n} - {item}")
                            n += 1

                        song_list[msg.guild.id] = "\n".join(map(str, songs))
                        timenow = time.strftime("%H:%M:%S")
                        print(f" <<< DIÁRIO DO BOT >>> {msg.author.display_name} pediu a seguinte playlist às {timenow}")
                        print(f"{len(video_names)} músicas adicionadas à fila:\n{song_list[msg.guild.id]}")
                        # await msg.channel.send(song_list[msg.guild.id])

                        for video in video_ids:
                            # await queue.put(video)
                            song_links[msg.guild.id].append(f"{video}")
                            # print(video)

                        while len(song_links[msg.guild.id]) > 0:
                            loop = asyncio.get_event_loop()
                            data = await loop.run_in_executor(None,
                                                              lambda: ytdl.extract_info(song_links[msg.guild.id][0], download=False))
                            song = data['url']
                            player = discord.FFmpegPCMAudio(song, **ffmpeg_options,
                                                            executable="C:\\ffmpeg\\bin\\ffmpeg.exe")
                            voice_clients[msg.guild.id].play(player)
                            while voice_clients[msg.guild.id].is_playing():
                                pega_tempo = time.time()
                                await asyncio.sleep(1)
                            song_links[msg.guild.id].pop(0)
                    else:
                        song_links[msg.guild.id].append(url)
                        while len(song_links[msg.guild.id]) > 0:
                            loop = asyncio.get_event_loop()
                            data = await loop.run_in_executor(None,
                                                              lambda: ytdl.extract_info(song_links[msg.guild.id][0], download=False))
                            song = data['url']
                            timenow = time.strftime("%H:%M:%S")
                            print(f" <<< DIÁRIO DO BOT >>> {msg.author.display_name} pediu a música ({data['title']}) às {timenow}")
                            player = discord.FFmpegPCMAudio(song, **ffmpeg_options,
                                                            executable="C:\\ffmpeg\\bin\\ffmpeg.exe")
                            voice_clients[msg.guild.id].play(player)
                            while voice_clients[msg.guild.id].is_playing():
                                pega_tempo = time.time()
                                await asyncio.sleep(1)
                            song_links[msg.guild.id].pop(0)

                elif 'spotify' in url:
                    timenow = time.strftime("%H:%M:%S")
                    print(f" <<< DIÁRIO DO BOT >>> {msg.author.display_name} tentou pedir música do Spotify enviando ({msg.content}) às {timenow}")
                    await msg.channel.send("A biblioteca que o Discord usava para tocar músicas do Spotify foi "
                                           "descontinuada pelo próprio Spotify, em outras palavras, o Spotify impede que "
                                           "qualquer BOT toque músicas diretamente da plataforma, o que os BOTs "
                                           "geralmente fazem, é buscar no youtube, pelas músicas da playlist do Spotify "
                                           "que você manda ele tocar, mas infelizmente meu mestre ainda não implementou "
                                           "esse algorítimo em mim.")

                else:
                    timenow = time.strftime("%H:%M:%S")
                    print(f" <<< DIÁRIO DO BOT >>> {msg.author.display_name} tentou pedir alguma coisa enviando ({msg.content}) às {timenow}")
                    await msg.channel.send(
                        "Desculpe, mas eu só consigo tocar as músicas do YouTube e do Youtube Music.")

            else:
                item = msg.content.split(" ")[1:]
                if len(item) <= 1:
                    await msg.channel.send(
                        "Para que eu possa tocar alguma coisa, você tem que ~~deixar de ser burro~~ inserir algo válido")
                else:
                    search = f"ytsearch:{item}"
                    timenow = time.strftime("%H:%M:%S")
                    print(f" <<< DIÁRIO DO BOT >>> {msg.author.display_name} enviou: ({msg.content}) às {timenow}")
                    loop = asyncio.get_event_loop()
                    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(search, download=False))
                    url = data["entries"][0]['url']
                    print(f" <<< DIÁRIO DO BOT >>> Tocando {data['entries'][0]['title']} à pedido da pesquisa de {msg.author.display_name} às {timenow}")
                    song = f"{url}"
                    song_links[msg.guild.id].append(song)
                    await msg.channel.send(f"Fala, {msg.author.display_name}! Vê se é essa aqui: {song}")
                    while len(song_links[msg.guild.id]) > 0:
                        loop = asyncio.get_event_loop()
                        data = await loop.run_in_executor(None,
                                                          lambda: ytdl.extract_info(song_links[msg.guild.id][0], download=False))
                        song = data['url']
                        player = discord.FFmpegPCMAudio(song, **ffmpeg_options,
                                                        executable="C:\\ffmpeg\\bin\\ffmpeg.exe")
                        voice_clients[msg.guild.id].play(player)
                        while voice_clients[msg.guild.id].is_playing():
                            pega_tempo = time.time()
                            await asyncio.sleep(1)
                        song_links[msg.guild.id].pop(0)

        except Exception as err:
            if type(err) == IndexError:
                print(err)
            else:
                print(type(err))

    if msg.content.startswith("-clear"):
        timenow = time.strftime("%H:%M:%S")
        print(f" <<< DIÁRIO DO BOT >>> {msg.author.display_name} enviou um -clear às {timenow}")
        if len(song_links[msg.guild.id]) > 0:
            song_links[msg.guild.id].clear()
            voice_clients[msg.guild.id].stop()
            await msg.channel.send("Certo, limpei a fila de músicas e parei de tocar 🦾")
        else:
            await msg.channel.send("Me fala como que você quer que eu limpe a playlist, se ela está vazia... "
                                   "Cê tá bebado? ")

    if msg.content.startswith("-pause"):
        try:
            voice_clients[msg.guild.id].pause()
            await msg.channel.send("Pausei a música! 😁")
            timenow = time.strftime("%H:%M:%S")
            print(f" <<< DIÁRIO DO BOT >>> {msg.author.display_name} enviou um -pause às {timenow}")
        except Exception as err:
            print(err)

    if msg.content.startswith("-stop"):
        try:
            voice_clients[msg.guild.id].stop()
            await msg.channel.send("Agora PARE! 😉")
            timenow = time.strftime("%H:%M:%S")
            print(f" <<< DIÁRIO DO BOT >>> {msg.author.display_name} enviou um -stop às {timenow}")
        except Exception as err:
            print(err)

    if msg.content.startswith("-resume"):
        try:
            voice_clients[msg.guild.id].resume()
            timenow = time.strftime("%H:%M:%S")
            await msg.channel.send("Claro, estou aqui para isso! 😉")
            print(f" <<< DIÁRIO DO BOT >>> {msg.author.display_name} enviou um -resume às {timenow}")
        except Exception as err:
            print(err)

    if msg.content.startswith("-shuffle"):
        try:
            random.shuffle(song_links[msg.guild.id])
            await msg.channel.send("Certo, embaralhei as músicas pra você! 😉")
            timenow = time.strftime("%H:%M:%S")
            print(f" <<< DIÁRIO DO BOT >>> {msg.author.display_name} enviou um -shuffle às {timenow}")
        except Exception as err:
            print(err)

    if msg.content.startswith("-skip"):
        try:
            voice_clients[msg.guild.id].stop()
            timenow = time.strftime("%H:%M:%S")
            print(f" <<< DIÁRIO DO BOT >>> {msg.author.display_name} enviou um -skip às {timenow}")
        except Exception as err:
            print(err)

    if msg.content.startswith('-repeat'):
        try:
            for i in range(99):
                song_links[msg.guild.id].append(url)
            await msg.channel.send('Repetindo! 🔄\nQuando quiser parar, use o comando -clear\nOU ENTÃO AGUENTA AS CONSEQUÊNCIASSS....')
            timenow = time.strftime("%H:%M:%S")
            print(f" <<< DIÁRIO DO BOT >>> {msg.author.display_name} enviou um -repeat às {timenow}")
        except Exception as err:
            print(err)

    if msg.content.startswith('-list'):
        try:
            if len(song_links[msg.guild.id]) > 0:
                await msg.channel.send(f'Existem {len(song_links[msg.guild.id])} músicas na fila!')
                await msg.channel.send(f"{len(video_names)} músicas adicionadas à fila:\n{song_list[msg.guild.id]}")
                await msg.channel.send('Lembre-se que você pode embaralhá-las usando -shuffle 😉')
                timenow = time.strftime("%H:%M:%S")
                print(f" <<< DIÁRIO DO BOT >>> {msg.author.display_name} enviou um -list às {timenow}")
        except Exception as err:
            print(err)

    if msg.content.startswith('-roll20'):
        try:
            rolled20 = random.randint(1, 20)
            await msg.channel.send(f'{msg.author.display_name}, rolou {rolled20}!')
        except Exception as err:
            print(err)

    if msg.content.startswith('-roll100'):
        try:
            rolled100 = random.randint(1, 100)
            await msg.channel.send(f'{msg.author.display_name}, rolou {rolled100}!')
        except Exception as err:
            print(err)

    if msg.content.startswith("-kickbot"):
        try:

            voice_clients[msg.guild.id].stop()
            await voice_clients[msg.guild.id].disconnect()
            await msg.channel.send(
                "Quando quiser que eu volte é só chamar 😉")
            timenow = time.strftime("%H:%M:%S")
            print(f" <<< DIÁRIO DO BOT >>> {msg.author.display_name} enviou um -kickbot às {timenow}")

            """
            
            TO LEAVE A SERVER 
            
            guild_id = 000000000000000000
            guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
            if guild:
                await guild.leave()
                print(f"The bot has left the server with ID {guild_id}.")
            else:
                print(f"The bot is not a member of the server with ID {guild_id}.")
                
            """

        except Exception as err:
            print(err)


client.run(key)
