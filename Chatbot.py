import getpass
import re
from HTMLParser import HTMLParser
import logging.handlers
import sys

from ChatExchange.chatexchange.client import Client
from ChatExchange.chatexchange.browser import LoginError
from ChatExchange.chatexchange.events import MessagePosted
from fixedfont import fixed_font_to_normal, is_fixed_font
from Config import Config
import ModuleManifest
from Module import MetaModule
from ConsoleCommandHandler import ConsoleCommandHandler
import SaveIO


class Chatbot:
    def __init__(self):
        self.room = None
        self.client = None
        self.privileged_users = []
        self.owners = []
        self.owner_name = ""
        self.chatbot_name = ""
        self.enabled = True
        self.running = True
        self.site = ""
        self.owner_ids = []
        self.privileged_user_ids = []
        self.save_subdirs = [ 'main' ]
        self.modules = MetaModule(ModuleManifest.module_file_names, self)
        SaveIO._set_subdirs(self.save_subdirs)
        SaveIO._create_if_not_exists(SaveIO.data_dir)
        del self.save_subdirs
        duplicates = self.get_duplicate_commands()
        if duplicates:
            print 'WARNING: there are commands with the same name: ' + str(duplicates)

    def main(self, config_data, additional_general_config):
        if "owners" in Config.General:
            self.owners = Config.General["owners"]
        else:
            sys.exit("Error: no owners found. Please update Config.py.")
        if "privileged_users" in config_data:
            self.privileged_users = config_data["privileged_users"]
        if "owner_name" in Config.General:
            self.owner_name = Config.General["owner_name"]
        else:
            sys.exit("Error: no owner name found. Please update Config.py.")
        if "chatbot_name" in Config.General:
            self.chatbot_name = Config.General["chatbot_name"]
        else:
            sys.exit("Error: no chatbot name found. Please update Config.py.")
        # self.setup_logging() # if you want to have logging, un-comment this line
        
        if "site" in config_data:
            self.site = config_data["site"]
            print("Site: %s" % self.site)
        else:
            self.site = raw_input("Site: ")
        for o in self.owners:
            if self.site in o:
                self.owner_ids.append(o[self.site])
        if len(self.owner_ids) < 1:
            sys.exit("Error: no owners found for this site: %s." % self.site)
        for p in self.privileged_users:
            if self.site in p:
                self.privileged_user_ids.append(p[self.site])
        if "room" in config_data:
            room_number = config_data["room"]
            print("Room number: %i" % room_number)
        else:
            room_number = int(raw_input("Room number: "))
        if "prefix" in config_data:
            self.prefix = config_data["prefix"]
        else:
            self.prefix = '>>'
        print("Prefix: %s" % self.prefix)
        if "email" in Config.General:
            email = Config.General["email"]
        elif "email" in additional_general_config:
            email = additional_general_config["email"]
        else:
            email = raw_input("Email address: ")
        
        self.client = Client(self.site)
        
        try:    
            if "password" in Config.General:  # I would not recommend to store the password in Config.py
                password = Config.General["password"]
                self.client.login(email, password)
            elif "password" in additional_general_config:
                password = additional_general_config["password"]
                self.client.login(email, password)
            else:
                for attempts in range(3):
                    try:
                        password = getpass.getpass("Password: ")
                        self.client.login(email, password)
                        break
                    except LoginError:
                        if attempts < 2:
                            print "Incorrect password."
                        else:
                            raise
        except LoginError:
            sys.exit("Incorrect password, shutting down.")

        self.room = self.client.get_room(room_number)
        self.room.join()
        bot_message = "Bot started."
        self.room.send_message(bot_message)

        on_loads = self.modules.get_on_load_methods()
        for on_load in on_loads:
            on_load(self)
            
        self.room.watch_socket(self.on_event)

        while self.running:
            inputted = raw_input("<< ")
            if inputted.strip() == "":
                continue
            if inputted.startswith("$") and len(inputted) > 2:
                command_in = inputted[2:]
                cmd_handler = ConsoleCommandHandler(self, inputted[1] == "+")
                command_out = self.command(command_in, cmd_handler, None)
                if command_out is not False and command_out is not None:
                    cmd_handler.reply(command_out)
            else:
                self.room.send_message(inputted)

    def get_duplicate_commands(self):
        checked_cmds = []
        dupe_cmds = []
        all_cmds = self.modules.list_commands()
        for command in all_cmds:
            if command.name not in checked_cmds:
                checked_cmds.append(command.name)
            else:
                if command.name not in dupe_cmds:
                    dupe_cmds.append(command.name)
        return dupe_cmds

    def setup_logging(self):  # logging method taken from ChatExchange/examples/chat.py
        logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        logger.setLevel(logging.DEBUG)

        # In addition to the basic stderr logging configured globally
        # above, we'll use a log file for chatexchange.client.
        wrapper_logger = logging.getLogger('chatexchange.client')
        wrapper_handler = logging.handlers.TimedRotatingFileHandler(
            filename='client.log',
            when='midnight', delay=True, utc=True, backupCount=7,
        )
        wrapper_handler.setFormatter(logging.Formatter(
            "%(asctime)s: %(levelname)s: %(threadName)s: %(message)s"
        ))
        wrapper_logger.addHandler(wrapper_handler)

    def requires_char_check(self, cmd_name):
        cmd_list = self.modules.list_commands()
        for cmd in cmd_list:
            if cmd.name == cmd_name:
                return cmd.char_check
        return True

    def requires_special_arg_parsing(self, cmd_name):
        cmd_list = self.modules.list_commands()
        for cmd in cmd_list:
            if cmd.name == cmd_name:
                return cmd.special_arg_parsing is not None
        return False

    def do_special_arg_parsing(self, cmd_name, full_cmd):
        cmd_list = self.modules.list_commands()
        for cmd in cmd_list:
            if cmd.name == cmd_name and cmd.special_arg_parsing is not None:
                return cmd.special_arg_parsing(full_cmd)
        return False

    def on_event(self, event, client):
        watchers = self.modules.get_event_watchers()
        for w in watchers:
            w(event, client, self)
        should_return = False
        if not self.enabled:
            should_return = True
        if isinstance(event, MessagePosted) and (not self.enabled) and event.user.id in self.owner_ids and event.message.content.startswith("&gt;&gt;"):
            should_return = False
        if not self.running:
            should_return = True
        if not isinstance(event, MessagePosted):
            should_return = True
        if should_return:
            return

        message = event.message
        h = HTMLParser()
        content = h.unescape(message.content_source)

        if event.user.id == self.client.get_me().id:
            return

        fixed_font = is_fixed_font(content)
        if fixed_font:
            fixed_font = True
            content = fixed_font_to_normal(content)
        content = re.sub(r"^%s\s+" % self.prefix, self.prefix, content)
        content = re.sub("(^[^ ]+)(\r?\n)", r"\1 ", content)
        if not fixed_font:
            stripped_content = re.sub(r"\s+", " ", content)
            stripped_content = stripped_content.strip()
        else:
            stripped_content = content
        parts = stripped_content.split(" ")
        if not parts[0].startswith(self.prefix) and (len(parts) != 2 or not parts[0].startswith(":")):
            return

        if len(parts) == 2 and parts[1] == "!delete!" and parts[0].startswith(":"):
            try:
                if event.user.id in self.privileged_user_ids or event.user.id in self.owner_ids:
                    msg_id_to_delete = int(parts[0][1:])
                    self.client.get_message(msg_id_to_delete).delete()
            except:
                pass

        if parts[0].startswith(self.prefix):
            cmd_args = stripped_content[len(self.prefix):]
            if self.requires_special_arg_parsing(cmd_args.split(" ")[0]):
                cmd_args = content[len(self.prefix):]
            if self.requires_char_check(cmd_args.split(" ")[0]) and \
                    event.user.id not in self.owner_ids and re.compile("[^a-zA-Z0-9 _-]").search(cmd_args):
                message.reply("Command contains invalid characters.")
                return
            output = self.command(cmd_args, message, event)
            if output is not False and output is not None:
                if len(output) > 500:
                    message.reply("Output would be longer than 500 characters (the limit), so only the first 500 characters are posted now.")
                    self.room.send_message(output[:500])
                else:
                    message.reply(output)

    def command(self, cmd, msg, event):
        cmd_args = cmd.split(' ')
        cmd_name = cmd_args[0].lower()
        args = cmd_args[1:]
        if self.requires_special_arg_parsing(cmd_name):
            args = self.do_special_arg_parsing(cmd_name, cmd)
            if args is False:
                return "Argument parsing failed."
        r = self.modules.command(cmd_name, args, msg, event)
        if r is not False:
            return r
        else:
            return "Command not found."

    def bot_stopping(self):
        on_stops = self.modules.get_on_stop_methods()
        for on_stop in on_stops:
            on_stop(self)