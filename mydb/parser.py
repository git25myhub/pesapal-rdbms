import re

def parse(sql):
    sql = sql.strip().rstrip(";")

    if sql.upper().startswith("CREATE TABLE"):
        return parse_create_table(sql)

    if sql.upper().startswith("INSERT INTO"):
        return parse_insert(sql)

    if sql.upper().startswith("SELECT"):
        return parse_select(sql)

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

def parse_insert(sql):
    pattern = r"INSERT INTO (\w+)\s+VALUES\s*\((.+)\)"
    match = re.match(pattern, sql, re.IGNORECASE)

    if not match:
        raise ValueError("Invalid INSERT syntax")

    table = match.group(1)
    raw_values = match.group(2)

    values = []
    for val in raw_values.split(","):
        val = val.strip()
        if val.startswith('"') and val.endswith('"'):
            values.append(val[1:-1])
        elif val.isdigit():
            values.append(int(val))
        else:
            raise ValueError(f"Unsupported value: {val}")

    return {
        "type": "INSERT",
        "table": table,
        "values": values
    }

def parse_select(sql):
    # Pattern to match: SELECT * FROM table [WHERE column = value]
    pattern = r"SELECT\s+\*\s+FROM\s+(\w+)(?:\s+WHERE\s+(\w+)\s*=\s*(.+))?\s*$"
    match = re.match(pattern, sql, re.IGNORECASE)

    if not match:
        raise ValueError("Invalid SELECT syntax. Supported: SELECT * FROM table [WHERE column = value]")

    table = match.group(1)
    where_clause = None

    # If WHERE clause is present
    if match.group(2):
        column = match.group(2)
        raw_value = match.group(3).strip()

        # Parse value (string or integer)
        if raw_value.startswith('"') and raw_value.endswith('"'):
            value = raw_value[1:-1]
        elif raw_value.isdigit():
            value = int(raw_value)
        else:
            raise ValueError(f"Invalid WHERE value: {raw_value}")

        where_clause = {
            "column": column,
            "value": value
        }

    return {
        "type": "SELECT",
        "table": table,
        "where": where_clause
    }
