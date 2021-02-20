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


@client.event
async def on_message(message):

    if message.content == '!nuke':
        messages = await message.channel.history(limit=1000).flatten()
        for mess in messages:
            if str(mess.author.name) == str(client.user)[:-5]:
                await mess.delete()
        return

    if message.content == '!help':
        await message.channel.send("""
            1. !e and image -> Prints image as emojis in size 20 x 20
            2. !e 30 30     -> Prints image as emojis in size 30 x 30
            3. !e 30        -> Prints image as emojis with width of 30 keeping proportions
            4. Dont send me jpegs
            """)
        return

    if message.content.startswith('!e'):
        if not message.attachments:
            await message.channel.send('No attachment found!')
            return

        shape = [int(x) for x in message.content[2:].split()]
        if len(shape) == 0:
            shape = [20]
        if len(shape) > 2 or type(shape[0]) != int:
            await message.channel.send('Wrong dimensions!')
            return

        url = message.attachments[0].url
        download(url)

        try:
            messages = Painter.encode_image(IMG_NAME, shape)
        except:
            await message.channel.send('Error occured while processing image')
            if url.endswith('.jpg') or url.endswith('.jpeg'):
                await message.channel.send('jpeg my ass')
            return

        for mess in messages:
            await message.channel.send(mess)

    if message.content.startswith('w2g'):
        try:
            link = message.content[4:]
            await w2g.run(link, message.channel)
        except:
            await message.channel.send('Error occured, try again')


discord_id = open("discord_id.txt", "r").read()
client.run(discord_id)
