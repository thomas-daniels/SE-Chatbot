import re

def replace_deco(func, bot):
    def replace_paras(*args, **kwargs):
        replace_dict = {
            "$PREFIX": bot.prefix,
            "$OWNER_NAME": bot.owner_name,
            "$BOT_NAME": bot.chatbot_name
        }
        
        regex = re.compile("(%s)" % "|".join(map(re.escape, replace_dict.keys())))        
        return regex.sub(lambda mo: replace_dict[mo.string[mo.start():mo.end()]], func(*args, **kwargs))
    return replace_paras

def on_bot_load(bot):
    bot.command = replace_deco(bot.command, bot)

commands = [ ]
