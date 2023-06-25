import disnake
import pymongo
from datetime import datetime as dt, timedelta

from disnake.ext import commands

db = pymongo.MongoClient("mongodb+srv://root:root@hitomi.v3rqm.mongodb.net/?retryWrites=true&w=majority")
cluster = db["Tomiko"]
guilds = cluster["settings"]
users = cluster["users"]
cooldown = cluster["cooldown"]
info = cluster["info"]
icons = cluster["icons"]
beta = [0]
beta_test = True


def get_user(entry: disnake.Message | disnake.Member) -> dict:
    if isinstance(entry, disnake.Message):
        member = entry.author
        guild = entry.guild
    else:
        member = entry
        guild = entry.guild
    guild: disnake.Guild
    member: disnake.Member

    g = get_guild(entry.guild)
    item = users.find_one({"gid": guild.id, "id": member.id})
    icon = icons.find_one({"id": member.id})
    if not icon:
        icon = {"id": member.id, "icons": "<:be:1119317469077717092><:ta:1119317471929839696>" if beta_test else ""}
        icons.insert_one(icon)
    if not item:
        item = {
            "gid": guild.id,
            "id": member.id,
            "status": "",
            "money": g['startbal'],
            "fires": 0,
            "banner": ""
        }
        users.insert_one(item)
    item["icons"] = icon["icons"]
    return item


def get_guild(guild: disnake.Guild) -> dict:
    item = guilds.find_one({"gid": guild.id})
    if not item:
        item = {
            "gid": guild.id,
            "startbal": 250,
            "min": 100,
            "max": 500,
            "timeout_reward": 2,  # hours
            "cost": 25,
            "timeout_timely": 1
        }
        guilds.insert_one(item)
    return item


def get_timeout(user: disnake.Member, cmd: str) -> tuple[bool, int] | tuple[bool, dt]:
    now = dt.now()
    c = cooldown.find_one({"gid": user.guild.id, "id": user.id, "cmd": cmd})
    if not c:
        cooldown.insert_one({"gid": user.guild.id, "id": user.id, "cmd": cmd, "c": now})
        return True, 0
    g = get_guild(user.guild)
    to = g[f"timeout_{cmd}"] * 60 * 60  # hours
    if (now - c["c"]).total_seconds() < to:
        return False, dt.now() + timedelta(seconds=to - (now - c["c"]).total_seconds())
    cooldown.update_one({"gid": user.guild.id, "id": user.id, "cmd": cmd}, {"$set": {"c": now}})
    return True, 0


async def get_premium(bot: commands.InteractionBot, user: int):
    g = await bot.fetch_guild(1117477749771210754)
    try:
        u = await g.fetch_member(user)
    except (Exception,):
        return False
    r = disnake.utils.get(await g.fetch_roles(), id=1119300923899003033)
    if u:
        if r in u.roles:
            return True
    return False
