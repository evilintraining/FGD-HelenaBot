import discord
from discord.ext import commands
import os

client = commands.Bot(command_prefix=".")
token = os.getenv("HELENABOT_TOKEN")

@client.event
async def on_ready():
    await client.change_presence(status = discord.Status.idle, activity=discord.Game("Studying .help"))
    print("Going online")

@client.command()
async def ping(ctx):
    await ctx.send("Pong with {0}".format(round(client.latency,2)))

@client.command(name="whoami")
async def whoami(ctx):
    await ctx.send("You are Master {0}".format(ctx.message.aurhor.name))

client.run(token)