from discord.ext import commands

class Administration(commands.Cog):
    """
    COG POUR LES COMMANDES D'ADMINISTRATION
    """
    def __init__(self, bot):
        self.bot = bot



def setup(bot: commands.Bot):
    bot.add_cog(Administration(bot))
