# pylint:disable=inconsistent-return-statements

"""
This module provides a class to visualise Click CLI structures
"""

import io
from contextlib import redirect_stdout
from copy import deepcopy
from typing import Union, Dict, Any, List

import treelib

from click import Group, MultiCommand

from click_tree_viz.click_utils import ClickNode, recurse_click_cli
from click_tree_viz.rich_utils import build_rich_tree


class ClickTreeViz:
    """
    This class is used to traverse the nested CLI structure of a click Click object
    and then provide several mechanisms for visualising or exporting the CLI structure
    """

    def __init__(self, click_stuct: Union[MultiCommand, Group]):
        """
        The constructor for this class accepts a nested Click CLI object
        Args:
            click_stuct: The structure to traverse and convert
        """
        # Copy value just in case
        self._raw_struct = deepcopy(click_stuct)

        # Flat list of ClickNode objects
        self._list_leaf_nodes = recurse_click_cli(click_structure=self._raw_struct)

        # Convert to treelib.tree.Tree structure
        self._treelib_obj = self._as_tree(node_sequence=self._list_leaf_nodes)
        self._treelib_obj_params = self._extend_leaf_params(treelib_obj=self._treelib_obj)

        # Graphviz method provided by treelib yields once only
        self._graphviz_cached = None

    @staticmethod
    def _as_tree(node_sequence: List[ClickNode]) -> treelib.tree.Tree:
        """
        This method constructs a list of Click leaf nodes (custom dataclass)
        to a Treelib object.
        Args:
            node_sequence: The list of nodes that need to be created as a treelib object

        Returns:
            The constructed treelib object

        """
        # Use tree lib to take clean struct and hold in memory
        working_tree = treelib.tree.Tree()
        working_tree.create_node(identifier="CLI")
        for leaf in node_sequence:
            working_tree.create_node(
                identifier=leaf.path,
                tag=leaf.name,
                data=leaf.as_dict(),
                parent="CLI" if leaf.is_root else leaf.parent_path,
            )

        return working_tree

    @staticmethod
    def _extend_leaf_params(treelib_obj: treelib.tree.Tree) -> treelib.tree.Tree:
        """Add parameters and commands to the tree structure"""

        # Copy so working with different reference
        working_treelib_obj = deepcopy(treelib_obj)

        # Iterate over each node
        for node in treelib_obj.nodes:
            # Retrieve node object
            working_node = treelib_obj[node]
            # Filter to nodes with data property
            if working_node.data is not None:
                params = working_node.data.get("params", [])
                for param in params:
                    # Join any multi-options
                    opts = ",".join(param["opts"])
                    # Add to copied tree
                    working_treelib_obj.create_node(
                        identifier=working_node.identifier + "." + opts,
                        tag=f'[{param["type"]}] {opts}',
                        parent=node,
                    )
        return working_treelib_obj

    def to_dict(self, **kwargs) -> Dict[str, Any]:
        """Uses treelib to convert nodes to a dictionary structure"""
        return self._treelib_obj.to_dict(with_data=True, **kwargs)

    def to_json(self, **kwargs) -> str:
        """Uses treelib to convert nodes to a JSON structure"""
        return self._treelib_obj.to_json(with_data=True, **kwargs)

    def to_graphviz(self, shape: str = "plain", layout_dir: str = "LR", **kwargs) -> str:
        """
        This method leverages the treelib graphviz function, but instead of printing
        to the stdout this is captured and returned as a string object. Additionally
        the returned graphviz definition is extended to add a layout direction

        Args:
            shape: The shape to render each node
            layout_dir: The direction which the tree will render
            **kwargs: Any extra arguments to pass to treelib.tree.Tree.to_graphviz

        Returns:
            A string of graphviz configuration ready for rendering in another tool
        """

        # If graphviz object is already generated, retrieve cached version
        if self._graphviz_cached is not None:
            return self._graphviz_cached

        # treelib graphviz writes once to stdout
        stream = io.StringIO()
        with redirect_stdout(stream):
            self._treelib_obj_params.to_graphviz(shape=shape, **kwargs)
        output = stream.getvalue()

        # Replace closing } tag with layout condition
        output_with_layout = output.replace("}", f'rankdir="{layout_dir}";\n}}')

        # save to attr so that we can call >1x
        self._graphviz_cached = output_with_layout
        return self._graphviz_cached

    def print(self, **kwargs):
        """Uses built in treelib print function"""
        return self._treelib_obj_params.show(**kwargs)

    def rich_print(self, return_object: bool = False):
        """Converts treelib structure to rich.tree.Tree object
        and prints it to the console"""

        result = build_rich_tree(self._treelib_obj, return_obj=return_object)
        if return_object:
            return result
