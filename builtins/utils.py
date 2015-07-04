from Module import Command
from datetime import datetime
import re


def command_alive(cmd, bot, args, msg, event):
    return "Yes, I'm alive."


def command_utc(cmd, bot, args, msg, event):
    return datetime.utcnow().ctime()


def command_listcommands(cmd, bot, args, msg, event):
    return "Commands: %s" % (', '.join([command.name for command in bot.modules.list_commands()]))


def command_help(cmd, bot, args, msg, event):
    if len(args) == 0:
        return "I'm $BOT_NAME, $OWNER_NAME's chatbot. You can find the source code [on GitHub](https://github.com/ProgramFOX/SE-Chatbot). You can get a list of all commands by running `$PREFIXlistcommands`, or you can run `$PREFIXhelp command` to learn more about a specific command."
    else:
        return bot.modules.get_help(args[0]) or "The command you want to look up, does not exist."

commands = [Command('alive', command_alive, "A command to see whether the bot is there. Syntax: `$PREFIXalive`", False, False),
            Command('utc', command_utc, "Shows the current UTC time. Syntax: `$PREFIXutc`", False, False),
            Command('listcommands', command_listcommands, "Returns a list of all commands. Syntax: `$PREFIXlistcommands`", False, False),
            Command('help', command_help, "Shows information about the chat bot, or about a specific command. Syntax: `$PREFIXhelp [ command ]`", False, False)]
