from typing import Union, Dict, Any, List

from click import Command, Group, MultiCommand

from src.click_tree_viz import _ClickNode


def recurse(
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
        recurse(
            click_structure=_as_dict(click_obj),
            current_path=(current_path + [clean_name]),
            all_paths=all_paths,
        )
    return all_paths
