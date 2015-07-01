from Module import Command
from datetime import datetime
from CommandHelp import CommandHelp


def command_alive(cmd, bot, args, msg, event):
    return "Yes, I'm alive."


def command_utc(cmd, bot, args, msg, event):
    return datetime.utcnow().ctime()


def command_listcommands(cmd, bot, args, msg, event):
    command_keys = bot.commands.keys()
    if bot.in_shadows_den:
        command_keys += bot.shadows_den_specific_commands.keys()
    module_commands = bot.modules.list_commands()
    for mod_cmd in module_commands:
        command_keys.append(mod_cmd.name)
    command_keys.sort()
    return "Commands: %s" % (", ".join(command_keys),)


def command_help(cmd, bot, args, msg, event):
    if len(args) == 0:
        return "I'm %s, %s's chatbot. You can find the source code [on GitHub](https://github.com/ProgramFOX/SE-Chatbot). You can get a list of all commands by running `>>listcommands`, or you can run `>>help command` to learn more about a specific command." % (bot.chatbot_name, bot.owner_name)
    command_to_look_up = args[0]
    if command_to_look_up in CommandHelp:
        return CommandHelp[command_to_look_up]
    elif command_to_look_up in bot.commands or command_to_look_up in bot.shadows_den_specific_commands or \
            command_to_look_up in bot.owner_commands or command_to_look_up in bot.privileged_commands:
        return "Command exists, but no help entry found."
    else:
        return "The command you want to look up, does not exist."

commands = [Command('alive', command_alive, "", False, False),
            Command('utc', command_utc, "", False, False),
            Command('listcommands', command_listcommands, "", False, False),
            Command('help', command_help, "", False, False)]