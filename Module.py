import importlib
import types
from ConsoleCommandHandler import ConsoleCommandHandler
import os
import traceback


class Command:  # An executable command.
    def __init__(self, name, execute, help_data='', privileged=False, owner_only=False, char_check=True,
                 special_arg_parsing=None):
        self.name = name
        self.execute = types.MethodType(execute, self)
        self.help_data = help_data or "Command exists, but no help entry found."
        self.privileged = privileged
        self.owner_only = owner_only
        self.char_check = char_check
        self.special_arg_parsing = special_arg_parsing


class Module:  # Contains a list of Commands.
    def __init__(self, commands, bot, on_event, on_bot_load, on_bot_stop, module_name):
        self.bot = bot
        self.commands = commands
        self.on_event = on_event
        self.on_bot_load = on_bot_load
        self.on_bot_stop = on_bot_stop
        self.module_name = module_name
        self.enabled = True

    def command(self, name, args, msg, event):
        if not self.enabled:
            return False
        matches = self.find_commands(name)
        if matches:
            command = matches[0]
            if (not command.privileged and not command.owner_only) or isinstance(msg, ConsoleCommandHandler) \
                    or (command.privileged and (event.user.id in self.bot.privileged_user_ids or event.user.id in self.bot.owner_ids)) \
                    or (command.owner_only and event.user.id in self.bot.owner_ids):
                return command.execute(self.bot, args, msg, event)
            else:
                return "You don't have the privilege to execute this command."
        else:
            return False

    def get_help(self, name):
        matches = self.find_commands(name)
        if matches:
            return matches[0].help_data
        else:
            return ''

    def find_commands(self, name):
        return list(filter(lambda x: x.name == name, self.commands))

    def list_commands(self):
        if not self.enabled:
            return []
        cmd_list = []
        for command in self.commands:
            cmd_list.append(command)
        return cmd_list


class MetaModule:  # Contains a list of Modules.
    def __init__(self, modules, bot, module_name, path=''):
        self.modules = []
        self.bot = bot
        self.module_name = module_name
        self.enabled = True
        if path and not path[-1] == '.':
            self.path = path + '.'
        else:
            self.path = ''
        for module in modules:
            self.modules.append(self.load_module(module))

    def command(self, name, args, msg, event):
        if not self.enabled:
            return False
        response = False
        for module in self.modules:
            response = module.command(name, args, msg, event)
            if response is not False:
                break
        return response

    def get_help(self, name):
        if not self.enabled:
            return False
        response = False
        for module in self.modules:
            if not module.enabled:
                continue
            response = module.get_help(name)
            if response:
                break
        return response

    def load_module(self, file_):
        file_ = self.path + file_
        try:
            module_file = importlib.import_module(file_)
        except ImportError as e:
            msg = "Error at importing " + file_ + os.linesep
            msg += "ImportError: " + e.msg
            msg += os.linesep
            msg += traceback.format_exc()
            raise ModuleLoadError(msg)
        try:
            mdls = module_file.modules
            try:
                module_name = module_file.module_name
            except AttributeError:
                module_name = file_
            if not isinstance(module_name, str):
                raise MalformedModuleException("Module: '%s', 'module_name' is not a string." % file_)
            if type(mdls) is list:
                return MetaModule(mdls, self.bot, module_name, file_[:file_.rfind('.')])
            else:
                raise MalformedModuleException("Module: '" + file_ + "', 'modules' is not a list.")
        except AttributeError:
            try:
                cmds = module_file.commands
                try:
                    on_event = module_file.on_event
                except AttributeError:
                    on_event = None
                try:
                    on_bot_load = module_file.on_bot_load
                except AttributeError:
                    on_bot_load = None
                try:
                    on_bot_stop = module_file.on_bot_stop
                except AttributeError:
                    on_bot_stop = None
                try:
                    module_name = module_file.module_name
                except AttributeError:
                    module_name = file_
                if not isinstance(module_name, str):
                    raise MalformedModuleException("Module: '%s', 'module_name' is not a string." % file_)
                try:
                    save_subdir = module_file.save_subdir
                    if isinstance(save_subdir, str):
                        self.bot.save_subdirs.append(save_subdir)
                    else:
                        raise MalformedModuleException("Module: '%s', 'save_subdir' is not a string." % file_)
                except AttributeError:
                    pass
                if type(cmds) is list:
                    return Module(cmds, self.bot, on_event, on_bot_load, on_bot_stop, module_name)
                else:
                    raise MalformedModuleException("Module: '" + file_ + "', 'commands' is not a list.")
            except AttributeError:
                raise MalformedModuleException("Module: '" + file_ + "' does not contain a variable called either 'modules' or 'commands'.")

    def list_commands(self):
        if not self.enabled:
            return []
        cmd_list = []
        for module in self.modules:
            cmd_list.extend(module.list_commands())
        return cmd_list

    def get_event_watchers(self):
        if not self.enabled:
            return []
        watchers = []
        for m in self.modules:
            if isinstance(m, MetaModule):
                watchers.extend(m.get_event_watchers())
            elif m.on_event is not None:
                watchers.append(m.on_event)
        return watchers

    def get_on_load_methods(self):
        if not self.enabled:
            return []
        on_loads = []
        for m in self.modules:
            if isinstance(m, MetaModule):
                on_loads.extend(m.get_on_load_methods())
            elif m.on_bot_load is not None:
                on_loads.append(m.on_bot_load)
        return on_loads

    def get_on_stop_methods(self):
        if not self.enabled:
            return []
        on_stops = []
        for m in self.modules:
            if isinstance(m, MetaModule):
                on_stops.extend(m.get_on_stop_methods())
            elif m.on_bot_stop is not None:
                on_stops.append(m.on_bot_stop)
        return on_stops

    def find_module_by_name(self, name):
        if not self.enabled:
            return None
        if self.module_name == name:
            return self
        for m in self.modules:
            if m.module_name == name:
                return m
            if isinstance(m, MetaModule):
                m1 = m.find_module_by_name(name)
                if m1 is not None:
                    return m1
        return None

    def disable_module(self, name):
        if not self.enabled:
            return False
        if self.module_name == name:
            self.enabled = False
            return True
        for m in self.modules:
            if m.module_name == name:
                m.enabled = False
                return True
            if isinstance(m, MetaModule):
                m1 = m.disable_module(name)
                if m1:
                    return True
        return False

    def enable_module(self, name):
        if self.module_name == name:
            self.enabled = True
            return True
        if not self.enabled:
            return False
        for m in self.modules:
            if m.module_name == name:
                m.enabled = True
                return True
            if isinstance(m, MetaModule):
                m1 = m.enable_module(name)
                if m1:
                    return True
        return False


class ModuleLoadError(Exception):
    pass


class MalformedModuleException(Exception):
    pass
