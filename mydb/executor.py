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

        if ast["type"] == "JOIN":
            return self.join(ast)

        if ast["type"] == "EXPLAIN":
            return self.explain(ast["query"])

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

            # Use index if available for O(1) lookup
            if column in table.indexes:
                index = table.indexes[column]["map"]
                if value in index:
                    row_index = index[value]
                    rows = [table.rows[row_index]]
                else:
                    rows = []
            else:
                # Fallback to table scan
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
        for row_index, row in enumerate(table.rows):
            if row[where_column] == where_value:
                # If updating an indexed column, update the index
                if set_column in table.indexes:
                    old_key = row[set_column]
                    new_key = set_value
                    
                    # Check for duplicate if new key already exists (and it's not the same row)
                    if new_key in table.indexes[set_column]["map"]:
                        existing_row_index = table.indexes[set_column]["map"][new_key]
                        if existing_row_index != row_index:
                            raise ValueError(f"Duplicate value for indexed column '{set_column}': {new_key}")
                    
                    # Remove old key from index
                    if old_key in table.indexes[set_column]["map"]:
                        del table.indexes[set_column]["map"][old_key]
                    
                    # Add new key to index
                    table.indexes[set_column]["map"][new_key] = row_index
                
                # Update the row
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

        # Rebuild all indexes after deletion (simplest and most correct approach)
        if deleted_count > 0:
            table.rebuild_indexes()

        save_database(self.tables)
        return f"{deleted_count} row(s) deleted"

    def join(self, ast):
        left_table_name = ast["left_table"]
        right_table_name = ast["right_table"]
        left_column = ast["left_column"]
        right_column = ast["right_column"]

        # Validate tables exist
        if left_table_name not in self.tables:
            raise TableNotFoundError(f"Table '{left_table_name}' does not exist")
        if right_table_name not in self.tables:
            raise TableNotFoundError(f"Table '{right_table_name}' does not exist")

        left_table = self.tables[left_table_name]
        right_table = self.tables[right_table_name]

        left_headers = list(left_table.columns.keys())
        right_headers = list(right_table.columns.keys())

        # Validate columns exist
        if left_column not in left_headers:
            raise ValueError(f"Unknown column '{left_column}' in table '{left_table_name}'")
        if right_column not in right_headers:
            raise ValueError(f"Unknown column '{right_column}' in table '{right_table_name}'")

        # Prefer index on right table for O(1) lookup
        result_rows = []

        if right_column in right_table.indexes:
            # Use index for fast lookup
            index = right_table.indexes[right_column]["map"]
            for left_row in left_table.rows:
                key = left_row[left_column]
                if key in index:
                    right_row_index = index[key]
                    right_row = right_table.rows[right_row_index]
                    # Combine rows
                    combined_row = {}
                    # Add left table columns with table prefix
                    for col in left_headers:
                        combined_row[f"{left_table_name}.{col}"] = left_row[col]
                    # Add right table columns with table prefix
                    for col in right_headers:
                        combined_row[f"{right_table_name}.{col}"] = right_row[col]
                    result_rows.append(combined_row)
        else:
            # Fallback to nested loop (table scan)
            for left_row in left_table.rows:
                key = left_row[left_column]
                for right_row in right_table.rows:
                    if right_row[right_column] == key:
                        # Combine rows
                        combined_row = {}
                        # Add left table columns with table prefix
                        for col in left_headers:
                            combined_row[f"{left_table_name}.{col}"] = left_row[col]
                        # Add right table columns with table prefix
                        for col in right_headers:
                            combined_row[f"{right_table_name}.{col}"] = right_row[col]
                        result_rows.append(combined_row)

        if not result_rows:
            return "(0 rows)"

        # Build output with prefixed column names
        output_headers = [f"{left_table_name}.{col}" for col in left_headers] + \
                        [f"{right_table_name}.{col}" for col in right_headers]

        # Header
        output = []
        output.append(" | ".join(output_headers))
        output.append("-" * (len(output[0])))

        # Rows
        for row in result_rows:
            line = " | ".join(str(row[col]) for col in output_headers)
            output.append(line)

        output.append(f"\n({len(result_rows)} rows)")
        return "\n".join(output)

    def explain(self, stmt):
        """Explain how a query will be executed without actually running it."""
        if stmt["type"] == "JOIN":
            return self.explain_join(stmt)
        
        if stmt["type"] == "SELECT":
            return self.explain_select(stmt)
        
        raise ValueError("EXPLAIN not supported for this statement type")

    def explain_join(self, stmt):
        """Explain a JOIN query execution plan."""
        left_table_name = stmt["left_table"]
        right_table_name = stmt["right_table"]
        left_column = stmt["left_column"]
        right_column = stmt["right_column"]

        # Validate tables exist
        if left_table_name not in self.tables:
            raise TableNotFoundError(f"Table '{left_table_name}' does not exist")
        if right_table_name not in self.tables:
            raise TableNotFoundError(f"Table '{right_table_name}' does not exist")

        right_table = self.tables[right_table_name]

        # Determine strategy based on index availability
        if right_column in right_table.indexes:
            strategy = f"INDEX LOOKUP ({right_table_name}.{right_column})"
            cost = "O(n)"
        else:
            strategy = "NESTED LOOP JOIN"
            cost = "O(n²)"

        output = []
        output.append("QUERY PLAN")
        output.append("----------")
        output.append("Operation: JOIN")
        output.append("Join Type: INNER")
        output.append(f"Left Table: {left_table_name}")
        output.append(f"Right Table: {right_table_name}")
        output.append(f"Join Condition: {left_table_name}.{left_column} = {right_table_name}.{right_column}")
        output.append(f"Strategy: {strategy}")
        output.append(f"Estimated Cost: {cost}")

        return "\n".join(output)

    def explain_select(self, stmt):
        """Explain a SELECT query execution plan."""
        table_name = stmt["table"]
        where_clause = stmt.get("where")

        # Validate table exists
        if table_name not in self.tables:
            raise TableNotFoundError(f"Table '{table_name}' does not exist")

        table = self.tables[table_name]

        output = []
        output.append("QUERY PLAN")
        output.append("----------")
        output.append("Operation: SELECT")
        output.append(f"Table: {table_name}")

        if where_clause:
            column = where_clause["column"]
            if column in table.indexes:
                output.append(f"Filter: {column} = ?")
                output.append("Strategy: INDEX LOOKUP")
                output.append("Estimated Cost: O(1)")
            else:
                output.append(f"Filter: {column} = ?")
                output.append("Strategy: TABLE SCAN")
                output.append("Estimated Cost: O(n)")
        else:
            output.append("Strategy: FULL TABLE SCAN")
            output.append("Estimated Cost: O(n)")

        return "\n".join(output)
