import disnake
from disnake.ext import commands


class PremiumCog(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.slash_command(
        name=disnake.Localized(key="PRO"),
        description=disnake.Localized(key="PRO_DESCRIPTION")
    )
    async def pro(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @pro.sub_command(
        name=disnake.Localized(key="TIMELY"),
        description=disnake.Localized(key="TIMELY_DESCRIPTION")
    )
    async def timely(self, inter: disnake.ApplicationCommandInteraction):
        await inter.send("✅")


def setup(bot):
    bot.add_cog(PremiumCog(bot))
