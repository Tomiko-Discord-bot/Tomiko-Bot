import disnake
from disnake.ext import commands
from utils import i18n


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot
        self.messages = {}

    @commands.slash_command(
        name=disnake.Localized(key="HELP"),
        description=disnake.Localized(key="HELP_DESCRIPTION")
    )
    async def help(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        locales = i18n.Init(inter)
        embed = disnake.Embed(
            title=locales.get("HELP_TITLE"),
            description=locales.get("HELP_EMBED_DESCRIPTION"),
            colour=0x2b2d31
        )
        embed.set_thumbnail(url=inter.author.display_avatar.url)
        select = disnake.ui.Select(custom_id="help")
        select.add_option(
            label=locales.get("HELP_ECONOMY"),
            emoji="<:fire:1117506834371182592>",
            description=locales.get("HELP_ECONOMY_DESCRIPTION"),
            value="economy"
        )
        select.add_option(
            label=locales.get("HELP_GENERAL"),
            emoji="<:edit:1117546025859682484>",
            description=locales.get("HELP_GENERAL_DESCRIPTION"),
            value="general"
        )
        select.add_option(
            label=locales.get("HELP_PRO"),
            emoji="<:premium:1119969423093137438>",
            description=locales.get("HELP_PRO_DESCRIPTION"),
            value="pro"
        )
        await inter.send(embed=embed, components=[select])

    @commands.Cog.listener()
    async def on_dropdown(self, inter: disnake.MessageInteraction):
        if isinstance(inter.component, disnake.StringSelectMenu) and inter.data.custom_id == "help":
            await inter.response.defer()
            locales = i18n.Init(inter)
            embed = disnake.Embed(title=locales.get("HELP_TITLE"), colour=0x2b2d31)
            embed.set_thumbnail(url=inter.author.display_avatar.url)
            category = inter.data.values[0]
            cmds = []
            for cmd in self.bot.get_cog(f"{category.capitalize()}Cog").get_slash_commands():
                cmds.append("`"+cmd.qualified_name+"`")
            embed.add_field(
                name=locales.get(f"HELP_{category.upper()}_EMOJI")+" — "+locales.get(f"HELP_{category.upper()}"),
                value=" ".join(cmds)
            )
            await inter.message.edit(embed=embed)


def setup(bot):
    bot.add_cog(HelpCog(bot))
