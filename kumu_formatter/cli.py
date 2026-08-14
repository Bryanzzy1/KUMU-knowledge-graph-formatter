"""Command-line entry point."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from .builder import build_graph
from .config import Config


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a Kumu JSON blueprint from technique / precondition / "
        "postcondition CSVs."
    )
    parser.add_argument(
        "-i", "--input-dir", default=".",
        help="Directory holding the three input CSVs (default: current directory).",
    )
    parser.add_argument(
        "-o", "--output", default=None,
        help="Output JSON path (default: <input-dir>/kumu_graph_complete.json).",
    )
    parser.add_argument("--relationships-file", default=None)
    parser.add_argument("--precondition-file", default=None)
    parser.add_argument("--postcondition-file", default=None)
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Log every skipped or unmatched row.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    config = Config()
    if args.relationships_file:
        config.relationships_file = args.relationships_file
    if args.precondition_file:
        config.precondition_file = args.precondition_file
    if args.postcondition_file:
        config.postcondition_file = args.postcondition_file

    input_dir = Path(args.input_dir)
    output = Path(args.output) if args.output else input_dir / config.output_file

    graph = build_graph(input_dir, config)
    output.write_text(json.dumps(graph.to_dict(), indent=2), encoding="utf-8")
    print(
        f"Wrote {len(graph.elements)} elements and "
        f"{len(graph.connections)} connections to {output}"
    )
    return 0
