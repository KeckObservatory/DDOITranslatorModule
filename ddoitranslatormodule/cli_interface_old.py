import argparse
import importlib
from pathlib import Path

from numpy import sort
from .cli.FunctionTree import FunctionTree
from yaml import load, Loader

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
    
    print(functions)

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
            "list" : module_path_list,
            "name" : module_path_list[-1]
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
    parser = argparse.ArgumentParser(description='Translator wrapper', add_help=False)

    parser.add_argument('-l', '--list', dest='list', action='store_true',
                        help="Display all functions availible from this translator")
    parser.add_argument('function', nargs='*',
                        help="Function to invoke. [function ... ] [arguments ...]")
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='Display more detailed information about execution')

    return parser


def parse_arguments(args, funcs, tree, cfg):
    matches = []
    for f in funcs:
        if f['name'] == args.function[0]:
            matches.append(f)

    if len(matches) == 1:
        # If there is one match, use it
        module = matches[0]
    elif len(matches) > 1:
        # If there is more than one match, try to resolve the ambiguity
        print(f"Ambiguity found: {[f['module_path'] for f in matches]}")
    else:
        # No matches found, walk the tree
        print("No matches found")
        
    # Use tree to figure out when function name ends and arguments begin
    module_path, arguments, leaf = tree.parse_function_list([__package__, cfg['functions_dir']] + args.function)
    try:
        module = importlib.import_module(module_path)
        if not leaf:
            print('Indicated function is a directory, not a file. Exiting...')
        else:
            if hasattr(module, "execute"):
                module.execute(arguments)
            else:
                print("Module does not contain an `execute` function. Exiting...")
            # print(f'Module path: {module_path}, which {"is" if leaf else "is not"} a leaf')
    except ValueError as e:
        print(f"Unable to import module {module_path}")
    if args.verbose:
        print(f"Script function: {module_path}")
        print(f"Arguments: {arguments}")

def load_table(filename):
    with open(filename, 'r') as stream:
        tbl = load(stream, Loader=Loader)
        super_function_sorted = {}
        for key in tbl.keys():
            sub_func = {
                'subfunc' : key,
                'args' : tbl[key]['arguments']
            }
            if tbl[key]['function'] in super_function_sorted.keys():
                super_function_sorted[tbl[key]['function']].append(sub_func)
            else:
                super_function_sorted[tbl[key]['function']] = [sub_func]
        return tbl, super_function_sorted

def get_expansion_function(func_name, table_name):
    """Searches the function expansion table for a matching function name

    Parameters
    ----------
    func_name : str
        name of the function to match
    """
    table, _ = load_table(table_name)

    if func_name not in table.keys():
        return None
    else:
        return table[func_name]

def main():

    """
    Program flow

    Generate the function tree

    Assume that the first argument is the function:
        Look through the yaml expansion table to see if it's there
            If it is, RUN
        Look through the leaves of the function tree
            If there is only one match, RUN
            If there is ambiguity, ALERT THE USER
    - If we are here, the first argument isn't enough
    Follow the tree down to get the function, and RUN
    """

    parser = get_parser()
    args = parser.parse_args()

    cfg = {
        "function_prefix": "func",
        "functions_dir": "functions",
        "expansion_table" : "./ddoitranslatormodule/cli/expansion_table.yaml"
    }
    
    funcs = get_functions(cfg)
    print(funcs)
    tree = FunctionTree(root=__package__)
    for f in funcs:
        tree.add_list_to_tree(f['list'])
    

    tbl, sorted = load_table(cfg["expansion_table"])

    print(tbl)
    print("")
    print(sorted)


    if args.list:
        tree.print_tree(sorted_expansion_table=sorted)
        return

    if len(args.function) > 0:
        # Use tree to figure out when function name ends and arguments begin
        module_path, arguments, leaf = tree.parse_function_list(
            [__package__, cfg['functions_dir']] + args.function)
        module = importlib.import_module(module_path)
        if not leaf:
            print('Indicated function is a directory, not a file. Exiting...')
            return
        if hasattr(module, "execute"):
            args = module.add_cmdline_args(cfg, parser)
            module.execute(args)
        else:
            print("Module does not contain an `execute` function. Exiting...")
        print(f'Module path: {module_path}, which {"is" if leaf else "is not"} a leaf')
        print(f"Arguments: {arguments}")



