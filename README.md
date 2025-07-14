### Kumu Knowledge Graph JSON Generator

## 🎯 Goal

This Python script reads structured CSV files containing cybersecurity techniques, preconditions, and postconditions, then generates a **Kumu-compatible JSON blueprint** to build a **semantic knowledge graph** in the [Kumu](https://kumu.io) visualization tool.

The graph includes:
- Nodes for Techniques, Preconditions, and Postconditions  
- Edges showing:
  - Preconditions belonging to Techniques
  - Techniques resulting in Postconditions
  - Semantic relationships between Postconditions and linked Preconditions

---

## 📂 Required CSV Input Files

The script requires **three specifically formatted CSV files** placed in the same directory:

### 1. `Formatted relationships.csv`
Defines the core techniques with associated preconditions and postconditions.

| Tech ID | Tech Name | List of Precond             | List of PostCond            |
|---------|-----------|-----------------------------|-----------------------------|
| D3-CIA  | SomeTech  | Precondition A; Precondition B | Postcondition X; Postcondition Y |

### 2. `Precondition.csv`
Contains a list of preconditions with IDs and descriptions.

| index        | precondition            |
|--------------|-------------------------|
| D3-CIA-I1    | System must be isolated |

### 3. `Postcondition.csv`
Contains postconditions with linked precondition references.

| index        | Postcondition                    | Matching Preconditions from ChatGPT |
|--------------|----------------------------------|--------------------------------------|
| D3-CIA-C1    | Network traffic is encrypted     | D3-CIA-I1, D3-CIA-I2                 |

💡 **Note**:  
- Column headers must exactly match the above.
- The `index` column in `Precondition.csv` and `Postcondition.csv` is renamed during processing for clarity.

---

## ⚙️ How the Code Works

### Step-by-Step Breakdown:

1. **Read and Rename Columns**  
   Loads and normalizes column names across the three CSV files for consistency.

2. **Map Data**  
   Creates internal mappings:
   - `Technique_ID` ↔ `Technique_Name`
   - `Precondition_ID` ↔ `Precondition_Description`
   - `Postcondition_ID` ↔ `Postcondition_Description`

3. **Construct Relationships**  
   - Links preconditions to techniques
   - Links techniques to postconditions
   - Links postconditions to preconditions (semantic matching)

4. **Generate Kumu Elements and Connections**  
   Builds a list of `elements` and `connections` using:
   - `add_element()` for node creation
   - `add_connection()` for edge creation with deduplication

5. **Export JSON**  
   The final structure is saved as:
   ```json
   {
     "elements": [...],
     "connections": [...]
   }

   📄 Output File Format

The script outputs a file named: kumu_graph_complete.json

Example Structure:

{
  "elements": [
    {
      "label": "D3-CIA(SomeTech)",
      "type": "Technique",
      "description": "SomeTech"
    },
    {
      "label": "D3-CIA-I1",
      "type": "Postcondition",
      "description": "System must be isolated"
    },
    {
      "label": "D3-CIA-C1P",
      "type": "Precondition",
      "description": "Network traffic is encrypted"
    }
  ],
  "connections": [
    {
      "from": "D3-CIA(SomeTech)",
      "to": "D3-CIA-I1",
      "type": "is_postcondition_for",
      "direction": "directed"
    },
    {
      "from": "D3-CIA-C1P",
      "to": "D3-CIA(SomeTech)",
      "type": "results_in_postcondition",
      "direction": "directed"
    },
    {
      "from": "D3-CIA-I1",
      "to": "D3-CIA-C1P",
      "type": "semantically_links_to",
      "direction": "directed"
    }
  ]
}

## 📄 Output File Format

The script outputs a file named: `kumu_graph_complete.json`

### Example Structure:

```json
{
  "elements": [
    {
      "label": "D3-CIA(SomeTech)",
      "type": "Technique",
      "description": "SomeTech"
    },
    {
      "label": "D3-CIA-I1",
      "type": "Postcondition",
      "description": "System must be isolated"
    },
    {
      "label": "D3-CIA-C1P",
      "type": "Precondition",
      "description": "Network traffic is encrypted"
    }
  ],
  "connections": [
    {
      "from": "D3-CIA(SomeTech)",
      "to": "D3-CIA-I1",
      "type": "is_postcondition_for",
      "direction": "directed"
    },
    {
      "from": "D3-CIA-C1P",
      "to": "D3-CIA(SomeTech)",
      "type": "results_in_postcondition",
      "direction": "directed"
    },
    {
      "from": "D3-CIA-I1",
      "to": "D3-CIA-C1P",
      "type": "semantically_links_to",
      "direction": "directed"
    }
  ]
}
```
