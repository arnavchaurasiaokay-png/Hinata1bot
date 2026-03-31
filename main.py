from bot import Bot
from flask import Flask
import threading
import database  # 👈 change here

app = Flask(__name__)

# ✅ Safe wrapper (no import issue)
def ping_db():
    try:
        return database.ping_db()
    except:
        return False

@app.route("/")
def home():
    if ping_db():
        return "Bot Alive ✅"
    else:
        return "Database Error ❌"

def run_web():
    app.run(host="0.0.0.0", port=8080)

def run_bot():
    Bot().run()

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    run_bot()
