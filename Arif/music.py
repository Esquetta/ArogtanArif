import asyncio
import datetime
import time

import discord
import youtube_dl
from discord.ext import commands
from discord import Embed
import discord.errors
from youtube_dl import DownloadError

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

    @classmethod
    async def regather_stream(cls, data, *, loop):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(data, download=False))
        return cls(discord.FFmpegPCMAudio(data['url']), data=data)


class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}
        self.queue = asyncio.Queue()
        self.next = asyncio.Event()
        self.current = None

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and after.channel is None:
            if not [m for m in before.channel.members if not m.bot]:
                voice = discord.utils.get(self.bot.voice_clients)
                channel = discord.utils.get(self.bot.get_all_channels(), guild__name=f'{voice.guild}')
                time.sleep(1)
                await voice.disconnect()
                await channel.channels[0].send("Disconnected from channel because of inactivity.")

    @commands.command(name="join", help="Arif connects a voice channel.", aliases=["connect"], pass_context=True)
    async def join(self, ctx):
        if ctx.author.voice is None:
            await  ctx.send("You must be connected a voice channel for use this command.")
        voice_channel = ctx.author.voice.channel

        if ctx.voice_client is None:
            await  voice_channel.connect()
        else:
            await  ctx.voice_client.move_to(voice_channel)

    @commands.command("disconnect", help="Arif leaves voice channel", aliases=["leave"], pass_context=True)
    async def disconnect(self, ctx):
        try:
            await  ctx.voice_client.disconnect()
            await  ctx.send("Disconnected!")
        except AttributeError:
            await  ctx.send("I can't disconnect because I'm not connected to an voice channel.")

    @commands.command(name="play", help="Arif plays a music.", aliases=["sing"], pass_context=True, no_pm=True)
    async def play(self, ctx, *, url):
        if ctx.author.voice is None:
            await  ctx.send("Connect a voice channel.")
        embed = Embed(title="Now Playing", colour=ctx.guild.owner.colour,
                      timestamp=datetime.datetime.utcnow())
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        while True:
            self.next.clear()
            try:
                if not self.queue.qsize() > 0:
                    voice_channel = ctx.author.voice.channel
                    await  voice_channel.connect()
                    embed = Embed(title="", colour=ctx.guild.owner.colour,
                                  timestamp=datetime.datetime.utcnow())
                    embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                    async with ctx.typing():
                        player = await YTDLSource.from_url(url, loop=self.bot.loop)
                        ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
                        embed.set_thumbnail(url=player.data["thumbnail"])
                        fields = [("Music", f"{player.title}", True),
                                  ("Author:", f"{player.data['channel']}", True),
                                  ]
                        for name, value, inline in fields:
                            embed.add_field(name=name, value=value, inline=inline)
                        await ctx.send(embed=embed)
                        await self.next.wait()
                else:
                    embed = Embed(title="", colour=ctx.guild.owner.colour,
                                  timestamp=datetime.datetime.utcnow())
                    embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                    async with ctx.typing():
                        self.current=await self.queue.get()
                        ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
                        embed.set_thumbnail(url=self.current.data["thumbnail"])
                        fields = [("Music", f"{self.current.title}", True),
                                  ("Author:", f"{self.current.data['channel']}", True),
                                  ]
                        for name, value, inline in fields:
                            embed.add_field(name=name, value=value, inline=inline)
                        await ctx.send(embed=embed)
                        await self.next.wait()

            except discord.ClientException:
                async with ctx.typing():
                    player = await YTDLSource.from_url(url, loop=self.bot.loop)
                    await  self.queue.put(player)
                    embed = Embed(title="Added Queue", colour=ctx.guild.owner.colour,
                                  timestamp=datetime.datetime.utcnow())
                    embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                    embed.set_thumbnail(url=player.data["thumbnail"])
                    fields = [("Music", f"{player.title}", True),
                              ("Author:", f"{player.data['channel']}", True),
                              ]
                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)
                    await ctx.send(embed=embed)
            except DownloadError:
                await ctx.send("Unsupported URL")
            except PermissionError:
                await ctx.send("I'dont have permission this voice channel.")

    @commands.command(name="pause", help="Arif stops music.", pass_context=True)
    async def pause(self, ctx):
        try:
            if ctx.voice_client is None:
                await  ctx.send("There is no music so you can't stop it.")
            elif ctx.voice_client.is_playing():
                await  ctx.send("Stopped. ▶")
                await  ctx.voice_client.pause()
            else:
                await ctx.send("I'm in your voice channel but you didn't give me music name or url.")
        except TypeError:
            pass

    @commands.command(name="resume", help="Arif continues stopped music.", aliases=["devam"], pass_context=True)
    async def resume(self, ctx):
        try:
            if ctx.voice_client.is_paused():
                await ctx.send("In progress. ⏩")
                await ctx.voice_client.resume()
        except AttributeError:
            await  ctx.send("There is no paused music so you cant resume it.")
        except TypeError:
            pass

    @commands.command(name="volume", help="Increase or decrease voice volume.", aliases=["sound"],
                      invoke_without_command=True)
    async def volume(self, ctx, volume: str):
        if volume.isdigit():
            if ctx.voice_client is None:
                return await ctx.send("Not connected to a voice channel.")
            elif ctx.voice_client is not None and not ctx.voice_client.is_playing():
                return await ctx.send("There no playing music here.")
            else:
                await ctx.send(
                    "You must enter number(not decimals) value for this, but be carefull dont fuck your ears.")
            ctx.voice_client.source.volume = int(volume) / 100
            await ctx.send(f"Changed volume to {volume}%")

    @commands.command(name="Skip", aliases=["skip"])
    async def skip(self, ctx):
        if ctx.voice_client.is_playing():
            await ctx.voice_client.stop()
            await ctx.send(f'**`{ctx.author}`**: Skipped the song!')
        else:
            await ctx.send('*There is no playing music.*')


def setup(client):
    client.add_cog(Music(client))
