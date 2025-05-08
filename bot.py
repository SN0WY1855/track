import os
import discord
from discord.ext import commands, tasks
import praw
 
intents = discord.Intents.default()
 
reddit = praw.Reddit(
    client_id=os.environ['REDDIT_CLIENT_ID'],
    client_secret=os.environ['REDDIT_CLIENT_SECRET'],
    user_agent=os.environ['REDDIT_USER_AGENT']
)
 
TOKEN = os.environ['DISCORD_TOKEN']
 
bot = commands.Bot(command_prefix='!', intents=intents)
 
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
    channel = discord.utils.get(bot.get_all_channels(), name='track')
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
