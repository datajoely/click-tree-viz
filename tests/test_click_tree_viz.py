import json

from .examples.naval import naval
from .examples.termui import termui

from click_tree_viz import ClickTreeViz
from rich_utils import build_rich_tree


def test_naval_cli():
    naval_cli = naval.cli
    tree = ClickTreeViz(naval_cli)
    tree.boring_print()  # prove this works without error
    dict_data = tree.to_dict()
    assert len(dict_data.keys()) == 1
    assert set([list(x.keys())[0] for x in dict_data["CLI"]["children"]]) == {
        "mine",
        "ship",
    }

    assert json.dumps(tree.to_dict()) == tree.to_json()

    graph_viz = tree.to_graphviz()
    assert graph_viz.count("->") == 21


def test_naval_rich_tree():
    naval_cli = naval.cli
    tree_obj = ClickTreeViz(naval_cli)
    rich_obj = build_rich_tree(tree_obj.treelib_obj, return_obj=True)
    tree_dict = tree_obj.to_dict()
    assert len(tree_dict['CLI'].keys()) == len(rich_obj.children)
    assert set([list(x.keys())[0] for x in tree_dict["CLI"]["children"]]) == set(
        x.label.renderable.renderables[0].plain.split()[-1] for x in rich_obj.children
    )


def test_termui_cli():
    termui_cli = termui.cli
    tree = ClickTreeViz(termui_cli)
    processed = tree.to_dict()
    expected = {
        "CLI": {
            "children": [
                {
                    "clear": {
                        "data": {
                            "help": "Clears the entire screen.",
                            "is_group": False,
                            "name": "clear",
                            "params": [],
                            "route": ["clear"],
                        }
                    }
                },
                {
                    "colordemo": {
                        "data": {
                            "help": "Demonstrates ANSI color " "support.",
                            "is_group": False,
                            "name": "colordemo",
                            "params": [],
                            "route": ["colordemo"],
                        }
                    }
                },
                {
                    "edit": {
                        "data": {
                            "help": "Opens an editor with some " "text in it.",
                            "is_group": False,
                            "name": "edit",
                            "params": [],
                            "route": ["edit"],
                        }
                    }
                },
                {
                    "locate": {
                        "data": {
                            "help": "Opens a file or URL In the "
                            "default application.",
                            "is_group": False,
                            "name": "locate",
                            "params": [
                                {"name": "url", "opts": ["url"], "type": "argument"}
                            ],
                            "route": ["locate"],
                        }
                    }
                },
                {
                    "menu": {
                        "data": {
                            "help": "Shows a simple menu.",
                            "is_group": False,
                            "name": "menu",
                            "params": [],
                            "route": ["menu"],
                        }
                    }
                },
                {
                    "open": {
                        "data": {
                            "help": "Opens a file or URL In the "
                            "default application.",
                            "is_group": False,
                            "name": "open",
                            "params": [
                                {"name": "url", "opts": ["url"], "type": "argument"}
                            ],
                            "route": ["open"],
                        }
                    }
                },
                {
                    "pager": {
                        "data": {
                            "help": "Demonstrates using the " "pager.",
                            "is_group": False,
                            "name": "pager",
                            "params": [],
                            "route": ["pager"],
                        }
                    }
                },
                {
                    "pause": {
                        "data": {
                            "help": "Waits for the user to press " "a button.",
                            "is_group": False,
                            "name": "pause",
                            "params": [],
                            "route": ["pause"],
                        }
                    }
                },
                {
                    "progress": {
                        "data": {
                            "help": "Demonstrates the " "progress bar.",
                            "is_group": False,
                            "name": "progress",
                            "params": [
                                {
                                    "help": "The number " "of items to " "process.",
                                    "name": "count",
                                    "opts": ["--count"],
                                    "type": "option",
                                }
                            ],
                            "route": ["progress"],
                        }
                    }
                },
            ],
            "data": None,
        }
    }
    assert expected == processed
