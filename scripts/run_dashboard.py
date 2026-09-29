import sys
import os
import webbrowser
import threading
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nexus.dashboard.server import run_server

def open_browser():
    time.sleep(1)
    webbrowser.open("http://localhost:8090")

if __name__ == "__main__":
    threading.Thread(target=open_browser).start()
    run_server()
