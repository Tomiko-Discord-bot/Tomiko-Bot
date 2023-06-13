import disnake


class Init:
    def __init__(self, inter):
        self.inter = inter
        try:
            _ = inter.bot.i18n.get("WELCOME")[str(inter.locale)]
            self.locale = str(inter.locale)
        except KeyError:
            self.locale = "en-US"

    def get(self, key):
        return self.inter.bot.i18n.get(key)[self.locale]


def timeout_emb(localisation: Init, time, member: disnake.Member) -> disnake.Embed:
    embed = disnake.Embed(
        title=f"{localisation.get('TIMEOUT_TITLE')}",
        description=f"{localisation.get('TIMEOUT_DESCRIPTION')} {str(time).split('.')[0]}",
        colour=0x2b2d31
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    return embed


def no_fires_emb(localisation: Init, member: disnake.Member) -> disnake.Embed:
    embed = disnake.Embed(
        title=f"{localisation.get('ERROR')}",
        description=f"{localisation.get('NO_MONEY')}",
        colour=disnake.Colour.red()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    return embed
