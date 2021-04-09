import io
from contextlib import redirect_stdout
from copy import deepcopy
from dataclasses import dataclass
from typing import Union, Dict, Any, List, Optional

from click import Group, MultiCommand, Command
from treelib.tree import Tree


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
            return '.'.join(self.route[:-1])
        return self.route[0]

    @property
    def path(self) -> str:
        return '.'.join(self.route)

    def as_dict(self):
        return self.__dict__


class ClickTreeViz:
    def __init__(self, click_stuct: Union[MultiCommand, Group]):
        self._raw_struct = deepcopy(click_stuct)
        self._clean_struct = traverse_down(self._raw_struct)
        self.tree = self._as_tree(self._clean_struct)
        self._graphviz = None

    @staticmethod
    def _as_tree(struct: List[_ClickNode]):
        # Use tree lib to take clean struct and hold in memory
        working_tree = Tree()
        working_tree.create_node(tag='CLI', identifier='CLI', data='🌴')
        for leaf in struct:
            try:
                working_tree.create_node(
                    tag=leaf.name,
                    identifier=leaf.path,
                    data=leaf.as_dict(),
                    parent='CLI' if leaf.is_root else leaf.parent_path
                )
            except:
                breakpoint()

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


def traverse_down(
        click_structure: Union[Dict[str, Any], Command, Group, MultiCommand],
        current_path: List[Any] = None,
        all_paths: List[Any] = None,
) -> List[_ClickNode]:
    if current_path is None and all_paths is None:
        current_path = []
        all_paths = []

    def _as_dict(obj: Union[Dict[str, Any], Command, Group]) -> Union[Dict[str, Any]]:
        """Aids recursion so that we are always working with dictionaries"""
        if hasattr(obj, "commands"):
            return obj.commands
        elif isinstance(obj, dict):
            return obj
        else:
            return {}

    def _is_group(obj: Union[Group, Command, MultiCommand]) -> bool:
        return isinstance(obj, Group) and hasattr(obj, "commands")

    def _get_params(obj: Union[Group, Command, MultiCommand]) -> List[Dict[str, Any]]:
        return [x.opts for x in obj.params]

    for clean_name, click_obj in _as_dict(click_structure).items():
        all_paths.append(
            _ClickNode(
                name=clean_name,
                route=current_path + [clean_name],
                is_group=_is_group(click_obj),
                params=_get_params(click_obj),
                help=click_obj.help,
            )
        )

        # Recurse down
        traverse_down(
            click_structure=_as_dict(click_obj),
            current_path=(current_path + [clean_name]),
            all_paths=all_paths,
        )
    return all_paths
