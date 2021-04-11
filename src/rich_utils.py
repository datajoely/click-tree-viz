from typing import Optional, Dict, Union, Any

import treelib
from rich.abc import RichRenderable
from rich.console import Console, RichCast, ConsoleRenderable
from rich.tree import Tree as RichTree
from rich.panel import Panel


def _resolve_name(rich_tree: RichTree, lookup: Dict[str, str]) -> str:
    return lookup.get(str(rich_tree.label))


def _make_rich_renderable(new_node_identifier):
    # todo mechanism for doing help, params and pagination
    return Panel(new_node_identifier)


def _find_or_create_node(
        parent_identifier: Optional[str],
        new_node_identifier: str,
        rich_tree: RichTree,
        data_tree: treelib.Tree,
        renderable_lookup: Dict[str, str],
):
    # Have we found parent?
    if _resolve_name(rich_tree, renderable_lookup) == parent_identifier:

        # iterate through the children and check for target; BASE CASE 1
        for child in rich_tree.children:
            if _resolve_name(child, renderable_lookup) == new_node_identifier:
                return child
        else:
            # the parent has bee found, but the child does not exist; BASE CASE 2
            rich_renderable = _make_rich_renderable(new_node_identifier)

            # store rich panel lookup for complex objects
            renderable_lookup[str(rich_renderable)] = new_node_identifier

            # Add to rich hierarchy
            new_rich_tree = rich_tree.add(rich_renderable)
            return new_rich_tree

    # Keep recursing until we find the parent
    for child in rich_tree.children:
        _find_or_create_node(
            parent_identifier=parent_identifier,
            new_node_identifier=new_node_identifier,
            rich_tree=child,
            data_tree=data_tree,
            renderable_lookup=renderable_lookup,
        )


def build_rich_tree(cli_tree: treelib.Tree):
    if cli_tree.nodes:
        root_text = f'🌴 {cli_tree.root}'
        root_renderable = root_text # changing this to panel is weird
        rich_tree = RichTree(label=root_renderable)

        renderable_lookup = {str(root_text): cli_tree.root}
        for node in cli_tree.nodes:
            working_node = cli_tree.nodes[node]
            _find_or_create_node(
                parent_identifier=working_node.bpointer,
                new_node_identifier=working_node.identifier,
                data_tree=cli_tree,
                rich_tree=rich_tree,
                renderable_lookup=renderable_lookup,
            )
        Console().print(rich_tree)
