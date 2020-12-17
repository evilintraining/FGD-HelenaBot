import discord
from discord.ext import commands
import os
import psycopg2

# Bot init
client = commands.Bot(command_prefix="h! ")
token = os.getenv("HELENABOT_TOKEN")
botcolor = 0xC793C3

# DB init
database = os.getenv("DATABASE_URL")
conn = psycopg2.connect(database, sslmode='require')

# SQL commands
start_sql = os.getenv("START_SQL")
#join_sql = os.getenv("JOIN_SQL")
#update_sql = os.getenv("UPDATE_SQL")
#leaderboard_sql = os.getenv("LEADER_SQL")

@client.event
async def on_ready():
    await client.change_presence(status = discord.Status.online, activity=discord.Game("Studying event management"))
    print("Going online")

# h! start "Xmas Lotto 2020" xmas20 solo 100

@client.command(name="start")
async def start_event(ctx, event_name, event_tag, event_type, goal):
    await ctx.send("Starting {0} Event ({1}), {2} with goal of {3}".format(event_name, event_tag, event_type, goal))
    try:
        # Insert Event into DB
        cursor = conn.cursor()
        cursor.execute(start_sql.format(ctx.message.guild.id, event_type, event_name, event_tag, goal))
        conn.commit()
    except (Exception, psycopg2.Error) as error:
        print("Start event error: {0}".format(error))
    finally:

        # Display Creation Embed
        embed = discord.Embed(title="{0} has started!".format(event_name), 
            description = "Use '{0} join {1}' to join the event and '{0} update {1} [amount]' to update your score!".format(client.command_prefix, event_tag),
            color = botcolor,
            thumbnail= ctx.guild.icon_url
            )
        await ctx.send(embed=embed)

        if (conn):
            cursor.close()

# h! join xmas20 20  
@client.command()
async def join(ctx, event_tag, new_val=0):
    await ctx.send("Master {0} is joining {1} with {2}".format(ctx.message.author.name, event_tag, new_val))
    # Insert into DB
    # Check for victory conditions

# h! update xmas20 20
@client.command()
async def update(ctx, new_val):
    await ctx.send("Updating Master {0}'s count to {1}.".format(ctx.message.author.name, new_val))
    # update 

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