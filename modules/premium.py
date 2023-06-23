import disnake
from disnake.ext import commands
from utils import database as db, i18n
import random


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
        locales = i18n.Init(inter)
        if not await db.get_premium(self.bot, inter.author.id):
            return await inter.send(locales.get("NO_PREMIUM"))
        t = db.get_timeout(inter.author, "timely")
        if t[0]:
            g = db.get_guild(inter.guild)
            reward = random.randint(g["min"], g["max"]*3)
            embed = disnake.Embed(
                title=f"{locales.get('REWARD').capitalize()} — {inter.author.display_name.capitalize()}",
                colour=0x2b2d31
            )
            embed.add_field(
                name=f"> {locales.get('REWARD_FIELD_NAME')}",
                value=f"{locales.get('REWARD_FIELD_VALUE')} **{reward}** <:dollar:1117546022856577084>"
            )
            embed.set_thumbnail(url=inter.author.display_avatar.url)
            db.users.update_one({"gid": inter.guild.id, "id": inter.author.id}, {"$inc": {"money": reward}})
            await inter.send(embed=embed)
        else:
            await inter.send(embed=i18n.timeout_emb(locales, t[1], inter.author))


def setup(bot):
    bot.add_cog(PremiumCog(bot))
