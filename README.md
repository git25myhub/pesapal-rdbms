# Pesapal Junior Dev Challenge 2026
# Mini Relational Database Management System (RDBMS)

## Author

Stephen Kariuki

## 📌 Overview

This project is a from-scratch implementation of a simple relational database management system (RDBMS) built in Python as part of the Pesapal Junior Developer Challenge 2026.

The goal of this project is not to compete with production-grade databases such as PostgreSQL or MySQL, but to demonstrate a clear understanding of core database concepts, system design, and the ability to incrementally build a working system.

At this stage, the project implements:
- An interactive SQL-like REPL
- Table creation with schema definitions
- Basic column constraints (PRIMARY KEY, UNIQUE)
- In-memory table management

Future stages will add CRUD operations, persistence, indexing, joins, and a small web demo.

## 🎯 Design Philosophy

This project prioritizes:
- Clarity over performance
- Correctness over feature completeness
- Explicit design decisions over hidden magic

Limitations are intentional and documented. The focus is on learning, transparency, and system-level thinking.

## ✨ Features Implemented (Part 1–2)

### ✅ Interactive REPL
- Custom command-line interface
- Supports multi-line SQL statements
- Executes statements once a terminating semicolon (;) is encountered

Example:
```sql
CREATE TABLE users (
  id INT PRIMARY KEY,
  email TEXT UNIQUE
);
```

### ✅ Table Creation (CREATE TABLE)
- Define tables with named columns
- Supported data types:
  - INT
  - TEXT
  - BOOL (reserved for later use)
- Supported constraints:
  - PRIMARY KEY
  - UNIQUE

Example:
```sql
CREATE TABLE users (
  id INT PRIMARY KEY,
  email TEXT UNIQUE
);
```

### ✅ Data Insertion (`INSERT INTO`)
- Insert rows into an existing table
- Values must match the table schema order
- Supports basic data types:
  - `INT`
  - `TEXT` (double-quoted)

Example:
```sql
INSERT INTO users VALUES (1, "stephen@example.com");
INSERT INTO users VALUES (2, "jane@example.com");
```

Behavior:
- Insertion fails if the target table does not exist
- Insertion fails if the number of values does not match the schema

### ✅ Data Retrieval (`SELECT`)
- Retrieve all rows from a table using `SELECT *`
- Displays results in a tabular format
- Includes row count output

Example:
```sql
SELECT * FROM users;
```

Output:
```
id | email
----------
1 | stephen@example.com
2 | jane@example.com

(2 rows)
```

### ✅ Conditional Queries (`WHERE`)
- Supports single-condition equality filters
- Filters rows based on column values
- Type-safe evaluation (no eval)

Example:
```sql
SELECT * FROM users WHERE id = 1;
SELECT * FROM users WHERE email = "jane@example.com";
```

Behavior:
- Returns only rows matching the WHERE condition
- Returns "(0 rows)" if no matches found
- Raises error if column doesn't exist

### ✅ UPDATE and DELETE
- UPDATE rows using conditional WHERE clauses
- DELETE rows safely using WHERE filters
- Full-table UPDATE/DELETE is intentionally disallowed (WHERE is mandatory)
- Automatic persistence after mutations

Examples:
```sql
UPDATE users SET email = "new@mail.com" WHERE id = 1;
DELETE FROM users WHERE id = 2;
```

Behavior:
- UPDATE modifies rows matching the WHERE condition
- DELETE removes rows matching the WHERE condition
- Both operations require WHERE clause (prevents accidental full-table operations)
- Returns count of affected rows
- Automatically saves changes to disk

### ✅ Indexing
- Automatic hash-based indexes for PRIMARY KEY and UNIQUE columns
- Indexes are used automatically for WHERE equality filters (O(1) lookup)
- Indexes enforce PRIMARY KEY and UNIQUE constraints on INSERT and UPDATE
- Indexes are automatically maintained on INSERT, UPDATE, and DELETE operations
- Indexes are rebuilt on database load and after DELETE operations

Example:
```sql
CREATE TABLE users (id INT PRIMARY KEY, email TEXT UNIQUE);
INSERT INTO users VALUES (1, "stephen@example.com");
INSERT INTO users VALUES (2, "jane@example.com");
-- This will fail due to unique constraint:
INSERT INTO users VALUES (3, "stephen@example.com");
```

Benefits:
- O(1) lookup performance for indexed columns in WHERE clauses
- Automatic constraint enforcement (no duplicate PRIMARY KEY or UNIQUE values)
- Transparent to users - indexes are used automatically when available
- Fallback to table scan for non-indexed columns

### ✅ In-Memory Schema Representation
- Tables are stored in memory using Python data structures
- Each table tracks:
  - Column definitions
  - Constraints
  - Rows (populated via INSERT statements)

### ✅ JSON-Based Disk Persistence
- Automatic save to disk after every `CREATE TABLE`, `INSERT`, `UPDATE`, and `DELETE` operation
- Data is automatically loaded when the REPL starts
- Persistence uses JSON format stored in `data/db.json`
- Human-readable format for easy debugging

Behavior:
- Data persists across REPL sessions
- Tables and rows are automatically restored on startup
- No manual save/load commands required

## 🧱 Current Architecture
```
mydb/
├── repl.py        # Interactive SQL shell
├── parser.py      # SQL parsing into an AST
├── executor.py    # Executes parsed commands
├── table.py       # Table data model
├── exceptions.py  # Custom database errors
├── storage.py     # JSON-based persistence layer
```

Each layer has a single responsibility, closely mirroring how real database systems are structured.

## 🧪 How to Run (Windows CMD)
1. Clone the repository
```bash
git clone <repo-url>
cd pesapal-rdbms
```

2. Create and activate a virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Start the database REPL
```bash
python -m mydb.repl
```

## 🖥️ Example Session
```text
Welcome to MyDB. Type 'exit' to quit.

mydb> CREATE TABLE users (
....>   id INT PRIMARY KEY,
....>   email TEXT UNIQUE
....> );
Table 'users' created

mydb> INSERT INTO users VALUES (1, "stephen@example.com");
1 row inserted

mydb> INSERT INTO users VALUES (2, "jane@example.com");
1 row inserted

mydb> SELECT * FROM users;
id | email
----------
1 | stephen@example.com
2 | jane@example.com

(2 rows)

mydb> SELECT * FROM users WHERE id = 1;
id | email
----------
1 | stephen@example.com

(1 rows)

mydb> SELECT * FROM users WHERE email = "jane@example.com";
id | email
----------
2 | jane@example.com

(1 rows)

mydb> UPDATE users SET email = "updated@mail.com" WHERE id = 1;
1 row(s) updated

mydb> SELECT * FROM users;
id | email
----------
1 | updated@mail.com
2 | jane@example.com

(2 rows)

mydb> DELETE FROM users WHERE id = 2;
1 row(s) deleted

mydb> SELECT * FROM users;
id | email
----------
1 | updated@mail.com

(1 rows)

mydb> INSERT INTO users VALUES (2, "jane@example.com");
1 row inserted

mydb> SELECT * FROM users WHERE id = 1;
id | email
----------
1 | updated@mail.com

(1 rows)

mydb> INSERT INTO users VALUES (1, "duplicate@example.com");
Error: Duplicate value for indexed column 'id': 1
```

## 🚧 Known Limitations (Intentional)
- SQL statements must end with a semicolon (;)
- WHERE supports only equality (=); no AND/OR, no comparison operators (<, >, etc.)
- UPDATE supports single-column SET only (no multiple columns yet)
- DELETE requires WHERE clause (full-table DELETE is intentionally disallowed)
- No ORDER BY or column projections yet (only SELECT *)
- Persistence is JSON-based (not crash-safe, no transactions yet)
- Indexes are hash-based (equality only, no range queries or B-trees)
- No composite indexes (single-column indexes only)

These limitations will be addressed incrementally in later stages.

## 🛣️ Roadmap (Next Steps)
Planned features:
- WHERE clause support
- UPDATE and DELETE operations
- Transaction support and crash-safe persistence
- Primary & unique key indexing
- Basic JOIN support
- Simple web application demo using this database

## 🧾 Supported SQL Syntax (Current)

```sql
CREATE TABLE table_name (
  column TYPE [PRIMARY KEY] [UNIQUE]
);

INSERT INTO table_name VALUES (...);

SELECT * FROM table_name [WHERE column = value];

UPDATE table_name SET column = value WHERE column = value;

DELETE FROM table_name WHERE column = value;
```

This grammar will be extended incrementally.

## 📚 References & Credits
- PostgreSQL documentation (conceptual reference)
- SQLite design overview
- Python standard library
- AI assistance (ChatGPT) used for guidance and code review, with full understanding and manual implementation

## 📝 Final Note
This project is an educational exercise designed to demonstrate fundamental database internals and engineering discipline.
Feedback and discussion are welcome.
