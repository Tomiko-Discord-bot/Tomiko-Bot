import disnake
from disnake.ext import commands
from utils import database as db, i18n


class GeneralCog(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.slash_command(
        name=disnake.Localized(key="SETTINGS"),
        description=disnake.Localized(key="SETTINGS_DESCRIPTION"),
        default_member_permissions=disnake.Permissions(administrator=True)
    )
    async def settings(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        g = db.get_guild(inter.guild)
        locales = i18n.Init(inter)
        embed = disnake.Embed(
            title=locales.get("SETTINGS").capitalize(),
            colour=0x2b2d31
        )
        embed.add_field(
            name=locales.get("SETTINGS_STARTBAL"),
            value=f"```{g['start_balance']}```",
            inline=False
        )
        embed.add_field(
            name=locales.get("SETTINGS_COST"),
            value=f"```{g['cost']}```"
        )
        embed.add_field(
            name=locales.get("SETTINGS_MIN"),
            value=f"```{g['reward'][0]}```"
        )
        embed.add_field(
            name=locales.get("SETTINGS_MAX"),
            value=f"```{g['reward'][1]}```"
        )
        embed.add_field(
            name=locales.get("SETTINGS_REWARD_TIMEOUT"),
            value=f"```{g['timeout_reward']}```"
        )
        select = disnake.ui.Select(custom_id="settings")
        select.add_option(
            label=locales.get("SETTINGS_STARTBAL_BTN"),
            description=locales.get("SETTINGS_STARTBAL_DESCR"),
            value="startbal",
            emoji="<:arrow:1117858180249178245>"
        )
        select.add_option(
            label=locales.get("SETTINGS_COST_BTN"),
            description=locales.get("SETTINGS_COST_DESCR"),
            value="cost",
            emoji="<:arrow:1117858180249178245>"
        )
        select.add_option(
            label=locales.get("SETTINGS_MIN_BTN"),
            description=locales.get("SETTINGS_MIN_DESCR"),
            value="min",
            emoji="<:arrow:1117858180249178245>"
        )
        select.add_option(
            label=locales.get("SETTINGS_MAX_BTN"),
            description=locales.get("SETTINGS_MAX_DESCR"),
            value="max",
            emoji="<:arrow:1117858180249178245>"
        )
        select.add_option(
            label=locales.get("SETTINGS_TIMEOUT_BTN"),
            description=locales.get("SETTINGS_TIMEOUT_DESCR"),
            value="timeout",
            emoji="<:arrow:1117858180249178245>"
        )
        embed.set_thumbnail(url=inter.author.display_avatar.url)
        await inter.send(embed=embed, components=[select])


def setup(bot):
    bot.add_cog(GeneralCog(bot))
