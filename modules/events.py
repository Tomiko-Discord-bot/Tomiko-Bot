import disnake
from disnake.ext import commands, tasks
from data import params
from utils import database as db
from utils.time import get_time
from datetime import datetime as dt


class EventsCog(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot
        self.t = round(dt.now().timestamp())

    @commands.Cog.listener()
    async def on_connect(self):
        print(f"[{get_time()}] Connected")
        self.print_ping.start()
        self.info_loop.start()

    @tasks.loop(seconds=60)
    async def print_ping(self):
        text = f"Guilds: {len(self.bot.guilds)} Ping: {round(self.bot.latency*1000, 2)}ms"
        print(f"[{get_time()}] {text}")
        await self.bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.listening, name=text))

    @tasks.loop(seconds=60)
    async def info_loop(self):
        channel = await self.bot.fetch_channel(1117480245075906601)
        msg = await channel.fetch_message(1118254885234802749)
        i = db.info.find_one({"Tomiko": "best"})
        embed = disnake.Embed(
            title="Статус — Tomiko",
            colour=0x2b2d31
        )
        embed.description = f"""**Запущен:** <t:{self.t}:R>
**Пинг:** {round(self.bot.latency*1000, 2)}ms
**Серверов:** {len(self.bot.guilds)}
**Использовано команд:** {i['commands_used']}
        """
        embed.set_footer(text="Обновляется каждые 60 секунд.")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await msg.edit(embed=embed, components=[
            disnake.ui.Button(label="Top.gg", emoji="<:topgg:1118253569594900610>", url="https://top.gg/", disabled=True),
            disnake.ui.Button(label="Server-discord.com", emoji="<:sdc:1118253567673896960>", url="https://bots.server-discord.com/", disabled=True),
            disnake.ui.Button(label="Boticord.top", emoji="<:boticord:1118253563911622699>", url="https://boticord.top/", disabled=True),
        ])

    @commands.Cog.listener()
    async def on_application_command(self, inter: disnake.ApplicationCommandInteraction):
        db.info.update_one({"Tomiko": "best"}, {"$inc": {"commands_used": 1}})

    @commands.Cog.listener()
    async def on_guild_join(self, guild: disnake.Guild):
        db.get_guild(guild)
        # Уведомление о новом сервере
        my_guild = await self.bot.fetch_guild(params.MY_GUILD)
        my_channel = await my_guild.fetch_channel(params.NEW_GUILD_CHANNEL)
        embed = disnake.Embed(title=f"New guild - {guild.name}", colour=0x2b2d31)
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.description = f"Members: {guild.member_count}"
        invite = None
        for channel in guild.text_channels:
            try:
                invite = (await channel.create_invite()).url
                break
            except (Exception,):
                pass
        await my_channel.send(embed=embed, components=[disnake.ui.Button(url=invite, label="Join")] if invite else None)

        # Приветственное сообщение
        try:
            msg = self.bot.i18n.get("WELCOME")[str(guild.preferred_locale)].replace("{BOTVER}", str(params.BOT_VERSION))
        except KeyError:
            msg = self.bot.i18n.get("WELCOME")["en-US"].replace("{BOTVER}", str(params.BOT_VERSION))
        embed = disnake.Embed(title="Tomiko.", description=msg, colour=0x2b2d31)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        sent = 0
        for channel in guild.text_channels:
            try:
                await channel.send(embed=embed)
                sent = 1
                break
            except (Exception,):
                pass
        if not sent:
            await (await guild.fetch_member(guild.owner_id)).send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, msg: disnake.Message):
        # Занесение участника в базу данных
        if not msg.author.bot:
            db.get_user(msg)

    @commands.Cog.listener()
    async def on_slash_command_error(
            self,
            inter: disnake.ApplicationCommandInteraction,
            exception: disnake.InteractionException
    ):
        await inter.send(str(exception))


def setup(bot):
    bot.add_cog(EventsCog(bot))
