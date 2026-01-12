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
        self.indexes = {}

        # Create indexes for PRIMARY KEY and UNIQUE columns
        for col_name, col_meta in columns.items():
            if col_meta.get("primary"):
                self.indexes[col_name] = {
                    "type": "primary",
                    "map": {}
                }
            elif col_meta.get("unique"):
                self.indexes[col_name] = {
                    "type": "unique",
                    "map": {}
                }

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

        # Check for duplicate keys in indexed columns before inserting
        for col_name, index in self.indexes.items():
            key = row[col_name]
            if key in index["map"]:
                raise ValueError(f"Duplicate value for indexed column '{col_name}': {key}")

        # Insert the row
        row_index = len(self.rows)
        self.rows.append(row)

        # Populate indexes
        for col_name, index in self.indexes.items():
            key = row[col_name]
            index["map"][key] = row_index

    def rebuild_indexes(self):
        """Rebuild all indexes from current rows. Used after DELETE operations."""
        # Clear all indexes
        for index in self.indexes.values():
            index["map"].clear()

        # Rebuild indexes from rows
        column_names = list(self.columns.keys())
        for row_index, row in enumerate(self.rows):
            for col_name, index in self.indexes.items():
                key = row[col_name]
                index["map"][key] = row_index
