import discord
from discord.ext import commands
import os
import psycopg2

# Bot init
client = commands.Bot(command_prefix="*h ")
token = os.getenv("HELENABOT_TOKEN")
master_id = os.getenv("MASTER_ID")
botcolor = 0xC793C3

# DB init
database = os.getenv("DATABASE_URL")

# SQL commands
start_sql = os.getenv("START_SQL")
join_sql = os.getenv("JOIN_SQL")
update_sql = os.getenv("UPDATE_SQL")
event_sql = os.getenv("EVENT_SQL")
#leaderboard_sql = os.getenv("LEADER_SQL")

@client.event
async def on_ready():
    await client.change_presence(status = discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name= "over events"))

# h! start "Xmas Lotto 2020" xmas20 solo 100
@client.command(name="start")
async def start_event(ctx, event_name, event_tag, event_type, goal):
    try:

        # check for inputs

        # Insert Event into DB
        conn = psycopg2.connect(database, sslmode='require')
        cursor = conn.cursor()
        cursor.execute(start_sql.format(ctx.message.guild.id, event_type, event_name, event_tag, goal))
        conn.commit()

    except (Exception, psycopg2.Error) as error:
        await call_master("""Master, an error occurred in start!\n
            Inputs:\n\tevent_name='{0}'\n\tevent_tag='{1}'\n\tevent_type='{2}'\n\tgoal='{3}'\n
            Error:\n{4}""".format(event_name, event_tag, event_type, goal, error))
    
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

    success = False
    
    try:

        # Connect to database
        conn = psycopg2.connect(database, sslmode='require')
        cursor = conn.cursor()

        # pull all event details form the surver

        # Check if event tag exists, event is active

        # Insert User into DB
        
        cursor.execute(join_sql.format(ctx.message.guild.id, ctx.message.author.id, new_val, event_tag))
        conn.commit()

    except (Exception, psycopg2.Error) as error:
        await call_master("Master, an error occurred in join!\nInputs:\n\tevent_tag='{0}'\n\tnew_val='{1}'\nError:\n{2}".format(event_tag, new_val, error))
    
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
async def update(ctx, event_tag, new_val):

    #await ctx.send("Updating Master {0}'s count to {1}.".format(ctx.message.author.name, new_val))

    try:

        # Pull event details

        # Check if event tag exists, event is active

        # Get Event ID and Goal 
        event_id = ''
        goal = ''

        # Insert User into DB
        conn = psycopg2.connect(database, sslmode='require')
        cursor = conn.cursor()
        cursor.execute(update_sql.format(ctx.message.guild.id, ctx.message.author.id, new_val, event_tag))
        conn.commit()

        # Check for rank and victory conditions - order participants, and determine rank

    except (Exception, psycopg2.Error) as error:
        await call_master("Update event error: {0}".format(error))
    
    finally:

        # Display Creation Embed
        embed = discord.Embed(title= "You are at {0}/{1}, rank {2}! Keep going!".format(new_val, goal, ctx.message.author.name), 
            color = botcolor
            )
        embed.set_thumbnail(url = ctx.message.author.avatar_url)
        await ctx.send(embed=embed)

        if (conn):
            cursor.close()
            conn.close()

# h! leaderboard xmas2020
@client.command()
async def leaderboard(ctx, event_tag):
    try:

        # Input parsing

        # Connect to database
        conn = psycopg2.connect(database, sslmode='require')
        cursor = conn.cursor()


        # Pull event details belonging to server
        cursor.execute(event_sql.format(ctx.message.guild.id))
        rows = cursor.fetchall()

        this_event = []
        for row in rows:
            await ctx.send("id: {0}, name: {1} alias: {2} status: {3}".format(row[0], row[1], row[2], row[3]))

        #ranking = []

        # We can actually test the retrieve event thingy here first
        event_tag = ''
    
    except (Exception, psycopg2.Error) as error:
        await call_master("Leaderboard error: {0}".format(error))
    
    finally:

        # Display Ranking Embed
        await ctx.send("Showing leaderboard for {0}".format(event_tag))


@client.command()
async def testembed(ctx):
    embed = discord.Embed(title="{0} has started!".format("Xmas Lotto 2020"), 
            description = "Use '{0} join {1}' to join the event and \n'{0} update {1} [amount]' to update your score!\nFirst one to reach {2} wins!".format("!h", "xmas20", 100),
            color = botcolor
            )
    embed.set_thumbnail(url = ctx.guild.icon_url)
    await ctx.send(embed=embed)

    embed = discord.Embed(title="{0} has joined the race! Good Luck!".format(ctx.message.author.name), 
        color = botcolor
        )
    embed.set_thumbnail(url = ctx.message.author.avatar_url)
    await ctx.send(embed=embed)

    # Leaderboard Embed
    embed = discord.Embed(title="{0}".format("Xmas Lotto 2020 - Event Leaderboard"),
            description = "",
            color = botcolor
            )
    embed.set_thumbnail(url= ctx.guild.icon_url)
    embed.add_field(name="#{0} - {1}".format(1, 'Evil'), value="{0}/{1}\n{2}".format(0, 100, "formatted date")) # just loop this
    await ctx.send(embed=embed)

'''
@client.command()
async def ping(ctx):
    await ctx.send("Pong with {0}".format(round(client.latency,2)))

@client.command(name="whoami")
async def whoami(ctx):
    await ctx.send("You are Master {0}".format(ctx.message.author.name))
'''

@client.command()
async def himaster(ctx):
    master = client.get_user(int(master_id)) # get_member to display nickname?
    await ctx.send("My Master is {0}. {1}".format(master.name, "Hello Master!"))
    await call_master("Hello Master!")

# Call Evil for help if something is wrong 
async def call_master(bug_message):
    master = client.get_user(int(master_id))
    await master.send(bug_message)  

client.run(token)