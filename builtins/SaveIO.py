import os
import pickle

current_dir = base = os.path.join(os.path.dirname(os.path.abspath(__file__)))
root_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
data_dir = os.path.abspath(os.path.join(root_dir, "botdata"))

_create_if_not_exists(data_dir)

def save(obj, module, name):
    module_dir = os.path.abspath(os.path.join(data_dir, module))
	_create_if_not_exists(module_dir)
    file = os.path.abspath(os.path.join(module_dir, name + ".p"))
    with open(file, "w+") as f:
        try:
            pickle.dump(obj, f)
        except:
            print "Error while saving data '%s'. Data has not been saved." % (name)
            
def load(module, name):
    module_dir = os.path.abspath(os.path.join(data_dir, module))
    file = os.path.abspath(os.path.join(module_dir, name + ".p"))
    with open(file, "r") as f:
        return pickle.load(f)
        
def _create_if_not_exists(dir_path):
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
        except:
            print "Could not create directory %s." % (dir_path)