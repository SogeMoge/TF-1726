import os
import subprocess
from dotenv import load_dotenv

import sqlite3
from sqlite3 import Error

import discord
from discord.ext import commands
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

db = os.environ.get("DATABASE")
conn = create_connection(db)

@bot.event
async def on_ready():
        print(f"{bot.user} is ready!")

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
    # embed.set_footer(text=ctx.author.name, icon_url = ctx.author.avatar_url)
    await ctx.respond(embed=embed)

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
                                looser_id integer REFERENCES members(member_id),
                                looser_score integer NOT NULL,
                                rating_diff integer NOT NULL,
                                tournament boolean DEFAULT FALSE,
                                game_date date NOT NULL
                            );"""

sql_drop_members_table = """DROP TABLE members;"""

sql_drop_properties_table = """DROP TABLE properties;"""

sql_drop_games_table = """DROP TABLE games;"""


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
async def drop_tables(ctx):
    """Drop tables for fresh start"""
    if conn is not None:
        # create members table
        drop_table(conn, sql_drop_members_table)

        # create settings table
        drop_table(conn, sql_drop_properties_table)

        # create games table
        drop_table(conn, sql_drop_games_table)
    else:
        print("Error! cannot create the database connection.")

    await ctx.respond(f"Tables dropped!")    

bot.run(token)