import io
from contextlib import redirect_stdout
from copy import deepcopy
from typing import Union, Dict, Any, List

from click import Group, MultiCommand
from treelib.tree import Tree

from traversal_utils import recurse


class ClickTreeViz:
    def __init__(self, click_stuct: Union[MultiCommand, Group]):
        self._raw_struct = deepcopy(click_stuct)
        self._clean_struct = recurse(self._raw_struct)
        self.treelib = self._as_tree(self._clean_struct)
        self._graphviz = None

    @staticmethod
    def _as_tree(struct: List[Any]):
        # Use tree lib to take clean struct and hold in memory
        working_tree = Tree()
        working_tree.create_node(identifier="CLI", data="🌴")
        for leaf in struct:
            working_tree.create_node(
                identifier=leaf.path,
                data=leaf.as_dict(),
                parent="CLI" if leaf.is_root else leaf.parent_path,
            )

        return working_tree

    def to_dict(self) -> Dict[str, Any]:
        return self.treelib.to_dict(with_data=True)

    def to_json(self) -> str:
        return self.treelib.to_json(with_data=True)

    def to_graphviz(self) -> str:
        if self._graphviz is not None:
            return self._graphviz

        # treelib graphviz writes once to stdout
        stream = io.StringIO()
        with redirect_stdout(stream):
            self.treelib.to_graphviz()
        output = stream.getvalue()

        # save to attr so that we can call >1x
        self._graphviz = output
        return self._graphviz

    def boring_print(self):
        return self.treelib.show()

    def rich_print(self):
        raise NotImplementedError
