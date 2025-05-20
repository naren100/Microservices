import subprocess
import time
import sys
import os

def free_port(port):
    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True, text=True, check=True
        )
        pids = result.stdout.strip().splitlines()
        for pid in pids:
            print(f"🔪 Killing process {pid} on port {port}")
            subprocess.run(["kill", "-9", pid])
    except subprocess.CalledProcessError:
        pass  # No process found on port — nothing to kill

# Free up ports
free_port(8000)
free_port(8001)

python_executable = sys.executable
project_root = os.path.dirname(os.path.abspath(__file__))

menu_dir = os.path.join(project_root, "menu_service")
order_dir = os.path.join(project_root, "order_service")

menu_cmd = [python_executable, "-m", "uvicorn", "main:app", "--port", "8000", "--reload"]
order_cmd = [python_executable, "-m", "uvicorn", "main:app", "--port", "8001", "--reload"]

menu_proc = subprocess.Popen(menu_cmd, cwd=menu_dir)
order_proc = subprocess.Popen(order_cmd, cwd=order_dir)

print("🚀 Services started on ports 8000 (menu) and 8001 (order). Press Ctrl+C to shut down.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 Shutting down services...")
    menu_proc.terminate()
    order_proc.terminate()
    menu_proc.wait()
    order_proc.wait()
    print("✅ All services stopped.")
