import discord
from discord.ext import commands, tasks
import os
import asyncpraw

# Reddit API details
REDDIT_CLIENT_ID = os.environ['REDDIT_CLIENT_ID']
REDDIT_CLIENT_SECRET = os.environ['REDDIT_CLIENT_SECRET']

# ✅ directly set user agent here no env needed
REDDIT_USER_AGENT = 'track bot by /u/pin0bun'

# initialize Reddit instance (async)
reddit = asyncpraw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

# Discord bot token
TOKEN = os.environ['DISCORD_TOKEN']

# setup intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

# create bot
bot = commands.Bot(command_prefix='!', intents=intents)

SUB1 = 'IndianTeenagers'
SUB2 = 'TeenIndia'

# hardcoded server-channel map
TRACK_CHANNELS = {
    1342622803035160646: 1369963139738898503,  # server 1
    1358724438878716015: 1370007666826674227,  # server 2
}

async def get_gap_data():
    sub1 = await reddit.subreddit(SUB1)
    sub2 = await reddit.subreddit(SUB2)
    
    # Load subreddits to access their attributes
    await sub1.load()
    await sub2.load()

    sub1_count = sub1.subscribers
    sub2_count = sub2.subscribers
    gap = sub1_count - sub2_count
    est_days = round(gap / 494, 1)
    return sub1_count, sub2_count, gap, est_days

@bot.event
async def on_ready():
    print(f'{bot.user} is online!')
    await bot.change_presence(activity=discord.Game(name='Tracking Sub Growth'))
    update_gap.start()

@tasks.loop(minutes=30)
async def update_gap():
    for guild_id, channel_id in TRACK_CHANNELS.items():
        channel = bot.get_channel(channel_id)
        if channel:
            try:
                sub1_count, sub2_count, gap, est_days = await get_gap_data()
                await channel.send(
                    f'current members:\n{SUB1}: {sub1_count}\n{SUB2}: {sub2_count}\ngap: {gap}\nestimated days to catch up: {est_days}'
                )
            except Exception as e:
                print(f'update error in guild {guild_id}: {e}')
        else:
            print(f'channel not found in guild {guild_id}')

@bot.command()
async def gap(ctx):
    sub1_count, sub2_count, gap, est_days = await get_gap_data()
    await ctx.send(
        f'{SUB1}: {sub1_count}\n{SUB2}: {sub2_count}\ngap: {gap}\nestimated days to catch up: {est_days}'
    )

bot.run(TOKEN)
