import discord
from discord.ext import commands
import youtube_dl
import os
import random
import re
from keep_alive import keep_alive

import birthdays
import boggle
import connect4
import hangman
import mastermind
import reverse_wordle
import semexam
import wordle

# client = discord.Client()
client = commands.Bot(command_prefix='[')
PREFIX = '['
cascade_enabled = True

# Event: when the bot is ready
@client.event
async def on_ready():
  print("Logged in as {0.user}".format(client))

# a message is received
@client.event
async def on_message(message):
  # do nothing if the message is from ourselves
  if message.author == client.user:
    return

  if "69" in message.content:
    await message.add_reaction('6️⃣')
    await message.add_reaction('9️⃣')

  if "@someone" in message.content.lower():
    await message.channel.send("@someone: " + random.choice(message.channel.members).mention)
  
  if message.content.startswith(PREFIX):
    cmd = message.content[1:]  # after the prefix
    args = cmd.split()
    trigger = args.pop(0).lower()  # remove 1st word (the triggering command) from args & store in trigger

    # if cmd.startswith("quit"):
    
    global cascade_enabled
    if trigger == "cascade":
      if len(args) > 0:
        if args[0] == "on":
          cascade_enabled = True
          await message.channel.send("Cascade enabled.")
        elif args[0] == "off":
          cascade_enabled = False
          await message.channel.send("Cascade stopped.")
      elif cascade_enabled is True:
        await message.channel.send("-cascade")

    elif re.search('b(irth)?d(ay)?s?', trigger) is not None:
      await birthdays.main(message, client, args)
    
    elif trigger == "boggle" or trigger == "b":
      await boggle.main(message, client, args)
    
    elif trigger == "connect4" or trigger == "c4":
      await connect4.main(message, client)
    
    elif trigger == "hangman" or trigger == "hm" or trigger == "h":
      await hangman.main(message, client, cmd.replace(trigger, '', 1).lstrip().lower())  # remove trigger from cmd
    
    elif trigger == "mastermind" or trigger == "mm":
      await mastermind.main(message, client, args)

    elif trigger == "reversewordle" or trigger == "reversew" or trigger == "rw":
      await reverse_wordle.main(message, client, args)
    
    elif trigger == "semexam" or trigger == "se":
      await semexam.main(message, client, args)

    elif trigger == "wordle" or trigger == "w":
      await wordle.main(message, client, args)
  
  await client.process_commands(message)


# vc stuff; incomplete
@client.command(aliases=['join', 'comeoninhere'])
async def connect(ctx):
  voice_channel = ctx.message.author.voice
  if voice_channel is not None:
    voice_channel = voice_channel.channel
    try:
      return await voice_channel.connect()  # type VoiceClient
    except discord.ClientException:
      await ctx.send("Already connected to a voice channel.")
      return discord.utils.get(client.voice_clients, guild=ctx.guild)  # returns same thing as statement in try-block
  else:
    await ctx.send("Connect to a voice channel first.")

@client.command(aliases=['p'])
async def play(ctx, url: str):
  song_exists = os.path.isfile("song.mp3")
  try:
    if song_exists:
      os.remove("song.mp3")
  except PermissionError:
    await ctx.send("Wait for the current playing music to end or use the 'stop' command")
    return
 
  voice = await connect(ctx)

  ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
      'key': 'FFmpegExtractAudio',
      'preferredcodec': 'mp3',
      'preferredquality': '192',
    }],
  }

  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])
  for file in os.listdir("./"):
    if file.endswith(".mp3"):
      os.rename(file, "song.mp3")
  voice.play(discord.FFmpegPCMAudio("song.mp3"))

@client.command(aliases=['dc', 'leave', 'fuckoff', 'gtfo', 'yeet'])
async def disconnect(ctx):
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
  if voice is not None:
    await voice.disconnect()
  else:
    await ctx.send("Not connected to a voice channel.")

@client.command()
async def pause(ctx):
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
  if voice.is_playing():
    voice.pause()
  else:
    await ctx.send("No audio currently playing.")

@client.command()
async def resume(ctx):
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
  if voice.is_paused():
    voice.resume()
  else:
    await ctx.send("The audio is not paused.")

@client.command()
async def stop(ctx):
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
  voice.stop()



keep_alive()
client.run(os.environ['TOKEN'])
