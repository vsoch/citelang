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


def generate(data, outfile=None, min_credit=0.01, height=800):
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
        title={
            "text": "Credit allocation for %s<br><sup>The total credit graph adds to ~1, and cutoffi is %s</sup>"
            % (data["name"], min_credit),
            "x": 0.5,
        },
        font={"size": 12},
        showlegend=False,
        autosize=False,
        height=height,
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
    node_name = "%s<br>%s" % (
        tree_dict["name"],
        round(tree_dict["credit"], tree_dict["round_by"]),
    )
    labels.append(node_name)
    values.append(tree_dict["size"])
    for child in tree_dict.get("children"):
        parents.append(node_name)
        unwrap_tree(child, labels, parents, values)
    return labels, parents, values
