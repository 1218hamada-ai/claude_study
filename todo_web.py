"""ToDoリスト Webアプリ（Flask版）"""

from flask import Flask, render_template, request, redirect, url_for
from todo import load_todos, save_todos

app = Flask(__name__)


@app.route("/")
def index():
    todos = load_todos()
    return render_template("index.html", todos=todos)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()
    if title:
        todos = load_todos()
        new_id = max((t["id"] for t in todos), default=0) + 1
        todos.append({"id": new_id, "title": title, "done": False})
        save_todos(todos)
    return redirect(url_for("index"))


@app.route("/done/<int:task_id>", methods=["POST"])
def done(task_id):
    todos = load_todos()
    for task in todos:
        if task["id"] == task_id:
            task["done"] = True
            break
    save_todos(todos)
    return redirect(url_for("index"))


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete(task_id):
    todos = load_todos()
    todos = [t for t in todos if t["id"] != task_id]
    save_todos(todos)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
