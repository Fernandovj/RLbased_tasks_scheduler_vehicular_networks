import thread
import socket
import os
import time
import sys
import signal

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Environment variable SUMO_HOME not defined")


class UnusedPortLock:
    lock = thread.allocate_lock()

    def __init__(self):
        self.acquired = False

    def __enter__(self):
        self.acquire()

    def __exit__(self):
        self.release()

    def acquire(self):
        if not self.acquired:
            UnusedPortLock.lock.acquire()
            self.acquired = True

    def release(self):
        if self.acquired:
            UnusedPortLock.lock.release()
            self.acquired = False


def find_unused_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.bind(('127.0.0.1', 0))
    sock.listen(socket.SOMAXCONN)
    ipaddr, port = sock.getsockname()
    sock.close()
    
    return port

def terminate_sumo(sumo):
	if sumo.returncode == None:
	    os.kill(sumo.pid, signal.SIGTERM)
	    time.sleep(0.5)
	    if sumo.returncode == None:
	        os.kill(sumo.pid, signal.SIGKILL)
	        time.sleep(1)
	        if sumo.returncode == None:
	            time.sleep(10)