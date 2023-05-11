import discord
import youtube_dl
import creds

from discord.ext import commands

intents = discord.Intents.all()
# Allows users to create commands by starting their command with !
bot = commands.Bot(command_prefix='!', intents=intents)

# Defines an event handler for when the bot is ready to start processing commands
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# Define the play command that takes a url as an argument
@bot.command()
async def play(ctx, url):
    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel")
        return

    # Sends the bot to the current voice channel the user is in
    channel = ctx.message.author.voice.channel
    voice_client = await channel.connect()

    # Checks to see if the client is already playing. If it is, it will stop
    if voice_client.is_playing():
        voice_client.stop()

    # Dict of options that will be passed to youtube-dl when it downloads the audio from YouTube
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio/%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }]
    }

    # Creates a youtube-dl instance which uses the opts, then downloads the audio from the specified url
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        source = await discord.FFmpegOpusAudio.from_probe(filename)

    # Plays the audio in the voice channel and outputs a message saying what it is playing
    voice_client.play(source)
    await ctx.send(f"Now playing: {info['title']}")

# Allows users to stop the bot and disconnects the bot from the voice channel
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Bot disconnected")
    else:
        await ctx.send("I am not connected to a voice channel")

bot.run(creds.token)
