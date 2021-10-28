import discord
from discord.ext import commands
import youtube_dl



class music(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command(name="join", help="Arif odaya gelir fakat müzik çalmaz.", aliases=["katıl"])
    async def join(self, ctx):
        if ctx.author.voice is None:
            await  ctx.send("Sesli kanala geçin.")
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await  voice_channel.connect()
        else:
            await  ctx.voice_client.move_to(voice_channel)

    @commands.command("disconnect", help="Arif odadan ayrılır", aliases=["ayrıl"])
    async def disconnect(self, ctx):
        await  ctx.voice_client.disconnect()
        await  ctx.send("Odadan ayrılırdı.")

    @commands.command(name="play", help="Arif müzik çalar.", aliases=["oynat"])
    async def play(self, ctx, url):
        voice_channel = ctx.author.voice.channel
        await  voice_channel.connect()
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': '-vn'}
        YDL_OPTIONS = {'format': "bestaudio"}
        vc = ctx.voice_client
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            source = await  discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)

            vc.play(source)

    @commands.command(name="pause", help="Arif müziği durdurur.", aliases=["durdur"])
    async def pause(self, ctx):
        await  ctx.voice_client.pause()
        await  ctx.send("Durduruldu.")

    @commands.command(name="resume", help="Arif durmuş olan müziğe  devam eder.", aliases=["devam"])
    async def resume(self, ctx):
        await ctx.voice_client.resume()
        await ctx.send("Devam ediliyor.⏩")

    @commands.command(name="Help", help="Arifin Müzik Komutları", aliases=["yardım"])
    async def help(self, ctx):
        embedM = discord.Embed(title="---Arif Müzik Komutları---", color=0xfc0303)
        embedM.add_field(name="Arif.oynat", value="Arif müzik çalar")
        embedM.add_field(name="Arif.durdur", value="Arif müziği keser")
        embedM.add_field(name="Arif.ayrıl", value="Arif odadan ayrılır.")
        embedM.add_field(name="Arif.devam", value="Arif durmuş müziğe devam eder.")
        embedM.add_field(name="Arif.katıl", value="Arif odaya gelir.")
        await ctx.send(content=None, embed=embedM)


def setup(client):
    client.add_cog(music(client))
