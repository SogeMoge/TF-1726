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

@bot.slash_command(guild_ids=[747905921115619399])  # create a slash command for the supplied guilds
async def hello(ctx):
    """Say hello to the bot"""  # the command description can be supplied as the docstring
    await ctx.send(f"Hello, {ctx.author.display_name}!")

@bot.slash_command(guild_ids=[747905921115619399,433922248802304023])  # create a slash command for the supplied guilds
async def info(ctx):
    """Useful X-Wing resourses"""  # the command description can be supplied as the docstring
    embed = discord.Embed(title="X-Wing resources", colour=discord.Colour(0xFFD700))
    embed.add_field(name="Actual Rules documents", value="https://www.atomicmassgames.com/xwing-documents", inline=True)
    embed.add_field(name="Official AMG Rules Forum", value="http://bit.ly/xwingrulesforum", inline=False)
    embed.add_field(name="Buying guide", value="https://bit.ly/2WzBq0c", inline=False)
    embed.add_field(name="Black Market A68", value="https://bit.ly/3DLZuhe")
    # embed.set_footer(text=ctx.author.name, icon_url = ctx.author.avatar_url)
    await ctx.send(embed=embed)

@bot.slash_command(guild_ids=[747905921115619399,433922248802304023])  # create a slash command for the supplied guilds
async def builders(ctx):
    """X-Wing community builders"""  # the command description can be supplied as the docstring
    embed = discord.Embed(title="X-Wing builders", colour=discord.Colour(0xFFD700))
    embed.add_field(name="YASB 2.0 (Web)", value="https://raithos.github.io", inline=True)
    embed.add_field(name="Launch Bay Next (Web)", value="https://launchbaynext.app", inline=False)
    embed.add_field(name="Launch Bay Next (Android)", value="https://bit.ly/3bP3GjG", inline=False)
    embed.add_field(name="Launch Bay Next (iOS)", value="https://apple.co/3CToHVX")
    # embed.set_footer(text=ctx.author.name, icon_url = ctx.author.avatar_url)
    await ctx.send(embed=embed)

bot.run(token)