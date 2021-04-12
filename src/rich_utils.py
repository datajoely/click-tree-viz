"""
This module provides utilities for building out a complex rich tree representation
of a Click cli object
"""

from typing import Optional, Dict, Tuple, List, Any

import treelib
from rich import box
from rich.console import Console, RenderGroup, ConsoleRenderable
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree as RichTree

COLOURS = {"group": "[yellow]", "argument": "[red]", "option": "[magenta]"}

ICONS = {"command": "⚙️", "group": "📂", "tree": "🌴"}

PANEL_MAX_WIDTH = 40


def _make_rich_renderable(node_id: str, cli_tree: treelib.Tree) -> ConsoleRenderable:
    """
    This method constructs the relevant rich renderable for the the given node
    identifier. If the node in question has parameters a special table is created,
    otherwise a simple panel is created.
    Args:
        node_id: The node to process
        cli_tree:  The treelib Tree structure uses to retrieve metadata

    Returns:
        A rich renderable object
    """

    node_data = cli_tree.nodes[node_id].data
    is_group = node_data.get("is_group")
    cmd_desc = node_data.get("help")
    params = node_data.get("params")
    title = f'{"" if is_group else ICONS.get("command") + " "}{node_data.get("name")}'

    def _new_simple_panel(text: str, desc: str):
        """This method constructs a simple text panel if no parameters are present"""

        text_title = [
            Text(
                f"{ICONS.get('group')} {text}",
                no_wrap=True,
                overflow="ellipsis",
                style="bold",
            )
        ]
        text_desc = [Text(desc, overflow="ellipsis", style="italic")] if desc else []
        return Panel.fit(
            renderable=RenderGroup(*(text_title + text_desc)), width=PANEL_MAX_WIDTH,
        )

    def _new_param_tbl(desc: str, text: str, headers: List[str]):
        """This method constructs a table in order to detail parameters """
        return Panel.fit(
            renderable=RenderGroup(
                Text(text, no_wrap=True, overflow="ellipsis", style="bold"),
                Table(
                    *headers,
                    show_lines=False,
                    show_header=True,
                    show_edge=False,
                    box=box.SIMPLE_HEAD,
                ),
            ),
            title=desc,
            width=PANEL_MAX_WIDTH,
            box=box.ROUNDED,
        )

    def _format_param_row(param: Dict[str, Any]) -> Tuple[str, Text]:
        """Processes a given param dict so that it can be visualised as a table row"""
        joined_options = ", ".join(param["opts"])
        resolved_colours = COLOURS.get(param["type"], "")
        first_col = resolved_colours + joined_options
        second_col = param.get("help", "")
        return first_col, Text(second_col, no_wrap=True, overflow="ellipsis")

    # If any params have 'help' key
    if params and any([x.get("help", False) for x in params]):
        component = _new_param_tbl(desc=title, text=cmd_desc, headers=["param", "desc"])
    # If params are present without any help key
    elif params:
        component = _new_param_tbl(desc=title, text=cmd_desc, headers=["param"])
    else:
        component = _new_simple_panel(text=title, desc=cmd_desc)

    # If table is present, retrieve it so that we can add rows
    panels = component.renderable.renderables
    if params and len(panels) > 0 and isinstance(panels[-1], Table):
        tbl = panels[-1]
        for row in map(_format_param_row, params):
            # Add row to table
            tbl.add_row(*row)

    return component


def _find_or_create_node(
    parent_node_id: Optional[str],
    new_node_id: str,
    rich_tree: RichTree,
    cli_tree: treelib.Tree,
    renderable_lookup: Dict[str, str],
):
    """
    This method depth-first recurses down the rich tree and creates nodes if needed
    Args:
        parent_node_id: The parent identifier of the node in scope
        new_node_id: The identifier of the node to create or find
        rich_tree: The rich tree which needs to be traversed/appended to
        cli_tree: The treelib structure which can be referenced for metadata
        renderable_lookup: The mapping of rich IDs to treelib IDs since complex
            rich objects get silly labels like:
            "<rich.panel.Panel object at 0x10e5b0160>"

    Returns:
        The rich tree object with the relevant node retrieved (if exists) or created
    """

    def _resolve_name(r_tree: RichTree, lookup: Dict[str, str]) -> str:
        return lookup.get(str(r_tree.label))

    # Have we found parent?
    if _resolve_name(rich_tree, renderable_lookup) == parent_node_id:

        # iterate through the children and check for target; BASE CASE 1
        for child in rich_tree.children:
            if _resolve_name(child, renderable_lookup) == new_node_id:
                return child
        else:
            # the parent has bee found, but the child does not exist; BASE CASE 2
            rich_renderable = _make_rich_renderable(
                node_id=new_node_id, cli_tree=cli_tree
            )

            # store rich panel lookup for complex objects
            renderable_lookup[str(rich_renderable)] = new_node_id

            # Add to rich hierarchy
            new_rich_tree = rich_tree.add(rich_renderable, highlight=False)
            return new_rich_tree

    # Keep recursing until we find the parent
    for child in rich_tree.children:
        _find_or_create_node(
            parent_node_id=parent_node_id,
            new_node_id=new_node_id,
            rich_tree=child,
            cli_tree=cli_tree,
            renderable_lookup=renderable_lookup,
        )


def build_rich_tree(
    cli_tree: treelib.Tree, return_obj: bool = False
) -> Optional[ConsoleRenderable]:
    """
    This method takes a treelib Tree structure constructed by processing the click
    object and then converts this to a richly formatted object that can be printed
    on the console using the 'rich' library
    Args:
        cli_tree: The treelib Tree object
        return_obj: If required, we can avoid printing the object and simply return it
            as a python reference

    Returns:
        (Optional) object that can be printed in the rich console

    """
    if cli_tree.nodes:

        # Format and create the root node
        root_text = Panel.fit(f"{cli_tree.root} tree {ICONS.get('tree')}")
        root_renderable = root_text
        rich_tree = RichTree(label=root_renderable, highlight=True)

        # Initialise the lookup object pre-recursion
        renderable_lookup = {str(root_text): cli_tree.root}

        # Create each node in the treelib Tree structure in the rich_tree object
        for node in cli_tree.nodes:
            # Get node object with metadata
            working_node = cli_tree.nodes[node]
            _find_or_create_node(
                parent_node_id=working_node.bpointer,
                new_node_id=working_node.identifier,
                cli_tree=cli_tree,
                rich_tree=rich_tree,
                renderable_lookup=renderable_lookup,
            )

        # Return object if requested
        if return_obj:
            return rich_tree

        # Print to the console
        Console().print(rich_tree)
