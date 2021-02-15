import Painter
import discord
import requests
from random import random
import time
from discord import ChannelType
import copy

client = discord.Client()
IMG_NAME = 'temp.png'


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.content.startswith('!xd'):
        await message.channel.send('Dość!')
        # number = message.content.split(' ')[-1]
        # number = int(number) if number.isnumeric() else 5

        # mention = message.mentions[0]
        # voice_channels = [c for c in message.channel.guild.voice_channels]
        # origin_channel = [c for c in voice_channels if c.id == mention.voice.channel.id][0]
        # # origin_channel = next(filter(lambda c: c.id == mention.voice.channel.id, voice_channels))
        # if not mention.voice or not mention.voice.channel:
        #     await message.channel.send(f"{str(mention)} is not connected to a voice channel")
        #     return
        # start_time = time.time()
        # await mention.move_to(voice_channels[-2])
        # while time.time() - start_time < number:
        #     for i in range(1, 3):
        #         time.sleep(0.5)
        #         if mention.voice.channel is origin_channel:
        #             break
        #         await mention.move_to(voice_channels[-i])
        # await mention.move_to(origin_channel)
        return

    if message.content == '!nuke':
        messages = await message.channel.history(limit=1000).flatten()
        for mess in messages:
            if str(mess.author.name) == str(client.user)[:-5]:
                await mess.delete()
        return

    if message.content == '!jp2':
        await message.channel.send("""
            1. !e and image -> Prints image as emojis in size 20 x 20
            2. !e 30 30     -> Prints image as emojis in size 30 x 30
            3. !e 30        -> Prints image as emojis with width of 30 keeping proportions
            4. dont send me jpegs
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

        messages = Painter.encode_image(IMG_NAME, shape)
        try:
            messages = Painter.encode_image(IMG_NAME, shape)
        except:
            await message.channel.send('Error occured while processing image')
            if url.endswith('.jpg') or url.endswith('.jpeg'):
                await message.channel.send('jpeg my ass')
            return

        for mess in messages:
            await message.channel.send(mess)


def download(url):
    r = requests.get(url)
    with open(IMG_NAME, 'wb') as outfile:
        outfile.write(r.content)


discord_id = open("discord_id.txt", "r").read()
client.run(discord_id)
