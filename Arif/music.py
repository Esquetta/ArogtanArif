import asyncio
import discord
import youtube_dl
from discord import ClientException
from discord.ext import commands

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)  # Downloads  music  to our given options


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if "entries" in data:
            data = data["entries"][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="join", help="Arif connects a voice channel.", aliases=["katıl"], pass_context=True)
    async def join(self, ctx):
        if ctx.author.voice is None:
            await  ctx.send("You must be connected a voice channel for use this command.")
        voice_channel = ctx.author.voice.channel

        if ctx.voice_client is None:
            await  voice_channel.connect()
        else:
            await  ctx.voice_client.move_to(voice_channel)

    @commands.command("disconnect", help="Arif leaves voice channel", aliases=["ayrıl"], pass_context=True)
    async def disconnect(self, ctx):
        try:
            await  ctx.voice_client.disconnect()
            await  ctx.send("Disconnected!")
        except AttributeError:
            await  ctx.send("I can't disconnect because I'm not connected to an voice channel.")

    @commands.command(name="play", help="Arif plays a music.", aliases=["oynat"], pass_context=True, no_pm=True)
    async def play(self, ctx, *, url):

        if ctx.author.voice is None:
            await  ctx.send("Connect a voice channel.")
        try:
            voice_channel = ctx.author.voice.channel
            await  voice_channel.connect()

            async with ctx.typing():
                player = await YTDLSource.from_url(url, loop=self.bot.loop)
                ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

            await ctx.send(f'Now Playing: {player.title}')
        except ClientException:
            async with ctx.typing():
                player = await YTDLSource.from_url(url, loop=self.bot.loop)
                ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

            await ctx.send(f'Now Playing: {player.title}')

    @commands.command(name="pause", help="Arif stops music.", aliases=["durdur"], pass_context=True)
    async def pause(self, ctx):
        try:
            if ctx.voice_client.is_playing():
                await  ctx.send("Stopped. ▶")
                await  ctx.voice_client.pause()
        except AttributeError:
            await  ctx.send("There is no music so you can't stop it.")


    @commands.command(name="resume", help="Arif continues stopped music.", aliases=["devam"], pass_context=True)
    async def resume(self, ctx):
        try:
            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                await ctx.send("In progress. ⏩")
                await ctx.voice_client.resume()
        except AttributeError:
            await  ctx.send("There is no paused music so you cant resume it.")

    @commands.command(name="volume", help="Increase or decrease voice volume.", aliases=["Ses"],
                      invoke_without_command=True)
    async def volume(self, ctx, volume: int):
        if ctx.voice_client is None:
            await  ctx.send("No connected voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Music volume now  {volume}%")

    @commands.command(name="Skip")
    async def skip(self, ctx):
        if ctx.voice_client.is_playing():
            await  ctx.voice_client.skip()
        else:
            await ctx.send("Müzik yokki abi geçeyim.")


def setup(client):
    client.add_cog(Music(client))
