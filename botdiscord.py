import discord
from discord.ext import commands
import youtube_dl

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

TOKEN = 'MTE0MzI1NjgxNjY0MjQzMzExNA.Gus3GG.0cMXk21St5LATUdrc5n5rCZ3jPg0mS6g_WsylY'  # Remplacez 'YOUR_TOKEN_HERE' par votre propre token bot
BOT_PREFIX = '/'

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)
queue = []

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


@bot.command()
async def play(ctx, *, query):
    channel = ctx.author.voice.channel
    voice_channel = ctx.voice_client

    if not voice_channel:
        voice_channel = await channel.connect()

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        url = info['formats'][0]['url']
        title = info['title']

    queue.append((title, url))

    if not voice_channel.is_playing():
        await play_queue(ctx)

@bot.command()
async def pause(ctx):
    ctx.voice_client.pause()

@bot.command()
async def resume(ctx):
    ctx.voice_client.resume()

@bot.command()
async def skip(ctx):
    ctx.voice_client.stop()
    await play_queue(ctx)

async def play_queue(ctx):
    if not queue:
        return

    title, url = queue.pop(0)
    voice_channel = ctx.voice_client

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    voice_channel.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS), after=lambda e: play_queue(ctx))
    await ctx.send(f"Now playing: {title}")

bot.run(TOKEN)
