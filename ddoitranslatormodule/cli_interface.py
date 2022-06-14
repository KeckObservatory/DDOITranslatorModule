# Parse the directory tree to find all classes that extend the translator module
# function

# Build that into a Argument Parser

# Create a method that executes those translator module functions
import argparse
import importlib
from pathlib import Path

def get_functions(cfg):
    # Find the package path with all the functions in it
    # collect each one into a ... dict? nested correctly?
    
    # Get functions directory
    func_dir = Path(__file__).parent / 'functions'
    # Get all functions
    functions = [i for i in func_dir.rglob(f'{cfg["function_prefix"]}*.py')]
    func_dicts = []
    for f in functions:
        # Get the absolute path, everything before the functions directory
        levels = str(f).split(str(func_dir))[-1]
        # Split on / to get modules/submodules, and remove the first empty one
        levels = levels.split('/')[1:]
        # Add in the package itself
        module_path = [__package__] + levels
        # Form into an import string
        module_path = ".".join(module_path)
        # Strip off the '.py. from the end
        module_path = module_path[:-3]
        res = {
            "module_path" : module_path,
            "abs_path" : str(f)
        }
        func_dicts.append(res)

    return func_dicts

def print_functions_tree(cfg):
    """Prints the functions availible in this module in nested tree form

    Parameters
    ----------
    cfg : dict
        config file containing the function prefix
    """
    func_dir = Path(__file__).parent / 'functions'
    print(get_function_tree_str(func_dir, cfg))

def get_function_tree_str(directory, cfg, str = "", prefix = ""):
    """Generates a string representation of the functions availible within a given
    directory

    Parameters
    ----------
    directory : pathlib.Path
        root of the tree
    cfg : dict
        config containing function prefix
    str : str, optional
        starting string, by default ""
    prefix : str, optional
        indentation prefix, by default ""

    Returns
    -------
    str
        A string Tree representation of all availible functions
    """

    dirs = []
    for d in directory.iterdir():
        if d.is_dir() and not d.match('__*__'):
            dirs.append(d)
        elif d.is_file() and d.match(cfg['function_prefix'] + "*.py"):
            str += prefix + d.stem + "\n"
    for d in dirs:
        str += "\n" + prefix + d.stem + "\n"
        str += get_function_tree_str(directory/d, cfg, "", prefix + "\t")
    return str

def get_help_string(file):
    try:
        mod = importlib.import_module(file)
        print("I didn't error!")
        return mod.help
    except:
        print("No help gound")
        return "" 
    # Try to import the file
        # if you can, try to get the help string and return it
    # Otherwise, return ""

def get_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--functions', dest='functions', action='store_true', help="Display all functions availible from this translator")

    return parser.parse_args()

def main():

    args = get_parser()

    cfg = {
        "function_prefix" : "func"
    }

    # tree = get_functions(cfg)
    # for i in get_functions(cfg):
    #     print(i)
        
    # print(tree)
    if args.functions:
        print_functions_tree(cfg)

    # importlib.import_module("ddoitranslatormodule.subfuncs2.func_sub2")
    # get_help_string("ddoitranslatormodule.subfuncs2.func_sub2")
