# Parse the directory tree to find all classes that extend the translator module
# function

# Build that into a Argument Parser

# Create a method that executes those translator module functions
import argparse
import importlib
from importlib.util import module_for_loader
from logging import root
from operator import mod
from pathlib import Path
from posixpath import split

class term_colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_functions(cfg):
    
    # Get functions directory
    func_dir = Path(__file__).parent / cfg['functions_dir']
    # Get all functions
    functions = [i for i in func_dir.rglob(f'{cfg["function_prefix"]}*.py')]
    func_dicts = []
    func_tree = {}
    for f in functions:
        # Get the absolute path, everything before the functions directory
        levels = str(f).split(str(func_dir))[-1]
        # Split on / to get modules/submodules, and remove the first empty one
        levels = levels.split('/')[1:]
        # Add in the package itself
        module_path_list = [__package__] + [cfg['functions_dir']] + levels
        module_path_list[-1] = module_path_list[-1][:-3]
        # Form into an import string
        module_path = ".".join(module_path_list)
        # Strip off the '.py. from the end
        # module_path = module_path[:-3]
        res = {
            "module_path" : module_path,
            "abs_path" : str(f),
            "list" : module_path_list
        }
        func_dicts.append(res)

        for item in module_path_list:
            if hasattr(func_tree, item):
                pass

    return func_dicts

def get_help_string(module_path):
    try:
        mod = importlib.import_module(module_path)
        print("I didn't error!")
        help = getattr(mod, 'help_string')
        if help:
            return help
        else:
            print(f"No help_string attribute found in {module_path}")
    except:
        print(f"Error importing {module_path}")
        return 


def get_function_from_args(arguments, functions):

    # loop over the arguments, trying to match against a list in functions
    # Keep track as we go, and save whatever got furthest
    pass

class FunctionTree():

    class TreeNode():

        def __init__(self, parent=None, content=""):
            
            self.parent = parent
            self.children = []
            self.content = content

        def add_child(self, child):
            self.children.append(child)

        def is_not_leaf(self):
            return len(self.children) > 0

        def children_contain_element(self, el):
            for child in self.children:
                if child.content == el:
                    return child
            return None
    
    def __init__(self, root):
        self.root = self.TreeNode(content=root)

    def add_list_to_tree(self, arr, root_node=None):
        # If there's nothing in the array, there's nothing to do
        if len(arr) < 1:
            return
        else:
            # If the root matches the first element, then move forward one in the list
            # *without* moving a level deeper
            if self.root.content == arr[0]:
                self.add_list_to_tree(arr[1:], root_node=self.root)
                return
            # Ensure there is a root node specified
            if root_node:
                el = arr[0]
                child = root_node.children_contain_element(el)
                if child:
                    self.add_list_to_tree(arr[1:], root_node=child)
                else:
                    new_child = self.TreeNode(parent=root_node, content=el)
                    root_node.add_child(new_child)
                    self.add_list_to_tree(arr[1:], root_node=new_child)
            else:
                # If there is no root node specified, use the tree's base root
                self.add_list_to_tree(arr, root_node=self.root)


    def print_tree(self, root=None, indent=""):
        if root:
            if root.is_not_leaf() > 0:
                print(f"\n{indent}{root.content}")
                for child in root.children:
                    self.print_tree(root=child, indent="\t" + indent)
            else:
                print(f"{indent} {term_colors.OKGREEN}{root.content}{term_colors.ENDC}")
        else:
            self.print_tree(root=self.root)

    def parse_function_list(self, function_list):
        node = self.root
        split_point = 0
        func_path = function_list
        final_node_is_leaf = False
        # Skip the first element, since it is the root of the tree
        for idx, f in enumerate(func_path[1:]):
            child = node.children_contain_element(f)
            if child:
                node = child
            else:
                split_point = idx + 1
                final_node_is_leaf = not node.is_not_leaf()
                break
        

        mod_path = ".".join(func_path[:split_point])
        # print("Script function: " + ".".join(mod_path))
        # print(f"Arguments: {func_path[split_point:]}")
        return (mod_path, func_path[split_point:], final_node_is_leaf)
    
def get_parser():
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


    
