import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
from datetime import datetime
from yt_dlp import YoutubeDL
# from keep_alive import keep_alive
# from openai import OpenAI

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# keep_alive()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="alfa!", intents=intents)

queues = {}
# YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
TARGET_CHANNEL_ID = 1433509065228812360
AUTHORIZED_USERS = {393106685788422145}

def create_embed(title: str, description: str, color=discord.Color.blue()):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text=f"Developer: Imuzi | {now}")
    return embed

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_member_join(member: discord.Member):
    WELCOME_CHANNEL_ID = 1439952370506272858 # 656852072133558273  # your welcome channel ID
    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    # Fallback: try system channel or first available text channel
    if channel is None:
        channel = member.guild.system_channel
        if channel is None:
            for ch in member.guild.text_channels:
                if ch.permissions_for(member.guild.me).send_messages:
                    channel = ch
                    break
    if channel is None:
        print("❌ No valid channel found for welcome message.")
        return
    description = (
        f"👋 Welcome to **{member.guild.name}**, {member.mention}!\n\n"
        "📌 **Please change your nickname** to follow the server format.\n"
        "📌 **alfa!setnickname [CLANNAME - PlayerName]** and **Example: ALFACENTAURI - Imuzi**.\n"
        "If you need help, contact a moderator."
    )
    embed = create_embed(
        title="Welcome!",
        description=description,
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    try:
        await channel.send(embed=embed)
    except discord.Forbidden:
        print("❌ Missing permissions to send welcome embed.")

@bot.command(name="commands")
async def commands_list(ctx):
    description = (
        "🎵 **Music Commands**\n"
        "`alfa!join` - Join your voice channel\n"
        "`alfa!leave` - Leave the voice channel\n"
        "`alfa!play [song]` - Play a YouTube song\n"
        "`alfa!pause` - Pause the current song\n"
        "`alfa!resume` - Resume paused song\n"
        "`alfa!stop` - Stop playing and clear queue\n"
        "`alfa!queue` - Show the current song queue\n\n"
        "👤 **User Commands**\n"
        "`alfa!ping` - Check bot latency\n"
        "`alfa!setnickname [nickname]` - Change your nickname\n"
        "ℹ **Tip:** Use commands with `alfa!` prefix."
    )
    await ctx.send(embed=create_embed("📜 Bot Commands", description))

@bot.command(name="setnickname", aliases=["nick", "nickname"])
async def setnickname(ctx, *, new_nick: str = None):
    if not new_nick:
        await ctx.send(
            embed=create_embed(
                "❌ Error",
                "```Please provide a nickname.\nExample: alfa!setnickname ALFACENTAURI - Imuzi```",
                discord.Color.red()
            )
        )
        return

    try:
        await ctx.author.edit(nick=new_nick)
        await ctx.send(
            embed=create_embed(
                "✅ Nickname Updated",
                f"```Your nickname has been changed to:\n{new_nick}```",
                discord.Color.green()
            )
        )
    except discord.Forbidden:
        await ctx.send(
            embed=create_embed(
                "❌ Permission Error",
                "```I do not have permission to change nicknames.```",
                discord.Color.red()
            )
        )
        
# @bot.command()
# @commands.cooldown(1, 15, commands.BucketType.user)
# async def ask(ctx, *, question=None):
#     if not question:
#         await ctx.send(
#             embed=create_embed(
#                 "❌ Error",
#                 "```Ask me something!\nExample: alfa!ask What is Python?```",
#                 discord.Color.red()
#             )
#         )
#         return
#     thinking = await ctx.send(
#         embed=create_embed("🤖 Thinking...", "```Let me think...```")
#     )
#     try:
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a helpful Discord assistant."},
#                 {"role": "user", "content": question}
#             ],
#             max_tokens=500
#         )
#         answer = response.choices[0].message.content
#         await thinking.edit(
#             embed=create_embed("💬 ChatGPT", answer)
#         )
#     except Exception as e:
#         await thinking.edit(
#             embed=create_embed(
#                 "❌ Error",
#                 f"```{str(e)}```",
#                 discord.Color.red()
#             )
#         )
        
@bot.command()
async def ping(ctx):
    embed = create_embed("", "```🏓 Pong!```")
    await ctx.send(embed=embed)

@bot.command()
async def message(ctx, *, content: str = None):
    # Permission check (user ID–based)
    if ctx.author.id not in AUTHORIZED_USERS:
        await ctx.send(
            embed=create_embed(
                "❌ Access Denied",
                "```You are not allowed to use this command.```",
                discord.Color.red()
            )
        )
        return

    # Content check
    if not content:
        await ctx.send(
            embed=create_embed(
                "❌ Error",
                "```Please provide a message.\nExample: alfa!message Hello admins```",
                discord.Color.red()
            )
        )
        return

    # Get target channel
    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if not channel:
        await ctx.send(
            embed=create_embed(
                "❌ Error",
                "```Target channel not found.```",
                discord.Color.red()
            )
        )
        return

    # Build message body
    description = (
        f"👤 **From:** {ctx.author.mention}\n"
        f"🆔 **User ID:** `{ctx.author.id}`\n\n"
        f"💬 **Message:**\n"
        f"```{content}```"
    )

    # Send to admin channel
    await channel.send(
        embed=create_embed(
            "📩 Message",
            description,
            discord.Color.blue()
        )
    )

    # Confirmation to sender
    await ctx.send(
        embed=create_embed(
            "✅ Message Sent",
            "```Your message has been delivered to the specific channel.```",
            discord.Color.green()
        )
    )

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(embed=create_embed("✅ Joined", f"Joined **{channel}**"))
    else:
        await ctx.send(embed=create_embed("❌ Error", "```You are not in a voice channel!```", discord.Color.red()))

# Leave
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send(embed=create_embed("👋 Left", "```Disconnected from voice channel```"))
    else:
        await ctx.send(embed=create_embed("❌ Error", "```I am not in a voice channel!```", discord.Color.red()))

# Play
@bot.command()
async def play(ctx, *, search=None):
    if not search:  # Check if user provided a song name or URL
        await ctx.send(embed=create_embed("❌ Error", "```You must provide a song name or URL to play!```", discord.Color.red()))
        return

    voice_client = ctx.voice_client
    if not voice_client:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            voice_client = await channel.connect()
        else:
            await ctx.send(embed=create_embed("❌ Error", "```You are not in a voice channel!```", discord.Color.red()))
            return

    # Search on YouTube
    YDL_OPTIONS_SEARCH = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch1',  # search and return 1 result
    }

    with YoutubeDL(YDL_OPTIONS_SEARCH) as ydl:
        info = ydl.extract_info(search, download=False)
        if 'entries' in info:
            info = info['entries'][0]  # first search result
        url2 = info['url']
        title = info.get('title', 'Unknown title')

    # Queue setup
    if ctx.guild.id not in queues:
        queues[ctx.guild.id] = []

    queues[ctx.guild.id].append((url2, title))

    if not voice_client.is_playing():
        await play_next(ctx)
    else:
        await ctx.send(embed=create_embed("➕ Added to Queue", f"```**{title}** has been added to the queue```"))


async def play_next(ctx):
    voice_client = ctx.voice_client
    queue = queues[ctx.guild.id]
    if queue:
        url, title = queue.pop(0)
        voice_client.play(FFmpegPCMAudio(url, **FFMPEG_OPTIONS), after=lambda e: bot.loop.create_task(play_next(ctx)))
        await ctx.send(embed=create_embed("🎵 Now Playing", f"```**{title}**```"))
    else:
        await ctx.send(embed=create_embed("Queue Empty", "```No more songs in the queue```", discord.Color.orange()))

# Pause
@bot.command()
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send(embed=create_embed("⏸ Paused", "```Playback paused```"))
    else:
        await ctx.send(embed=create_embed("❌ Error", "```Nothing is playing```", discord.Color.red()))

# Resume
@bot.command()
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send(embed=create_embed("▶ Resumed", "```Playback resumed```"))
    else:
        await ctx.send(embed=create_embed("❌ Error", "```Nothing is paused```", discord.Color.red()))

# Stop
@bot.command()
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        queues[ctx.guild.id] = []
        await ctx.send(embed=create_embed("⏹ Stopped", "```Playback stopped and queue cleared```"))
    else:
        await ctx.send(embed=create_embed("❌ Error", "```Nothing is playing```", discord.Color.red()))

# Queue
@bot.command()
async def queue(ctx):
    q = queues.get(ctx.guild.id, [])
    if not q:
        await ctx.send(embed=create_embed("ℹ Queue Empty", "```No songs in queue```", discord.Color.orange()))
    else:
        description = ""
        for i, song in enumerate(q):
            description += f"{i+1}. {song[1]}\n"
        await ctx.send(embed=create_embed("🎶 Queue", description))

bot.run(TOKEN)