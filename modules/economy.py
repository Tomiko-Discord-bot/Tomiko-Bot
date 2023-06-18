import asyncio
import disnake
from disnake.ext import commands
from utils import database as db, i18n
import random


def frange(start=0, stop=1, jump=0.1):
    nsteps = int((stop-start)/jump)
    dy = stop-start
    return [start + float(i)*dy/nsteps for i in range(nsteps)]


class EconomyCog(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot
        self.casino = {}
        self.messages = {}

    @commands.slash_command(
        name=disnake.Localized(key="PROFILE"),
        description=disnake.Localized(key="PROFILE_DESCRIPTION")
    )
    async def profile(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        user = db.get_user(inter.author)
        locales = i18n.Init(inter)
        embed = disnake.Embed(
            title=f"{locales.get('PROFILE').capitalize()} — {inter.author.display_name.capitalize()}",
            colour=0x2b2d31
        )
        embed.description = user["icons"] + ("<:TomikoPro:1120020955863990282>" if await db.get_premium(
            self.bot, inter.author.id) else "")
        embed.set_thumbnail(url=inter.author.display_avatar.url)
        embed.set_image(url=user["banner"] if user["banner"] else None)
        status = user["status"] if user["status"] else locales.get("PROFILE_NONE")
        embed.add_field(
            name=f"<:edit:1117546025859682484> {locales.get('PROFILE_EDIT')}",
            value=f"```{status}```",
            inline=False
        )
        embed.add_field(
            name=f"<:dollar:1117546022856577084> {locales.get('PROFILE_MONEY')}",
            value=f"```{user['money']}```",
            inline=True
        )
        embed.add_field(
            name=f"<:fire:1117506834371182592> {locales.get('PROFILE_FIRE')}",
            value=f"```{user['fires']}```",
            inline=True
        )
        await inter.send(embed=embed, components=[
            disnake.ui.Button(
                label=locales.get("PROFILE_EXCHANGE_BTN"),
                custom_id="profile_exchange",
                style=disnake.ButtonStyle.green
            ),
            disnake.ui.Button(
                label=locales.get("PROFILE_UP_BTN"),
                custom_id="profile_up",
                style=disnake.ButtonStyle.blurple,
                disabled=True
            ),
            disnake.ui.Button(
                label=locales.get("PROFILE_EDIT_BTN"),
                custom_id="profile_edit",
                style=disnake.ButtonStyle.blurple
            )
        ])
        self.messages[(await inter.original_message()).id] = inter.author.id

    @commands.slash_command(
        name=disnake.Localized(key="REWARD"),
        description=disnake.Localized(key="REWARD_DESCRIPTION")
    )
    async def reward(self, inter: disnake.ApplicationCommandInteraction):
        t = db.get_timeout(inter.author, "reward")
        db.get_user(inter.author)
        locales = i18n.Init(inter)
        if t[0]:
            g = db.get_guild(inter.guild)
            reward = random.randint(g["min"], g["max"])
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

    @commands.slash_command(
        name=disnake.Localized(key="CASINO"),
        description=disnake.Localized(key="CASINO_DESCRIPTION")
    )
    async def casino(self, inter: disnake.ApplicationCommandInteraction, bet: int = commands.Param(
        name=disnake.Localized(key="BET"),
        description=disnake.Localized(key="BET_DESCR")
    )):
        locales = i18n.Init(inter)
        u = db.get_user(inter.author)
        if u["fires"] < bet or bet < 1:
            return await inter.send(embed=i18n.no_fires_emb(locales, inter.author))
        db.users.update_one({"gid": inter.guild.id, "id": inter.author.id}, {"$inc": {"fires": -bet}})
        chance = random.randint(1, 3)
        if chance <= 2:
            r = frange(1, 5, .1)
        else:
            r = frange(1, 10, .1)
        t = random.choice(r)
        embed = disnake.Embed(
            title=f"{locales.get('CASINO').capitalize()} — {inter.author.display_name.capitalize()}",
            colour=0x2b2d31,
            description=locales.get("CASINO_EMB_DESCR")
        )
        embed.set_thumbnail(url=inter.author.display_avatar.url)
        await inter.send(embed=embed, components=[disnake.ui.Button(label=locales.get("STOP"), custom_id="casino_stop")])
        self.casino[inter.author.id] = [inter.guild.id, True]
        self.messages[(await inter.original_message()).id] = inter.author.id
        for i in r:
            if self.casino[inter.author.id][0] == inter.guild.id and self.casino[inter.author.id][1]:
                embed.clear_fields()
                embed.add_field(
                    name=locales.get('CASINO_NAME'),
                    value=f"```{i}```"
                )
                if i == t:
                    embed.clear_fields()
                    embed.description = locales.get("CASINO_LOOSE")
                    embed.add_field(
                        name=locales.get("CASINO_LOOSE_NAME"),
                        value=f"```{bet}```"
                    )
                    embed.add_field(
                        name=locales.get("CASINO_COF"),
                        value=f"```{i}```"
                    )
                    await inter.edit_original_message(embed=embed, components=[])
                    break
                await inter.edit_original_message(embed=embed)
                await asyncio.sleep(1)
            else:
                db.users.update_one({"gid": inter.guild.id, "id": inter.author.id}, {"$inc": {"fires": round(bet*i)}})
                embed.clear_fields()
                embed.description = locales.get("CASINO_WIN_DESCR")
                embed.add_field(
                    name=locales.get("CASINO_WIN"),
                    value=f"```{round(bet*i)}```",
                    inline=False
                )
                embed.add_field(
                    name=locales.get("CASINO_COF"),
                    value=f"```{i}```"
                )
                embed.add_field(
                    name=locales.get("CASINO_PIC"),
                    value=f"```{t}```"
                )
                await inter.edit_original_message(components=[], embed=embed)
                break

    @commands.slash_command(
        name=disnake.Localized(key="PAY"),
        description=disnake.Localized(key="PAY_DESCRIPTION")
    )
    async def pay(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member = commands.Param(
        name=disnake.Localized(key="MEMBER"),
        description=disnake.Localized(key="MEMBER_DESCRIPTION")
    ), money: int = commands.Param(
        name=disnake.Localized(key="MONEY"),
        description=disnake.Localized(key="MONEY_DESCRIPTION")
    )):
        await inter.response.defer()
        u = db.get_user(inter.author)
        locales = i18n.Init(inter)
        if u["money"] < money or money < 1:
            return await inter.send(embed=i18n.no_money_emb(locales, inter.author))
        if member.bot:
            return
        db.users.update_one({"gid": inter.guild.id, "id": member.id}, {"$inc": {"money": money}})
        db.users.update_one({"gid": inter.guild.id, "id": inter.author.id}, {"$inc": {"money": -money}})
        embed = disnake.Embed(
            title=f"{locales.get('PAY').capitalize()} — {inter.author.display_name.capitalize()}",
            description=locales.get("PAY_EMB").replace("{dollars}", str(money)).replace("{member}", member.display_name.capitalize())
        )
        await inter.send(embed=embed)

    @commands.slash_command(
        name=disnake.Localized(key="MINES"),
        description=disnake.Localized(key="MINES_DESCRIPTION")
    )
    async def mines(self, inter: disnake.ApplicationCommandInteraction, bet: int = commands.Param(
        name=disnake.Localized(key="BET"),
        description=disnake.Localized(key="BET_DESCR")
    )):
        await inter.response.defer()
        u = db.get_user(inter.author)
        locales = i18n.Init(inter)
        if u["fires"] < bet or bet < 1:
            return await inter.send(embed=i18n.no_fires_emb(locales, inter.author))
        db.users.update_one({"gid": inter.guild.id, "id": inter.author.id}, {"$inc": {"fires": -bet}})
        boom = []

        def add():
            v = (random.randint(0, 2), random.randint(0, 2))
            if v not in boom:
                boom.append(v)
            else:
                return add()
        for _ in range(3):
            add()

        buttons = [
            [disnake.ui.Button(emoji="💣", custom_id=f"mine_{line}_{row}_{boom}_{bet}") for row in range(3)] for line in
            range(3)
        ]
        embed = disnake.Embed(
            title=f"{locales.get('MINES').capitalize()} — {inter.author.display_name.capitalize()}",
            colour=0x2b2d31,
            description=locales.get("MINES_EMB_DESCRIPTION")
        )
        embed.set_thumbnail(url=inter.author.display_avatar.url)
        await inter.send(embed=embed, components=buttons)
        self.messages[(await inter.original_message()).id] = inter.author.id

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        try:
            author = self.messages[inter.message.id]
        except KeyError:
            return
        if inter.author.id != author:
            return
        locales = i18n.Init(inter)
        if inter.component.custom_id == "casino_stop":
            self.casino[inter.author.id][1] = False
        elif inter.component.custom_id.startswith("mine"):
            await inter.response.defer()
            s = inter.component.custom_id.split("_")
            boom = eval(s[3])  # [(line, row) x3]
            pos = (int(s[1]), int(s[2]))  # line, row
            bet = s[4]
            buttons = []
            b = False
            checked = False

            def check():
                nonlocal b, checked
                for line in range(3):
                    buttons.append([])
                    for n, row in enumerate(inter.message.components[line].children, start=0):
                        custom_id = f"mine_{line}_{n}_{boom}_{bet}"
                        emoji = "💣"
                        disabled = True if custom_id == inter.component.custom_id else False
                        this_pos = (line, n)
                        if this_pos in boom and disabled:
                            emoji = "🔥"
                            b = True
                            if not checked:
                                checked = True
                                buttons.clear()
                                return check()
                        if b:
                            if this_pos in boom:
                                emoji = "🔥"
                            disabled = True
                        if row.disabled:
                            emoji = "💣"
                            disabled = True
                        buttons[line].append(disnake.ui.Button(
                            emoji=emoji,
                            custom_id=custom_id,
                            disabled=disabled
                        ))
            check()
            embed = inter.message.embeds[0]
            if b:
                embed.description = locales.get("MINES_LOST_EMB")
                embed.add_field(
                    name=f"> {locales.get('BET').capitalize()}:",
                    value=f"```{bet}```"
                )
            else:
                buttons.append([disnake.ui.Button(label=locales.get("STOP"), custom_id="m_stop")])

            await inter.edit_original_message(embed=embed, components=buttons)
        elif inter.component.custom_id == "m_stop":
            await inter.response.defer()
            x = 0
            buttons = []
            bet = 0
            for i in range(3):
                buttons.append([])
                for n, btn in enumerate(inter.message.components[i].children, start=0):
                    pos = (i, n)
                    boom = eval(btn.custom_id.split("_")[3])
                    bet = int(btn.custom_id.split("_")[4])
                    if pos in boom:
                        btn.emoji = "🔥"
                    if btn.disabled:
                        x += 1.3
                    btn.disabled = True
                    buttons[i].append(disnake.ui.Button.from_component(btn))
            embed = inter.message.embeds[0]
            embed.description = locales.get("MINES_WIN_EMB")
            embed.add_field(
                name=f"> {locales.get('MINES_WIN')}:",
                value=f"```{round(bet*x)}```",
                inline=False
            )
            embed.add_field(
                name=f"> {locales.get('BET').capitalize()}:",
                value=f"```{bet}```"
            )
            embed.add_field(
                name=locales.get('CASINO_COF'),
                value=f"```{x}```"
            )
            db.users.update_one({"gid": inter.guild.id, "id": inter.author.id}, {"$inc": {"fires": round(bet*x)}})
            await inter.edit_original_message(embed=embed, components=buttons)
        elif inter.component.custom_id == "profile_exchange":
            await inter.response.defer()
            g = db.get_guild(inter.guild)
            embed = inter.message.embeds[0]
            fields = embed.fields[1:]
            embed.clear_fields()
            embed.add_field(
                name=f"<:information:1117477318890369074> {locales.get(key='COST')}",
                value=f"```{g['cost']}$ = 1🔥```",
                inline=False
            )
            for f in fields:
                embed.add_field(
                    name=f.name,
                    value=f.value,
                    inline=f.inline
                )
            await inter.edit_original_message(embed=embed, components=[
                disnake.ui.Button(label=locales.get("MONEY_TO_FIRES"), custom_id="money_to_fires",
                                  style=disnake.ButtonStyle.blurple),
                disnake.ui.Button(label=locales.get("FIRES_TO_MONEY"), custom_id="fires_to_money",
                                  style=disnake.ButtonStyle.blurple),
                disnake.ui.Button(label=locales.get("RETURN"), custom_id="return_profile",
                                  style=disnake.ButtonStyle.red),
            ])
        elif inter.component.custom_id == "money_to_fires":
            await inter.response.send_modal(disnake.ui.Modal(
                title=locales.get("MONEY_TO_FIRES"),
                custom_id="money_to_fires",
                components=[disnake.ui.TextInput(
                    label=locales.get("HOW_MANY_FIRES"),
                    max_length=9,
                    custom_id="fires"
                )]
            ))
        elif inter.component.custom_id == "fires_to_money":
            await inter.response.send_modal(disnake.ui.Modal(
                title=locales.get("FIRES_TO_MONEY"),
                custom_id="fires_to_money",
                components=[disnake.ui.TextInput(
                    label=locales.get("HOW_MANY_FIRES"),
                    max_length=9,
                    custom_id="fires"
                )]
            ))
        elif inter.component.custom_id == "return_profile":
            await inter.response.defer()
            u = db.get_user(inter.author)
            embed = disnake.Embed(
                title=f"{locales.get('PROFILE').capitalize()} — {inter.author.display_name.capitalize()}",
                colour=0x2b2d31
            )
            embed.description = u["icons"] + ("<:TomikoPro:1120020955863990282>" if await db.get_premium(
                self.bot, inter.author.id) else "")
            embed.set_thumbnail(url=inter.author.display_avatar.url)
            embed.set_image(url=u["banner"] if u["banner"] else None)
            status = u["status"] if u["status"] else locales.get("PROFILE_NONE")
            embed.add_field(
                name=f"<:edit:1117546025859682484> {locales.get('PROFILE_EDIT')}",
                value=f"```{status}```",
                inline=False
            )
            embed.add_field(
                name=f"<:dollar:1117546022856577084> {locales.get('PROFILE_MONEY')}",
                value=f"```{u['money']}```",
                inline=True
            )
            embed.add_field(
                name=f"<:fire:1117506834371182592> {locales.get('PROFILE_FIRE')}",
                value=f"```{u['fires']}```",
                inline=True
            )
            await inter.edit_original_message(embed=embed, components=[
                disnake.ui.Button(
                    label=locales.get("PROFILE_EXCHANGE_BTN"),
                    custom_id="profile_exchange",
                    style=disnake.ButtonStyle.green
                ),
                disnake.ui.Button(
                    label=locales.get("PROFILE_UP_BTN"),
                    custom_id="profile_up",
                    style=disnake.ButtonStyle.blurple,
                    disabled=True
                ),
                disnake.ui.Button(
                    label=locales.get("PROFILE_EDIT_BTN"),
                    custom_id="profile_edit",
                    style=disnake.ButtonStyle.blurple
                )
            ])
        elif inter.component.custom_id == "profile_edit":
            await inter.response.defer(ephemeral=True)
            await inter.edit_original_message(components=[
                disnake.ui.Button(
                    label=locales.get("EDIT_DESCRIPTION"),
                    custom_id="edit_descr",
                    style=disnake.ButtonStyle.blurple
                ),
                disnake.ui.Button(
                    label=locales.get("EDIT_BANNER"),
                    custom_id="edit_banner",
                    style=disnake.ButtonStyle.blurple
                ),
                disnake.ui.Button(
                    label=locales.get("RETURN"),
                    custom_id="return_profile",
                    style=disnake.ButtonStyle.red
                )
            ])
        elif inter.component.custom_id == "edit_descr":
            await inter.response.send_modal(disnake.ui.Modal(
                title=locales.get("EDIT_DESCRIPTION"),
                custom_id="edit_descr",
                components=[
                    disnake.ui.TextInput(
                        label=locales.get("EDIT_DESCRIPTION") + ":",
                        custom_id="edit_descr"
                    )
                ]
            ))
        elif inter.component.custom_id == "edit_banner":
            await inter.response.send_modal(disnake.ui.Modal(
                title=locales.get("EDIT_BANNER"),
                custom_id="edit_banner",
                components=[
                    disnake.ui.TextInput(
                        label=locales.get("EDIT_BANNER") + ":",
                        custom_id="edit_banner"
                    )
                ]
            ))

    @commands.Cog.listener()
    async def on_modal_submit(self, inter: disnake.ModalInteraction):
        try:
            author = self.messages[inter.message.id]
        except KeyError:
            return
        if inter.author.id != author:
            return
        locales = i18n.Init(inter)
        s = inter.custom_id.split("_")
        if "to" in s:
            await inter.response.defer(ephemeral=True)
            try:
                fires = int(inter.text_values["fires"])
            except ValueError:
                return await inter.send(f"{inter.text_values['fires']} не число!", ephemeral=True)
            u = db.get_user(inter.author)
            g = db.get_guild(inter.guild)
            cost = int(g["cost"])
            if inter.custom_id == "money_to_fires":
                if int(fires * cost) > int(u["money"]) or fires < 1:
                    return await inter.send(embed=i18n.no_money_emb(locales, inter.author), ephemeral=True)
                embed = inter.message.embeds[0].to_dict()
                embed["fields"][1]["value"] = f"```{u['money']-(fires*cost)}```"
                embed["fields"][2]["value"] = f"```{u['fires']+fires}```"
                db.users.update_one({"gid": inter.guild.id, "id": inter.author.id},
                                    {"$inc": {"money": -(int(fires*cost)), "fires": fires}})
                await inter.message.edit(embed=disnake.Embed().from_dict(embed))
            elif inter.custom_id == "fires_to_money":
                if int(u["fires"]) < int(fires) or fires < 1:
                    return await inter.send(embed=i18n.no_fires_emb(locales, inter.author), ephemeral=True)
                embed = inter.message.embeds[0].to_dict()
                embed["fields"][1]["value"] = f"```{u['money']+round(fires*cost)}```"
                embed["fields"][2]["value"] = f"```{u['fires']-fires}```"
                db.users.update_one({"gid": inter.guild.id, "id": inter.author.id},
                                    {"$inc": {"money": round(fires*cost), "fires": -fires}})
                await inter.message.edit(embed=disnake.Embed().from_dict(embed))
            await inter.delete_original_response()
        if "edit" in s:
            await inter.response.defer(ephemeral=True)
            if s[1] == "descr":
                embed = inter.message.embeds[0].to_dict()
                fields = embed["fields"]
                fields[0]["value"] = f"```{inter.text_values['edit_descr'][:1000]}```"
                db.users.update_one({"id": inter.author.id, "gid": inter.guild.id},
                                    {"$set": {"status": inter.text_values['edit_descr'][:1000]}})
                await inter.message.edit(embed=disnake.Embed().from_dict(embed))
            elif s[1] == "banner":
                embed = inter.message.embeds[0]
                try:
                    embed.set_image(url=inter.text_values['edit_banner'])
                except (Exception,):
                    return await inter.send(embed=i18n.error_emb(locales, inter.author))
                db.users.update_one({"id": inter.author.id, "gid": inter.guild.id},
                                    {"$set": {"banner": inter.text_values['edit_banner']}})
                await inter.message.edit(embed=disnake.Embed().from_dict(embed.to_dict()))
            await inter.delete_original_response()


def setup(bot):
    bot.add_cog(EconomyCog(bot))
