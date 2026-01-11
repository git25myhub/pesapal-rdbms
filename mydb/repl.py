from mydb.parser import parse
from mydb.executor import Database

def run_repl():
    db = Database()
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
