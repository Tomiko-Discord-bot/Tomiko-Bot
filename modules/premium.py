import disnake
from disnake.ext import commands


class PremiumCog(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot


def setup(bot):
    bot.add_cog(PremiumCog(bot))
