import Settings
    
    
class Command: # An executable command.
    def __init__(self, name, execute, help_data='', privileged=False):
        self.name = name
        self.execute = execute
        self.help_data = help_data or "Command exists, but no help entry found."
        self.privileged = privileged
        
    

class Module: # Contains a list of Commands.
    def __init__(self, commands):
        self.commands = commands
        
    def command(self, name, args, msg, event):
        matches = self.find_commands(name)
        if matches:
            command = matches[0]
            if not command.privileged or msg is None or event.user.id in Settings.owner_ids:
                return command.execute(args, msg, event)
            else:
                return "You don't have the privilege to execute this command."
        else:    
            return ''

    def get_help(self, name):
        matches = self.find_commands(name)
        if matches:
            return matches[0].help_data
        else:
            return ''
    
    def find_commands(self, name):
        return filter(lambda x: x.name == name, self.commands)
    
    def list_commands(self):
        cmd_list = []
        for command in self.commands:
            cmd_list.append(command.name)
        return cmd_list


class MetaModule: # Contains a list of Modules.
    def __init__(self, modules):
        self.modules = []
        for module in modules:
            self.modules.append(self.load_module(module))
        
    def command(self, name, args, msg, event):
        response = False
        for module in self.modules:
            response = module.command(name, args, msg, event)
            if response:
                break
        return response or "Command not found."
        
    def help(self, name):
        response = False
        for module in self.modules:
            response = module.get_help(name)
            if response:
                break
        return response or "Help entry not found."
    
    def load_module(self, file):
        module_file = __import__(file)
        return module_file.module
    
    def list_commands(self):
        cmd_list = []
        for module in self.modules:
            try:
                cmd_list.extend(module.list_commands())
            except ImportError:
                raise ModuleDoesNotExistException("Module: '" + module + '"Could not be found.')
        return cmd_list
        

class ModuleDoesNotExistException(Exception):
    pass
