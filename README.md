# Kumu Knowledge Graph Formatter

Reads three CSV files of cybersecurity techniques, preconditions, and
postconditions and writes a [Kumu](https://kumu.io) JSON blueprint you can
import to build a semantic knowledge graph.

The graph has three node types and three edge types:

| Node | |
| --- | --- |
| Technique | a defensive or offensive technique |
| Precondition | a state required before a technique applies |
| Postcondition | a state a technique produces |

| Edge | From | To |
| --- | --- | --- |
| `is_precondition_for` | Precondition | Technique |
| `results_in_postcondition` | Technique | Postcondition |
| `semantically_links_to` | Precondition | Postcondition |

## Input files

Three CSVs in one directory. Column headers must match, and the headers below
are the defaults (override any of them, see Configuration).

`Formatted relationships.csv`, the core techniques with their conditions as
delimited lists:

| Tech ID | Tech Name | List of Precond | List of PostCond |
| --- | --- | --- | --- |
| D3-CIA | Credential Isolation | System must be isolated; Access controls enforced | Network traffic is encrypted; Credentials rotated |

`Precondition.csv`, precondition IDs and descriptions:

| index | precondition |
| --- | --- |
| D3-CIA-I1 | System must be isolated |

`Postcondition.csv`, postconditions and the preconditions they link back to:

| index | Postcondition | Matching Preconditions from ChatGPT |
| --- | --- | --- |
| D3-CIA-C1 | Network traffic is encrypted | D3-CIA-I1, D3-CIA-I2 |

A condition ID is a technique ID plus a suffix (`D3-CIA-I1` belongs to
`D3-CIA`), which is how conditions connect to their parent technique.

## How it works

1. Add every technique as a node.
2. Add every precondition as a node and connect it to its parent technique.
3. Add every postcondition as a node, suffixed with `P` so it never collides
   with a precondition of the same base ID.
4. Connect each technique to the postconditions it produces.
5. Connect each precondition to the postconditions that link back to it.

Nodes are deduplicated by label, edges by (from, to, type). Rows with a
missing ID or an unresolvable parent are skipped and logged under `--verbose`.

## Install

```bash
pip install -r requirements.txt
```

## Usage

```bash
python -m kumu_formatter -i path/to/csvs -o kumu_graph.json
```

Run against the bundled sample data:

```bash
python -m kumu_formatter -i examples -o out.json
```

Import the output into Kumu under Data, Import JSON Blueprint.

| Flag | Meaning |
| --- | --- |
| `-i, --input-dir` | directory holding the three CSVs (default: current) |
| `-o, --output` | output JSON path (default: `<input-dir>/kumu_graph_complete.json`) |
| `--relationships-file`, `--precondition-file`, `--postcondition-file` | override input file names |
| `-v, --verbose` | log every skipped or unmatched row |

## Configuration

All file names, column headers, delimiters, and node/edge type labels live in
`kumu_formatter/config.py`. Pass a `Config` into `build_graph` to run on data
that uses different headers:

```python
from kumu_formatter import Config, build_graph

config = Config(technique_id_col="Technique", list_delimiter=",")
graph = build_graph("path/to/csvs", config)
graph.to_dict()
```

## Output

```json
{
  "elements": [
    { "label": "D3-CIA(Credential Isolation)", "type": "Technique", "description": "Credential Isolation" },
    { "label": "D3-CIA-I1", "type": "Precondition", "description": "System must be isolated" },
    { "label": "D3-CIA-C1P", "type": "Postcondition", "description": "Network traffic is encrypted" }
  ],
  "connections": [
    { "from": "D3-CIA-I1", "to": "D3-CIA(Credential Isolation)", "direction": "directed", "type": "is_precondition_for" },
    { "from": "D3-CIA(Credential Isolation)", "to": "D3-CIA-C1P", "direction": "directed", "type": "results_in_postcondition" },
    { "from": "D3-CIA-I1", "to": "D3-CIA-C1P", "direction": "directed", "type": "semantically_links_to" }
  ]
}
```

## Layout

```
kumu_formatter/
  builder.py    # read CSVs, build the graph
  graph.py      # node/edge accumulator with dedup
  config.py     # file names, columns, delimiters, type labels
  cli.py        # command-line entry point
examples/       # sample CSVs
tests/          # pytest suite
```

## Tests

```bash
pip install pytest
python -m pytest
```
