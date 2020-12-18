import discord
from discord.ext import commands
import os
import psycopg2

# Bot init
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix="*h ", intents=intents, help_command=None)
token = os.getenv("HELENABOT_TOKEN")
master_id = os.getenv("MASTER_ID")
botcolor = 0xC793C3

# DB init
database = os.getenv("DATABASE_URL")

# SQL commands
start_sql = os.getenv("START_SQL")
join_sql = os.getenv("JOIN_SQL")
update_sql = os.getenv("UPDATE_SQL")
victory_sql = os.getenv("VICTORY_SQL")
event_sql = os.getenv("EVENT_SQL")
leaderboard_sql = os.getenv("LEADER_SQL")
end_sql = os.getenv("END_SQL")

@client.event
async def on_ready():
    await client.change_presence(status = discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name= "over FGD Events | " + client.command_prefix + "help"))

@client.command()
async def help(ctx):
    embed = discord.Embed(title="Helena's Guide to Event Participation",
            description = "Replace the items in [brackets] with the correct data.",
            color = botcolor
            )
    embed.set_thumbnail(url= client.user.avatar_url)
    embed.add_field(name="Joining an Event", value="{0}join [event_tag]\nex. {0}join xmas20".format(client.command_prefix))
    embed.add_field(name="Updating Your Score", value="{0}update [event_tag] [amount]\nex. {0}update xmas20 10".format(client.command_prefix))
    embed.add_field(name="Viewing the Leaderboard", value="{0}leaderboard [event_tag]\nex. {0}leaderboard xmas20".format(client.command_prefix))
    
    await ctx.send(embed=embed)

# *h start "Xmas Lotto 2020" xmas20 solo 100
@client.command(name="start")
@commands.has_permissions(administrator=True)
async def start_event(ctx, event_name, event_tag, event_type, goal):
    
    event_success = False

    try:

        # Insert Event into DB
        conn = psycopg2.connect(database, sslmode='require')
        cursor = conn.cursor()
        cursor.execute(start_sql.format(ctx.message.guild.id, event_type, event_name, event_tag, goal))
        conn.commit()
        event_success = True

        # TODO: More security - no 2 events can have the same event tag on the server, etc

    except (Exception, psycopg2.Error) as error:
        
        await call_master("""Master, an error occurred in start!\n
            Inputs:\n\tevent_name='{0}'\n\tevent_tag='{1}'\n\tevent_type='{2}'\n\tgoal='{3}'\n
            Error:\n{4}""".format(event_name, event_tag, event_type, goal, error))
    
    finally:

        # Try to delete the message that caused the command
        await ctx.message.delete()

        if event_success:

            # Display Creation Embed
            embed = discord.Embed(title="{0} has started!".format(event_name), 
                description = "Use '\{0}join {1}' to join the event and \n'\{0}update {1} [amount]' to update your score!\nFirst one to reach {2} wins!".format(client.command_prefix, event_tag, goal),
                color = botcolor
                )
            embed.set_thumbnail(url = ctx.guild.icon_url)
            await ctx.send(embed=embed)

        if (conn):
            cursor.close()
            conn.close()

# *h join xmas20 20  
@client.command()
async def join(ctx, event_tag, new_val=0):
    
    try:

        # Connect to database
        conn = psycopg2.connect(database, sslmode='require')
        cursor = conn.cursor()

        # Pull event details belonging to server
        cursor.execute(event_sql.format(ctx.message.guild.id))
        rows = cursor.fetchall()

        event_id = ''
        event_name = ''
        event_status = ''
        event_goal = ''
        for row in rows:
            if (row[2] == event_tag):
                event_id = row[0]
                event_name = row[1]
                event_status = row[3]
                event_goal = row[4]

        # Missing Event - incorrect tag
        if event_status is '': 
            embed = discord.Embed(title="404 - Event Tag not Found!",
                description = "Please check the event tag.",
                color = botcolor
            )
            await ctx.send(embed=embed)
            if (conn):
                cursor.close()
                conn.close()
            return

        # Completed Event - can't update
        if event_status is 'ended':
            embed = discord.Embed(title="Event has finished",
                description = "Thank you for participating!",
                color = botcolor
            )
            await ctx.send(embed=embed)
            if (conn):
                cursor.close()
                conn.close()
            return

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
    
# *h update xmas20 20
@client.command()
async def update(ctx, event_tag, new_val):

    try:

        # Connect to database
        conn = psycopg2.connect(database, sslmode='require')
        cursor = conn.cursor()

        # Pull event details belonging to server
        cursor.execute(event_sql.format(ctx.message.guild.id))
        rows = cursor.fetchall()

        event_id = ''
        event_name = ''
        event_status = ''
        event_goal = ''
        for row in rows:
            if (row[2] == event_tag):
                event_id = row[0]
                event_name = row[1]
                event_status = row[3]
                event_goal = row[4]

        # Missing Event - incorrect tag
        if event_status is '': 
            embed = discord.Embed(title="404 - Event Tag not Found!",
                description = "Please check the event tag.",
                color = botcolor
            )
            await ctx.send(embed=embed)
            if (conn):
                cursor.close()
                conn.close()
            return

        # Completed Event - can't update
        if event_status is 'ended':
            embed = discord.Embed(title="Event has finished",
                description = "Thank you for participating!",
                color = botcolor
            )
            await ctx.send(embed=embed)
            if (conn):
                cursor.close()
                conn.close()
            return

        # Update User
        cursor.execute(update_sql.format(new_val, event_id, ctx.message.author.id))
        conn.commit()

        # Check for victory conditions by pulling from leaderboard
        cursor.execute(leaderboard_sql.format(event_id))
        rows = cursor.fetchall()

        goal_complete_now = False
        goal_completed = False
        
        for row in rows:
            if (str(ctx.message.author.id) == str(row[0])) and (row[3] is None) and (int(new_val) >= event_goal):
                goal_complete_now = True 
            elif (str(ctx.message.author.id) == str(row[0])) and (row[3] is not None):
                goal_completed = True

        #await ctx.send("Goal Now: {0}, Goal Completed: {1}".format(goal_complete_now, goal_completed))

        if goal_complete_now:

            # Set Completion date in DB
            cursor.execute(victory_sql.format(event_id, ctx.message.author.id))
            conn.commit()
        
            # Display victory embed
            embed = discord.Embed(title= event_name,
                description = "You've reached the goal!\n**Congratulations!**", 
                color = botcolor
                )
            embed.set_thumbnail(url = ctx.message.author.avatar_url)
            await ctx.send(embed=embed)

        elif goal_completed:
            # Keep Farming Embed 
            embed = discord.Embed(title= event_name, 
                description = "You are at {0}/{1}, over the goal!\n*Let's see how far you've come,\nLet's see how far you'll go~*".format(new_val, event_goal), 
                color = botcolor
                )
            embed.set_thumbnail(url = ctx.message.author.avatar_url)
            await ctx.send(embed=embed)
        else:
            # Display normal embed - TODO: add more encouraging messages and display them at random 
            embed = discord.Embed(title= event_name,
                description = "You are at {0}/{1}!\nKeep going!".format(new_val, event_goal), 
                color = botcolor
                )
            embed.set_thumbnail(url = ctx.message.author.avatar_url)
            await ctx.send(embed=embed)

    except (Exception, psycopg2.Error) as error:
        await call_master("Master, an error occurred in update!\nInputs:\n\tevent_tag='{0}'\n\tnew_val='{1}'\nError:\n{2}".format(event_tag, new_val, error))
    
    finally:

        if (conn):
            cursor.close()
            conn.close()

# *h leaderboard xmas20
@client.command()
async def leaderboard(ctx, event_tag):
    try:

        # Input parsing - not triggering, TODO: low priority fix
        if event_tag == '':
            embed = discord.Embed(title="Incomplete command!",
                description = "Please enter an event tag.",
                color = botcolor
            )
            await ctx.send(embed=embed)
            return

        # Connect to database
        conn = psycopg2.connect(database, sslmode='require')
        cursor = conn.cursor()

        # Pull event details belonging to server
        cursor.execute(event_sql.format(ctx.message.guild.id))
        rows = cursor.fetchall()

        event_id = ''
        event_name = ''
        event_status = ''
        event_goal = ''
        for row in rows:
            if (row[2] == event_tag):
                event_id = row[0]
                event_name = row[1]
                event_status = row[3]
                event_goal = row[4]

        # Missing Event - incorrect tag 
        if event_status is '': 
            embed = discord.Embed(title="404 - Event Tag not Found!",
                description = "Please check the event tag.",
                color = botcolor
            )
            await ctx.send(embed=embed)
            if (conn):
                cursor.close()
                conn.close()
            return
        
        # Print out the Leaderboard
        cursor.execute(leaderboard_sql.format(event_id))
        rows = cursor.fetchall()

        # Build the Embed
        embed = discord.Embed(title="{0} - Event Leaderboard".format(event_name),
            description = "",
            color = botcolor
            )
        embed.set_thumbnail(url= ctx.guild.icon_url)

        ranking = 0
        prev_amount = -1
        increment = 1

        # Loop through results and build the embed
        for row in rows:

            member_name = str(ctx.guild.get_member(int(row[0])))
            member_nickname = ctx.guild.get_member(int(row[0])).nick
            member_amount = row[1]
            member_update = row[2]
            member_complete = row[3]
            member_ranking = 0

            # Calculate Rank
            if prev_amount != member_amount:
                member_ranking = ranking + increment
                ranking = ranking + increment
                increment = 1
            else:
                member_ranking = ranking
                increment += 1
            
            prev_amount = member_amount
            
            # Handle Date
            datestring = "Date updated: " + member_update.strftime("%m/%d/%Y, %H:%M:%S")
            if member_complete is not None:
                datestring += "\nDate completed: " + member_complete.strftime("%m/%d/%Y, %H:%M:%S")

            # Handle Name
            namestring = member_name
            if member_nickname is not None:
                namestring += " (" + member_nickname + ")"

            # Build Individual Ranking Row
            embed.add_field(name="#{0} - {1}".format(member_ranking, namestring), 
                value="{0}/{1}\n{2}".format(member_amount, event_goal, datestring))
        
        await ctx.send(embed=embed)
    
    except (Exception, psycopg2.Error) as error:
        await call_master("Master, an error occurred in leaderboard!\nInputs:\n\tevent_tag='{0}'\nError:\n{1}".format(event_tag, error))

    finally:

        if (conn):
            cursor.close()
            conn.close()

# *h end xmas20
@client.command(name="end")
@commands.has_permissions(administrator=True)
async def end_event(ctx, event_tag):
    try:

        # Connect to database
        conn = psycopg2.connect(database, sslmode='require')
        cursor = conn.cursor()

        # Pull event details belonging to server
        cursor.execute(event_sql.format(ctx.message.guild.id))
        rows = cursor.fetchall()

        event_id = ''
        event_name = ''
        event_status = ''
        event_goal = ''
        for row in rows:
            if (row[2] == event_tag):
                event_id = row[0]
                event_name = row[1]
                event_status = row[3]
                event_goal = row[4]

        # Missing Event - incorrect tag
        if event_status is '': 
            embed = discord.Embed(title="404 - Event Tag not Found!",
                description = "Please check the event tag.",
                color = botcolor
            )
            await ctx.send(embed=embed)
            if (conn):
                cursor.close()
                conn.close()
            return

        # Completed Event - can't update
        if event_status is 'ended':
            embed = discord.Embed(title="Event has already ended",
                description = "Overkill!",
                color = botcolor
            )
            await ctx.send(embed=embed)
            if (conn):
                cursor.close()
                conn.close()
            return

        # Update Event Status to ended
        cursor.execute(end_sql.format(event_id))
        conn.commit()

        # Try to delete the message that caused the command
        await ctx.message.delete()

        # Event Ended Embed
        embed = discord.Embed(title="{0} has ended!".format(event_name), 
            description = "Good job to all participants!\n Use {0}leaderboard {1} to see the final tally!".format(client.command_prefix, event_tag),
            color = botcolor
            )
        embed.set_thumbnail(url = ctx.guild.icon_url)
        await ctx.send(embed=embed)

    except (Exception, psycopg2.Error) as error:
        await call_master("Master, an error occurred in update!\nInputs:\n\tevent_tag='{0}'\n\tnew_val='{1}'\nError:\n{2}".format(event_tag, new_val, error))
    
    finally:

        if (conn):
            cursor.close()
            conn.close()
   

'''
# Troubleshooting Kit
@client.command()
async def testembed(ctx):

    # Leaderboard Embed
    embed = discord.Embed(title="{0}".format("Xmas Lotto 2020 - Event Leaderboard"),
            description = "",
            color = botcolor
            )
    embed.set_thumbnail(url= ctx.guild.icon_url)
    embed.add_field(name="#{0} - {1}".format(1, 'Evil'), value="{0}/{1}\n{2}".format(0, 100, "formatted date")) # just loop this
    
    await ctx.send(embed=embed)

@client.command()
async def himaster(ctx):
    master = client.get_user(int(master_id)) # get_member to display nickname?
    await ctx.send("My Master is {0}.".format(master.name))
    await ctx.send("The current server is {0}.".format(ctx.guild))
    await ctx.send("Master's Server Nickname is {0}.".format(ctx.guild.get_member(int(master_id)).nick))

    await call_master("Hello Master!")

@client.command()
async def himember(ctx, member_id):
    member = client.get_user(int(member_id))
    await ctx.send("This member is {0}.".format(member))
    member_nick = ctx.guild.get_member(int(member_id)).nick
    await ctx.send("Also known as {0} on this server".format(member_nick))
'''
# Call Evil for help if something is wrong 
async def call_master(bug_message):
    master = client.get_user(int(master_id))
    await master.send(bug_message)  

client.run(token)