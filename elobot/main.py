import os
import subprocess
from dotenv import load_dotenv
from datetime import date
import random

# modules for YASB link parsing
import re
import requests
import json
from html import unescape
import asyncio

import sqlite3
from sqlite3 import Error

import discord
from discord.ext import commands
from discord.utils import get
from discord.commands import Option
from discord.commands import permissions
from discord.ui import Button, View, Select

# custom bot modules
import sql_select
import sql_insert
import sql_update
import sql_db
import db_properties
import db_tables

##### Configure logging #####
import logging
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='elobot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

intents = discord.Intents().all()
bot = discord.Bot(intents=intents)

#### Load .env vars and discord token"
load_dotenv()
token = os.environ.get("DISCORD_TOKEN")

##### League vars #####
results_channel_id = int(os.environ.get("RESULTS_CHANNEL_ID"))
test_guild_id = int(os.environ.get("TEST_GUILD_ID"))
russian_guild_id = int(os.environ.get("RUSSIAN_GUILD_ID"))
db_admin_id = int(os.environ.get("DB_ADMIN_ID"))
db = os.environ.get("DATABASE")
##### League vars #####

##### Welcome channel vars #####
channel_welcome_id = int(os.environ.get("CHANNEL_WELCOME_ID"))
channel_navigation_id= int(os.environ.get("CHANNEL_NAVIGATION_ID"))
channel_roles_id= int(os.environ.get("CHANNEL_ROLES_ID"))
channel_location_id= int(os.environ.get("CHANNEL_LOCATION_ID"))
##### Welcome channel vars #####


##### YASB PARSING VARS #####
GITHUB_USER = 'Gan0n29'
GITHUB_BRANCH = 'xwing-legacy'
BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/ttt-xwing-overlay/{GITHUB_BRANCH}/src/assets/plugins/xwing-data2/"
MANIFEST = 'data/manifest.json'
check_frequency = 900  # 15 minutes
##### YASB PARSING WARS #####

update_reaction = "\U0001f504"  # circle arrows
accept_reactions = ["\U00002705", "\U0000274e"]  # check and cross marks
date = date.today()


def create_connection(db_file):
    """create a database connection to the SQLite database
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

conn = create_connection(db)


def delta_points(opponent_rating, member_rating):
    """
    Compute delta points for opponents
    :param opponent_rating: current opponent rating
    :param member_rating: current player ratng
    """
    E = round(
        1 / (1 + 10 ** ((opponent_rating - member_rating) / 400)), 2
    )
    return E


def rating(win, K, R, E):
    """
    Compute new rating
    :param win: 1 for win, 0 for loss
    :param K: K property extracted from DB
    :param R: current rating of player
    :param E: delta poins of player
    """
    Rn = round(R + K * (win - E), 2)
    return Rn

class UpdateView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        custom_id="update1",
        label="Update",
        style=discord.ButtonStyle.primary,
        emoji=update_reaction,
    )
    async def button_callback(self, button, interaction):
        embed = discord.Embed(
            title="League leaderboard", colour=discord.Colour(0xFFD700)
        )
        min_games = sql_select.minimal_games_property(conn)

        n = 0
        cur = conn.cursor()
        for row in cur.execute(
            f"""SELECT m.member_name, m.rating, a.cnt_win, b.cnt_loose
                from members m
                left join
                (select m.member_id, count(g.winner_id) cnt_win
                from  members m 
                left JOIN games g ON m.member_id=g.winner_id
                group by m.member_id
                ) a on m.member_id = a.member_id
                left join
                (select m.member_id, count(g.looser_id) cnt_loose
                from  members m 
                left JOIN games g ON m.member_id=g.looser_id
                group by m.member_id
                ) b on m.member_id = b.member_id
                where 1=1
                AND cnt_win+cnt_loose>={min_games}
                ORDER BY m.rating DESC
                ;"""
        ):
            n = n + 1
            embed.add_field(
                name="\u200b",
                value="{} - {} | R:{} W:{} L:{}".format(
                    n, row[0], row[1], row[2], row[3]
                ),
                inline=False,
            )
        min_games = sql_select.minimal_games_property(conn)
        await interaction.response.edit_message(
            content=f"Top resuts, played at least {min_games} game(s)\nUpdated from {date.today()}",
            embed=embed,
            view=UpdateView(),
        )

#########################                 #########################
#########################     EVENTS      #########################
#########################                 #########################

@bot.event
async def on_ready():
    bot.add_view(UpdateView())
    print(f"{bot.user} is ready!")


# @bot.event
# async def on_message(message):

#     if (
#         bot.user.mentioned_in(message)
#         and message.mention_everyone is False
#     ):
#         await message.channel.send("hi")

@bot.event
async def on_member_join(member):
    channel_welcome = bot.get_channel(channel_welcome_id)
    channel_navigation = bot.get_channel(channel_navigation_id)
    channel_roles = bot.get_channel(channel_roles_id)
    channel_locaton = bot.get_channel(channel_location_id)

    
    embed = discord.Embed(
            title="Добро пожаловать, пилот!",
            colour=discord.Colour.random(),
            description=f"Поприветствуем {member.mention}"
    )
    embed.add_field(name="C чего начать:",
                    value=f"""Пробегись по трём каналам в разделе **SYSTEM**:\n- {channel_navigation.mention} Узнаешь как здесь ориентироваться\n- {channel_roles.mention} Выберешь подходящие для себя роли\n- {channel_locaton.mention} Расскажи где ты живёшь, *чтобы получить роль своего города*\n""",
                    inline=False
    )
    if member.guild.id == test_guild_id:
        embed.add_field(name="This is a test",
                    value="test",
                    inline=False
        )
        channel_welcome = bot.get_channel(757377279474139156)   
        await channel_welcome.send(embed=embed)
    elif member.guild.id == russian_guild_id:
        await channel_welcome.send(embed=embed)
    else:
        return

#########################                 #########################
####################  LEGACY BUILDER PARSING ######################
#########################                 #########################

@bot.event
async def on_message(message):
    if message.author.bot: #check that author is not the bot itself
        return
    elif '://xwing-legacy.com/?f' in message.content:
        yasb_channel = message.channel

        # convert YASB link to XWS
        yasb_link = message.content
        yasb_convert = yasb_link.replace('://xwing-legacy.com/', '://squad2xws.herokuapp.com/yasb/xws') 
        yasb_xws = requests.get(yasb_convert)

        #############
        # don't know if it works at all???
        yasb_xws = unescape(yasb_xws) # delete all characters which prevents proper parsing

        yasb_json = yasb_xws.json() # raw XWS in JSON
        yasb_json = json.dumps(yasb_json) # convert single quotes to double quotes
        yasb_dict = json.loads(yasb_json) # convert JSON to python object
        #############
        for key, value in yasb_dict.items(): # add embed title with list name as hyperlink
            if key in ["name"]:
                embed = discord.Embed(
                    title=value,
                    colour=discord.Colour.random(),
                    url=message.content,
                    description="YASB Legacy 2.0 list"
                )

        embed.set_footer(
            text=message.author.display_name, icon_url=message.author.display_avatar
        )

        ####### TO DO ######## compare parsed results to data in xwing-data manifest
        # # get JSON manifest from ttt-xwing-overlay repo
        # manifest_link = requests.get(BASE_URL + MANIFEST)
        # manifest = manifest_link.json()

        # files = (
        #     manifest['damagedecks'] +
        #     manifest['upgrades'] +
        #     [manifest['conditions']] +
        #     [ship for faction in manifest['pilots']
        #         for ship in faction['ships']]
        # )

        # _data = {}
        # loop = asyncio.get_event_loop()
        # # get JSON manifest from ttt-xwing-overlay repo
    
    for key, value in yasb_dict.items(): # add embed fields with faction and list name
        if key in ["faction"]:
            embed.add_field(name=key,
                        value=value,
                        inline=True
            )

    pilots_total = len(yasb_dict["pilots"])

    for pilot in range(pilots_total): # add embed fields for each pilot in a list
        embed.add_field(name=yasb_dict["pilots"][pilot]["id"],
                        # value=list(yasb_dict["pilots"][pilot]["upgrades"].values()),
                        value=re.sub(r"[\[\]\']",'\u200b',str(list(yasb_dict["pilots"][pilot]["upgrades"].values()))),
                        inline=False
            )
    await yasb_channel.send(embed=embed)
    await message.delete()
    # await yasb_channel.send(yasb_dict["pilots"][0]["id"])
    # await yasb_channel.send(len(yasb_dict["pilots"]))
    # await channel.send(yasb_dict["pilots"][1])
    # await channel.send(yasb_dict["pilots"][2])
    # await channel.send(yasb_dict["pilots"][3])

    
# http://xwing-legacy.com/ -> http://squad2xws.herokuapp.com/yasb/xws 
# http://xwing-legacy.com/?f=Separatist%20Alliance&d=v8ZsZ200Z305X115WW207W229Y356X456W248Y542XW470WW367WY542XW470WW367W&sn=Royal%20escort&obs=

#########################                 #########################
#########################  INFO COMMANDS  #########################
#########################                 #########################

# @bot.slash_command(guild_ids=[test_guild_id])  # create a slash command for the supplied guilds
# async def hello(ctx):
#     """Say hello to the bot"""  # the command description can be supplied as the docstring
#     await ctx.respond(f"Hello, {ctx.author.display_name}!")


@bot.slash_command(
    guild_ids=[test_guild_id, russian_guild_id]
)  # create a slash command for the supplied guilds
async def links(ctx):
    """Useful X-Wing resources"""  # the command description can be supplied as the docstring
    # embed = discord.Embed(title="X-Wing resources", colour=discord.Colour(0xFFD700))
    # embed.add_field(name="Actual Rules documents", value="https://www.atomicmassgames.com/xwing-documents", inline=True)
    # embed.add_field(name="Official AMG Rules Forum", value="http://bit.ly/xwingrulesforum", inline=False)
    # embed.add_field(name="Buying guide", value="https://bit.ly/2WzBq0c", inline=False)
    # embed.add_field(name="Black Market A68", value="https://bit.ly/3DLZuhe")
    # # embed.set_footer(text=ctx.author.name, icon_url = ctx.author.avatar_url)
    # await ctx.respond(embed=embed)
    button1 = Button(
        label="X-Wing 2.6 Rules",
        url="https://www.atomicmassgames.com/xwing-documents",
    )
    button2 = Button(
        label="AMG Rules Forum", url="http://bit.ly/xwingrulesforum"
    )
    button3 = Button(
        label="X-Wing Legacy 2.0 Rules", url="https://infinitearenas.com/legacy/docs/"
    )
    button4 = Button(
        label="Buying guide per factions", url="https://bit.ly/2WzBq0c"
    )
    button5 = Button(
        label="Black Market A68", url="https://bit.ly/3DLZuhe"
    )
    view = View(button1, button2, button3, button4, button5)
    await ctx.respond("Useful links:", view=view)


@bot.slash_command(
    guild_ids=[test_guild_id, russian_guild_id]
)  # create a slash command for the supplied guilds
async def builders(ctx):
    """Squad Builders for X-Wing from comunity"""  # the command description can be supplied as the docstring
    # embed = discord.Embed(title="X-Wing builders", colour=discord.Colour(0xFFD700))
    # embed.add_field(name="YASB 2.0 (Web)", value="https://raithos.github.io", inline=True)
    # embed.add_field(name="Launch Bay Next (Web)", value="https://launchbaynext.app", inline=False)
    # embed.add_field(name="Launch Bay Next (Android)", value="https://bit.ly/3bP3GjG", inline=False)
    # embed.add_field(name="Launch Bay Next (iOS)", value="https://apple.co/3CToHVX")
    # await ctx.respond(embed=embed)
    button1 = Button(
        label="YASB 2.6 (Web)", url="https://yasb.app/"
    )
    button2 = Button(
        label="YASB Legacy 2.0 (Web)", url="https://xwing-legacy.com/"
    )
    button3 = Button(
        label="Launch Bay Next (Web)", url="https://launchbaynext.app"
    )
    button4 = Button(
        label="Launch Bay Next (Android)", url="https://bit.ly/3bP3GjG"
    )
    button5 = Button(
        label="Launch Bay Next (iOS)", url="https://apple.co/3CToHVX"
    )
    view = View(button1, button2, button3, button4, button5)
    await ctx.respond("Squad Builders:", view=view)


@bot.slash_command(
    guild_ids=[test_guild_id, russian_guild_id]
)  # create a slash command for the supplied guilds
async def scenario_roll(
    ctx,
    rounds_number: Option(int, "№ of rounds", required=True),
):
    """Get random scenario list for provided number of rounds"""  # the command description can be supplied as the docstring
    scenario_list = ['Assault at the Satellite Array', 'Chance Engagement', 'Salvage Mission', 'Scramble the Transmissions']
    if rounds_number in range(1, 4):
        # pick # of random scenario from the list
        play_list = random.sample(scenario_list, k=rounds_number)

        embed = discord.Embed(
                title=f"Scenario list for {rounds_number} rounds",
                colour=discord.Colour.random(),
            )
        embed.add_field(name="Set 1:", value=play_list, inline=False)
    elif rounds_number in range(5, 8):
        # pick # of random scenario from the list
        play_list_1 = random.sample(scenario_list, k=4)
        play_list_2 = random.sample(scenario_list, k=(rounds_number-4))

        embed = discord.Embed(
                title=f"Scenario list for {rounds_number} rounds",
                colour=discord.Colour.random(),
            )
        embed.add_field(name="Set 1:", value=play_list_1, inline=False)
        embed.add_field(name="Set 2:", value=play_list_2, inline=False)
    elif rounds_number < 1:
        embed = discord.Embed(colour=discord.Colour(0xFF0000))
        embed.add_field(
            name="ERROR",
            value=f"{rounds_number} rounds? Why even bother?",
            inline=True,
        )
        await ctx.respond(embed=embed)
        return
    else:
        embed = discord.Embed(colour=discord.Colour(0xFF0000))
        embed.add_field(
            name="ERROR",
            value=f"Do you really want to play {rounds_number} rounds of AMG Wing?",
            inline=True,
        )
        await ctx.respond(embed=embed)
        return

    await ctx.respond(embed=embed)


#########################                   #########################
#########################  LEAGUE COMMANDS  #########################
#########################                   #########################


@bot.slash_command(
    guild_ids=[test_guild_id], default_permission=False
)
@permissions.has_role("league admin")
async def register(ctx, member: discord.Member):
    """Give league member role to a mentioned user."""
    #    await ctx.respond(f"Hi, {member.name} also  known as {member.display_name}")

    #    try:
    role = get(
        ctx.guild.roles, name="league"
    )  # role you want to add to a user
    if role in member.roles:  # checks if user has such role
        await ctx.respond(
            f"{member.display_name} has league role already"
        )
    else:
        # Inserts row with user data into db as well as default game stat values
        insert_member_sql_querry = f"""INSERT INTO members (member_id, member_name) VALUES ({member.id}, '{member.name}');"""
        sql_insert.statement(conn, insert_member_sql_querry)
        conn.commit()
        # add league role
        await member.add_roles(role)
        # pretty outpun in chat
        embed = discord.Embed(
            title=f"Registration successful\nWelcome to the league!",
            colour=discord.Colour(0x6790A7),
        )
        embed.set_footer(
            text=member.display_name, icon_url=member.display_avatar
        )
        await ctx.respond(embed=embed)


#    except: # simple error handler if bot tries to insert duplicated value
#        await ctx.respond(f"It seems that registration for {member.display_name} has failed")


@bot.slash_command(
    guild_ids=[test_guild_id, russian_guild_id],
    default_permission=False,
)
@permissions.has_role("league")
async def status(ctx):
    """Get personal league stats."""
    pos = sql_select.rating_position(conn, ctx.author.id)
    # pos = 1
    rows = sql_select.member_stats(conn, ctx.author.id)
    for row in rows:
        embed = discord.Embed(
            title="League profile", colour=discord.Colour(0xFFD700)
        )
        embed.add_field(name="Position", value=pos, inline=False)
        embed.add_field(name="Rating", value=row[1], inline=False)
        embed.add_field(name="Wins", value=row[2], inline=True)
        embed.add_field(name="Losses", value=row[3], inline=True)
        embed.add_field(name="Winrate", value=f"{row[4]}%", inline=True)
        embed.set_footer(
            text=ctx.author.display_name,
            icon_url=ctx.author.display_avatar,
        )
        await ctx.respond(embed=embed)


@bot.slash_command(
    guild_ids=[test_guild_id, russian_guild_id],
    default_permission=False,
)
@permissions.has_role("league")
async def check(ctx, member: discord.Member):
    """Get mutual games count."""
    # check if players have reached maximum of mutual games
    role_check = discord.utils.get(ctx.guild.roles, name="league")
    if role_check not in member.roles:
        embed = discord.Embed(colour=discord.Colour(0xFF0000))
        embed.add_field(
            name="ERROR",
            value="{} is not a league member!".format(
                member.display_name
            ),
            inline=True,
        )
        await ctx.respond(embed=embed)
        return
    gcount = sql_select.mutual_games_played(conn, ctx.author.id, member.id)

    embed = discord.Embed(colour=discord.Colour(0x6790A7))
    embed.add_field(
        name="Games played",
        value="{} and {} have played {} games in total, not including tournament games.".format(
            ctx.author.display_name, member.display_name, gcount
        ),
        inline=True,
    )
    await ctx.respond(embed=embed)


@bot.slash_command(
    guild_ids=[test_guild_id, russian_guild_id],
    default_permission=False,
)
@permissions.has_role("league admin")
async def top(ctx):
    """Show full league leaderbord."""
    embed = discord.Embed(
        title="League leaderboard", colour=discord.Colour(0xFFD700)
    )
    # cursor.execute(f'SELECT COUNT(member_id) FROM rating;')
    # pnum = cursor.fetchone()[0]
    min_games = sql_select.minimal_games_property(conn)
    member_list = []

    for member in ctx.guild.members:
        rows = sql_select.member_stats(conn, member.id)
        for row in rows:
            wins = row[2]
            losses = row[3]
            if wins + losses >= min_games:
                member_list.append(f"{member.id}")
    member_string = ", ".join(member_list)

    if not member_list:  # do this!
        await ctx.respond(
            f"Nobody has reached minimum number of games, play more!"
        )
        return

    n = 0
    cur = conn.cursor()
    for row in cur.execute(
        f"SELECT member_name, rating FROM members WHERE member_id IN ({member_string}) ORDER BY rating DESC;"
    ):
        n = n + 1
        embed.add_field(
            name="\u200b",
            value="{} - {}".format(n, row[0]),
            inline=False,
        )
    await ctx.respond(
        f"Top resuts, played at least {min_games} game(s)",
        embed=embed,
        view=UpdateView(),
    )

    # button = Button(
    #     label="Update",
    #     style=discord.ButtonStyle.primary,
    #     emoji=update_reaction,
    # )

    # async def button_callback(interaction):
    #     # await interaction.response.edit_massage(content="Updated results from {date}", embed=embed)
    #     embed = discord.Embed(
    #         title="League leaderboard", colour=discord.Colour(0xFFD700)
    #     )
    #     n = 0
    #     cur = conn.cursor()
    #     for row in cur.execute(
    #         f'SELECT member_name||" - "||rating FROM members ORDER BY rating DESC;'
    #     ):
    #         n = n + 1
    #         embed.add_field(
    #             name="\u200b",
    #             value="{} - {}".format(n, row[0]),
    #             inline=False,
    #         )
    #     await interaction.response.edit_message(
    #         content=f"Updated from {date}", embed=embed, view=view
    #     )

    # button.callback = button_callback

    # view = View(button, timeout=None)
    # await ctx.send(f"Results from {date}", embed=embed, view=view)


@bot.slash_command(
    guild_ids=[test_guild_id], default_permission=False
)
@permissions.has_role("league")
async def game(
    ctx,
    winner: Option(discord.Member, "@user", required=True),
    winner_points: Option(int, "Points destroyed", required=True),
    looser: Option(discord.Member, "@user", required=True),
    looser_points: Option(int, "Points destroyed", required=True),
):
    """Submit regular leage game results."""
    role_check = discord.utils.get(ctx.guild.roles, name="league")

    mutual_games_property = sql_select.mutual_games_property(conn)
    mutual_games_count = sql_select.mutual_games_played(
        conn, winner.id, looser.id
    )

    if ctx.channel.id != results_channel_id:
        embed = discord.Embed(colour=discord.Colour(0xFF0000))
        embed.add_field(
            name="ERROR", value="Wrong channel!", inline=True
        )
        await ctx.respond(embed=embed)
        return
    elif ctx.author.id not in [winner.id, looser.id]:
        embed = discord.Embed(colour=discord.Colour(0xFF0000))
        embed.add_field(
            name="ERROR",
            value="You can not enter results for others!",
            inline=True,
        )
        await ctx.respond(embed=embed)
        return
    elif role_check not in winner.roles:
        embed = discord.Embed(colour=discord.Colour(0xFF0000))
        embed.add_field(
            name="ERROR",
            value="{} is not a league member!".format(
                winner.display_name
            ),
            inline=True,
        )
        await ctx.respond(embed=embed)
        return
    elif role_check not in looser.roles:
        embed = discord.Embed(colour=discord.Colour(0xFF0000))
        embed.add_field(
            name="ERROR",
            value="{} is not a league member!".format(
                looser.display_name
            ),
            inline=True,
        )
        await ctx.respond(embed=embed)
        return
    elif mutual_games_count >= mutual_games_property:
        embed = discord.Embed(colour=discord.Colour(0xFF0000))
        embed.add_field(
            name="ERROR",
            value="{} and {} have played {} games already!".format(
                winner.display_name,
                looser.display_name,
                mutual_games_property,
            ),
            inline=True,
        )
        await ctx.respond(embed=embed)
        return

    # K = execute_sql(conn, sql_get_k)
    K = sql_select.k_regular(conn)

    ## extract current rating for message winner
    # winner rating
    # Ra = select_rating_sql(conn, winner.id)
    Ra = sql_select.rating(conn, winner.id)

    ## extract current rating for mentioned looser
    # looser rating
    # Rop = select_rating_sql(conn, looser.id)
    Rop = sql_select.rating(conn, looser.id)
    ### calculating ELO ###

    ## gathered delta points from current game result
    # Ea = round( 1 / (1 + 10 ** ((Rop - Ra) / 400)), 2)
    Ea = delta_points(Rop, Ra)
    # Eop = round( 1 / (1 + 10 ** ((Ra - Rop) / 400 )), 2)
    Eop = delta_points(Ra, Rop)

    ## calculate new rating
    # Calculate new Ra as Rna, 1 for win
    # Rna = round( Ra + K * (1 - Ea), 2)
    Rna = rating(1, K, Ra, Ea)
    Rna_diff = round(Rna - Ra, 2)

    # Calculate new Rop as Rnop, 0 for loss
    # Rnop = round( Rop + K * (0 - Eop), 2)
    Rnop = rating(0, K, Rop, Eop)
    Rnop_diff = round(Rop - Rnop, 2)

    curr_date = sql_select.curr_date(conn)
    # insert game entry
    game_result = (
        winner.id,
        winner_points,
        Rna_diff,
        looser.id,
        looser_points,
        Rnop_diff,
        curr_date,
    )
    game_id = sql_insert.regular_win(conn, game_result)

    sql_update.member(conn, (Rna, winner.id))
    sql_update.member(conn, (Rnop, looser.id))

    # Pretty output of updated rating for participant
    embed_win = discord.Embed(
        title="Updated League profile", colour=discord.Colour(0x00FFFF)
    )
    embed_win.add_field(name="Game_id", value=game_id, inline=False)
    embed_win.add_field(name="Old Rating", value=Ra, inline=True)
    embed_win.add_field(name="Diff", value=Rna_diff, inline=True)
    embed_win.add_field(name="New Rating", value=Rna, inline=True)
    embed_win.set_footer(
        text=winner.display_name, icon_url=winner.display_avatar
    )

    embed_loss = discord.Embed(
        title="Updated League profile", colour=discord.Colour(0x00FFFF)
    )
    embed_loss.add_field(name="Game_id", value=game_id, inline=False)
    embed_loss.add_field(name="Old Rating", value=Rop, inline=True)
    embed_loss.add_field(name="Diff", value=Rnop_diff, inline=True)
    embed_loss.add_field(name="New Rating", value=Rnop, inline=True)
    embed_loss.set_footer(
        text=looser.display_name, icon_url=looser.display_avatar
    )

    await ctx.respond(
        f"(Game {game_id}): {winner.display_name} won against {looser.display_name} with {winner_points} - {looser_points} score!"
    )
    emb_msg = await ctx.send(embeds=[embed_win, embed_loss])
    for reaction in accept_reactions:
        await emb_msg.add_reaction(reaction)


@bot.slash_command(
    guild_ids=[test_guild_id], default_permission=False
)
@permissions.has_role("league admin")
async def tournament_game(
    ctx,
    winner: Option(discord.Member, "@user", required=True),
    winner_points: Option(int, "Points destroyed", required=True),
    looser: Option(discord.Member, "@user", required=True),
    looser_points: Option(int, "Points destroyed", required=True),
):
    """Submit tournament leage game results."""
    role_check = discord.utils.get(ctx.guild.roles, name="league")

    if ctx.channel.id != results_channel_id:
        embed = discord.Embed(colour=discord.Colour(0xFF0000))
        embed.add_field(
            name="ERROR", value="Wrong channel!", inline=True
        )
        await ctx.respond(embed=embed)
        return
    elif role_check not in winner.roles:
        embed = discord.Embed(colour=discord.Colour(0xFF0000))
        embed.add_field(
            name="ERROR",
            value="{} is not a league member!".format(
                winner.display_name
            ),
            inline=True,
        )
        await ctx.respond(embed=embed)
        return
    elif role_check not in looser.roles:
        embed = discord.Embed(colour=discord.Colour(0xFF0000))
        embed.add_field(
            name="ERROR",
            value="{} is not a league member!".format(
                looser.display_name
            ),
            inline=True,
        )
        await ctx.respond(embed=embed)
        return

    # K = execute_sql(conn, sql_get_k)
    K = sql_select.k_tournament(conn)

    # game will not count for mutual games
    tournament = 1

    ## extract current rating for message winner
    # winner rating
    # Ra = select_rating_sql(conn, winner.id)
    Ra = sql_select.rating(conn, winner.id)

    ## extract current rating for mentioned looser
    # looser rating
    # Rop = select_rating_sql(conn, looser.id)
    Rop = sql_select.rating(conn, looser.id)
    ### calculating ELO ###

    ## gathered delta points from current game result
    # Ea = round( 1 / (1 + 10 ** ((Rop - Ra) / 400)), 2)
    Ea = delta_points(Rop, Ra)
    # Eop = round( 1 / (1 + 10 ** ((Ra - Rop) / 400 )), 2)
    Eop = delta_points(Ra, Rop)

    ## calculate new rating
    # Calculate new Ra as Rna, 1 for win
    # Rna = round( Ra + K * (1 - Ea), 2)
    Rna = rating(1, K, Ra, Ea)
    Rna_diff = round(Rna - Ra, 2)

    # Calculate new Rop as Rnop, 0 for loss
    # Rnop = round( Rop + K * (0 - Eop), 2)
    Rnop = rating(0, K, Rop, Eop)
    Rnop_diff = round(Rop - Rnop, 2)

    curr_date = sql_select.curr_date(conn)
    # insert game entry
    game_result = (
        winner.id,
        winner_points,
        Rna_diff,
        looser.id,
        looser_points,
        Rnop_diff,
        tournament,
        curr_date,
    )
    game_id = sql_insert.tournament_win(conn, game_result)

    sql_update.member(conn, (Rna, winner.id))
    sql_update.member(conn, (Rnop, looser.id))

    # Pretty output of updated rating for participant
    embed_win = discord.Embed(
        title="Updated League profile", colour=discord.Colour(0x00FFFF)
    )
    embed_win.add_field(name="Game_id", value=game_id, inline=False)
    embed_win.add_field(name="Old Rating", value=Ra, inline=True)
    embed_win.add_field(name="Diff", value=Rna_diff, inline=True)
    embed_win.add_field(name="New Rating", value=Rna, inline=True)
    embed_win.set_footer(
        text=winner.display_name, icon_url=winner.display_avatar
    )

    embed_loss = discord.Embed(
        title="Updated League profile", colour=discord.Colour(0x00FFFF)
    )
    embed_loss.add_field(name="Game_id", value=game_id, inline=False)
    embed_loss.add_field(name="Old Rating", value=Rop, inline=True)
    embed_loss.add_field(name="Diff", value=Rnop_diff, inline=True)
    embed_loss.add_field(name="New Rating", value=Rnop, inline=True)
    embed_loss.set_footer(
        text=looser.display_name, icon_url=looser.display_avatar
    )

    msg = await ctx.respond(
        f"(Game {game_id}): {winner.display_name} won in a tournament against {looser.display_name} with {winner_points} - {looser_points} score!"
    )
    await ctx.send(embeds=[embed_win, embed_loss])


@bot.slash_command(
    guild_ids=[test_guild_id], default_permission=False
)
@permissions.has_role("league admin")
async def fun_win(
    ctx,
    winner: discord.Member,
):
    points = sql_select.fun_event_win_points(conn)
    # Ra = select_rating_sql(conn, winner.id)
    Ra = sql_select.rating(conn, winner.id)
    Rna = Ra + points
    sql_update.member(conn, (Rna, winner.id))
    embed = discord.Embed(
        title="Fun event win", colour=discord.Colour(0x00B300)
    )
    embed.add_field(name="Old rating", value=Ra, inline=False)
    embed.add_field(name="Win points", value=points, inline=True)
    embed.add_field(name="New rating", value=Rna, inline=True)
    embed.set_footer(
        text=winner.display_name, icon_url=winner.display_avatar
    )
    await ctx.respond(embed=embed)


@bot.slash_command(
    guild_ids=[test_guild_id], default_permission=False
)
@permissions.has_role("league admin")
async def fun_game(
    ctx,
    participant: discord.Member,
):
    points = sql_select.fun_event_participation_points(conn)
    # Ra = select_rating_sql(conn, participant.id)
    Ra = sql_select.rating(conn, participant.id)
    Rna = Ra + points
    sql_update.member(conn, (Rna, participant.id))
    embed = discord.Embed(
        title="Fun event participation", colour=discord.Colour(0x00B300)
    )
    embed.add_field(name="Old rating", value=Ra, inline=False)
    embed.add_field(
        name="Participation points", value=points, inline=True
    )
    embed.add_field(name="New rating", value=Rna, inline=True)
    embed.set_footer(
        text=participant.display_name,
        icon_url=participant.display_avatar,
    )
    await ctx.respond(embed=embed)


# @bot.slash_command(guild_ids=[test_guild_id])
# async def date(ctx):
#     date = subprocess.Popen("date", stdout=subprocess.PIPE, universal_newlines=True, shell=True)
#     output = date.stdout.read()
#     await ctx.respond(f"{output}")


##########################             ##########################
########################## DB COMMANDS ##########################
##########################             ##########################


@bot.slash_command(guild_ids=[test_guild_id], default_permission=False)
@permissions.permission(user_id=db_admin_id, permission=True)
async def league_create_tables(ctx):
    """Create tables first time"""
    if conn is not None:

        sql_db.create_table(conn, db_tables.sql_create_members_table)

        sql_db.create_table(conn, db_tables.sql_create_properties_table)

        sql_db.create_table(conn, db_tables.sql_create_games_table)

        sql_insert.set_properties(conn, db_properties.k_regular_properties)

        sql_insert.set_properties(conn, db_properties.k_tournament_properties)

        sql_insert.set_properties(conn, db_properties.pt_fun_event_win_properties)

        sql_insert.set_properties(conn, db_properties.pt_fun_event_participation_properties)

        sql_insert.set_properties(conn, db_properties.num_mutual_games)

        sql_insert.set_properties(conn, db_properties.num_minimal_games)
    else:
        print("Error! cannot create the database connection.")

    await ctx.respond(f"Tables created!")


@bot.slash_command(guild_ids=[test_guild_id], default_permission=False)
@permissions.permission(user_id=db_admin_id, permission=True)
async def league_recreate_tables(ctx):
    """Drop and Create tables for fresh start"""
    if conn is not None:

        sql_db.drop_table(conn, db_tables.sql_drop_members_table)

        sql_db.drop_table(conn, db_tables.sql_drop_properties_table)

        sql_db.drop_table(conn, db_tables.sql_drop_games_table)

        sql_db.create_table(conn, db_tables.sql_create_members_table)

        sql_db.create_table(conn, db_tables.sql_create_properties_table)

        sql_db.create_table(conn, db_tables.sql_create_games_table)

        sql_insert.set_properties(conn, db_properties.k_regular_properties)

        sql_insert.set_properties(conn, db_properties.k_tournament_properties)

        sql_insert.set_properties(conn, db_properties.pt_fun_event_win_properties)

        sql_insert.set_properties(conn, db_properties.pt_fun_event_participation_properties)

        sql_insert.set_properties(conn, db_properties.num_mutual_games)

        sql_insert.set_properties(conn, db_properties.num_minimal_games)

    else:
        print("Error! cannot create the database connection.")

    await ctx.respond(f"Tables recreated!")


# SELECT *
#    FROM games
#    WHERE game_date BETWEEN "2010-01-01" AND "2013-01-01"
#    WHERE game_date > '2021-12-01'
bot.run(token)
