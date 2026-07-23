"""Column names, file names, and connection types used to build the graph.

Override any of these on the command line or by passing a Config into the
builder, so the formatter works on data that uses different headers or files.
"""

from dataclasses import dataclass, field


@dataclass
class Config:
    # Input CSV file names, resolved relative to the input directory.
    relationships_file: str = "Formatted relationships.csv"
    precondition_file: str = "Precondition.csv"
    postcondition_file: str = "Postcondition.csv"

    # Output file name, resolved relative to the output directory.
    output_file: str = "kumu_graph_complete.json"

    # Columns in the relationships file.
    technique_id_col: str = "Tech ID"
    technique_name_col: str = "Tech Name"
    precond_list_col: str = "List of Precond"
    postcond_list_col: str = "List of PostCond"

    # Columns in the precondition file.
    precond_index_col: str = "index"
    precond_desc_col: str = "precondition"

    # Columns in the postcondition file.
    postcond_index_col: str = "index"
    postcond_desc_col: str = "Postcondition"
    postcond_links_col: str = "Matching Preconditions from ChatGPT"

    # Delimiter that separates items inside a list cell.
    list_delimiter: str = ";"
    # Delimiter that separates linked precondition IDs in the postcondition file.
    links_delimiter: str = ","

    # Node type labels.
    technique_type: str = "Technique"
    precondition_type: str = "Precondition"
    postcondition_type: str = "Postcondition"

    # Edge type labels.
    precond_to_technique_type: str = "is_precondition_for"
    technique_to_postcond_type: str = "results_in_postcondition"
    postcond_to_precond_type: str = "semantically_links_to"

    # Suffix appended to postcondition IDs so they never collide with a
    # precondition that shares the same base ID.
    postcondition_suffix: str = "P"

    # Prefixes that mark the trailing part of a condition ID (e.g. I1, C2, SS1).
    # Used to strip the suffix and recover the parent technique ID.
    condition_prefixes: tuple = field(default_factory=lambda: ("I", "C", "SS"))
