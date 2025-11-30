"""
Generate a Mermaid call graph for the project (functions, parameters, calls).

What it does:
    - Parses Python files in the project root (excluding dot/underscore files and mermaid-scheme).
    - Builds nodes for each function with parameters and first docstring line.
    - Adds edges for function calls resolved by name (static AST).
    - Groups nodes by module as Mermaid subgraphs.

Usage:
    python mermaid-scheme/generate_mermaid_callgraph.py --output project_callgraph.mmd

Options:
    --format flowchart|graph            (default: flowchart)
    --rankdir TB|LR                     (default: TB)
    --max-edges N                       (default: 12, limit fan-out per function)
    --root PATH                         (default: project root = parent of this script)
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


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
        base = f"{self.name}({args_str})"
        if self.doc:
            return f"{base}<br/>{self.doc}"
        return base


def sanitize_id(name: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in name)


def parse_functions(path: Path, module_name: str) -> List[FunctionInfo]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    functions: List[FunctionInfo] = []
    current_stack: List[str] = []
    calls_map: Dict[str, List[str]] = {}

    def call_name(node: ast.AST) -> Optional[str]:
        func = node.func if isinstance(node, ast.Call) else node
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
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

    for fn in functions:
        fn.calls = calls_map.get(fn.name, [])
    return functions


def collect_project_functions(root: Path) -> List[FunctionInfo]:
    funcs: List[FunctionInfo] = []
    for path in sorted(root.glob("*.py")):
        if path.name.startswith(".") or path.name.startswith("_"):
            continue
        if path.parts and "mermaid-scheme" in path.parts:
            continue
        module = path.stem
        funcs.extend(parse_functions(path, module))
    return funcs


def resolve_calls(funcs: List[FunctionInfo]) -> List[Tuple[str, str]]:
    name_to_fq: Dict[str, Set[str]] = {}
    for f in funcs:
        name_to_fq.setdefault(f.name, set()).add(f.fqname)

    edges: List[Tuple[str, str]] = []
    for f in funcs:
        for callee in f.calls:
            for target in name_to_fq.get(callee, ()):
                edges.append((f.fqname, target))
    return edges


def build_mermaid(
    funcs: List[FunctionInfo],
    edges: List[Tuple[str, str]],
    rankdir: str = "TB",
    max_edges: Optional[int] = 12,
    diagram_type: str = "flowchart",
) -> str:
    lines: List[str] = []
    direction = "TD" if rankdir == "TB" else "LR"
    lines.append(f"{diagram_type} {direction}")

    # group by module
    by_module: Dict[str, List[FunctionInfo]] = {}
    for f in funcs:
        by_module.setdefault(f.module, []).append(f)

    node_ids: Dict[str, str] = {}
    for module, items in sorted(by_module.items()):
        lines.append(f'  subgraph "{module}"')
        lines.append("    direction TB")
        for fn in sorted(items, key=lambda x: x.name):
            node_id = sanitize_id(fn.fqname)
            node_ids[fn.fqname] = node_id
            label = fn.label().replace('"', "'")
            lines.append(f'    {node_id}["{label}"]')
        lines.append("  end")

    # deduplicate edges
    unique_edges: Dict[str, Set[str]] = {}
    for src, dst in edges:
        unique_edges.setdefault(src, set()).add(dst)

    # apply pruning
    for src, dsts in unique_edges.items():
        sorted_dsts = sorted(dsts)
        keep = sorted_dsts if max_edges is None else sorted_dsts[:max_edges]
        for dst in keep:
            if src in node_ids and dst in node_ids:
                lines.append(f"  {node_ids[src]} --> {node_ids[dst]}")
        if max_edges is not None and len(sorted_dsts) > max_edges:
            lines.append(f'  %% pruned {len(sorted_dsts) - max_edges} edges from {src}')

    # legend
    lines.append("  %% Legend")
    lines.append('  note1["function(args)<br/>first doc line"]:::legend')
    lines.append("  classDef legend fill:#fef3c7,stroke:#facc15,color:#1f2937;")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generate Mermaid call graph for the project.")
    parser.add_argument("--output", default="project_callgraph.mmd", help="Output file path")
    parser.add_argument("--format", default="flowchart", choices=["flowchart", "graph"], help="Mermaid diagram type")
    parser.add_argument("--rankdir", default="TB", choices=["TB", "LR"], help="Layout direction")
    parser.add_argument("--max-edges", type=int, default=12, help="Max outgoing edges per function (prunes high fan-out)")
    parser.add_argument("--root", default=None, help="Project root (default: parent of this script)")
    args = parser.parse_args()

    project_root = Path(args.root) if args.root else Path(__file__).resolve().parent.parent
    funcs = collect_project_functions(project_root)
    edges = resolve_calls(funcs)

    mermaid_text = build_mermaid(
        funcs,
        edges,
        rankdir=args.rankdir,
        max_edges=args.max_edges,
        diagram_type=args.format,
    )

    output_path = Path(args.output)
    output_path.write_text(mermaid_text, encoding="utf-8")
    print(f"Wrote Mermaid call graph to {output_path}")


if __name__ == "__main__":
    main()
