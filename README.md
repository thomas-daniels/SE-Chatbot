# SE-Chatbot, a chat bot for the Stack Exchange chat rooms. #

A chat bot for the Stack Exchange chat rooms.

The bot is licensed under [CPOL (The Code Project Open License) v1.02](http://www.codeproject.com/info/cpol10.aspx). You can find a copy of this license in `LICENSE.htm`.

### Setup ###

Before you can use the bot, you need to install some dependencies such as [ChatExchange3](https://github.com/ByteCommander/ChatExchange3) (the Python 3 port of [ChatExchange](https://github.com/Manishearth/ChatExchange) and BeautifulSoup4. You can install them by running `setup.sh` on Linux (requires `pip` to be installed) or `setup.bat` (requires `git` and `pip`, in `C:\<YourPythonFolder>\Scripts\` to be added to your PATH).

You'll also need to copy `templates/ConfigTemplate.py` to `Config.py`. You will also need to add some required configuration data in `Config.py`. The comments in that file tell you which values you can add and how to add them.

### Running ###
To run the bot, you have to use Python 3. When you run it, it will prompt you for necessary information that you have not provided in Config.py. If you wish to use a specific configuration, run the bot with the argument `-c configuration_name`. You can also use `-s site_name`, `-r room_number`, `-e email_address` and `-p password`. The last four items will always override data stored in a configuration, if set.

### Logging ###

You can use logging on the bot. It is disabled by default, but you can enable it by un-commenting the `self.setup_logging()` line in `Chatbot.py` (in the `main` method).

### Executing commands/posting messages using the command line ###

You can execute commands from the bot by providing input on the command line. `$+command args` will execute the command and post the result to the chat room, and `$-command args` will only post the result to the command line. If your input does not start with a `$`, the bot will post the given input to the chat room.

### Commands in a chat room ###

Commands in a chat room are executed like `>>command optional arguments`. To get a list of all commands, run `>>listcommands`. To get help on a specific command, run `>>help command`.

### Modules ###

You can extend the bot by adding your own modules, which you can group into meta-modules. See the templates in the templates/ folder for help on how to create a module.
