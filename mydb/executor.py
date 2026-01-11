from mydb.table import Table
from mydb.exceptions import TableExistsError, TableNotFoundError

class Database:
    def __init__(self):
        self.tables = {}

    def execute(self, ast):
        if ast["type"] == "CREATE_TABLE":
            return self.create_table(ast)

        if ast["type"] == "INSERT":
            return self.insert(ast)

        raise ValueError("Unsupported command")

    def create_table(self, ast):
        name = ast["table"]
        if name in self.tables:
            raise TableExistsError(f"Table '{name}' already exists")

        table = Table(name, ast["columns"])
        self.tables[name] = table
        return f"Table '{name}' created"

    def insert(self, ast):
        table_name = ast["table"]
        values = ast["values"]

        if table_name not in self.tables:
            raise TableNotFoundError(f"Table '{table_name}' does not exist")

        table = self.tables[table_name]
        table.insert(values)

        return "1 row inserted"
