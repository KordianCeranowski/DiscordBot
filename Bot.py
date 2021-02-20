import Painter
import discord
import requests
import w2g


client = discord.Client()
IMG_NAME = 'temp.png'


def download(url):
    r = requests.get(url)
    with open(IMG_NAME, 'wb') as outfile:
        outfile.write(r.content)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


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

    download(url)
    try:
        image_parts = Painter.encode_image(IMG_NAME, shape)
        for mess in image_parts:
            await message.channel.send(mess)
    except:
        await message.channel.send('Error occured while processing image')


async def generate_w2g_room(message, key):
    try:
        link = message.content[len(key):]
        await w2g.run(link, message.channel)
    except:
        await message.channel.send('Error occured, try again')


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
            await options[command](message, command)


discord_id = open("discord_id.txt", "r").read()
client.run(discord_id)
