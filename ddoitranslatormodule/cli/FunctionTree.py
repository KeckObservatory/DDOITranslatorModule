from .term_colors import term_colors

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
        
        # At this point, we either have a file, a directory, or something that doesn't exist
        
        mod_path = ".".join(func_path[:split_point])
        # print("Script function: " + ".".join(mod_path))
        # print(f"Arguments: {func_path[split_point:]}")
        return (mod_path, func_path[split_point:], final_node_is_leaf)
    