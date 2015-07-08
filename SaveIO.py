import os
import sys
import pickle

_allowed_subdirs = []

data_dir = "botdata/"

def save(obj, subdir, name, filetype="p"):
    global _allowed_subdirs
    module_dir = os.path.join(data_dir, subdir)
    if module_dir not in _allowed_subdirs:
        raise InvalidDirectoryException("The subdirectory given is not a module's allowed subdirectory.")
    create_if_not_exists(module_dir)
    file_ = os.path.join(module_dir, name + "." + filetype)
    with open(file_, "w+") as f:
        if filetype == "p":
            try:
                pickle.dump(obj, f)
            except:
                if "-q" not in sys.argv:
                    print "[SaveIO] WARNING: Error while saving data '%s'. Data has not been saved." % (name)
        else:
            if not isinstance(obj, basestring):
                raise TypeError("Only strings may be saved in non-pickle files.")
            else:
                f.write(obj)

            
def load(subdir, name, filetype="p"):
    global _allowed_subdirs
    module_dir = os.path.join(data_dir, subdir)
    if module_dir not in _allowed_subdirs:
        raise InvalidDirectoryException("The subdirectory given is not a module's allowed subdirectory.")
    file_ = os.path.join(module_dir, name + "." + filetype)
    if not os.path.exists(file_) or os.stat(file_).st_size == 0:
        if "-q" not in sys.argv:
            print "[SaveIO] INFO: Attempt to load non-existent file. An empty file has been created."
        if filetype == "p":
            _create_empty_pickle_file(file_)
        else:
            with open(file_, "w+") as f:
                f.close()
    with open(file_, "r") as f:
        if filetype == "p":
            return pickle.load(f)
        else:
            return f.readall()

        
def set_subdirs(dir_list):
    global _allowed_subdirs
    _allowed_subdirs = []
    for i in range(len(dir_list)):
        dir_ = os.path.join(data_dir, dir_list[i])
        if dir_ in _allowed_subdirs:
            raise DuplicateDirectoryException(dir_)
        create_if_not_exists(dir_)
        _allowed_subdirs.append(dir_)

        
def create_if_not_exists(dir_path):
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
        except:
            if "-q" not in sys.argv:
                print "[SaveIO] WARNING: Could not create directory %s." % (dir_path)

            
def _create_empty_pickle_file(filepath):
    with open(filepath, "w+") as f:
        f.write("(dp0\n.")

            
class InvalidDirectoryException(Exception):
    pass

    
class DuplicateDirectoryException(Exception):
    pass
