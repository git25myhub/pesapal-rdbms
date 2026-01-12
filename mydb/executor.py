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

        if not table.rows:
            return "(0 rows)"

        # Header
        output = []
        headers = list(table.columns.keys())
        output.append(" | ".join(headers))
        output.append("-" * (len(output[0])))

        # Rows
        for row in table.rows:
            line = " | ".join(str(row[col]) for col in headers)
            output.append(line)

        output.append(f"\n({len(table.rows)} rows)")
        return "\n".join(output)
