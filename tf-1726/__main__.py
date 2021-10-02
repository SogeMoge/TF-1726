import os
from dotenv import load_dotenv

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix = "%")
load_dotenv()
token = os.environ.get("DISCORD_TOKEN")

@bot.event
async def on_ready():
        print(f"{bot.user} is ready!")

@bot.slash_command(guild_ids=[747905921115619399,433922248802304023])  # create a slash command for the supplied guilds
async def hello(ctx):
    """Say hello to the bot"""  # the command description can be supplied as the docstring
    await ctx.send(f"Hello, {ctx.author.display_name}!")

bot.run(token)