from treelib import Tree as Treelib
from rich.tree import Tree


def build_rich_tree(cli_tree: Treelib):
    tree_id = cli_tree.identifier

    for node in cli_tree.nodes:
        print(node.sucessors(tree_id))
