import painter
import discord
import requests
from time import localtime
import opensubtitles
import asyncio

IMG_NAME = '/home/pi/repos/DiscordBot/resources/temp.png'
client = discord.Client()


async def send_help(message, key):
    await message.channel.send(
        "```yml\n" + 
        "\n".join([
            "$help: send_help",
            "$e: turn_image_to_emojis",
            "$subs: get_subtitles",
            "$nuke: cleanup_messages",
            "$play: join voice and play sound"
        ])
        + "```"
    )


async def cleanup_messages(message, key):
    messages = await message.channel.history(limit=1000).flatten()
    for mess in messages:
        if str(mess.author.name) == str(client.user)[:-5]:
            await mess.delete()


async def turn_image_to_emojis(message, key):
    def download(url):
        r = requests.get(url)
        with open(IMG_NAME, 'wb') as outfile:
            outfile.write(r.content)

    if not message.attachments:
        await message.channel.send('No attachment found!')
        return
    shape = [int(x) for x in message.content[len(key):].split()]
    if len(shape) == 0:
        shape = [30]
    if len(shape) > 2:
        await message.channel.send('Wrong dimensions!')
        return
    url = message.attachments[0].url
    if url.endswith('.jpg') or url.endswith('.jpeg'):
        await message.channel.send('Please do not send .jpg or .jpeg files')
        return

    try:
        download(url)
        image_parts = painter.encode_image(IMG_NAME, shape)
        for mess in image_parts:
            await message.channel.send(mess)
    except:
        await message.channel.send('Error occured while processing image')


async def get_subtitles(message, key):
    video_name = message.content[len(key)+1:]
    try:
        lyrics_link = opensubtitles.get_subtitles(video_name)
        await message.channel.send(lyrics_link)
    except:
        await message.channel.send('Error occured')

async def play(message, key):
    user_voice_channel = message.author.voice.channel
    bot_voice_channel = discord.utils.get(client.voice_clients, guild=message.guild)
    if user_voice_channel != None:
        if bot_voice_channel == None:
            bot_voice_channel = await user_voice_channel.connect()
        bot_voice_channel.play(discord.FFmpegPCMAudio('sound.mp3'), after=lambda e: print('done', e))


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    options = {
        '$nuke': cleanup_messages,
        '$help': send_help,
        '$e': turn_image_to_emojis,
        '$subs': get_subtitles,
        '$play': play
    }

    for command in options:
        if message.content.startswith(command) and message.author != client.user:
            t = localtime()
            just = lambda x: str(x).rjust(2, '0')
            print(f"[{just(t.tm_hour)}:{just(t.tm_min)}:{just(t.tm_sec)}]: {command}")
            await options[command](message, command)


if __name__ == "__main__":
    discord_id = open("token.txt", "r").read()
    client.run(discord_id)
