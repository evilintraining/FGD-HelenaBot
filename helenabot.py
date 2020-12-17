import discord
from discord.ext import commands
import os
import psycopg2

# Bot init
client = commands.Bot(command_prefix="!h ")
token = os.getenv("HELENABOT_TOKEN")
master_id = os.getenv("MASTER_ID")
botcolor = 0xC793C3

# DB init
database = os.getenv("DATABASE_URL")

# SQL commands
start_sql = os.getenv("START_SQL")
join_sql = os.getenv("JOIN_SQL")
#update_sql = os.getenv("UPDATE_SQL")
#leaderboard_sql = os.getenv("LEADER_SQL")

@client.event
async def on_ready():
    await client.change_presence(status = discord.Status.online, activity=discord.Game("Studying event management"))
    print("Going online")

# h! start "Xmas Lotto 2020" xmas20 solo 100

@client.command(name="start")
async def start_event(ctx, event_name, event_tag, event_type, goal):
    try:
        # Insert Event into DB

        conn = psycopg2.connect(database, sslmode='require')
        cursor = conn.cursor()
        cursor.execute(start_sql.format(ctx.message.guild.id, event_type, event_name, event_tag, goal))
        conn.commit()

    except (Exception, psycopg2.Error) as error:
        call_master(ctx, "Start event error: {0}".format(error))
    
    finally:

        # Display Creation Embed
        embed = discord.Embed(title="{0} has started!".format(event_name), 
            description = "Use '{0} join {1}' to join the event and \n'{0} update {1} [amount]' to update your score!\nFirst one to reach {2} wins!".format(client.command_prefix, event_tag, goal),
            color = botcolor
            )
        embed.set_thumbnail(url = ctx.guild.icon_url)

        await ctx.send(embed=embed)

        if (conn):
            cursor.close()
            conn.close()

# h! join xmas20 20  
@client.command()
async def join(ctx, event_tag, new_val=0):
    
    try:

        # Insert User into DB
        conn = psycopg2.connect(database, sslmode='require')
        cursor = conn.cursor()
        cursor.execute(join_sql.format(ctx.message.guild.id, ctx.message.author.id, new_val, event_tag))
        conn.commit()

    except (Exception, psycopg2.Error) as error:
        call_master(ctx, "Join event error: {0}".format(error))
    
    finally:

        # Display Creation Embed
        embed = discord.Embed(title="{0} has joined the race! Good Luck!".format(ctx.message.author.name), 
            color = botcolor
            )
        embed.set_thumbnail(url = ctx.message.author.avatar_url)
        await ctx.send(embed=embed)

        if (conn):
            cursor.close()
            conn.close()
    

# h! update xmas20 20
@client.command()
async def update(ctx, new_val):
    await ctx.send("Updating Master {0}'s count to {1}.".format(ctx.message.author.name, new_val))
    # update 
    # Check for victory conditions

# h! leaderboard
@client.command()
async def leaderboard(ctx, event_tag):
    await ctx.send("Showing leaderboard for {0}".format(event_tag))


@client.command()
async def testembed(ctx):
    embed = discord.Embed(title="{0} has started!".format("Xmas Lotto 2020"), 
            description = "Use '{0} join {1}' to join the event and \n'{0} update {1} [amount]' to update your score!\nFirst one to reach {2} wins!".format("!h", "Xmas2020", 100),
            color = botcolor
            )
    embed.set_thumbnail(url = ctx.guild.icon_url)
    await ctx.send(embed=embed)

    embed = discord.Embed(title="{0} has joined the race! Good Luck!".format(ctx.message.author.name), 
        color = botcolor
        )
    embed.set_thumbnail(url = ctx.message.author.avatar_url)
    await ctx.send(embed=embed)

@client.command()
async def ping(ctx):
    await ctx.send("Pong with {0}".format(round(client.latency,2)))

@client.command(name="whoami")
async def whoami(ctx):
    await ctx.send("You are Master {0}".format(ctx.message.author.name))

@client.command()
async def himaster(ctx):
    call_master(ctx, "Hello Master!")

# Call Evil for help if something is wrong
async def call_master(ctx, bug_message):
    master = client.get_user(int(master_id)) # get member to display nickname?
    await ctx.send("My Master is {0}. {1}".format(master.name, bug_message))
    #await master.send(bug_message)  

client.run(token)