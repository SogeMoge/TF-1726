import os
import subprocess
from dotenv import load_dotenv
from datetime import date

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

intents = discord.Intents().all()
bot = discord.Bot(intents=intents)
load_dotenv()
token = os.environ.get("DISCORD_TOKEN")


results_channel_id = int(os.environ.get("RESULTS_CHANNEL_ID"))
test_guild_id = int(os.environ.get("TEST_GUILD_ID"))
russian_guild_id = int(os.environ.get("RUSSIAN_GUILD_ID"))
db_admin_id = int(os.environ.get("DB_ADMIN_ID"))
db = os.environ.get("DATABASE")


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


# def create_table(conn, create_table_sql):
#     """create a table from the create_table_sql statement
#     :param conn: Connection object
#     :param create_table_sql: a CREATE TABLE statement
#     :return:
#     """
#     try:
#         c = conn.cursor()
#         c.execute(create_table_sql)
#     except Error as e:
#         print(e)


# def sql_db.drop_table(conn, sql_db.drop_table_sql):
#     """drop a table from the sql_db.drop_table_sql statement
#     :param conn: Connection object
#     :param create_table_sql: a DROP TABLE statement
#     :return:
#     """
#     try:
#         c = conn.cursor()
#         c.execute(sql_db.drop_table_sql)
#     except Error as e:
#         print(e)

# def sql_update.member(conn, rating):
#     """
#     update member's rating and streak
#     :param conn:
#     :param rating:
#     :return: project id
#     """
#     sql = """ UPDATE members
#               SET rating = ?
#               WHERE member_id = ?"""
#     cur = conn.cursor()
#     cur.execute(sql, rating)
#     conn.commit()

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


# def sql_select.member_stats(conn, member_id):
#     """
#     Select and print league statistics for member
#     "param member_id: get stats for ctx.author.id
#     """
#     sql_win = f""" SELECT count(g.winner_id) cnt_win
#                    FROM  members m 
#                    LEFT JOIN games g ON m.member_id=g.winner_id
#                    WHERE 1=1
#                    AND g.fun_event = 0
#                    AND m.member_id={member_id} """
#     cur_w = conn.cursor()
#     cur_w.execute(sql_win)
#     cnt_win = cur_w.fetchone()[0]

#     sql_loss = f"""SELECT count(g.looser_id) cnt_loose
#                    FROM  members m 
#                    LEFT JOIN games g ON m.member_id=g.looser_id
#                    WHERE 1=1
#                    AND g.fun_event = 0
#                    AND m.member_id={member_id} """
#     cur_l = conn.cursor()
#     cur_l.execute(sql_loss)
#     cnt_loss = cur_l.fetchone()[0]

#     if cnt_win + cnt_loss > 0:
#         winrate = int(round(cnt_win / (cnt_win + cnt_loss) * 100, 0))

#         sql = f""" SELECT member_id, rating, {cnt_win} , {cnt_loss}, {winrate}
#                    from members
#                    where 1=1
#                    and member_id={member_id}; """
#         cur = conn.cursor()
#         cur.execute(sql)
#         rows = cur.fetchall()
#         return rows
#     else:
#         sql = f""" SELECT member_id, rating, {cnt_win} , {cnt_loss}, 0
#                    from members
#                    where 1=1
#                    and member_id={member_id}; """
#         cur = conn.cursor()
#         cur.execute(sql)
#         rows = cur.fetchall()
#         return rows


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
        label="Rules Referense",
        url="https://www.atomicmassgames.com/xwing-documents",
    )
    button2 = Button(
        label="AMG Rules Forum", url="http://bit.ly/xwingrulesforum"
    )
    button3 = Button(
        label="Buying guide per factions", url="https://bit.ly/2WzBq0c"
    )
    button4 = Button(
        label="Black Market A68", url="https://bit.ly/3DLZuhe"
    )
    view = View(button1, button2, button3, button4)
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
        label="YASB 2.0 (Web)", url="https://raithos.github.io"
    )
    button2 = Button(
        label="Launch Bay Next (Web)", url="https://launchbaynext.app"
    )
    button3 = Button(
        label="Launch Bay Next (Android)", url="https://bit.ly/3bP3GjG"
    )
    button4 = Button(
        label="Launch Bay Next (iOS)", url="https://apple.co/3CToHVX"
    )
    view = View(button1, button2, button3, button4)
    await ctx.respond("Squad Builders:", view=view)


#########################                   #########################
#########################  LEAGUE COMMANDS  #########################
#########################                   #########################


@bot.slash_command(
    guild_ids=[russian_guild_id], default_permission=False
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
    guild_ids=[russian_guild_id], default_permission=False
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
    guild_ids=[russian_guild_id], default_permission=False
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
    guild_ids=[russian_guild_id], default_permission=False
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
    guild_ids=[russian_guild_id], default_permission=False
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
