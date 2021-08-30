from discord.ext import commands
from discord.ext.commands import group, Context

class Bot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @group(invoke_without_command=True, name="bot")
    async def bot_group(self, ctx: Context):
        await ctx.invoke(self.bot.get_command("help"), "bot")


def setup(bot):
    bot.add_cog(Bot(bot))
    print("Cog Bot loaded")
