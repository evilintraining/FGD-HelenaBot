import discord
from discord.ext import commands
import os

client = commands.Bot(command_prefix="h!")
token = os.getenv("HELENABOT_TOKEN")

@client.event
async def on_ready():
    await client.change_presence(status = discord.Status.idle, activity=discord.Game("Studying .help"))
    print("Going online")

# h! start "Xmas Lotto 2020" xmas20 solo 100

@client.command(name="start")
async def start_event(ctx, event_name, event_tag, event_type, goal):
    await ctx.send("Starting {0} Event ({1}), {2} with goal of {3}".format(event_name, event_tag, event_type, goal))

# h! join
@client.command()
async def join(ctx):
    await ctx.send("Master {0} is joining the event".format(ctx.message.author.name))

# h! update 20
@client.command()
async def update(ctx, new_val):
    await ctx.send("Updating Master {0}'s count to {1}.".format(ctx.message.author.name, new_val))

# h! leaderboard
@client.command()
async def leaderboard(ctx, event_tag):
    await ctx.send("Showing leaderboard for {0}".format(event_tag))

@client.command()
async def ping(ctx):
    await ctx.send("Pong with {0}".format(round(client.latency,2)))

@client.command(name="whoami")
async def whoami(ctx):
    await ctx.send("You are Master {0}".format(ctx.message.author.name))

client.run(token)