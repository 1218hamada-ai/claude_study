"""にゃんDoリスト - ブラウザ版"""

import json
import re
import sys
from pathlib import Path

from flask import Flask, request, redirect, url_for

app = Flask(__name__)
TODO_FILE = Path(__file__).parent / "todos.json"


# --- データ操作 ---

def load_todos():
    if TODO_FILE.exists():
        return json.loads(TODO_FILE.read_text(encoding="utf-8"))
    return []


def save_todos(todos):
    TODO_FILE.write_text(json.dumps(todos, ensure_ascii=False, indent=2), encoding="utf-8")


def to_neko(text):
    """テキストを猫語に変換するニャ"""
    result = text
    result = re.sub(r'です', 'ですニャ', result)
    result = re.sub(r'ます', 'ますニャ', result)
    result = re.sub(r'した', 'したニャ', result)
    result = re.sub(r'ない', 'ニャい', result)
    result = re.sub(r'ある', 'あるニャ', result)
    result = re.sub(r'する', 'するニャ', result)
    result = re.sub(r'だ([。！\s]|$)', r'だニャ\1', result)
    if 'ニャ' not in result:
        result = result + ' ニャー'
    return result


# --- HTML テンプレート ---

def render_page(todos):
    rows = ""
    for task in todos:
        neko_title = to_neko(task["title"])
        done_class = "done" if task["done"] else ""
        check_btn = "" if task["done"] else f'''
            <form method="post" action="/done/{task['id']}" style="display:inline">
                <button type="submit" class="btn btn-done" title="完了ニャ">✅</button>
            </form>'''
        rows += f'''
        <tr class="{done_class}">
            <td class="id">{task['id']}</td>
            <td class="title">{neko_title}</td>
            <td class="status">{"😸 済ニャ！" if task["done"] else "🐱 まだニャ"}</td>
            <td class="actions">
                {check_btn}
                <form method="post" action="/delete/{task['id']}" style="display:inline">
                    <button type="submit" class="btn btn-delete" title="削除ニャ">🗑️</button>
                </form>
            </td>
        </tr>'''

    if not todos:
        rows = '<tr><td colspan="4" class="empty">タスクはニャいニャー！暇だニャ～ 🐈</td></tr>'

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🐱 にゃんDoリスト</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: "Segoe UI", "Yu Gothic UI", "Meiryo", sans-serif;
            background: linear-gradient(135deg, #fce4ec 0%, #fff3e0 50%, #e8f5e9 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 700px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            font-size: 2.2em;
            color: #5d4037;
            margin-bottom: 8px;
        }}
        .subtitle {{
            text-align: center;
            color: #8d6e63;
            margin-bottom: 24px;
            font-size: 0.95em;
        }}
        .add-form {{
            display: flex;
            gap: 8px;
            margin-bottom: 24px;
        }}
        .add-form input[type="text"] {{
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #ffcc80;
            border-radius: 12px;
            font-size: 1em;
            outline: none;
            transition: border-color 0.2s;
        }}
        .add-form input[type="text"]:focus {{
            border-color: #ff8a65;
        }}
        .add-form button {{
            padding: 12px 24px;
            background: #ff8a65;
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.2s;
            white-space: nowrap;
        }}
        .add-form button:hover {{ background: #ff7043; }}
        table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0 6px;
        }}
        th {{
            text-align: left;
            padding: 8px 12px;
            color: #8d6e63;
            font-size: 0.85em;
            font-weight: normal;
        }}
        td {{
            background: white;
            padding: 14px 12px;
        }}
        tr td:first-child {{ border-radius: 12px 0 0 12px; }}
        tr td:last-child {{ border-radius: 0 12px 12px 0; }}
        .id {{ width: 40px; text-align: center; color: #bdbdbd; font-weight: bold; }}
        .title {{ font-size: 1.05em; color: #424242; }}
        .status {{ width: 100px; text-align: center; font-size: 0.9em; }}
        .actions {{ width: 90px; text-align: center; }}
        tr.done td {{ opacity: 0.55; }}
        tr.done .title {{ text-decoration: line-through; }}
        .btn {{
            border: none;
            background: none;
            font-size: 1.2em;
            cursor: pointer;
            padding: 4px 6px;
            border-radius: 6px;
            transition: background 0.15s;
        }}
        .btn:hover {{ background: #f5f5f5; }}
        .empty {{
            text-align: center;
            padding: 40px 12px !important;
            color: #bdbdbd;
            font-size: 1.1em;
            border-radius: 12px !important;
        }}
        .footer {{
            text-align: center;
            margin-top: 20px;
            color: #bcaaa4;
            font-size: 0.85em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🐱 にゃんDoリスト</h1>
        <p class="subtitle">タスクは全部猫語で表示されるニャ！</p>

        <form class="add-form" method="post" action="/add">
            <input type="text" name="title" placeholder="新しいタスクを入力するニャ..." required autofocus>
            <button type="submit">追加ニャ！</button>
        </form>

        <table>
            <thead>
                <tr><th></th><th>タスク</th><th>状態</th><th></th></tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>

        <p class="footer">にゃー！以上ニャ！ 🐾</p>
    </div>
</body>
</html>'''


# --- ルーティング ---

@app.route("/")
def index():
    todos = load_todos()
    return render_page(todos)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()
    if title:
        todos = load_todos()
        task = {"id": len(todos) + 1, "title": title, "done": False}
        todos.append(task)
        save_todos(todos)
    return redirect(url_for("index"))


@app.route("/done/<int:task_id>", methods=["POST"])
def done(task_id):
    todos = load_todos()
    for task in todos:
        if task["id"] == task_id:
            task["done"] = True
            save_todos(todos)
            break
    return redirect(url_for("index"))


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete(task_id):
    todos = load_todos()
    todos = [t for t in todos if t["id"] != task_id]
    save_todos(todos)
    return redirect(url_for("index"))


# --- CLI互換 ---

def cli_main():
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command == "add" and len(sys.argv) >= 3:
        title = " ".join(sys.argv[2:])
        todos = load_todos()
        task = {"id": len(todos) + 1, "title": title, "done": False}
        todos.append(task)
        save_todos(todos)
        print(f"タスクを追加しました: {title}")
    elif command == "list":
        todos = load_todos()
        if not todos:
            print("タスクはニャいニャー！暇だニャ～")
            return
        print("\n--- にゃんDoリスト ---")
        for task in todos:
            status = "[済ニャ]" if task["done"] else "[ ]"
            print(f"  {task['id']}. {status} {to_neko(task['title'])}")
        print("  にゃー！以上ニャ！\n")
    else:
        print("使い方: python todo.py [web|add|list]")
        print("  web   … ブラウザ版を起動")
        print("  add   … タスクを追加")
        print("  list  … タスク一覧を表示")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        print("🐱 にゃんDoリストを起動中… http://localhost:5000")
        app.run(debug=True, port=5000)
    elif len(sys.argv) > 1:
        cli_main()
    else:
        print("🐱 にゃんDoリストを起動中… http://localhost:5000")
        app.run(debug=True, port=5000)
