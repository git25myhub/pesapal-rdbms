import sys
import os

# Add parent directory to path so we can import mydb
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, render_template, redirect, url_for
from mydb.parser import parse
from mydb.executor import Database
from mydb.storage import load_database, save_database

app = Flask(__name__)

# Load database on startup
tables = load_database()
db = Database()
db.tables = tables

def get_users():
    """Helper function to get users as structured data."""
    if "users" not in db.tables:
        return []
    
    table = db.tables["users"]
    headers = list(table.columns.keys())
    users = []
    
    for row in table.rows:
        user_dict = {}
        for col in headers:
            user_dict[col] = row[col]
        users.append(user_dict)
    
    return users

@app.route("/")
def index():
    users = get_users()
    return render_template("users.html", users=users)

@app.route("/add", methods=["POST"])
def add_user():
    email = request.form["email"]
    
    # Ensure users table exists
    if "users" not in db.tables:
        # Create users table if it doesn't exist
        create_sql = "CREATE TABLE users (id INT PRIMARY KEY, email TEXT UNIQUE);"
        create_ast = parse(create_sql)
        db.execute(create_ast)
    
    # Get the next ID (simple approach for demo)
    users = get_users()
    next_id = 1
    if users:
        next_id = max(user["id"] for user in users) + 1
    
    # Insert using SQL
    sql = f'INSERT INTO users VALUES ({next_id}, "{email}");'
    ast = parse(sql)
    db.execute(ast)
    
    return redirect(url_for("index"))

@app.route("/delete/<int:user_id>")
def delete_user(user_id):
    if "users" not in db.tables:
        return redirect(url_for("index"))
    
    sql = f"DELETE FROM users WHERE id = {user_id};"
    ast = parse(sql)
    db.execute(ast)
    
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
