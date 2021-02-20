import painter
import discord
import requests
import w2g
from time import localtime

IMG_NAME = 'resources/temp.png'
client = discord.Client()


def download(url):
    r = requests.get(url)
    with open(IMG_NAME, 'wb') as outfile:
        outfile.write(r.content)


async def cleanup_messages(message, key):
    messages = await message.channel.history(limit=1000).flatten()
    for mess in messages:
        if str(mess.author.name) == str(client.user)[:-5]:
            await mess.delete()


async def send_help(message, key):
    await message.channel.send("""
        '!nuke': cleanup_messages,
        '!help': send_help,
        '!e': turn_image_to_emojis,
        'w2g': generate_w2g_room
        """)


async def turn_image_to_emojis(message, key):
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


async def generate_w2g_room(message, key):
    try:
        link = message.content[len(key)+1:]
        print(link)
        await w2g.run(link, message.channel)
    except:
        await message.channel.send('Error occured, try again')


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    options = {
        '!nuke': cleanup_messages,
        '!help': send_help,
        '!e': turn_image_to_emojis,
        'w2g': generate_w2g_room
    }

    for command in options:
        if message.content.startswith(command):
            t = localtime()
            just = lambda x: str(x).rjust(2, '0')
            print(f"[{just(t.tm_hour)}:{just(t.tm_min)}:{just(t.tm_sec)}]: {command}")
            await options[command](message, command)


if __name__ == "__main__":
    discord_id = open("discord_id.txt", "r").read()
    client.run(discord_id)
