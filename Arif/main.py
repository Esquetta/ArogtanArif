import asyncio
import time
from discord.ext import commands
import discord




messages = joined = 0
maut = ""
message_content = ""


@client.event
async def on_member_join(member):
    global joined
    joined += 1
    for channel in member.guild.channels:
        if str(channel) == "Genel":
            await  channel.send_message(f"Sunucuya hoşgeldiniz {member.mention}")


@client.event
async def on_message(message):
    sv_id = client.get_guild(838090601009381387)
    sv_fbi = client.get_guild(276764068877041664)
    bad_words = ["Ananı", "Avradını", "Bacını", "Sikim", "Sokim"]
    global messages
    global maut
    global message_content
    maut = message.author
    message_content = message.content
    messages += 1
    channels = ["commands", "general", "genel"]
    # music_options = ["*****Müzik Komutları****", "Arif.Oynat", "Arif.Dur", "Arif.Çık", "Arif.Devam", "Arif.Katıl"]
    for i in bad_words:
        if message.content == str(i).capitalize():
            await  message.channel.purge(limit=1)
            time.sleep(2)
            await  message.channel.send(f"Topla lan ağzını it! {message.author}")
            break

    if message.author == client.user:
        return
    if message.content == str((client.command_prefix) + "Help"):
        embed = discord.Embed(title="Arif Komutları", description="Arif becerebildiği bazı şeyler")
        embed.add_field(name="Arif.Users", value="Sunucudaki kullanıcı Sayısını verir.")
        await message.channel.send(content=None, embed=embed)
    if message.content == str((client.command_prefix) + "Müzik"):
        embedM = discord.Embed(title="---Arif Müzik Komutları---", description="Beta'da")
        embedM.add_field(name="Arif.Oynat", value="Arif müzik çalar")
        embedM.add_field(name="Arif.Dur", value="Arif müziği keser")
        embedM.add_field(name="Arif.Çık", value="Arif odadan ayrılır.")
        embedM.add_field(name="Arif.Devam", value="Arif durmuş müziğe devam eder.")
        embedM.add_field(name="Arif.Katıl", value="Arif odaya gelir.")
        await message.channel.send(content=None, embed=embedM)

    if str(message.channel) == "resim-only" and message.content != "":
        await  message.channel.purge(limit=1)

    if str(message.channel) in channels:
        if message.content == str(client.command_prefix) + "Users":
            await  message.channel.send(f" Members count {sv_id.member_count}")

    print(message.content)


async def update_stats():
    await client.wait_until_ready()
    global messages, joined, maut, message_content

    while not client.is_closed():
        try:
            with open("stats.txt", "a") as f:
                f.write(
                    f"Time:int{int(time.time())} Messages: {messages} Members Joined: {joined} Message Author: {maut}   Message Content: {message_content} \n")
                messages = 0
                joined = 0

                await asyncio.sleep(5)
        except Exception as ex:
            print(ex)
            await asyncio.sleep(5)


@client.event
async def on_member_update(before, after):
    n = after.nick
    if n:
        if n.lower().count("Esqueta") > 0:
            last = before.nick
            if last:
                await  after.edit(nick=last)
            else:
                await after.edit(nick="Dur lan!")


@client.command(pass_context=True)
async def chnick(ctx, member: discord.Member, nick):
    await member.edit(nick=nick)
    await ctx.send(f'Kullanıcı adı değişirildi {member.mention} ')


def read_token():
    with open("token.txt", "r") as f:
        lines = f.readlines()
        return lines[0].strip()


@client.event
async def on_ready():
    print(f"Bot Online {client.user}")


client.loop.create_task(update_stats())
Token = read_token()
client.run(Token)
