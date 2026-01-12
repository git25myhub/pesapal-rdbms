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
    pattern = r"SELECT\s+\*\s+FROM\s+(\w+)"
    match = re.match(pattern, sql, re.IGNORECASE)

    if not match:
        raise ValueError("Only SELECT * FROM table is supported")

    table = match.group(1)

    return {
        "type": "SELECT",
        "table": table
    }
