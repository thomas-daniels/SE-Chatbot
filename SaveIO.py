import os
import pickle

_allowed_subdirs = []

current_dir = base = os.path.join(os.path.dirname(os.path.abspath(__file__)))
root_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
data_dir = os.path.abspath(os.path.join(root_dir, "botdata"))

def save(obj, module, name):
    module_dir = os.path.abspath(os.path.join(data_dir, module))
    if module_dir not in _allowed_subdirs:
        raise InvalidDirectoryException("The subdirectory given is not a module's allowed subdirectory.")
    _create_if_not_exists(module_dir)
    file = os.path.abspath(os.path.join(module_dir, name + ".p"))
    with open(file, "w+") as f:
        try:
            pickle.dump(obj, f)
        except:
            print "Error while saving data '%s'. Data has not been saved." % (name)
            
def load(module, name):
    module_dir = os.path.abspath(os.path.join(data_dir, module))
    if module_dir not in _allowed_subdirs:
        raise InvalidDirectoryException("The subdirectory given is not a module's allowed subdirectory.")
    file_ = os.path.abspath(os.path.join(module_dir, name + ".p"))
    if not os.path.exists(file_) or os.stat(file_).st_size == 0:
        _create_empty_pickle_file(file_)
    with open(file_, "r") as f:
        return pickle.load(f)
        
def _set_subdirs(dir_list):
    _allowed_subdirs = []
    for i in range(len(dir_list)):
        dir_ = os.path.abspath(os.path.join(root_dir, dir_list[i]))
        if dir_ in _allowed_subdirs:
            raise DuplicateDirectoryException("Duplicate name '" + dir_ + "'")
        _create_if_not_exists(dir_)
        _allowed_subdirs.append(dir_)
        
def _create_if_not_exists(dir_path):
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
        except:
            print "Could not create directory %s." % (dir_path)
            
def _create_empty_pickle_file(filepath):
    with open(filepath, "w+") as f:
        f.write("(dp0\n.")
            
class InvalidDirectoryException(Exception):
    pass
    
class DuplicateDirectoryException(Exception):
    pass

_create_if_not_exists(data_dir)