from bot import Bot
from keep_alive import keep_alive

# 🔹 UptimeRobot ke liye server start
keep_alive()

# 🔹 Bot run
Bot().run()
