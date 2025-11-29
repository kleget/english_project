"""
Generate a detailed flowchart of the current project pipeline.

Usage:
    python generate_high_quality_flowchart.py [png|svg|pdf] [high|ultra]

Defaults:
    format = png
    quality = high

The script relies on graphviz. Install the Python bindings and system
graphviz package if rendering fails.
"""

import sys
from pathlib import Path
from graphviz import Digraph


# A light theme that stays readable when the graph grows.
NODE_STYLE = {
    "shape": "box",
    "style": "rounded,filled",
    "fontname": "Helvetica",
    "fontsize": "11",
    "color": "#1f2937",
    "fillcolor": "#e5e7eb",
    "penwidth": "1.6",
}

EDGE_STYLE = {
    "fontname": "Helvetica",
    "fontsize": "10",
    "color": "#4b5563",
    "penwidth": "1.4",
}


def create_flowchart() -> Digraph:
    dot = Digraph(comment="English Project High Quality Flowchart")
    dot.attr(rankdir="TB", bgcolor="white", pad="0.5", nodesep="0.7", ranksep="1.0")
    dot.attr(dpi="450")
    dot.attr("node", **NODE_STYLE)
    dot.attr("edge", **EDGE_STYLE)

    # Entry and orchestration (main.py)
    with dot.subgraph(name="cluster_entry") as entry:
        entry.attr(label="main.py orchestration", style="filled", color="#bfdbfe", penwidth="2")
        entry.node("start", "Script start\nstart_time set", fillcolor="#dbeafe")
        entry.node("init_db", "initialize_all_databases()\ncreate processed_books table\nfor each category under book/txt", fillcolor="#dbeafe")
        entry.node("pass1", "main(rootdir, 1)\nprocess only non_science folders", fillcolor="#bfdbfe")
        entry.node("pass2", "main(rootdir, 2)\nprocess all other folders", fillcolor="#bfdbfe")
        entry.edge("start", "init_db")
        entry.edge("init_db", "pass1")
        entry.edge("pass1", "pass2", style="bold", label="second pass after non_science")

    # File preparation (file_processing.py)
    with dot.subgraph(name="cluster_files") as files:
        files.attr(label="file_processing.py", style="filled", color="#fde68a", penwidth="2")
        files.node("rename", "rename_files_in_directory()\nnormalize dots/spaces in filenames", fillcolor="#fef3c7")
        files.node("walk_pdf", "os.walk(rootdir)\ncollect PDF files", fillcolor="#fef3c7")
        files.node("pdf_to_txt", "pdf_to_txt()\npdftotext -layout\nsave to book/txt", fillcolor="#fde68a")
        files.edge("rename", "walk_pdf")
        files.edge("walk_pdf", "pdf_to_txt")

    # Listing text files for processing
    with dot.subgraph(name="cluster_listing") as listing:
        listing.attr(label="file listing", style="filled", color="#c7d2fe", penwidth="2")
        listing.node("structure", "get_directory_structure()\n& get_all_folders()", fillcolor="#e0e7ff")
        listing.node("list_txt", "print_all_files_from_rootdir()\nflatten txt paths", fillcolor="#c7d2fe")
        listing.edge("structure", "list_txt")

    # Per-book pipeline
    with dot.subgraph(name="cluster_book") as book:
        book.attr(label="per book processing", style="filled", color="#a7f3d0", penwidth="2")
        book.node("filter_pass", "reqursion(..., start_num)\nfilter by pass:\n- pass1: only non_science\n- pass2: everything else", fillcolor="#ecfdf3")
        book.node("skip_processed", "is_book_processed()\nskip if already in processed_books", fillcolor="#d1fae5")
        book.node("detect_lang", "detect_main_language()\nfastText over samples", fillcolor="#a7f3d0", shape="ellipse")
        book.node("choose_stop", "select_from_table(..., global_union)\nfrom runonscience/ennonscience", fillcolor="#a7f3d0")
        book.edge("filter_pass", "skip_processed")
        book.edge("skip_processed", "detect_lang")
        book.edge("detect_lang", "choose_stop", label="pick stoplist db")

    # Text ingestion and cleanup (text_analysis.py + lemmatize.py)
    with dot.subgraph(name="cluster_text") as text:
        text.attr(label="text ingestion", style="filled", color="#bbf7d0", penwidth="2")
        text.node("read_txt", "get_txt_file()\nread book/txt/*.txt", fillcolor="#dcfce7")
        text.node("hyphen", "fix_hyphenated_words()\nremove soft hyphens & join split words", fillcolor="#bbf7d0")
        text.node("cleanup", "removing_anomaly()\nstrip digits/punctuation\nlength sanity checks", fillcolor="#bbf7d0")
        text.node("lemmatize", "parallel_lemmatize_mp()\nru: pymorphy3\nen: spaCy\nmultiprocessing", fillcolor="#86efac")
        text.node("count_words", "analysand_func_dict()\ncount lemmas", fillcolor="#86efac")
        text.edge("read_txt", "hyphen")
        text.edge("hyphen", "cleanup")
        text.edge("cleanup", "lemmatize")
        text.edge("lemmatize", "count_words")

    # Filtering and deduplication
    with dot.subgraph(name="cluster_clean") as clean:
        clean.attr(label="filter & similarity merge", style="filled", color="#fbcfe8", penwidth="2")
        clean.node("drop_nonscience", "filter out stop words\nexclude global_union from non_science", fillcolor="#fef2f2")
        clean.node("algo_cleaner", "algo_cleaner()\nwrap DSU merging\nreturns cleaned list + duplicates", fillcolor="#fbcfe8")
        clean.node("algo_dsu", "algo_DSU()\ncluster near words by length & Levenshtein", fillcolor="#fbcfe8")
        clean.node("merge_counts", "sum counts per cluster\nkeep representative word", fillcolor="#fbcfe8")
        clean.edge("drop_nonscience", "algo_cleaner")
        clean.edge("algo_cleaner", "algo_dsu", style="dashed", label="internal call")
        clean.edge("algo_dsu", "merge_counts", style="dashed")

    # Database writes
    with dot.subgraph(name="cluster_db") as db:
        db.attr(label="database_operations.py", style="filled", color="#c4b5fd", penwidth="2")
        db.node("create_table", "create_table()\ncreate book table if missing", fillcolor="#ddd6fe")
        db.node("insert_book", "insert_many_into_table(db, book)\nsave word counts", fillcolor="#c4b5fd")
        db.node("insert_deleted", "insert_many_into_table(delete.db)\nstore merged-away words", fillcolor="#c4b5fd")
        db.node("mark_processed", "mark_book_as_processed()\ntrack processed_books", fillcolor="#c4b5fd")
        db.edge("create_table", "insert_book")
        db.edge("insert_book", "insert_deleted")
        db.edge("insert_deleted", "mark_processed")

    # Aggregation per category database
    with dot.subgraph(name="cluster_agg") as agg:
        agg.attr(label="database_aggregation.py", style="filled", color="#fecdd3", penwidth="2")
        agg.node("intersection", "create_intersection_table()\nwords common to all books", fillcolor="#ffe4e6")
        agg.node("union", "create_union_table()\nmerge all words\nkeep translations subset", fillcolor="#fecdd3")
        agg.edge("intersection", "union")

    # Translation and caching
    with dot.subgraph(name="cluster_translate") as trans:
        trans.attr(label="translations", style="filled", color="#e5e7eb", penwidth="2")
        trans.node("cache_lookup", "get_cached_translations()\ntranslations_cache.db", fillcolor="#f3f4f6")
        trans.node("api_batch", "translate_batch()\nYandex Cloud API\nru<->en batches", fillcolor="#e5e7eb")
        trans.node("cache_save", "save_to_global_translations_cache()\npersist both directions", fillcolor="#f3f4f6")
        trans.edge("cache_lookup", "api_batch", label="misses only")
        trans.edge("api_batch", "cache_save")

    # End node
    dot.node("end", "Finished\nelapsed time printed", shape="ellipse", fillcolor="#d1fae5", penwidth="2")

    # Main data flow
    dot.edge("pass1", "rename")
    dot.edge("pass2", "rename", style="dotted", label="reuses same prep")
    dot.edge("pdf_to_txt", "structure")
    dot.edge("list_txt", "filter_pass")
    dot.edge("choose_stop", "read_txt")
    dot.edge("count_words", "drop_nonscience")
    dot.edge("merge_counts", "create_table")
    dot.edge("mark_processed", "intersection", label="after last book in category")
    dot.edge("union", "end")

    # Non-science union feeds later passes
    dot.edge("union", "choose_stop", style="dashed", color="#ef4444", label="global_union stoplist\n(runonscience / ennonscience)")

    # Translations used inside create_union_table
    dot.edge("union", "cache_lookup", style="dashed", label="top frequent words")
    dot.edge("cache_save", "union", style="dashed", label="translations table")

    return dot


def apply_quality(flowchart: Digraph, fmt: str, quality: str) -> None:
    if fmt == "png":
        dpi = "450" if quality == "high" else "650"
        size = "22,32!" if quality == "high" else "26,38!"
        flowchart.attr(dpi=dpi, size=size)
    elif fmt in {"svg", "pdf"}:
        flowchart.attr(size="22,32")


def parse_args() -> tuple[str, str]:
    fmt = "png"
    quality = "high"

    if len(sys.argv) > 1 and sys.argv[1] in {"png", "svg", "pdf"}:
        fmt = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2] in {"high", "ultra"}:
        quality = sys.argv[2]

    return fmt, quality


def main() -> None:
    fmt, quality = parse_args()

    flowchart = create_flowchart()
    apply_quality(flowchart, fmt, quality)

    output_name = f"project_flowchart_{quality}_quality"
    output_path = Path(flowchart.render(output_name, format=fmt, view=False, cleanup=True))

    print(f"Rendered flowchart -> {output_path}")
    if fmt == "png":
        print(f"PNG dpi: {flowchart.graph_attr.get('dpi')}")
    print("Usage: python generate_high_quality_flowchart.py [png|svg|pdf] [high|ultra]")


if __name__ == "__main__":
    main()
