"""Read the three CSVs and build a Kumu blueprint.

The graph has three node types (Technique, Precondition, Postcondition) and
three edge types:

  Precondition  -> Technique      a precondition is required by a technique
  Technique     -> Postcondition  a technique produces a postcondition
  Precondition  -> Postcondition  a postcondition semantically links a precondition
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from .config import Config
from .graph import KumuGraph

logger = logging.getLogger(__name__)


def _technique_label(tech_id: str, tech_name: str) -> str:
    return f"{tech_id}({tech_name})"


def parent_technique_id(condition_id: str, config: Config) -> str | None:
    """Recover the parent technique ID from a condition ID.

    A condition ID is a technique ID plus a suffix such as I1, C2, or SS1
    (for example D3-CIA-I1 belongs to D3-CIA). Returns None when the ID does
    not look like a condition.
    """
    if condition_id is None or str(condition_id).strip() == "":
        return None
    parts = str(condition_id).split("-")
    if len(parts) < 2:
        return None
    suffix = parts[-1]
    has_digit = any(ch.isdigit() for ch in suffix)
    starts_with_prefix = any(suffix.startswith(p) for p in config.condition_prefixes)
    # A condition suffix is a prefix letter(s) followed by a number (I1, C2,
    # SS1) or a bare number. A letters-only tail (like CIA) is part of the
    # technique ID, not a suffix.
    if has_digit and (starts_with_prefix or suffix.isdigit()):
        return "-".join(parts[:-1])
    return None


def build_graph(input_dir: str | Path, config: Config | None = None) -> KumuGraph:
    config = config or Config()
    input_dir = Path(input_dir)

    df_rel = pd.read_csv(input_dir / config.relationships_file)
    df_pre = pd.read_csv(input_dir / config.precondition_file)
    df_post = pd.read_csv(input_dir / config.postcondition_file)

    technique_names = dict(
        zip(df_rel[config.technique_id_col], df_rel[config.technique_name_col])
    )
    precond_desc = dict(
        zip(df_pre[config.precond_index_col], df_pre[config.precond_desc_col])
    )

    graph = KumuGraph()

    # 1. Every technique becomes a node.
    for tech_id, tech_name in technique_names.items():
        graph.add_element(
            _technique_label(tech_id, tech_name), config.technique_type, tech_name
        )

    # 2. Every precondition becomes a node, connected to its parent technique.
    for _, row in df_pre.iterrows():
        pre_id = row.get(config.precond_index_col)
        if pd.isna(pre_id) or str(pre_id).strip() == "":
            logger.warning("Skipping precondition row with no ID: %s", row.to_dict())
            continue
        pre_desc = row.get(config.precond_desc_col, "")
        graph.add_element(pre_id, config.precondition_type, pre_desc)

        parent_id = parent_technique_id(pre_id, config)
        if parent_id is None:
            logger.warning("No parent technique for precondition %s", pre_id)
            continue
        parent_name = technique_names.get(parent_id, f"{parent_id} (name not found)")
        parent_label = _technique_label(parent_id, parent_name)
        graph.add_element(parent_label, config.technique_type, parent_name)
        graph.add_connection(pre_id, parent_label, config.precond_to_technique_type)

    # 3. Every postcondition becomes a node (suffixed so it never collides
    #    with a precondition of the same base ID).
    for _, row in df_post.iterrows():
        post_id = row.get(config.postcond_index_col)
        if pd.isna(post_id) or str(post_id).strip() == "":
            logger.warning("Skipping postcondition row with no ID: %s", row.to_dict())
            continue
        post_label = f"{post_id}{config.postcondition_suffix}"
        graph.add_element(
            post_label,
            config.postcondition_type,
            row.get(config.postcond_desc_col, ""),
        )

    # 4. Connect techniques to the postconditions they produce.
    for _, row in df_rel.iterrows():
        tech_id = row.get(config.technique_id_col)
        tech_name = row.get(config.technique_name_col)
        if pd.isna(tech_id):
            continue
        tech_label = _technique_label(tech_id, tech_name)
        raw = row.get(config.postcond_list_col, "")
        if not isinstance(raw, str) or not raw.strip():
            continue
        for post_desc in (p.strip() for p in raw.split(config.list_delimiter)):
            if not post_desc:
                continue
            # Prefer a real postcondition node whose description matches.
            match = next(
                (e["label"] for e in graph.elements
                 if e["type"] == config.postcondition_type and e["description"] == post_desc),
                post_desc,
            )
            graph.add_element(match, config.postcondition_type, post_desc)
            graph.add_connection(tech_label, match, config.technique_to_postcond_type)

    # 5. Semantic links: each postcondition points at its linked preconditions.
    for _, row in df_post.iterrows():
        post_id = row.get(config.postcond_index_col)
        if pd.isna(post_id) or str(post_id).strip() == "":
            continue
        post_label = f"{post_id}{config.postcondition_suffix}"
        links = row.get(config.postcond_links_col, "")
        if not isinstance(links, str):
            continue
        for pre_id in (p.strip() for p in links.split(config.links_delimiter)):
            if not pre_id:
                continue
            desc = precond_desc.get(pre_id, f"Description not found for {pre_id}")
            graph.add_element(pre_id, config.precondition_type, desc)
            graph.add_connection(pre_id, post_label, config.postcond_to_precond_type)

    logger.info(
        "Built %d elements and %d connections",
        len(graph.elements),
        len(graph.connections),
    )
    return graph
