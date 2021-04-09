from typing import Union, Dict, Any, List, Optional
from dataclasses import dataclass

from click import Command, Group, MultiCommand


@dataclass
class ClickNode:
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


def _as_dict(cli_obj: Union[Dict[str, Any], Command, Group]) -> Union[Dict[str, Any]]:
    """Aids recursion so that recursion focuses on dictionary objects"""
    if hasattr(cli_obj, "commands"):
        return cli_obj.commands
    elif isinstance(cli_obj, dict):
        return cli_obj
    else:
        return {}


def _is_group(cli_obj: Union[Group, Command, MultiCommand]) -> bool:
    """Detects if cli obj is a Group or not"""
    return isinstance(cli_obj, Group) and hasattr(cli_obj, "commands")


def _get_params(cli_obj: Union[Group, Command, MultiCommand]) -> List[Dict[str, Any]]:
    """This method extracts parameters from the cli object"""
    return [x.opts for x in cli_obj.params]


def recurse(
    click_structure: Union[Dict[str, Any], Command, Group, MultiCommand],
    current_path: List[Any] = None,
    all_paths: List[Any] = None,
) -> List[ClickNode]:
    """

    Args:
        click_structure:
        current_path:
        all_paths:

    Returns:

    """
    if current_path is None and all_paths is None:
        current_path = []
        all_paths = []

    for clean_name, click_obj in _as_dict(click_structure).items():
        all_paths.append(
            ClickNode(
                name=clean_name,
                route=current_path + [clean_name],
                is_group=_is_group(click_obj),
                params=_get_params(click_obj),
                help=click_obj.help,
            )
        )

        # Recurse down
        recurse(
            click_structure=_as_dict(click_obj),
            current_path=(current_path + [clean_name]),
            all_paths=all_paths,
        )
    return all_paths
