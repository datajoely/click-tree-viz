import io
from contextlib import redirect_stdout
from copy import deepcopy
from dataclasses import dataclass
from typing import Union, Dict, Any, List, Optional

from click import Group, MultiCommand
from treelib.tree import Tree

from traversal_utils import recurse

@dataclass
class _ClickNode:
    name: str
    route: List[str]
    params: List[Dict[str, Any]]
    is_group: bool
    help: Optional[str] = None

    @property
    def is_root(self) -> bool:
        return len(self.route) <= 1

    @property
    def parent_name(self) -> str:
        if len(self.route) > 1:
            return self.route[-2]
        return self.route[0]

    @property
    def parent_path(self) -> str:
        if len(self.route) > 1:
            return ".".join(self.route[:-1])
        return self.route[0]

    @property
    def path(self) -> str:
        return ".".join(self.route)

    def as_dict(self):
        return self.__dict__


class ClickTreeViz:
    def __init__(self, click_stuct: Union[MultiCommand, Group]):
        self._raw_struct = deepcopy(click_stuct)
        self._clean_struct = recurse(self._raw_struct)
        self.tree = self._as_tree(self._clean_struct)
        self._graphviz = None

    @staticmethod
    def _as_tree(struct: List[_ClickNode]):
        # Use tree lib to take clean struct and hold in memory
        working_tree = Tree()
        working_tree.create_node(tag="CLI", identifier="CLI", data="🌴")
        for leaf in struct:

            working_tree.create_node(
                tag=leaf.name,
                identifier=leaf.path,
                data=leaf.as_dict(),
                parent="CLI" if leaf.is_root else leaf.parent_path,
            )

        return working_tree

    def to_dict(self) -> Dict[str, Any]:
        return self.tree.to_dict(with_data=True)

    def to_json(self) -> str:
        return self.tree.to_json(with_data=True)

    def to_graphviz(self) -> str:
        if self._graphviz is not None:
            return self._graphviz

        # treelib graphviz writes once to stdout
        stream = io.StringIO()
        with redirect_stdout(stream):
            self.tree.to_graphviz()
        output = stream.getvalue()

        # save to attr so that we can call >1x
        self._graphviz = output
        return self._graphviz

    def print(self):
        return self.tree.show()
