import sys
import os 
import socket
import threading

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if base_path not in sys.path:
    sys.path.insert(0, base_path)

from libs.FPS_Calculator.python.modules.fps import FPS

from enum import Enum
from collections import deque

class XPlaneCommunicator:

    class RETURN_STATUS(Enum):
        OK = 0
        OK_CONNECTED = 1
        OK_DISCONNECTED = 2
        OK_LOOP_STARTED = 3
        OK_LOOP_STOPPED = 4
        
        ERROR = 5
        ERROR_CANNOT_CONNECT = 6
        ERROR_CANNOT_DISCONNECT = 7
        ERROR_CANNOT_START_LOOP = 8
        ERROR_CANNOT_STOP_LOOP = 9

    def __init__(self, xplane_listener_ip: str = "0.0.0.0", xplane_listener_port: int = 49000) -> None:

        self._my_name = "XPlaneCommunicator"
        
        self.xplane_listener_ip : str = xplane_listener_ip
        self.xplane_listener_port : int = xplane_listener_port

        self.listener_from_xplane = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.xplane_received_data_queue = deque(maxlen=100)

        self.fps_calculator_receiver = FPS()

        self.xplane_receiver_thread = threading.Thread(target=self.receive_data_from_xplane, args=())

        self._is_quit = False


    def connect(self) -> RETURN_STATUS:
        
        print(f"{self._my_name} :: Establishing connection to XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port}")

        status = XPlaneCommunicator.RETURN_STATUS.OK_CONNECTED

        self.listener_from_xplane.bind((self.xplane_listener_ip, self.xplane_listener_port))

        print(f"{self._my_name} :: Trying to receive data from XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port}")

        data, addr = self.listener_from_xplane.recvfrom(1024)

        print(f"Received data from XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port}, from address: {addr}, data: {data}, data length: {len(data)}")

        print(f"{self._my_name} :: Connection to XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port} established.")

        return status
    
    def receive_data_from_xplane(self) -> None:

        print(f"{self._my_name} :: receiving data from XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port}")

        current_fps, avg_fps = 0.0, 0.0

        while not self._is_quit:

            self.fps_calculator_receiver.start()

            data, addr = self.listener_from_xplane.recvfrom(1024)

            self.fps_calculator_receiver.update()

            current_fps = self.fps_calculator_receiver.get_fps()
            avg_fps =  self.fps_calculator_receiver.get_avg_fps()

            print(f"Current FPS: {current_fps} | Avg FPS: {avg_fps}")

            self.xplane_received_data_queue.append(data)

        print(f"{self._my_name} :: stopped receiving data from XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port}")

        return

    def start_receiving_loop(self) -> RETURN_STATUS:

        print(f"{self._my_name} :: Starting to receive data loop from XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port}")

        status = XPlaneCommunicator.RETURN_STATUS.OK_LOOP_STARTED

        self.xplane_receiver_thread.start()

        print(f"{self._my_name} :: Started to receive data loop from XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port}")

        return status

    def stop_receiving_loop(self) -> RETURN_STATUS:

        print(f"{self._my_name} :: Stopping to receive data loop from XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port}")

        status = XPlaneCommunicator.RETURN_STATUS.OK_LOOP_STOPPED

        self._is_quit = True

        self.xplane_receiver_thread.join()

        print(f"{self._my_name} :: Stopped to receive data loop from XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port}")

        return status

    def disconnect(self) -> RETURN_STATUS:
        
        print(f"{self._my_name} :: Disconnecting from XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port}")

        status = XPlaneCommunicator.RETURN_STATUS.OK_DISCONNECTED

        self.listener_from_xplane.close()

        print(f"{self._my_name} :: Disconnected from XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port}")

        return status


    def getStatusMessage(self, status: RETURN_STATUS) -> str:

        mapping = {
            XPlaneCommunicator.RETURN_STATUS.OK: "OK",
            XPlaneCommunicator.RETURN_STATUS.OK_CONNECTED: "OK connected",
            XPlaneCommunicator.RETURN_STATUS.OK_DISCONNECTED: "OK disconnected",
            XPlaneCommunicator.RETURN_STATUS.ERROR: "Error",
            XPlaneCommunicator.RETURN_STATUS.ERROR_CANNOT_CONNECT: "Error cannot CONNECT",
            XPlaneCommunicator.RETURN_STATUS.ERROR_CANNOT_DISCONNECT: "Error cannot DISCONNECT",
        }
        return mapping.get(status, "Unknown error")
