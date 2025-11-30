"""
Generate a structural flowchart (function call graph + parameters) for the project.

Focus:
    - Clusters by file (module)
    - Nodes are functions with their parameters
    - Edges represent calls between functions (resolved by static analysis of AST)

Usage:
    python generate_structural_flowchart.py [png|svg|pdf] [--root PROJECT_ROOT]

Default format: png

Note: Requires graphviz installed (both Python package and system binaries).
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from graphviz import Digraph


# Style presets
NODE_STYLE = {
    "shape": "box",
    "style": "rounded,filled",
    "fontname": "Helvetica",
    "fontsize": "10",
    "color": "#1f2937",
    "fillcolor": "#e5e7eb",
    "penwidth": "1.4",
}

EDGE_STYLE = {
    "fontname": "Helvetica",
    "fontsize": "9",
    "color": "#4b5563",
    "penwidth": "1.2",
}


@dataclass
class FunctionInfo:
    module: str
    name: str
    args: List[str]
    doc: str = ""
    calls: List[str] = field(default_factory=list)

    @property
    def fqname(self) -> str:
        return f"{self.module}.{self.name}"

    def label(self) -> str:
        args_str = ", ".join(self.args)
        doc_line = f"\n{self.doc}" if self.doc else ""
        return f"{self.name}({args_str}){doc_line}"


def parse_functions(path: Path, module_name: str) -> List[FunctionInfo]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    functions: List[FunctionInfo] = []
    current_stack: List[str] = []
    calls_map: Dict[str, List[str]] = {}

    def call_name(node: ast.AST) -> Optional[str]:
        if isinstance(node, ast.Call):
            func = node.func
        else:
            func = node
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            # attr of something, use attribute name
            return func.attr
        return None

    class Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef):
            func_name = node.name
            args = [a.arg for a in node.args.args]
            if args and args[0] == "self":
                args = args[1:]
            doc = (ast.get_docstring(node) or "").strip().splitlines()
            doc_first = doc[0] if doc else ""
            functions.append(FunctionInfo(module_name, func_name, args, doc_first))
            current_stack.append(func_name)
            self.generic_visit(node)
            current_stack.pop()

        def visit_Call(self, node: ast.Call):
            if current_stack:
                caller = current_stack[-1]
                callee = call_name(node)
                if callee:
                    calls_map.setdefault(caller, []).append(callee)
            self.generic_visit(node)

    Visitor().visit(tree)

    # Attach calls to corresponding functions
    for fn in functions:
        fn.calls = calls_map.get(fn.name, [])
    return functions


def collect_project_functions(root: Path) -> List[FunctionInfo]:
    funcs: List[FunctionInfo] = []
    for path in sorted(root.glob("*.py")):
        if path.name.startswith(".") or path.name.startswith("_"):
            continue
        if path.name in {"setup.py", "mermaid-scheme"}:
            continue
        module = path.stem
        funcs.extend(parse_functions(path, module))
    return funcs


def resolve_calls(funcs: List[FunctionInfo]) -> List[Tuple[str, str]]:
    """
    Resolve calls between known functions by name (case-sensitive).
    If multiple modules define the same name, connect to all matches.
    """
    name_to_fq: Dict[str, Set[str]] = {}
    for f in funcs:
        name_to_fq.setdefault(f.name, set()).add(f.fqname)

    edges: List[Tuple[str, str]] = []
    for f in funcs:
        for callee_name in f.calls:
            targets = name_to_fq.get(callee_name, set())
            for target in targets:
                edges.append((f.fqname, target))
    return edges


def build_graph(
    funcs: List[FunctionInfo],
    edges: List[Tuple[str, str]],
    fmt: str,
    prune_threshold: Optional[int] = 8,
    rankdir: str = "TB",
) -> Digraph:
    dot = Digraph(comment="Structural Flowchart", format=fmt)
    dot.attr(
        rankdir=rankdir,
        bgcolor="white",
        pad="0.5",
        nodesep="0.6",
        ranksep="1.0",
        dpi="300",
        splines="ortho",
        concentrate="true",
    )
    dot.attr("node", **NODE_STYLE)
    dot.attr("edge", **EDGE_STYLE)

    # Cluster by module
    by_module: Dict[str, List[FunctionInfo]] = {}
    for f in funcs:
        by_module.setdefault(f.module, []).append(f)

    for module, items in sorted(by_module.items()):
        with dot.subgraph(name=f"cluster_{module}") as sub:
            sub.attr(label=module, style="filled", color="#dbeafe", penwidth="2")
            for fn in sorted(items, key=lambda x: x.name):
                sub.node(fn.fqname, fn.label(), fillcolor="#bfdbfe")

    # Deduplicate edges
    unique_edges = {}
    for src, dst in edges:
        unique_edges.setdefault(src, set()).add(dst)

    # Optional pruning to reduce spaghetti
    if prune_threshold is not None:
        pruned_edges = []
        for src, dsts in unique_edges.items():
            sorted_dsts = sorted(dsts)
            keep = sorted_dsts[:prune_threshold]
            pruned_edges.extend((src, d) for d in keep)
        edges_to_draw = pruned_edges
    else:
        edges_to_draw = [(s, d) for s, dsts in unique_edges.items() for d in dsts]

    # Edges with same-module coloring
    for src, dst in edges_to_draw:
        src_mod = src.split(".")[0]
        dst_mod = dst.split(".")[0]
        edge_kwargs = {}
        if src_mod != dst_mod:
            edge_kwargs["color"] = "#0f172a"
            edge_kwargs["penwidth"] = "1.4"
        dot.edge(src, dst, **edge_kwargs)

    # Legend
    with dot.subgraph(name="cluster_legend") as leg:
        leg.attr(label="Legend", style="dashed", color="#e5e7eb")
        leg.node("legend_fn", "function(args)\n[first doc line]", shape="note", fillcolor="#fef3c7")
        leg.node("legend_call", "call edge", shape="plaintext")
        leg.edge("legend_fn", "legend_call", style="solid")

    return dot


def main():
    parser = argparse.ArgumentParser(description="Generate structural flowchart (call graph) for the project.")
    parser.add_argument("format", nargs="?", default="png", choices=["png", "svg", "pdf"], help="Output format")
    parser.add_argument("--root", default=None, help="Project root path (default: parent of this script)")
    parser.add_argument("--no-prune", action="store_true", help="Do not prune high fan-out nodes")
    parser.add_argument("--rankdir", default="TB", choices=["TB", "LR"], help="Graph orientation (top-bottom or left-right)")
    args = parser.parse_args()

    project_root = Path(args.root) if args.root else Path(__file__).resolve().parent.parent
    funcs = collect_project_functions(project_root)
    edges = resolve_calls(funcs)
    prune_threshold = None if args.no_prune else 8
    graph = build_graph(funcs, edges, args.format, prune_threshold=prune_threshold, rankdir=args.rankdir)

    output_name = f"structural_flowchart.{args.format}"
    output_path = graph.render(output_name, view=False, cleanup=True)
    print(f"Rendered: {output_path}")


if __name__ == "__main__":
    main()
