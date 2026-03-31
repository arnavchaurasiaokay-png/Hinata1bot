from bot import Bot
from flask import Flask
import threading
from database import ping_db

app = Flask(__name__)

# ✅ Health / Ping Route
@app.route("/")
def home():
    if ping_db():
        return "Bot Alive ✅"
    else:
        return "Database Error ❌"


# ✅ Run Flask server
def run_web():
    app.run(host="0.0.0.0", port=8080)


# ✅ Run Telegram Bot
def run_bot():
    Bot().run()


# ✅ Start both together
if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    run_bot()
