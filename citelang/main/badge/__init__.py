__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from citelang.logger import logger
import citelang.main.colors as colors


try:
    import plotly.graph_objs as go
except ImportError:
    logger.exit(
        "Plotly and dependencies are needed to generate this badge. pip install citelang[badge]."
    )


def generate(data, outfile=None):
    """
    Generate a static badge
    """
    labels, parents, values = unwrap_tree(data)
    ids, parentids = get_ids(labels, parents)

    # colors for subtrees
    colorset = colors.get_color_range(N=data["levels"] - 1)

    # add color for root (white)
    colorset = ["#ffffff"] + [str(x) for x in colorset]

    trace = go.Sunburst(
        ids=ids,
        labels=labels,
        parents=parentids,
        values=values,
        marker={"colors": colorset, "line": {"width": 1.5}},
    )

    layout = go.Layout(
        title={"text": "Package " + data["name"], "x": 0.5},
        font={"size": 12},
        showlegend=False,
        autosize=False,
        height=750,
        xaxis={"visible": False},
        yaxis={"visible": False},
        hovermode="closest",
    )

    fig = go.Figure(data=[trace], layout=layout)
    if outfile:
        fig.write_image(outfile)
    return fig


def get_ids(labels, parents):
    """
    Given labels and parent node ids, generate labels for the nodes.
    """
    if len(labels) != len(parents):
        logger.exit(
            "The list of labels should have the same length like the list of parents"
        )
    ids = [str(id) for id in range(len(labels))]

    # associate to each label the corresponding id
    dlabels = {label: idx for label, idx in zip(labels, ids)}

    # empty is for the root node
    parentids = [""] + [dlabels[label] for label in parents[1:]]
    return ids, parentids


def unwrap_tree(tree_dict, labels=None, parents=None, values=None):
    """
    Given a typical structured data with nodes and children, unwrap into flat lists.
    """
    labels = labels or []
    parents = parents or [""]
    values = values or []
    labels.append(tree_dict["name"])
    values.append(tree_dict["weight"])
    last_node = tree_dict["name"]
    for child in tree_dict.get("children"):
        parents.append(last_node)
        unwrap_tree(child, labels, parents, values)
    return labels, parents, values
