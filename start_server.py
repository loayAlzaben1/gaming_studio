import os
import subprocess
import time
import webbrowser

# Start Django server
server_process = subprocess.Popen(["python", "manage.py", "runserver"], cwd=os.getcwd())

# Start ngrok and wait for it to initialize
ngrok_process = subprocess.Popen(["ngrok", "http", "8000"], cwd=os.getcwd(), stdout=subprocess.PIPE, text=True)
time.sleep(2)  # Give ngrok time to start

# Extract ngrok URL
ngrok_url = None
for line in ngrok_process.stdout:
    if "https" in line and "ngrok-free.app" in line:
        ngrok_url = line.split("->")[0].strip().split()[-1]
        break

if ngrok_url:
    home_url = ngrok_url
    webbrowser.open(home_url)
    print(f"Opened home page at: {home_url}")
else:
    print("Failed to get ngrok URL. Falling back to local URL.")
    webbrowser.open("http://127.0.0.1:8000/")
    print("Opened home page at: http://127.0.0.1:8000/")

# Keep script running to keep processes alive
try:
    server_process.wait()
    ngrok_process.wait()
except KeyboardInterrupt:
    server_process.terminate()
    ngrok_process.terminate()