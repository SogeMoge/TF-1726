import os
import subprocess
from dotenv import load_dotenv

import sqlite3
from sqlite3 import Error

import discord
from discord.ext import commands
from discord.utils import get
from discord.commands import Option
from discord.commands import permissions

bot = discord.Bot()
load_dotenv()
token = os.environ.get("DISCORD_TOKEN")

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def drop_table(conn, drop_table_sql):
    """ drop a table from the drop_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a DROP TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(drop_table_sql)
    except Error as e:
        print(e)

def insert_sql(conn, sql_querry):
    """ execute querry from sql_querry statement
    :param conn: Connection object
    :param sql_querry: a SQL statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(sql_querry)
    except Error as e:
        print(e)

def insert_regular_win(conn, game_result):
    """
    Submit a new game in the games table
    :param conn:
    :param win_result:
    :return: game id
    """
    sql = ''' INSERT INTO games (winner_id,winner_score,winner_rating_diff,looser_id,looser_score,looser_rating_diff,game_date)
              VALUES(?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, game_result)
    conn.commit()
    return cur.lastrowid

def update_member(conn, rating):
    """
    update member's rating and streak
    :param conn:
    :param rating:
    :return: project id
    """
    sql = ''' UPDATE members
              SET rating = ?
              WHERE member_id = ?'''
    cur = conn.cursor()
    cur.execute(sql, rating)
    conn.commit()

def select_rating_sql(conn, member_id):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :param member_id:
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT rating FROM members WHERE member_id=?", (member_id,))

    return cur.fetchone()[0]

def select_k_regular(conn):
    """
    Query date
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT int_value FROM properties WHERE property_name = 'k_regular'")

    return cur.fetchone()[0]

def select_k_tournament(conn):
    """
    Query date
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT int_value FROM properties WHERE property_name = 'k_tournament'")

    return cur.fetchone()[0]

def select_curr_date(conn):
    """
    Query date
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT datetime('now', 'localtime')")

    return cur.fetchone()[0]

def set_properties(conn, properties):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO properties(property_name,int_value,float_value,char_value,date_value)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, properties)
    conn.commit()
    return cur.lastrowid


db = os.environ.get("DATABASE")
conn = create_connection(db)

@bot.event
async def on_ready():
        print(f"{bot.user} is ready!")

#########################                 #########################
#########################  INFO COMMANDS  #########################
#########################                 #########################

# @bot.slash_command(guild_ids=[747905921115619399])  # create a slash command for the supplied guilds
# async def hello(ctx):
#     """Say hello to the bot"""  # the command description can be supplied as the docstring
#     await ctx.respond(f"Hello, {ctx.author.display_name}!")

@bot.slash_command(guild_ids=[747905921115619399,433922248802304023])  # create a slash command for the supplied guilds
async def info(ctx):
    """Useful X-Wing resourses"""  # the command description can be supplied as the docstring
    embed = discord.Embed(title="X-Wing resources", colour=discord.Colour(0xFFD700))
    embed.add_field(name="Actual Rules documents", value="https://www.atomicmassgames.com/xwing-documents", inline=True)
    embed.add_field(name="Official AMG Rules Forum", value="http://bit.ly/xwingrulesforum", inline=False)
    embed.add_field(name="Buying guide", value="https://bit.ly/2WzBq0c", inline=False)
    embed.add_field(name="Black Market A68", value="https://bit.ly/3DLZuhe")
    # embed.set_footer(text=ctx.author.name, icon_url = ctx.author.avatar_url)
    await ctx.respond(embed=embed)

@bot.slash_command(guild_ids=[747905921115619399,433922248802304023])  # create a slash command for the supplied guilds
async def builders(ctx):
    """X-Wing community builders"""  # the command description can be supplied as the docstring
    embed = discord.Embed(title="X-Wing builders", colour=discord.Colour(0xFFD700))
    embed.add_field(name="YASB 2.0 (Web)", value="https://raithos.github.io", inline=True)
    embed.add_field(name="Launch Bay Next (Web)", value="https://launchbaynext.app", inline=False)
    embed.add_field(name="Launch Bay Next (Android)", value="https://bit.ly/3bP3GjG", inline=False)
    embed.add_field(name="Launch Bay Next (iOS)", value="https://apple.co/3CToHVX")
    await ctx.respond(embed=embed)

#########################                   #########################
#########################  LEAGUE COMMANDS  #########################
#########################                   #########################

@bot.slash_command(guild_ids=[747905921115619399], default_permission=False)
@permissions.has_role("league admin")
async def register(ctx, member: discord.Member):
    """Give league member role to a mentioned user."""
#    await ctx.respond(f"Hi, {member.name} also  known as {member.display_name}")

#    try:
    role = get(ctx.guild.roles, name="league")                    # role you want to add to a user
    if role in member.roles:                                      # checks if user has such role
        await ctx.respond(f"{member.display_name} has league role already")
    else:
        # Inserts row with user data into db as well as default game stat values
        insert_member_sql_querry = f"""INSERT INTO members (member_id, member_name) VALUES ({member.id}, '{member.name}');"""
        insert_sql(conn, insert_member_sql_querry)
        conn.commit()
        # add league role
        await member.add_roles(role)
        # pretty outpun in chat
        embed = discord.Embed(title=f"Registration successful\nWelcome to the league!", colour=discord.Colour(0x6790a7))
        embed.set_footer(text=member.display_name, icon_url = member.display_avatar)
        await ctx.respond(embed=embed)
#    except: # simple error handler if bot tries to insert duplicated value
#        await ctx.respond(f"It seems that registration for {member.display_name} has failed")

@bot.slash_command(guild_ids=[747905921115619399], default_permission=False)
@permissions.has_role("league")
async def results(ctx, winner: discord.Member, winner_points, looser: discord.Member, looser_points):
    """Submit regular leage game results."""
    sql_get_k = f"""SELECT int_value FROM properties WHERE property_name = 'k_regular';"""
    
    #pt = points
    
    # K = execute_sql(conn, sql_get_k)
    K = select_k_regular(conn)
    
    ## extract current rating for message winner
    # winner rating
    Ra = select_rating_sql(conn, winner.id)

    ## extract current rating for mentioned looser
    # looser rating
    Rop = select_rating_sql(conn, looser.id) 
    ### calculating ELO ###

    ## gathered delta points from current game result
    Ea = round( 1 / (1 + 10 ** ((Rop - Ra) / 400)), 2)
    Eop = round( 1 / (1 + 10 ** ((Ra - Rop) / 400 )), 2)
    
    ## calculate new rating
    # Calculate new Ra as Rna, 1 for win
    Rna = round( Ra + K * (1 - Ea), 2)
    Rna_diff = round(Rna - Ra, 2)
    # Calculate new Rop as Rnop, 0 for loss
    Rnop = round( Rop + K * (0 - Eop), 2)
    Rnop_diff = round(Rop - Rnop, 2)
    
    
    curr_date = select_curr_date(conn)
    #insert game entry
    game_result = (winner.id, winner_points, Rna_diff, looser.id, looser_points, Rnop_diff, curr_date);
    project_id = insert_regular_win(conn, game_result)

    update_member(conn, (Rna, winner.id))
    update_member(conn, (Rnop, looser.id))

    Ra = select_rating_sql(conn, winner.id)
    Rop = select_rating_sql(conn, looser.id)

    await ctx.respond(f"Results submitted!\n {winner.display_name} is now at {Ra}\n{looser.display_name} is now {Rop}")



# @bot.slash_command(guild_ids=[747905921115619399])
# async def date(ctx):
#     date = subprocess.Popen("date", stdout=subprocess.PIPE, universal_newlines=True, shell=True)
#     output = date.stdout.read()
#     await ctx.respond(f"{output}")

##########################             ##########################
##########################  DB TABLES  ##########################
##########################             ##########################

sql_create_members_table = """CREATE TABLE IF NOT EXISTS members (
                                member_id integer UNIQUE PRIMARY KEY,
                                member_name text NOT NULL,
                                rating INT DEFAULT 1500
                            );"""

# To-DO CREATE STAT VIEW

sql_create_properties_table = """CREATE TABLE IF NOT EXISTS properties (
                                id integer PRIMARY KEY autoincrement,
                                property_name text NOT NULL,
                                int_value integer,
                                float_value float,
                                char_value varchar,
                                date_value date
                            );"""

sql_create_games_table = """CREATE TABLE IF NOT EXISTS games (
                                game_id integer UNIQUE PRIMARY KEY autoincrement,
                                winner_id integer REFERENCES members(member_id),
                                winner_score integer NOT NULL,
                                winner_rating_diff integer NOT NULL,
                                looser_id integer REFERENCES members(member_id),
                                looser_score integer NOT NULL,
                                looser_rating_diff integer NOT NULL,
                                tournament boolean DEFAULT FALSE,
                                game_date date NOT NULL
                            );"""

sql_drop_members_table = """DROP TABLE members;"""

sql_drop_properties_table = """DROP TABLE properties;"""

sql_drop_games_table = """DROP TABLE games;"""

k_regular_properties = ("k_regular", 16, None, None, None)
k_tournament_properties = ("k_tournament", 32, None, None, None)



##########################             ##########################
########################## DB COMMANDS ##########################
##########################             ##########################

@bot.slash_command(guild_ids=[747905921115619399], default_permission=False)
@permissions.permission(user_id=218988865631944705, permission=True)
async def create_tables(ctx):
    """Create tables first time"""
    if conn is not None:
        # create members table
        create_table(conn, sql_create_members_table)

        # create settings table
        create_table(conn, sql_create_properties_table)

        # create games table
        create_table(conn, sql_create_games_table)
    else:
        print("Error! cannot create the database connection.")

    await ctx.respond(f"Tables created!")

@bot.slash_command(guild_ids=[747905921115619399], default_permission=False)
@permissions.permission(user_id=218988865631944705, permission=True)
async def recreate_tables(ctx):
    """Drop and Create tables for fresh start"""
    if conn is not None:
        # drop members table
        drop_table(conn, sql_drop_members_table)

        # drop properties table
        drop_table(conn, sql_drop_properties_table)

        # drop games table
        drop_table(conn, sql_drop_games_table)
        
        # create members table
        create_table(conn, sql_create_members_table)

        # create settings table
        create_table(conn, sql_create_properties_table)

        # create games table
        create_table(conn, sql_create_games_table)

        set_properties(conn, k_regular_properties)
        set_properties(conn, k_tournament_properties)
    else:
        print("Error! cannot create the database connection.")

    await ctx.respond(f"Tables recreated!")    

bot.run(token)