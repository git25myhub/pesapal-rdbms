from mydb.table import Table
from mydb.exceptions import TableExistsError

class Database:
    def __init__(self):
        self.tables = {}

    def execute(self, ast):
        if ast["type"] == "CREATE_TABLE":
            return self.create_table(ast)

        raise ValueError("Unsupported command")

    def create_table(self, ast):
        name = ast["table"]
        if name in self.tables:
            raise TableExistsError(f"Table '{name}' already exists")

        table = Table(name, ast["columns"])
        self.tables[name] = table
        return f"Table '{name}' created"
