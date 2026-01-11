class Table:
    def __init__(self, name, columns):
        """
        columns = {
            "id": {"type": "INT", "primary": True, "unique": True},
            "email": {"type": "TEXT", "unique": True}
        }
        """
        self.name = name
        self.columns = columns
        self.rows = []

        self.primary_key = None
        for col, meta in columns.items():
            if meta.get("primary"):
                self.primary_key = col

    def insert(self, values):
        if len(values) != len(self.columns):
            raise ValueError("Column count mismatch")

        row = {}
        for col, value in zip(self.columns.keys(), values):
            row[col] = value

        self.rows.append(row)
