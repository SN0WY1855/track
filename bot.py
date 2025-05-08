import discord
from discord.ext import commands, tasks
import os
import praw

TOKEN = os.environ['DISCORD_TOKEN']
REDDIT_CLIENT_ID = os.environ['REDDIT_CLIENT_ID']
REDDIT_CLIENT_SECRET = os.environ['REDDIT_CLIENT_SECRET']
REDDIT_USER_AGENT = os.environ['REDDIT_USER_AGENT']

bot = commands.Bot(command_prefix='!')

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

SUB1 = 'IndianTeenagers'
SUB2 = 'TeenIndia'

@bot.event
async def on_ready():
    print(f'{bot.user} is online!')
    update_gap.start()

@tasks.loop(minutes=30)
async def update_gap():
    sub1_count = reddit.subreddit(SUB1).subscribers
    sub2_count = reddit.subreddit(SUB2).subscribers
    gap = sub1_count - sub2_count
    est_days = round(gap / 494, 1)
    channel = discord.utils.get(bot.get_all_channels(), name='your-channel-name')
    if channel:
        await channel.send(
            f'current members:\n{SUB1}: {sub1_count}\n{SUB2}: {sub2_count}\ngap: {gap}\nestimated days to catch up: {est_days}'
        )

@bot.command()
async def gap(ctx):
    sub1_count = reddit.subreddit(SUB1).subscribers
    sub2_count = reddit.subreddit(SUB2).subscribers
    gap = sub1_count - sub2_count
    est_days = round(gap / 494, 1)
    await ctx.send(
        f'{SUB1}: {sub1_count}\n{SUB2}: {sub2_count}\ngap: {gap}\nestimated days to catch up: {est_days}'
    )

bot.run(TOKEN)
