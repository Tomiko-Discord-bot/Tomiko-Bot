import disnake
from disnake.ext import commands
from utils import database as db


class DevCog(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.slash_command(hidden=True, guild_ids=[1101154269509451847])
    async def icon(self, inter, user: disnake.User, icon: str):
        if inter.author.id != 1101103184577048688:
            return
        icons = db.icons.find_one({"id": user.id})["icons"]
        db.icons.update_one({"id": user.id}, {"$set": {"icons": icons + f" {icon}"}})
        await inter.send(f"Выдано {icon} челику {user.display_name}")

    @commands.slash_command(hidden=True, guild_ids=[1101154269509451847])
    async def create_info(self, inter):
        if inter.author.id != 1101103184577048688:
            return
        db.info.insert_one({"Tomiko": "best", "commands_used": 0})
        await inter.send("✅")

    @commands.slash_command(hidden=True, guild_ids=[1101154269509451847])
    async def update(self, inter, collection: str, values: str):
        if inter.author.id != 1101103184577048688:
            return
        await db.cluster[collection].update_many({}, {"$set": dict(values)})
        await inter.send("✅")


def setup(bot):
    bot.add_cog(DevCog(bot))
