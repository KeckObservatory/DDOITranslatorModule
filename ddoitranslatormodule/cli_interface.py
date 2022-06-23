import argparse
import importlib
from pathlib import Path
from .cli.FunctionTree import FunctionTree

def get_functions(cfg):
    """Recursively searches through the function directory specified in cfg and
    returns a list of dictionaries containing information about those functions

    Parameters
    ----------
    cfg : dict or dict-like
        Parsed configuration file

    Returns
    -------
    list of dict
        All of the functions in the specified directory that match the given
        prefix. Each dict contains:
        module_path: string that can be used to import the found function
        abs_path: the absolute path to that function
        list: the module path as a list of strings, rather than joined with .
    """
    
    # Get functions directory
    func_dir = Path(__file__).parent / cfg['functions_dir']

    # Get all functions
    functions = [i for i in func_dir.rglob(f'{cfg["function_prefix"]}*.py')]
    
    # Empty list for functions to fill
    func_dicts = []
    
    for f in functions:
        
        # Get the absolute path, everything before the functions directory
        levels = str(f).split(str(func_dir))[-1]
        
        # Split on / to get modules/submodules, and remove the first empty one
        levels = levels.split('/')[1:]
        
        # Add in the package itself
        module_path_list = [__package__] + [cfg['functions_dir']] + levels

        # String off the '.py' from the last element
        module_path_list[-1] = module_path_list[-1][:-3]
        
        # Form into an import string
        module_path = ".".join(module_path_list)
        
        res = {
            "module_path" : module_path,
            "abs_path" : str(f),
            "list" : module_path_list
        }
        func_dicts.append(res)

    return func_dicts

def get_help_string(module_path):
    """Retrieves the help string from a given module, if there is one

    Parameters
    ----------
    module_path : str
        import string for the module in question (e.g. package.subpackage.mod)

    Returns
    -------
    str
        The help string found if there is one, otherwise None
    """
    
    try:
        mod = importlib.import_module(module_path)
        help = getattr(mod, 'help_string')
        if help:
            return help
        else:
            print(f"No help_string attribute found in {module_path}")
            return None
    except:
        print(f"Error importing {module_path}")
        return 

def get_parser():
    """Gets an argument parser object from the command line

    Returns
    -------
    ArgumentParser
        The ArgumentParser object
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('-l', '--list', dest='list', action='store_true', help="Display all functions availible from this translator")
    parser.add_argument('function', nargs='*', help="Function to invoke. [function ... ] [arguments ...]")

    return parser.parse_args()

def main():

    args = get_parser()

    cfg = {
        "function_prefix" : "func",
        "functions_dir" : "functions"
    }
    
    funcs = get_functions(cfg)
    tree = FunctionTree(root=__package__)
    for f in funcs:
        tree.add_list_to_tree(f['list'])
    
    if args.list:
        tree.print_tree()

    if len(args.function) > 0:
        # Use tree to figure out when function name ends and arguments begin
        module_path, arguments, leaf = tree.parse_function_list([__package__, cfg['functions_dir']] + args.function)
        module = importlib.import_module(module_path)
        if not leaf:
            print('Indicated function is a directory, not a file. Exiting...')
            return
        if hasattr(module, "execute"):
            module.execute(arguments)
        else:
            print("Module does not contain an `execute` function. Exiting...")
        print(f'Module path: {module_path}, which {"is" if leaf else "is not"} a leaf')
        print(f"Arguments: {arguments}")


    
