"""
Main runner - Choose mode:
    python run.py api        - Run Flask API only
    python run.py simulator  - Run data simulator
    python run.py listener   - Run Firebase listener
    python run.py all        - Run everything
"""
import sys
import threading
import time
from config.firebase_config import FirebaseConfig
from services.backend import LimixBackend

FIREBASE_URL = 'https://limix-fishfarm-v2-default-rtdb.firebaseio.com'  

def run_api():
    from api.app import app
    app.run(host='0.0.0.0', port=5000, debug=True) 

def run_simulator():
    FirebaseConfig.initialize(database_url=FIREBASE_URL)
    backend = LimixBackend()
    backend.start_simulator(interval=10)

def run_listener():
    FirebaseConfig.initialize(database_url=FIREBASE_URL)
    backend = LimixBackend()
    backend.start_listener()

def run_all():
    FirebaseConfig.initialize(database_url=FIREBASE_URL)
    backend = LimixBackend()
    
    
    # Threads
    threading.Thread(target=backend.start_simulator, kwargs={'interval': 10}, daemon=True).start()
    threading.Thread(target=backend.start_listener, daemon=True).start()
    
    time.sleep(2)
    print("🚀 All services running!")
    run_api()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python run.py [api|simulator|listener|all]")
        sys.exit(1)
    
    mode = sys.argv[1]
    {'api': run_api, 'simulator': run_simulator, 
     'listener': run_listener, 'all': run_all}.get(mode, lambda: print("Invalid mode"))()
