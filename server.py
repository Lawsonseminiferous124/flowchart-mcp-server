from pathlib import Path
from graphviz import Digraph
from mcp.server.fastmcp import FastMCP, Image

mcp = FastMCP("flowchart-server")

OUTPUT_DIR = Path("charts")
OUTPUT_DIR.mkdir(exist_ok=True)

_STYLES: dict[str, dict] = {
    "academic": {
        "graph": {
            "bgcolor": "white",
            "fontname": "Helvetica",
            "splines": "polyline",
            "nodesep": "0.9",
            "ranksep": "1.3",
            "pad": "0.6",
        },
        "node": {"fontname": "Helvetica", "fontsize": "11", "margin": "0.35,0.22", "penwidth": "2.0"},
        "edge": {"fontname": "Helvetica", "fontsize": "10", "penwidth": "1.5"},
        "types": {
            "start":      {"shape": "oval",         "style": "filled", "fillcolor": "white",   "fontcolor": "black"},
            "end":        {"shape": "oval",         "style": "filled", "fillcolor": "black",   "fontcolor": "white"},
            "process":    {"shape": "box",          "style": "filled", "fillcolor": "white",   "fontcolor": "black"},
            "decision":   {"shape": "diamond",      "style": "filled", "fillcolor": "white",   "fontcolor": "black", "width": "2.2"},
            "io":         {"shape": "parallelogram","style": "filled", "fillcolor": "white",   "fontcolor": "black"},
            "subprocess": {"shape": "box",          "style": "filled", "fillcolor": "white",   "fontcolor": "black", "peripheries": "2"},
            "connector":  {"shape": "circle",       "style": "filled", "fillcolor": "white",   "fontcolor": "black", "width": "0.55", "height": "0.55"},
            "annotation": {"shape": "note",         "style": "filled", "fillcolor": "#F5F5F5", "fontcolor": "black"},
        },
    },

    "colorful": {
        "graph": {
            "bgcolor": "white",
            "fontname": "Helvetica",
            "splines": "polyline",
            "nodesep": "0.9",
            "ranksep": "1.3",
            "pad": "0.6",
        },
        "node": {"fontname": "Helvetica", "fontsize": "12", "margin": "0.4,0.25", "width": "1.6"},
        "edge": {"fontname": "Helvetica", "fontsize": "10"},
        "types": {
            "start":      {"shape": "oval",         "style": "filled,rounded", "fillcolor": "#27AE60", "fontcolor": "white"},
            "end":        {"shape": "oval",         "style": "filled,rounded", "fillcolor": "#C0392B", "fontcolor": "white"},
            "process":    {"shape": "box",          "style": "filled,rounded", "fillcolor": "#2980B9", "fontcolor": "white"},
            "decision":   {"shape": "diamond",      "style": "filled",         "fillcolor": "#E67E22", "fontcolor": "white", "width": "2.2"},
            "io":         {"shape": "parallelogram","style": "filled",         "fillcolor": "#16A085", "fontcolor": "white"},
            "subprocess": {"shape": "box",          "style": "filled,rounded", "fillcolor": "#8E44AD", "fontcolor": "white", "peripheries": "2"},
            "connector":  {"shape": "circle",       "style": "filled",         "fillcolor": "#7F8C8D", "fontcolor": "white", "width": "0.6",  "height": "0.6"},
            "annotation": {"shape": "note",         "style": "filled",         "fillcolor": "#FEF9E7", "fontcolor": "#7D6608"},
        },
    },

    "minimal": {
        "graph": {
            "bgcolor": "white",
            "fontname": "Helvetica",
            "splines": "spline",
            "nodesep": "0.7",
            "ranksep": "1.1",
            "pad": "0.6",
        },
        "node": {"fontname": "Helvetica", "fontsize": "11", "margin": "0.35,0.22"},
        "edge": {"fontname": "Helvetica", "fontsize": "10", "color": "#78909C"},
        "types": {
            "start":      {"shape": "oval",         "style": "filled",         "fillcolor": "#CFD8DC", "fontcolor": "#212121"},
            "end":        {"shape": "oval",         "style": "filled",         "fillcolor": "#455A64", "fontcolor": "white"},
            "process":    {"shape": "box",          "style": "filled,rounded", "fillcolor": "#F5F5F5", "fontcolor": "#212121"},
            "decision":   {"shape": "diamond",      "style": "filled",         "fillcolor": "#ECEFF1", "fontcolor": "#212121", "width": "2.2"},
            "io":         {"shape": "parallelogram","style": "filled",         "fillcolor": "#F5F5F5", "fontcolor": "#212121"},
            "subprocess": {"shape": "box",          "style": "filled,rounded", "fillcolor": "#ECEFF1", "fontcolor": "#212121", "peripheries": "2"},
            "connector":  {"shape": "circle",       "style": "filled",         "fillcolor": "#B0BEC5", "fontcolor": "white",   "width": "0.55", "height": "0.55"},
            "annotation": {"shape": "note",         "style": "filled",         "fillcolor": "#FAFAFA", "fontcolor": "#546E7A"},
        },
    },
}

_DEFAULT_NODE = {"shape": "box", "style": "filled,rounded", "fillcolor": "#95A5A6", "fontcolor": "white"}


def _render(
    nodes: list[dict],
    edges: list[dict],
    title: str,
    filename: str,
    style_name: str,
) -> bytes:
    """Core Graphviz rendering logic."""
    style = _STYLES.get(style_name, _STYLES["colorful"])
    type_styles = style["types"]

    dot = Digraph(format="svg")

    dot.attr(**style["graph"])
    dot.attr("node", **style["node"])
    dot.attr("edge", **style["edge"])

    if title:
        dot.attr(
            label=title,
            labelloc="t",
            labelfontsize="14",
            labelfontname="Helvetica-Bold",
        )

    for node in nodes:
        nid = str(node["id"])
        ntype = str(node.get("type", "process")).lower()
        label = str(node.get("label", nid))
        attrs = dict(type_styles.get(ntype, _DEFAULT_NODE))
        dot.node(nid, label=label, **attrs)

    for edge in edges:
        src = str(edge["from"])
        dst = str(edge["to"])
        label = str(edge.get("label", ""))
        dot.edge(src, dst, label=f" {label} " if label else "")

    output_path = str(OUTPUT_DIR / filename)
    rendered = dot.render(output_path, cleanup=True)
    with open(rendered, "rb") as f:
        return f.read()


@mcp.tool()
def generate_flowchart(
    nodes: list[dict],
    edges: list[dict],
    title: str = "",
    filename: str = "flowchart",
    style: str = "colorful",
) -> Image:
    """
    Render a flowchart SVG from a node/edge spec that you construct.

    You decide what goes in the chart — from a natural language description, a concept
    explanation, or code you read via the filesystem connector. Think through the full
    logical flow, then call this tool once with the complete spec.

    nodes: list of dicts, each with:
        id    (str) - unique identifier, e.g. "n1" or "check_auth"
        type  (str) - node type (see below)
        label (str) - text shown in the shape, keep it concise

    edges: list of dicts, each with:
        from  (str) - source node id
        to    (str) - destination node id
        label (str, optional) - e.g. "Yes", "No", "error"

    title    (str, optional) - chart title shown at the top
    filename (str, optional) - base name for the saved SVG file
    style    (str, optional) - "colorful" (default), "academic", or "minimal"

    Node types:
        start       oval             entry point (exactly one)
        end         oval             exit point (one or more)
        process     rectangle        computation or action
        decision    diamond          branch; always label both outgoing edges
        io          parallelogram    user input or program output
        subprocess  double rectangle named function or sub-process call
        connector   small circle     off-page connector
        annotation  note shape       clarifying comment

    Quality guidelines:
        - Every flowchart must have exactly one start and at least one end.
        - Decision nodes must have exactly two outgoing edges with contrasting labels.
        - Make loops explicit with a back-edge from the loop tail to the loop head.
        - Use subprocess for any named function call.
        - Prefer many small nodes over one giant process box.
    """
    data = _render(nodes, edges, title, filename, style)
    return Image(data=data, format="svg")


@mcp.tool()
def list_charts() -> list[str]:
    """List all previously generated flowchart SVG files in the charts/ directory."""
    charts = sorted(OUTPUT_DIR.glob("*.svg"))
    return [str(c) for c in charts] if charts else ["No charts generated yet."]


if __name__ == "__main__":
    mcp.run()