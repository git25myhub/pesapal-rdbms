import json
import os

DB_FILE = "data/db.json"


def load_database():
    """
    Load database state from disk.
    Returns a dictionary of table_name -> Table objects.
    """
    if not os.path.exists(DB_FILE):
        return {}

    with open(DB_FILE, "r") as f:
        raw = json.load(f)

    from mydb.table import Table
    
    tables = {}
    for table_name, table_data in raw.items():
        # Convert columns from list format back to dict format
        columns = {}
        for col_def in table_data["columns"]:
            columns[col_def["name"]] = {
                "type": col_def["type"],
                "primary": col_def.get("primary_key", False),
                "unique": col_def.get("unique", False)
            }
        
        # Create table
        table = Table(table_name, columns)
        
        # Convert rows from array format back to dict format
        column_names = list(columns.keys())
        for row_values in table_data["rows"]:
            row = {}
            for col_name, value in zip(column_names, row_values):
                row[col_name] = value
            table.rows.append(row)
        
        tables[table_name] = table

    return tables


def save_database(tables):
    """
    Save database state to disk.
    tables: dictionary of table_name -> Table objects
    """
    os.makedirs("data", exist_ok=True)

    # Convert Table objects to JSON-serializable format
    serialized = {}
    for table_name, table in tables.items():
        # Convert columns from dict to list format
        columns = []
        for col_name, col_meta in table.columns.items():
            columns.append({
                "name": col_name,
                "type": col_meta["type"],
                "primary_key": col_meta.get("primary", False),
                "unique": col_meta.get("unique", False)
            })
        
        # Convert rows from dict format to array format
        column_names = list(table.columns.keys())
        rows = []
        for row_dict in table.rows:
            row_array = [row_dict[col] for col in column_names]
            rows.append(row_array)
        
        serialized[table_name] = {
            "columns": columns,
            "rows": rows
        }

    with open(DB_FILE, "w") as f:
        json.dump(serialized, f, indent=2)
