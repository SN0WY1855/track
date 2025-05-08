import discord
from discord.ext import commands, tasks
import os
import asyncpraw
import logging

# Set up logging
logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Reddit API details
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = 'track bot by /u/pin0bun'

# Initialize Reddit instance
reddit = asyncpraw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

# Discord bot token
TOKEN = os.getenv('DISCORD_TOKEN')

# Setup intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

# Create bot
bot = commands.Bot(command_prefix='!', intents=intents)

SUB1 = 'IndianTeenagers'
SUB2 = 'TeenIndia'

# Hardcoded server-channel map
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
    logging.info(f'{bot.user} is online!')
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
                logging.error(f'update error in guild {guild_id}: {e}')
        else:
            logging.warning(f'channel not found in guild {guild_id}')

@bot.command()
async def gap(ctx):
    try:
        sub1_count, sub2_count, gap, est_days = await get_gap_data()
        await ctx.send(
            f'{SUB1}: {sub1_count}\n{SUB2}: {sub2_count}\ngap: {gap}\nestimated days to catch up: {est_days}'
        )
    except Exception as e:
        logging.error(f'Command error: {e}')
        await ctx.send("An error occurred while fetching gap data.")

bot.run(TOKEN)
