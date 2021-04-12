"""
This module provides utilities for traversing Click CLI structure
"""

from typing import Union, Dict, Any, List, Optional
from dataclasses import dataclass

from click import Command, Group, MultiCommand


@dataclass
class ClickNode:
    """
    This dataclass stores relevant metadata for each Click command type in a format
    easy to manipulate and work with
    """

    name: str
    route: List[str]
    params: List[Dict[str, Any]]
    is_group: bool
    help: Optional[str] = None

    @property
    def is_root(self) -> bool:
        """Boolean if this object represent the top level of the CLI tree"""
        return len(self.route) <= 1

    @property
    def parent_name(self) -> str:
        """The name of the object directly above this one in the CLI tree"""
        if len(self.route) > 1:
            return self.route[-2]
        return self.route[0]

    @property
    def parent_path(self) -> str:
        """The route to the object directly above this one in the CLI tree"""
        if len(self.route) > 1:
            return ".".join(self.route[:-1])
        return self.route[0]

    @property
    def path(self) -> str:
        """The route to this object in the CLI tree"""
        return ".".join(self.route)

    def as_dict(self) -> Dict[str, Any]:
        """Convenience method which returns this object as a JSON serialisable one"""
        return self.__dict__


def _as_dict(cli_obj: Union[Dict[str, Any], Command, Group]) -> Union[Dict[str, Any]]:
    """Aids recursion so that recursion focuses on dictionary objects"""
    if hasattr(cli_obj, "commands"):
        return cli_obj.commands

    if isinstance(cli_obj, dict):
        return cli_obj

    return {}


def _is_group(cli_obj: Union[Group, Command, MultiCommand]) -> bool:
    """Detects if cli obj is a Group or not"""
    return isinstance(cli_obj, Group) and hasattr(cli_obj, "commands")


def _get_params(cli_obj: Union[Group, Command, MultiCommand]) -> List[Dict[str, Any]]:
    """This method extracts parameters from the cli object"""
    return [
        {
            **dict(type=x.param_type_name, name=x.name, opts=x.opts),
            **(dict(help=x.help) if hasattr(x, "help") else {}),
        }
        for x in cli_obj.params
    ]


def recurse_click_cli(
    click_structure: Union[Dict[str, Any], Command, Group, MultiCommand],
    current_path: List[Any] = None,
    all_paths: List[Any] = None,
) -> List[ClickNode]:
    """
    This method performs a depth first traversal of the Click CLI object in order
    to retrieve the relevant metadata from each node
    Args:
        click_structure: The CLI structure to process in each iteration
        current_path: The path exhausted in each recursion
        all_paths: The complete list of paths exhausted in all recursions thus far

    Returns:
        A list of all nodes and associated metadata for the entire CLI tree

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
        recurse_click_cli(
            click_structure=_as_dict(click_obj),
            current_path=(current_path + [clean_name]),
            all_paths=all_paths,
        )
    return all_paths
