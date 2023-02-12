import asyncio
import datetime
import itertools
import random
import time
from functools import partial
from typing import Optional

import aiohttp
import discord
import discord.errors
import youtube_dl
from async_timeout import timeout
from discord import Embed
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
    __slots__ = (
        'bot', 'guild', 'channel', 'cog', 'queue', 'next', 'current', 'volume', 'ctx', 'previous', 'loop', 'auto_play',
        'requester', 'song_history')

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
        self.auto_play = False
        self.volume = .5
        self.current = None
        self.requester = ctx.author
        self.song_history = SongQueue()

        ctx.bot.loop.create_task(self.audio_player_task())

    async def audio_player_task(self):
        while not self.bot.is_closed():
            self.next.clear()
            try:
                async with timeout(180):
                    self.current = await self.queue.get()
            except asyncio.TimeoutError:
                self.queue.clear()
                self.destroy(self.guild)
                await self.ctx.voice_client.disconnect()
                return
            if not self.loop:

                self.guild.voice_client.play(self.current,
                                             after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
                await self.channel.send(embed=self.create_embed(), delete_after=15)
            elif self.loop:
                self.current = discord.FFmpegPCMAudio(self.current.data['url'], **ffmpeg_options)
                self.guild.voice_client.play(self.current,
                                             after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            await self.next.wait()
            await self.song_history.put(self.current)
            self.previous = self.current
            self.current = None

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self.cog.cleanup(guild))

    def create_embed(self):
        '''Hour/Min/Sec'''

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
        embed.set_footer(text=self.requester.name, icon_url=self.requester.avatar)
        return embed


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

    @commands.hybrid_command(name="join", help="Arif connects a voice channel.", with_app_command=True)
    async def join(self, ctx):
        if ctx.author.voice is None:
            embed = Embed(title=" :x: Missing Voice Channel",
                          description="You must be connected a voice channel.",
                          colour=ctx.author.colour, timestamp=datetime.datetime.utcnow())
            await ctx.message.add_reaction("❌")
            await ctx.send(embed=embed, ephemeral=True)
        else:
            voice_channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                await  voice_channel.connect()
            else:
                await  ctx.voice_client.move_to(voice_channel)

    @join.error
    async def join_error(self, ctx, exc):
        if isinstance(exc, discord.errors.NotFound):
            embed = Embed(title=" :x: Error",
                          description=f"{exc.text}",
                          colour=ctx.author.colour, timestamp=datetime.datetime.utcnow())
            await ctx.message.add_reaction("❌")
            await ctx.send(embed=embed, ephemeral=True)

    @commands.hybrid_command("disconnect", help="Arif leaves voice channel", with_app_command=True)
    async def disconnect(self, ctx):
        player = self.get_voice_state(ctx)
        try:
            await  ctx.voice_client.disconnect()
            del self.voice_states[ctx.guild.id]
            player.queue.clear()
            await  ctx.send("Disconnected!", ephemeral=True)
        except AttributeError:
            await  ctx.send("I can't disconnect because I'm not connected to an voice channel.", ephemeral=True)

    @commands.hybrid_command(name="play", help="Arif plays a music from URL or research.", with_app_command=True)
    async def play(self, ctx, *, url):
        if not ctx.voice_client:
            await ctx.invoke(self.join)
        embed = Embed(title="Added Queue", colour=ctx.guild.owner.colour,
                      timestamp=datetime.datetime.utcnow())
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar)
        state = self.get_voice_state(ctx)
        try:
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
        except Exception as exc:
            ms = f'An error occurred while processing this request: ```py\n{type(exc).__name__}: {exc}\n'
            error_Embed = Embed(title=" :x:Error",
                                description=f"{ms}.",
                                colour=ctx.author.colour, timestamp=datetime.datetime.utcnow())
            await ctx.message.add_reaction("❌")
            await ctx.send(embed=error_Embed)
            pass
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

    @commands.hybrid_command(name="resume", help="Arif continues stopped music.", with_app_command=True)
    async def resume(self, ctx):
        try:
            if ctx.voice_client.is_paused():
                await ctx.send("In progress. ⏩", ephemeral=True)
                await ctx.voice_client.resume()
        except AttributeError:
            await  ctx.send("There is no paused music so you cant resume it.", ephemeral=True)
        except TypeError:
            pass

    @commands.hybrid_command(name="volume", help="Increase or decrease voice volume.", with_app_command=True)
    async def volume(self, ctx, *, volume: float):
        try:
            player = self.get_voice_state(ctx)
            if ctx.voice_client is None:
                return await ctx.send("Not connected to a voice channel.", ephemeral=True)
            elif not ctx.voice_client.is_playing():
                return await ctx.send("There no playing music here.", ephemeral=True)
            if 0 < volume <= 150:
                if ctx.voice_client.source:
                    ctx.voice_client.source.volume = volume / 100
                    player.volume = volume / 100

                player.volume = volume / 100
                await ctx.send(f"Changed volume to {int(volume)}%", ephemeral=True)
            else:
                await ctx.send("Please enter a value between 1 and 150.", ephemeral=True)
        except TypeError:
            await ctx.send("You must enter numeric values.", ephemeral=True)

    @commands.hybrid_command(name="skip", with_app_command=True, help="Skips the current song.")
    async def skip(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send(f'**`{ctx.author.name}`**: Skipped the song!', ephemeral=True)
        else:
            await ctx.send('*There is no playing music.*', ephemeral=True)

    @commands.hybrid_command(name="pause", with_app_command=True, help="Pauses the music.")
    async def pause(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Paused ⏹", ephemeral=True)
        else:
            await ctx.send("There no playing music here.", ephemeral=True)

    @commands.hybrid_command(name="queue", with_app_command=True)
    async def queue_info(self, ctx):
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            return await ctx.send("I'm not connected a voice channel.", delete_after=15, ephemeral=True)
        player = self.get_voice_state(ctx)
        if player.queue.empty():
            await ctx.message.add_reaction("❌")
            return await ctx.send("There are currently no more queued song.")
        player_queue = list(itertools.islice(player.queue._queue, 0, 5))
        fmt = '\n'.join(f'**`{item.data["title"]}`**' for item in player_queue)
        embed = discord.Embed(title=f'Upcoming - Next {len(player_queue)}', description=fmt,
                              colour=ctx.guild.owner.colour)

        await ctx.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(name="history", with_app_command=True, help="Show played songs history.")
    async def song_history(self, ctx):
        player = self.get_voice_state(ctx)
        if player.song_history.empty():
            await ctx.message.add_reaction("❌")
            return await ctx.send("There are currently no more played song here.", ephemeral=True)
        player_queue = list(itertools.islice(player.song_history._queue, 0, 5))
        fmt = '\n'.join(f'**`{item.data["title"]}`**' for item in player_queue)
        embed = discord.Embed(title=f'Recently Played Songs - Played {len(player_queue)}', description=fmt,
                              colour=ctx.guild.owner.colour)

        await ctx.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(name="shuffle", with_app_command=True)
    async def shuffle(self, ctx):
        player = self.get_voice_state(ctx)
        if player.queue.qsize() > 0:
            player.queue.shuffle()
            await ctx.message.add_reaction("✅")
        else:
            return await ctx.send('Empty queue.', ephemeral=True)

    @commands.hybrid_command(name="loop", with_app_command=True)
    async def loop(self, ctx):
        if not ctx.voice_client.is_playing():
            return await ctx.send('Nothing being played at the moment.')
        player = self.get_voice_state(ctx)
        player.loop = not player.loop
        await ctx.message.add_reaction('✅')
        await ctx.send('Looping a song is now turned ' + ('on' if player.loop else 'off'), ephemeral=True)

    @commands.hybrid_command(name="remove", with_app_command=True)
    async def remove_from_queue(self, ctx, index: int):
        player = self.get_voice_state(ctx)
        if len(player.queue) == 0:
            return await ctx.send('Empty queue.', ephemeral=True)
        player.queue.remove(index - 1)
        await ctx.message.add_reaction('✅')

    @commands.hybrid_command(name="repeat", with_app_command=True)
    async def repeat(self, ctx):
        if not ctx.voice_client.is_playing():
            await ctx.message.add_reaction("❌")
            return await ctx.send('Nothing being played at the moment.', ephemeral=True)
        player = self.get_voice_state(ctx)
        await player.queue.put(player.current)
        await ctx.message.add_reaction('✅')
        await ctx.send("This song added end of the queue.", ephemeral=True)

    @commands.hybrid_command(name="loop", with_app_command=True)
    async def loop(self, ctx):
        if not ctx.voice_client.is_playing():
            await ctx.message.add_reaction("❌")
            return await ctx.send('Nothing being played at the moment.')
        player = self.get_voice_state(ctx)
        player.loop = not player.loop
        await ctx.message.add_reaction('✅')
        await ctx.send("Loop is " + ('on' if player.loop else 'off'), ephemeral=True)
        await ctx.send("When you use this command again loop is of.", ephemeral=True)

    @commands.hybrid_group(name="lyrics", with_app_command=True,
                           help="Returns current lyrics,if lyrics lenght higher then 200 characters returns link.")
    async def lyrics(self, ctx, name: Optional[str]):
        player = self.get_voice_state(ctx)
        name = name or player.current.title

        async with ctx.typing():
            async with aiohttp.request("GET", lyrics_url + name, headers={}) as req:
                if not 200 <= req.status <= 299:
                    return await ctx.send(
                        "No lyrics could be found.Or you could enter title of music here and try again.")
                data = await req.json()
                if len(data["lyrics"]) > 2000:
                    return await ctx.send(f"<{data['links']['genius']}>")
                embed = discord.Embed(title=data['title'], description=data['lyrics'], colour=ctx.author.colour,
                                      timestamp=datetime.datetime.utcnow())
                embed.set_thumbnail(url=data['thumbnail']['genius'])
                embed.set_author(name=data['author'])
                await ctx.send(embed=embed, ephemeral=True)

    @lyrics.error
    async def lyrics_error(self, ctx, exc):
        if isinstance(exc, AttributeError):
            await ctx.send("Bot plays nothing in this moment.")

    @commands.hybrid_command(name="playprevious", with_app_command=True, help="Plays previous song.")
    async def play_previous(self, ctx):
        player = self.get_voice_state(ctx)
        player_queue = []
        if ctx.voice_client.is_playing() and player.previous is not None:
            player_queue.append(player.previous)
            player_queue.append(player.current)
            for item in player.queue:
                player_queue.append(item)
            player.queue.clear()
            ctx.voice_client.stop()

            for item in player_queue:
                await player.queue.put(item)
            await ctx.message.add_reaction('✅')
        else:
            await ctx.send('Nothing being played at the moment.', ephemeral=True)

    @commands.hybrid_command(name="clearqueue", with_app_command=True, help="Clears song queue.")
    async def clear_queue(self, ctx):
        player = self.get_voice_state(ctx)
        if player.queue.qsize() > 0:
            player.queue.clear()
            await ctx.message.reply("Queue successfully cleared.", ephemeral=True)
        else:
            await ctx.send("Queue is empty now", ephemeral=True)

    @commands.hybrid_command(name="nowplaying", with_app_command=True, help="Shows current song info.")
    async def now_playing(self, ctx):
        state = self.get_voice_state(ctx)

        def check(m: discord.Message):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        if ctx.voice_client is None:
            await ctx.message.add_reaction("❌")
            return await ctx.send('Nothing being played at the moment.')

        await ctx.send(embed=state.create_embed(), ephemeral=True)


async def setup(bot):
    await bot.add_cog(Music(bot))
