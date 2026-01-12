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

### ✅ In-Memory Schema Representation
- Tables are stored in memory using Python data structures
- Each table tracks:
  - Column definitions
  - Constraints
  - Rows (populated via INSERT statements)

### ✅ JSON-Based Disk Persistence
- Automatic save to disk after every `CREATE TABLE` and `INSERT` operation
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
```

## 🚧 Known Limitations (Intentional)
- SQL statements must end with a semicolon (;)
- Only `SELECT * FROM table_name` is supported (no WHERE, ORDER BY, or projections yet)
- Persistence is JSON-based (not crash-safe, no transactions yet)
- No UPDATE or DELETE operations
- No query optimization or indexing

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

SELECT * FROM table_name;
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
