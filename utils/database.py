from typing import Tuple, Any

import disnake
import pymongo
from datetime import datetime as dt, datetime, timedelta

db = pymongo.MongoClient()
cluster = db["cluster_7"]
guilds = cluster["settings"]
users = cluster["users"]
cooldown = cluster["cooldown"]


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
    if not item:
        item = {
            "gid": guild.id,
            "id": member.id,
            "status": "",
            "money": g['start_balance'],
            "fires": 0,
            "banner": ""
        }
        users.insert_one(item)
    return item


def get_guild(guild: disnake.Guild) -> dict:
    item = guilds.find_one({"gid": guild.id})
    if not item:
        item = {
            "gid": guild.id,
            "start_balance": 250,
            "reward": [100, 500],
            "timeout_reward": 2,  # hours
            "cost": 25
        }
        guilds.insert_one(item)
    return item


def get_timeout(user: disnake.Member, cmd: str) -> tuple[bool, int] | tuple[bool, timedelta]:
    now = dt.now()
    c = cooldown.find_one({"gid": user.guild.id, "id": user.id, "cmd": cmd})
    if not c:
        cooldown.insert_one({"gid": user.guild.id, "id": user.id, "cmd": cmd, "c": now})
        return True, 0
    g = get_guild(user.guild)
    to = g[f"timeout_{cmd}"] * 60 * 60  # hours
    if (now - c["c"]).total_seconds() < to:
        return False, timedelta(seconds=to - (now - c["c"]).total_seconds())
    cooldown.update_one({"gid": user.guild.id, "id": user.id, "cmd": cmd}, {"$set": {"c": now}})
    return True, 0
