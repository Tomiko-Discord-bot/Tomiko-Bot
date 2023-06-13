from disnake.ext import commands

bot = commands.InteractionBot()
bot.i18n.load("data/locales/")
bot.load_extensions("modules")

bot.run(open("data/token").read())
