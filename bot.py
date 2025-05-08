import discord
from discord.ext import commands, tasks
import os
import praw

# Replace with your actual values
REDDIT_CLIENT_ID = 'your_client_id'
REDDIT_SECRET = 'your_client_secret'
REDDIT_USER_AGENT = 'track by /u/pin0bun PRAW/7.8.1 prawcore/2.4.0'

# Initialize the Reddit instance
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

# Discord Bot Token
TOKEN = os.environ['DISCORD_TOKEN']

# Define intents
intents = discord.Intents.default()

# Creating bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# Subreddit names
SUB1 = 'IndianTeenagers'
SUB2 = 'TeenIndia'

# Event triggered when bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} is online!')
    update_gap.start()  # start the loop to check every 30 mins

# Loop that runs every 30 mins
@tasks.loop(minutes=30)
async def update_gap():
    # Get the current subscriber count for both subreddits
    sub1_count = reddit.subreddit(SUB1).subscribers
    sub2_count = reddit.subreddit(SUB2).subscribers

    # Calculate the gap and estimate the days to surpass
    gap = sub1_count - sub2_count
    est_days = round(gap / 494, 1)  # avg growth rate (this number can be adjusted)

    # Send update to the "track" channel
    channel = discord.utils.get(bot.get_all_channels(), name='track')  # channel name is "track"
    if channel:
        await channel.send(
            f'current members:\n{SUB1}: {sub1_count}\n{SUB2}: {sub2_count}\ngap: {gap}\nestimated days to catch up: {est_days}'
        )

# Command to manually fetch the gap
@bot.command()
async def gap(ctx):
    sub1_count = reddit.subreddit(SUB1).subscribers
    sub2_count = reddit.subreddit(SUB2).subscribers
    gap = sub1_count - sub2_count
    est_days = round(gap / 494, 1)
    await ctx.send(
        f'{SUB1}: {sub1_count}\n{SUB2}: {sub2_count}\ngap: {gap}\nestimated days to catch up: {est_days}'
    )

# Running the bot
bot.run(TOKEN)
