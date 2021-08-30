#!/usr/bin/python3.8

import discord
from discord.ext import commands
import os
import logging
from private.config import TOKEN

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), help_command=None, intents=intents)

channel_command_id = "862063652671717417"
owner_ids = ["830486558896816128"]

@bot.event
async def on_ready():
    print(f"Bot name : {bot.user.name}\n"
          f"Bot id : {bot.user.id}\n")

# bot.load_extension("cogs.commands")
# # bot.load_extension("cogs.ErrorHandler")
# bot.load_extension("cogs.economy")
bot.load_extension("cogs.serverCommands")

bot.run(TOKEN)

