import asyncio
import datetime
import itertools
import random
import time
from functools import partial
from typing import Optional

import aiohttp
import discord
import youtube_dl
from discord.ext import commands
from discord import Embed
import discord.errors

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
lyrics_url = f"https://some-random-api.ml/lyrics?title="


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
        '''if data['_type']=='playlist':
            youtube_playist=list()
            if "entries" in data:
                for item in data["entries"]:
                    data =item
                    filename = data['url'] if stream else ytdl.prepare_filename(data)
                    youtube_playist.append(cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data))
            return youtube_playist'''

        if "entries" in data:
            data = data["entries"][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url']), data=data)


class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


class VoiceState:
    __slots__ = ('bot', 'guild', 'channel', 'cog', 'queue', 'next', 'current', 'volume', 'ctx', 'previous', 'loop')

    def __init__(self, ctx):
        self.bot = ctx.bot
        self.guild = ctx.guild
        self.channel = ctx.channel
        self.cog = ctx.cog
        self.ctx = ctx
        self.queue = SongQueue()
        self.next = asyncio.Event()
        self.previous = None
        self.loop = False

        self.volume = .5
        self.current = None

        ctx.bot.loop.create_task(self.audio_player_task())

    async def audio_player_task(self):
        while not self.bot.is_closed():
            if self.loop == False:
                self.next.clear()
                self.current = await self.queue.get()
                total_seconds = self.current.data["duration"]
                hours = (total_seconds - (total_seconds % 3600)) / 3600
                seconds_minus_hours = (total_seconds - hours * 3600)
                minutes = (seconds_minus_hours - (seconds_minus_hours % 60)) / 60
                seconds = seconds_minus_hours - minutes * 60
                embed = Embed(title="Now Playing", colour=self.guild.owner.colour,
                              timestamp=datetime.datetime.utcnow(),
                              description=f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬ {int(hours)}:{int(minutes)}:{int(seconds)}")
                embed.set_thumbnail(url=self.current.data["thumbnail"])
                fields = [("Music", f"{self.current.title}", True),
                          ("Author:", f"{self.current.data['channel']}", True),
                          ("Volume:", f"{int((self.volume * 100))}/150", True),
                          ]
                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)
                await self.channel.send(embed=embed)
                self.guild.voice_client.play(self.current,
                                             after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))

                self.previous = self.current
            elif self.loop == True:
                self.current = discord.FFmpegPCMAudio(self.current.data['url'], **ffmpeg_options)
                self.guild.voice_client.play(self.current,
                                             after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set()))
            await self.next.wait()


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx):
        try:
            player = self.voice_states[ctx.guild.id]
        except KeyError:
            player = VoiceState(ctx)
            self.voice_states[ctx.guild.id] = player
        return player

    async def cog_command_error(self, ctx, error):
        await ctx.send(f"An error accurred:{error}")

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
        player = self.get_voice_state(ctx)
        try:
            await  ctx.voice_client.disconnect()
            del self.voice_states[ctx.guild.id]
            player.queue.clear()
            await  ctx.send("Disconnected!")
        except AttributeError:
            await  ctx.send("I can't disconnect because I'm not connected to an voice channel.")

    @commands.command(name="play", help="Arif plays a music.", aliases=["sing"], pass_context=True, no_pm=True)
    async def play(self, ctx, *, url):
        if ctx.author.voice is None:
            await  ctx.send("Connect a voice channel.")
        if not ctx.voice_client:
            await ctx.invoke(self.join)
        embed = Embed(title="Added Queue", colour=ctx.guild.owner.colour,
                      timestamp=datetime.datetime.utcnow())
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        state = self.get_voice_state(ctx)
        try:
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
        except Exception as exc:
            ms = f'An error occurred while processing this request: ```py\n{type(exc).__name__}: {exc}\n```'
            await ctx.send(ms)
        else:
            embed.set_thumbnail(url=player.data["thumbnail"])
            fields = [("Music", f"{player.title}", True),
                      ("Author:", f"{player.data['channel']}", True),
                      ]
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            if ctx.voice_client.is_playing():
                await ctx.send(embed=embed, delete_after=10)
            await state.queue.put(player)

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
    async def volume(self, ctx, *, volume: float):
        try:
            player = self.get_voice_state(ctx)
            if ctx.voice_client is None:
                return await ctx.send("Not connected to a voice channel.")
            elif not ctx.voice_client.is_playing():
                return await ctx.send("There no playing music here.")
            if 0 < volume <= 150:
                if ctx.voice_client.source:
                    ctx.voice_client.source.volume = volume / 100
                    player.volume = volume / 100

                player.volume = volume / 100
                await ctx.send(f"Changed volume to {int(volume)}%")
            else:
                await ctx.send("Please enter a value between 1 and 150.")
        except TypeError:
            await ctx.send("You must enter numeric values.")

    @commands.command(name="Skip", aliases=["skip"])
    async def skip(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send(f'**`{ctx.author.name}`**: Skipped the song!')
        else:
            await ctx.send('*There is no playing music.*')

    @commands.command(name="pause", aliases=['Pause'])
    async def pause(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Paused ⏹")
        else:
            await ctx.send("There no playing music here.")

    @commands.command(name="Queue", aliases=["queue", "playlist"])
    async def queue_info(self, ctx):
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            return await ctx.send("I'm not connected a voice channel.", delete_after=15)
        player = self.get_voice_state(ctx)
        if player.queue.empty():
            await ctx.message.add_reaction("❌")
            return await ctx.send("There are currently no more queued song.")
        player_queue = list(itertools.islice(player.queue._queue, 0, 5))
        fmt = '\n'.join(f'**`{item.data["title"]}`**' for item in player_queue)
        embed = discord.Embed(title=f'Upcoming - Next {len(player_queue)}', description=fmt,
                              colour=ctx.guild.owner.colour)

        await ctx.send(embed=embed)

    @commands.command(name="shuffle", aliases=["Shuffle", "mix"])
    async def shuffle(self, ctx):
        player = self.get_voice_state(ctx)
        if player.queue.qsize() > 0:
            player.queue.shuffle()
            await ctx.message.add_reaction("✅")
        else:
            return await ctx.send('Empty queue.')

    @commands.command(name="loop")
    async def loop(self, ctx):
        if not ctx.voice_client.is_playing():
            return await ctx.send('Nothing being played at the moment.')
        player = self.get_voice_state(ctx)
        player.loop = not player.loop
        await ctx.message.add_reaction('✅')
        await ctx.send('Looping a song is now turned ' + ('on' if player.loop else 'off'))

    @commands.command(name="remove")
    async def remove_from_queue(self, ctx, index: int):
        player = self.get_voice_state(ctx)
        if len(player.queue) == 0:
            return await ctx.send('Empty queue.')
        player.queue.remove(index - 1)
        await ctx.message.add_reaction('✅')

    @commands.command(name="Repeat", aliases=["repeat"])
    async def repeat(self, ctx):
        if not ctx.voice_client.is_playing():
            await ctx.message.add_reaction("❌")
            return await ctx.send('Nothing being played at the moment.')
        player = self.get_voice_state(ctx)
        await player.queue.put(player.current)
        await ctx.message.add_reaction('✅')
        await ctx.send("This song added end of the queue.")

    @commands.command(name="loop", alises=["Loop"])
    async def loop(self, ctx):
        if not ctx.voice_client.is_playing():
            await ctx.message.add_reaction("❌")
            return await ctx.send('Nothing being played at the moment.')
        player = self.get_voice_state(ctx)
        player.loop = not player.loop
        await ctx.message.add_reaction('✅')
        await ctx.send("Autoplay is " + ('on' if player.loop else 'off'))
        await ctx.send("When you use this command again loop is of.")

    @commands.command(name="lyrics", aliases=["Lyrics"])
    async def lyrics(self, ctx, name: Optional[str]):
        player = self.get_voice_state(ctx)
        name = name or player.current.title

        async with ctx.typing():
            async with aiohttp.request("GET", lyrics_url + name, headers={}) as req:
                if not 200 <= req.status <= 299:
                    return await ctx.send(
                        "No lyric could be found.Or you could enter title of music here and try again.")
                data = await req.json()
                if len(data["lyrics"]) > 2000:
                    return await ctx.send(f"<{data['links']['genius']}>")
                embed = discord.Embed(title=data['title'], description=data['lyrics'], colour=ctx.author.colour,
                                      timestamp=datetime.datetime.utcnow())
                embed.set_thumbnail(url=data['thumbnail']['genius'])
                embed.set_author(name=data['author'])
                await ctx.send(embed=embed)

    @lyrics.error
    async def lyrics_error(self, ctx, exc):
        if isinstance(exc, AttributeError):
            await ctx.send("Bot plays nothing in this moment.")


def setup(client):
    client.add_cog(Music(client))
