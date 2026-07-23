from pathlib import Path

from kumu_formatter import Config, build_graph, parent_technique_id

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def test_parent_technique_id():
    config = Config()
    assert parent_technique_id("D3-CIA-I1", config) == "D3-CIA"
    assert parent_technique_id("D3-CIA-C2", config) == "D3-CIA"
    assert parent_technique_id("D3-NTA-SS1", config) == "D3-NTA"
    assert parent_technique_id("D3-CIA", config) is None
    assert parent_technique_id("", config) is None


def test_build_graph_on_examples():
    graph = build_graph(EXAMPLES)
    labels = {e["label"] for e in graph.elements}

    # Techniques, preconditions, and suffixed postconditions all present.
    assert "D3-CIA(Credential Isolation)" in labels
    assert "D3-CIA-I1" in labels
    assert "D3-CIA-C1P" in labels

    types = {e["type"] for e in graph.elements}
    assert types == {"Technique", "Precondition", "Postcondition"}

    edge_types = {c["type"] for c in graph.connections}
    assert "is_precondition_for" in edge_types
    assert "results_in_postcondition" in edge_types
    assert "semantically_links_to" in edge_types


def test_no_duplicate_elements_or_connections():
    graph = build_graph(EXAMPLES)
    labels = [e["label"] for e in graph.elements]
    assert len(labels) == len(set(labels))
    keys = [(c["from"], c["to"], c["type"]) for c in graph.connections]
    assert len(keys) == len(set(keys))
