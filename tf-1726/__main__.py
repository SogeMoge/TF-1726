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

@bot.slash_command(guild_ids=[747905921115619399])  # create a slash command for the supplied guilds
async def info(ctx):
    """Useful X-Wing resourses"""  # the command description can be supplied as the docstring
    embed = discord.Embed(title="X-Wing resources", colour=discord.Colour(0xFFD700))
    embed.add_field(name="https://www.atomicmassgames.com/xwing-documents", value=pos, inline=False)
    embed.set_footer(text=ctx.author.name, icon_url = ctx.author.avatar_url)
    await ctx.send(embed=embed)

bot.run(token)