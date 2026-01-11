import re

def parse(sql):
    sql = sql.strip().rstrip(";")

    if sql.upper().startswith("CREATE TABLE"):
        return parse_create_table(sql)

    raise ValueError("Unsupported SQL")

def parse_create_table(sql):
    pattern = r"CREATE TABLE (\w+)\s*\((.+)\)"
    match = re.match(pattern, sql, re.IGNORECASE)

    if not match:
        raise ValueError("Invalid CREATE TABLE syntax")

    table_name = match.group(1)
    columns_raw = match.group(2)

    columns = {}
    for col_def in columns_raw.split(","):
        parts = col_def.strip().split()
        col_name = parts[0]
        col_type = parts[1].upper()

        columns[col_name] = {
            "type": col_type,
            "primary": "PRIMARY" in col_def.upper(),
            "unique": "UNIQUE" in col_def.upper()
        }

    return {
        "type": "CREATE_TABLE",
        "table": table_name,
        "columns": columns
    }
