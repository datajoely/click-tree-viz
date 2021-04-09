import json

from .examples.naval import naval

from src.click_tree_viz import ClickTreeViz


def test_naval():
    naval_cli = naval.cli
    tree = ClickTreeViz(naval_cli)
    tree.print()  # prove this works without error
    dict_data = tree.to_dict()
    assert len(dict_data.keys()) == 1
    assert set(
        [list(x.keys())[0] for x in dict_data['CLI']['children']]
    ) == {'mine', 'ship'}

    assert json.dumps(tree.to_dict()) == tree.to_json()

    graph_viz = tree.to_graphviz()
    assert graph_viz.count('->') == 7
