import json
import pandas as pd
from IPython.display import display

def generate_kumu_json_and_display_dfs():
    """ Loads data from CSVs, structures it into DataFrames, displays DataFrame heads,
    and generates Kumu-compatible JSON.
    Ensures all techniques, preconditions, and postconditions from source data
    are included as elements and correctly connected."""

    # --- Read data from CSVs ---
    try:
        df_formatted = pd.read_csv('Formated relationships.csv')
        df_precondition = pd.read_csv('Precondition.csv')
        df_postcondition = pd.read_csv('Postcondition.csv')
    except FileNotFoundError as e:
        print(f"Error: Could not find a CSV file: {e}")
        return None
    except Exception as e:
        print(f"An error occurred while reading CSVs: {e}")
        return None

    # --- Data Preparation and Structuring ---
    # Rename columns for consistency
    df_precondition = df_precondition.rename(columns={'index': 'Precondition_ID', 'precondition': 'Precondition_Description'})
    df_postcondition = df_postcondition.rename(columns={'index': 'Postcondition_ID', 'Postcondition': 'Postcondition_Description', 'Matching Preconditions from ChatGPT': 'Linked_Precondition_IDs'})
    df_formatted = df_formatted.rename(columns={'Tech ID': 'Technique_ID', 'Tech Name': 'Technique_Name'})

    # Create mappings for quick lookups
    precondition_id_to_desc = df_precondition.set_index('Precondition_ID')['Precondition_Description'].to_dict()
    postcondition_id_to_desc = df_postcondition.set_index('Postcondition_ID')['Postcondition_Description'].to_dict()
    technique_id_to_name = df_formatted.set_index('Technique_ID')['Technique_Name'].to_dict()

    # 1. Create DataFrame for Techniques and their Individual Preconditions (for connections from Pre to Tech)
    tech_pre_list = []
    for index, row in df_formatted.iterrows():
        tech_name = row.get('Technique_Name')
        tech_id = row.get('Technique_ID')
        preconditions_str = row.get('List of Precond', '')
        if isinstance(preconditions_str, str) and preconditions_str.strip():
            # Split by semicolon, then strip leading/trailing whitespace
            pre_list = [p.strip() for p in preconditions_str.split(';') if p.strip()]
            for pre_desc in pre_list:
                # Try to find a matching Precondition_ID
                pre_id = None
                # Reverse lookup in precondition_id_to_desc
                for id, desc in precondition_id_to_desc.items():
                    if desc == pre_desc:
                         pre_id = id
                         break
                tech_pre_list.append({
                    'Technique_ID': tech_id,
                    'Technique_Name': tech_name,
                    'Precondition_Description': pre_desc,
                    'Precondition_ID': pre_id # This might be None if no direct match found
                })

    df_tech_pre = pd.DataFrame(tech_pre_list)
    print("\n--- Head of df_tech_pre ---")
    display(df_tech_pre.head())

    # 2. Create DataFrame for Techniques and their Individual Postconditions (for connections from Tech to Post)
    tech_post_list = []
    for index, row in df_formatted.iterrows():
        tech_name = row.get('Technique_Name')
        tech_id = row.get('Technique_ID')
        postconditions_str = row.get('List of PostCond', '')
        if isinstance(postconditions_str, str) and postconditions_str.strip():
             # Split by semicolon, then strip leading/trailing whitespace
            post_list = [p.strip() for p in postconditions_str.split(';') if p.strip()]
            for post_desc in post_list:
                # Try to find a matching Postcondition_ID
                post_id = None
                # Reverse lookup in postcondition_id_to_desc
                for id, desc in postcondition_id_to_desc.items():
                    if desc == post_desc:
                         post_id = id
                         break

                tech_post_list.append({
                    'Technique_ID': tech_id,
                    'Technique_Name': tech_name,
                    'Postcondition_Description': post_desc,
                    'Postcondition_ID': post_id # This might be None if no direct match found
                })
    print(tech_post_list)
    df_tech_post = pd.DataFrame(tech_post_list)
    print("\n--- Head of df_tech_post ---")
    display(df_tech_post)


    # 3. Semantic Links DataFrame (for connections from Post to Pre)
    df_semantic_links = df_postcondition.copy()
    print("\n--- Head of df_semantic_links ---")
    display(df_semantic_links.head())

    # --- Kumu JSON Structure ---
    elements = []
    connections = []

    added_element_labels = set()
    added_connection_tuples = set()

    def add_element(label, type, description=""):
        if pd.isna(label) or label == "":
             return # Don't add element if label is NaN or empty
        label_str = str(label) # Ensure label is a string
        if label_str not in added_element_labels:
            elements.append({"label": label_str, "type": type, "description": str(description) if not pd.isna(description) else ""})
            added_element_labels.add(label_str)

    def add_connection(source_label, target_label, conn_type, direction="directed"):
        if pd.isna(source_label) or source_label == "" or pd.isna(target_label) or target_label == "":
            # print(f"Warning: Skipping connection with empty source or target: from='{source_label}', to='{target_label}'")
            return # Don't add connection if source or target is NaN or empty
        source_str = str(source_label) # Ensure labels are strings
        target_str = str(target_label)
        conn_tuple = tuple(sorted((("from", source_str), ("to", target_str), ("type", conn_type))))
        if conn_tuple not in added_connection_tuples:
            connections.append({"from": source_str, "to": target_str, "direction": direction, "type": conn_type})
            added_connection_tuples.add(conn_tuple)

    def get_technique_id_from_condition_id(condition_id):
        """Extracts base technique ID from a condition ID (e.g., D3-CIA from D3-CIA-11 or D3-CIA-SS1)."""
        if pd.isna(condition_id) or condition_id == "":
            return None
        parts = str(condition_id).split('-')
        # Heuristic: assume the technique ID is the part before the condition suffix (like I#, C#, SS#)
        if len(parts) > 2 and (parts[-1].startswith('I') or parts[-1].startswith('C') or parts[-1].startswith('SS')):
             # Check if the part before the suffix looks like a technique ID (e.g., D3-CIA)
             if len(parts[-2]) > 1 and '-' in '-'.join(parts[:-1]):
                 return "-".join(parts[:-1])
             else: # Handle cases like D3-ABC-SS1 where D3-ABC is the tech ID
                  return "-".join(parts[:-1])
        elif len(parts) > 1: # Handle simple cases like D3-ABC-1
             if any(char.isdigit() for char in parts[-1]):
                  return "-".join(parts[:-1])
             else: # Handle cases like D3-ABC (already a technique ID)
                  return condition_id
        return condition_id # Default if heuristic doesn't apply or it's already a tech ID


    # --- Processing ---

    # 1. Add ALL Techniques as elements
    print("\n--- Adding all Techniques from df_formatted ---")
    for tech_id, tech_name in technique_id_to_name.items():
        add_element(str(tech_id + "("+tech_name+")"), "Technique", tech_name)
    print("--- Finished adding all Techniques ---")


    # 2. Add ALL Preconditions as elements and connect them to their Techniques
    print("\n--- Adding all Preconditions from df_precondition and connecting to Techniques ---")
    for index, row in df_precondition.iterrows():
        pre_id = row.get('Precondition_ID')
        pre_desc = row.get('Precondition_Description')

        if pre_id:
            add_element(pre_id, "Postcondition", pre_desc)

            # Connect precondition to its parent technique
            parent_tech_id = get_technique_id_from_condition_id(pre_id)

            if parent_tech_id and parent_tech_id != pre_id and parent_tech_id in technique_id_to_name:
                 parent_tech_name = technique_id_to_name[parent_tech_id]
                 add_element(parent_tech_id + "("+parent_tech_name+")", "Technique", parent_tech_name) # Ensure parent technique is also an element
                 add_connection(parent_tech_id + "("+parent_tech_name+")", pre_id, "is_postcondition_for")
            elif parent_tech_id and parent_tech_id != pre_id:
                  # Add as element with placeholder name if ID exists but name not found
                  add_element(parent_tech_id + "("+parent_tech_name+")", "Technique", f"Technique: {parent_tech_id} (Name not found)")
                  add_connection(parent_tech_id + "("+parent_tech_name+")", pre_id, "is_postcondition_for")
            elif not parent_tech_id:
                 print(f"Warning: Could not determine parent technique for precondition '{pre_id}'. Cannot add connection.")
        else:
             print(f"Warning: Skipping precondition from df_precondition with missing ID: {row.to_dict()}")

    print("--- Finished adding all Preconditions ---")

    # 3. Add ALL Postconditions as elements
    print("\n--- Adding all Postconditions from df_postcondition ---")
    for index, row in df_postcondition.iterrows():
        post_id = row.get('Postcondition_ID') + "P"
        post_desc = row.get('Postcondition_Description', '')

        if post_id:
             add_element(post_id, "Precondition", post_desc)
        else:
             print(f"Warning: Skipping postcondition from df_postcondition with missing ID: {row.to_dict()}")

    print("--- Finished adding all Postconditions ---")

    # 4. Add connections from Techniques to Postconditions (using df_tech_post)
    print("\n--- Adding connections from Techniques to Postconditions (from df_tech_post) ---")
    for index, row in df_tech_post.iterrows():
        tech_id = row.get('Technique_ID') + "("+row.get("Technique_Name")+")"
        print(row.get('Postcondition_ID'))
        post_id = row.get('Postcondition_ID') + "P" # This might be None if no ID match was found
        post_desc = row.get('Postcondition_Description')

        # Use Postcondition_ID if available, otherwise use description as label for the target
        post_label = post_id if post_id else post_desc

        # Ensure the target element exists (should have been added in step 3 or earlier)
        add_element(post_label, "Postcondition", post_desc if post_desc else post_label)

        # Add connection from Technique to Postcondition
        add_connection(post_label,tech_id,  "results_in_postcondition")
    print("Finished adding connections from Techniques to Postconditions")


    # 5. Process Semantic Links (Postcondition -> Linked Precondition) (using df_semantic_links)
    # Connections from Linked Precondition to Parent Technique were handled in Step 2.
    print("\n--- Processing semantic links (Postcondition -> Linked Precondition) from df_semantic_links ---")
    for index, row in df_semantic_links.iterrows():
        post_cond_id = row.get("Postcondition_ID") + "P"
        linked_pre_ids_str = row.get("Linked_Precondition_IDs", "")

        if pd.isna(post_cond_id) or post_cond_id == "":
            continue

        if isinstance(linked_pre_ids_str, str):
            linked_pre_ids = [pid.strip() for pid in linked_pre_ids_str.split(',') if pid.strip()]
            for linked_pre_id in linked_pre_ids:
                if not linked_pre_id: continue

                # Ensure linked precondition element exists (should have been added in Step 2)
                # Use description from mapping if available
                linked_pre_desc = precondition_id_to_desc.get(linked_pre_id, f"Description not found for {linked_pre_id}")
                add_element(linked_pre_id, "Precondition", linked_pre_desc)


                # Connection: Postcondition -> Linked Precondition (semantic link)
                add_connection(linked_pre_id, post_cond_id,"semantically_links_to")

    print("--- Finished processing semantic links ---")
    print(len(elements))
    print(elements)
    print(connections)
    kumu_data = {
        "elements": elements,
        "connections": connections
    }

    return json.dumps(kumu_data, indent=2)

# --- Execution ---
if __name__ == '__main__':
    kumu_json_output = generate_kumu_json_and_display_dfs()

    if kumu_json_output:
        print("\n--- Kumu JSON Output ---")

        # To save to a file:
        with open("kumu_graph_complete.json", "w") as f:
            f.write(kumu_json_output)
        print("\nKumu JSON saved to kumu_graph_complete.json")
