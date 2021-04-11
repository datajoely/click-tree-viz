import json

from .examples.naval import naval

from click_tree_viz import ClickTreeViz
from rich_utils import build_rich_tree


def test_naval():
    naval_cli = naval.cli
    tree = ClickTreeViz(naval_cli)
    tree.boring_print()  # prove this works without error
    dict_data = tree.to_dict()
    assert len(dict_data.keys()) == 1
    assert set(
        [list(x.keys())[0] for x in dict_data['CLI']['children']]
    ) == {'mine', 'ship'}

    assert json.dumps(tree.to_dict()) == tree.to_json()

    graph_viz = tree.to_graphviz()
    assert graph_viz.count('->') == 7


def test_naval_rich_tree():
    naval_cli = naval.cli
    tree = ClickTreeViz(naval_cli)
    build_rich_tree(tree.treelib)
