from mydb.parser import parse
from mydb.executor import Database
from mydb.storage import load_database

def run_repl():
    tables = load_database()
    db = Database()
    db.tables = tables
    print("Welcome to MyDB. Type 'exit' to quit.")

    buffer = ""

    while True:
        try:
            prompt = "mydb> " if not buffer else "....> "
            line = input(prompt)

            if line.lower() in ("exit", "quit"):
                break

            buffer += line.strip() + " "

            if ";" not in buffer:
                continue  # wait for full statement

            sql = buffer
            buffer = ""

            ast = parse(sql)
            result = db.execute(ast)
            print(result)

        except Exception as e:
            buffer = ""
            print(f"Error: {e}")

if __name__ == "__main__":
    run_repl()
