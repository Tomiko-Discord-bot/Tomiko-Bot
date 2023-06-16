import disnake
from disnake.ext import commands
from utils import database as db, i18n


class GeneralCog(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot
        self.messages = {}

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
            value=f"```{g['startbal']}```",
            inline=False
        )
        embed.add_field(
            name=locales.get("SETTINGS_COST"),
            value=f"```{g['cost']}```"
        )
        embed.add_field(
            name=locales.get("SETTINGS_MIN"),
            value=f"```{g['min']}```"
        )
        embed.add_field(
            name=locales.get("SETTINGS_MAX"),
            value=f"```{g['max']}```"
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
            value="timeout_reward",
            emoji="<:arrow:1117858180249178245>"
        )
        embed.set_thumbnail(url=inter.author.display_avatar.url)
        self.messages[(await inter.original_message()).id] = inter.author.id
        await inter.send(embed=embed, components=[select])

    @commands.Cog.listener()
    async def on_dropdown(self, inter: disnake.MessageInteraction):
        u = await inter.guild.fetch_member(inter.author.id)
        if not u.guild_permissions.administrator:
            return
        if inter.component.custom_id == "settings":
            locales = i18n.Init(inter)
            await inter.response.send_modal(disnake.ui.Modal(
                custom_id=inter.data.custom_id,
                title=locales.get(f"SETTINGS_{inter.values[0].upper()}_BTN"),
                components=[
                    disnake.ui.TextInput(
                        label=locales.get(f"SETTINGS_{inter.values[0].upper()}_BTN") + ":",
                        custom_id=inter.values[0]
                    )
                ]
            ))

    @commands.Cog.listener()
    async def on_modal_submit(self, inter: disnake.ModalInteraction):
        if inter.custom_id == "settings":
            await inter.response.defer(ephemeral=True)
            component = inter.data.components[0]["components"][0]
            try:
                value = int(component["value"])
            except ValueError:
                return await inter.send(f"{component['value']} - не число!")
            custom_id = component["custom_id"]
            embed = inter.message.embeds[0].to_dict()
            fields = embed["fields"]
            values = {
                "startbal": 0,
                "cost": 1,
                "min": 2,
                "max": 3,
                "timeout_reward": 4
            }
            fields[values[custom_id]]["value"] = f"```{value}```"
            db.guilds.update_one({"gid": inter.guild.id}, {"$set": {custom_id: value}})
            await inter.message.edit(embed=disnake.Embed().from_dict(embed))
            await inter.delete_original_response()


def setup(bot):
    bot.add_cog(GeneralCog(bot))
