from mydb.table import Table
from mydb.exceptions import TableExistsError, TableNotFoundError
from mydb.storage import save_database

class Database:
    def __init__(self):
        self.tables = {}

    def execute(self, ast):
        if ast["type"] == "CREATE_TABLE":
            return self.create_table(ast)

        if ast["type"] == "INSERT":
            return self.insert(ast)

        if ast["type"] == "SELECT":
            return self.select(ast)

        if ast["type"] == "UPDATE":
            return self.update(ast)

        if ast["type"] == "DELETE":
            return self.delete(ast)

        raise ValueError("Unsupported command")

    def create_table(self, ast):
        name = ast["table"]
        if name in self.tables:
            raise TableExistsError(f"Table '{name}' already exists")

        table = Table(name, ast["columns"])
        self.tables[name] = table
        save_database(self.tables)
        return f"Table '{name}' created"

    def insert(self, ast):
        table_name = ast["table"]
        values = ast["values"]

        if table_name not in self.tables:
            raise TableNotFoundError(f"Table '{table_name}' does not exist")

        table = self.tables[table_name]
        table.insert(values)
        save_database(self.tables)
        return "1 row inserted"

    def select(self, ast):
        table_name = ast["table"]

        if table_name not in self.tables:
            raise TableNotFoundError(f"Table '{table_name}' does not exist")

        table = self.tables[table_name]
        headers = list(table.columns.keys())

        # Apply WHERE filter if present
        rows = table.rows
        where_clause = ast.get("where")

        if where_clause:
            column = where_clause["column"]
            value = where_clause["value"]

            # Validate column exists
            if column not in headers:
                raise ValueError(f"Unknown column '{column}'")

            # Filter rows based on WHERE condition
            filtered_rows = []
            for row in rows:
                if row[column] == value:
                    filtered_rows.append(row)
            rows = filtered_rows

        if not rows:
            return "(0 rows)"

        # Header
        output = []
        output.append(" | ".join(headers))
        output.append("-" * (len(output[0])))

        # Rows
        for row in rows:
            line = " | ".join(str(row[col]) for col in headers)
            output.append(line)

        output.append(f"\n({len(rows)} rows)")
        return "\n".join(output)

    def update(self, ast):
        table_name = ast["table"]

        if table_name not in self.tables:
            raise TableNotFoundError(f"Table '{table_name}' does not exist")

        table = self.tables[table_name]
        headers = list(table.columns.keys())

        set_column = ast["set"]["column"]
        set_value = ast["set"]["value"]
        where_column = ast["where"]["column"]
        where_value = ast["where"]["value"]

        # Validate columns exist
        if set_column not in headers:
            raise ValueError(f"Unknown column '{set_column}'")
        if where_column not in headers:
            raise ValueError(f"Unknown column '{where_column}'")

        # Update rows matching WHERE condition
        count = 0
        for row in table.rows:
            if row[where_column] == where_value:
                row[set_column] = set_value
                count += 1

        save_database(self.tables)
        return f"{count} row(s) updated"

    def delete(self, ast):
        table_name = ast["table"]

        if table_name not in self.tables:
            raise TableNotFoundError(f"Table '{table_name}' does not exist")

        table = self.tables[table_name]
        headers = list(table.columns.keys())

        where_column = ast["where"]["column"]
        where_value = ast["where"]["value"]

        # Validate column exists
        if where_column not in headers:
            raise ValueError(f"Unknown column '{where_column}'")

        # Delete rows matching WHERE condition
        before_count = len(table.rows)
        table.rows = [row for row in table.rows if row[where_column] != where_value]
        deleted_count = before_count - len(table.rows)

        save_database(self.tables)
        return f"{deleted_count} row(s) deleted"
