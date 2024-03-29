import painter
import discord
import requests
from time import localtime
import opensubtitles
import asyncio
import json
import functools
import os
import nightcore


IMG_NAME = '/home/pi/repos/DiscordBot/resources/temp.png'

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

options = {}
register_option = lambda f: options.setdefault("$" + f.__name__, f)

playlist = []
gamer_mode = False
is_playing = False

async def send_yellow(channel, text):
    await channel.send(f"```fix\n{ text }```")


async def get_vc(message):
    user_voice_channel = message.author.voice.channel
    bot_voice_channel = discord.utils.get(client.voice_clients, guild=message.guild)
    if user_voice_channel != None:
        if bot_voice_channel == None:
            bot_voice_channel = await user_voice_channel.connect()
    return bot_voice_channel


@register_option
async def fucking_chipmunks(message, arguments):
    global gamer_mode
    gamer_mode = not gamer_mode
    await send_yellow(message.channel, f"Gamer mode is now {'ON' if gamer_mode else 'OFF'}")


@register_option
async def yt(message, arguments):
    global playlist
    global is_playing
    bot_voice_channel = await get_vc(message)
    playlist += [arguments[0]]
    if not is_playing: 
        await send_yellow(message.channel, "Playing now...")
        await play_next(message)
    else:
        await send_yellow(message.channel, "Added to playlist...")
        

async def play_next(message):
    global playlist
    global gamer_mode
    global is_playing
    is_playing = False

    if playlist:
        is_playing = True
        bot_voice_channel = await get_vc(message)

        # await send_yellow(message.channel, "Downloading...")
        os.system("rm -f /tmp/temp.wav")
        os.system(f"yt-dlp -x -q --audio-format wav -o /tmp/temp.wav {playlist[0]}")
        
        if gamer_mode:
            # await send_yellow(message.channel, "G4M3R M0D3 3N4BL3D, C0NV3RT1NG...")
            nc_audio = "/tmp/temp.wav" @ nightcore.Tones(3) @ nightcore.Percent(130)
            nc_audio.export("/tmp/temp.wav")

        # await send_yellow(message.channel, f"Playing {playlist[0]}")
        playlist = playlist[1:]
        bot_voice_channel.play(discord.FFmpegPCMAudio("/tmp/temp.wav"), after=lambda e: asyncio.run(play_next(message)))


@register_option
async def show_playlist(message, arguments):
    await send_yellow(message.channel, playlist)


@register_option
async def skip(message, arguments):
    bot_voice_channel = await get_vc(message)
    bot_voice_channel.stop()


@register_option
async def stop(message, arguments):
    global playlist
    playlist = []
    await skip(message, arguments)


@register_option
async def help(message, arguments):
    await send_yellow(message.channel, list(options.keys()))


@register_option
async def cleanup(message, arguments):
    messages = await message.channel.history(limit=1000).flatten()
    for mess in messages:
        if str(mess.author.name) == str(client.user)[:-5]:
            await mess.delete()


@register_option
async def turn_to_emojis(message, arguments):
    def download(url):
        r = requests.get(url)
        with open(IMG_NAME, 'wb') as outfile:
            outfile.write(r.content)

    if not message.attachments:
        await send_yellow(message.channel, 'No attachment found!')
        return
    shape = [int(x) for x in arguments]
    if len(shape) == 0:
        shape = [30]
    if len(shape) > 2:
        await send_yellow(message.channel, 'Wrong dimensions!')
        return
    url = message.attachments[0].url
    if url.endswith('.jpg') or url.endswith('.jpeg'):
        await send_yellow(message.channel, 'Please do not send .jpg or .jpeg files')
        return

    try:
        download(url)
        image_parts = painter.encode_image(IMG_NAME, shape)
        for mess in image_parts:
            await message.channel.send(mess)
    except:
        await send_yellow(message.channel, 'Error occured while processing image')


@register_option
async def get_subtitles(message, arguments):
    video_name = arguments[0]
    try:
        lyrics_link = opensubtitles.get_subtitles(video_name)
        await message.channel.send(lyrics_link)
    except:
        await send_yellow(message.channel, 'Error occured')


@register_option
async def record_alias(message, arguments):
    def download(url):
        r = requests.get(url)
        filename = url.split('/')[-1].lower()
        with open("resources/sound/" + filename, 'wb') as outfile:
            outfile.write(r.content)
        return filename

    alias, link = arguments
    with open('resources/aliases.json', 'r+') as file:
        data = json.load(file)
        filename = download(link)
        data += [{"alias": alias, "filename": filename, "link": link}]
        file.seek(0)
        json.dump(data, file, indent=4)


@register_option
async def play(message, arguments):
    user_voice_channel = message.author.voice.channel
    bot_voice_channel = discord.utils.get(client.voice_clients, guild=message.guild)
    if user_voice_channel != None:
        if bot_voice_channel == None:
            bot_voice_channel = await user_voice_channel.connect()
        with open('resources/aliases.json', 'r') as file:
            alias = arguments[0]
            data = json.load(file)
            for sound in data:
                if sound["alias"] == alias:
                    bot_voice_channel.play(discord.FFmpegPCMAudio("resources/sound/" + sound["filename"]), after=lambda e: print('done', e))
                    break


@register_option
async def show_aliases(message, arguments):
    with open('resources/aliases.json', 'r') as file:
        data = json.load(file)
        await send_yellow(message.channel, set([sound['alias'] for sound in data]))
            

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    print(message)
    print("CONTENT: " + message.content)
    for command in options:
        if message.content.startswith(command) and message.author != client.user:
            arguments = message.content[len(command)+1:].split()
            t = localtime()
            just = lambda x: str(x).rjust(2, '0')
            print(f"[{just(t.tm_hour)}:{just(t.tm_min)}:{just(t.tm_sec)}]: {command}: {arguments}")
            await options[command](message, arguments)


if __name__ == "__main__":
    discord_id = open("token.txt", "r").read()
    client.run(discord_id)
