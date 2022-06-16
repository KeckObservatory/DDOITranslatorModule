from .term_colors import term_colors


class FunctionTree():
    """Tree that represents the directory structure for the functions in a
    translator module
    """

    class TreeNode():
        """Inner class for the FunctionTree, represents a node in the tree
        """

        def __init__(self, parent=None, content=""):
            
            self.parent = parent
            self.children = []
            self.content = content

        def add_child(self, child):
            """Adds a child to this node

            Parameters
            ----------
            child : TreeNode
                Node that should be added as a child to this node
            """
            self.children.append(child)

        def is_not_leaf(self):
            """Determines if this node is a leaf or an inner node

            Returns
            -------
            bool
                True if the node is an inner node, false if it is a leaf
            """
            return len(self.children) > 0

        def children_contain_element(self, el):
            """Determines if the contents of the children of this node contain a
            given element

            Parameters
            ----------
            el : str
                Element to look for in the contents of this node's children

            Returns
            -------
            bool
                True if the contents of this node's children contain the given
                element
            """
            for child in self.children:
                if child.content == el:
                    return child
            return None
    
    def __init__(self, root):
        self.root = self.TreeNode(content=root)

    def add_list_to_tree(self, arr, root_node=None):
        """Takes in a file path as an array of strings and adds the nodes to the
        tree in the correct location, creating nodes as needed

        Parameters
        ----------
        arr : list or iterable
            list of strings to add, where each succesive list element is a child
            of the one before
        root_node : TreeNode, optional
            Node to start adding the list too. If none, uses this tree's root,
            which is typical when invoked externally. by default None
        """
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
        """Prints the tree to terminal, marking leaf nodes (in this case,
        functions) in green

        Parameters
        ----------
        root : TreeNode, optional
            Node to start printing at. If not specified, uses this tree's root
        indent : str, optional
            indent used recursively. Should not be set by the use
        """
        if root:
            if root.is_not_leaf() > 0:
                print(f"\n{indent}{root.content}")
                for child in root.children:
                    self.print_tree(root=child, indent="\t" + indent)
            else:
                print(f"{indent} {term_colors.GREEN}{root.content}{term_colors.END_COLOR}")
        else:
            self.print_tree(root=self.root)

    def parse_function_list(self, function_list):
        """Takes in a list of strings that contains both a path to a function,
        and also possible arguments for that function (in the form):

            [func_path1, func_path2, ... func_pathN, arg1, arg2, ... argN]

        Parameters
        ----------
        function_list : list
            list of strings

        Returns
        -------
        (str, list, list)
            string representing the module path (e.g. what would be imported),
            the list of arguments used to create that string, and the arguments
            at the end of the function path
        """
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
        
        # At this point, we either have a file, a directory, or something that doesn't exist
        
        mod_path = ".".join(func_path[:split_point])
        # print("Script function: " + ".".join(mod_path))
        # print(f"Arguments: {func_path[split_point:]}")
        return (mod_path, func_path[split_point:], final_node_is_leaf)
    