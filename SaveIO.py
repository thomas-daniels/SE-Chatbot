import os
import pickle

_allowed_subdirs = []

data_dir = "botdata/"

def save(obj, module, name):
    global _allowed_subdirs
    module_dir = os.path.join(data_dir, module)
    if module_dir not in _allowed_subdirs:
        raise InvalidDirectoryException("The subdirectory given is not a module's allowed subdirectory.")
    _create_if_not_exists(module_dir)
    file_ = os.path.join(module_dir, name + ".p")
    with open(file_, "w+") as f:
        try:
            pickle.dump(obj, f)
        except:
            print "Error while saving data '%s'. Data has not been saved." % (name)

            
def load(module, name):
    global _allowed_subdirs
    module_dir = os.path.join(data_dir, module)
    if module_dir not in _allowed_subdirs:
        raise InvalidDirectoryException("The subdirectory given is not a module's allowed subdirectory.")
    file_ = os.path.join(module_dir, name + ".p")
    if not os.path.exists(file_) or os.stat(file_).st_size == 0:
        _create_empty_pickle_file(file_)
    with open(file_, "r") as f:
        return pickle.load(f)

        
def _set_subdirs(dir_list):
    global _allowed_subdirs
    _allowed_subdirs = []
    for i in range(len(dir_list)):
        dir_ = os.path.join(data_dir, dir_list[i])
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
