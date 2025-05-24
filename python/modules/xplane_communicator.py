import sys
import os 
import socket
import threading
import struct


base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if base_path not in sys.path:
    sys.path.insert(0, base_path)

from libs.FPS_Calculator.python.modules.fps import FPS
from typing import Dict, Union


from enum import Enum
from collections import deque


XPLANE_HEADER_SIZE = 5
XPLANE_DATA_SIZE = 36
XPLANE_NUM_DATA = 172
XPLANE_MAX_PACKET_SIZE = XPLANE_HEADER_SIZE + (XPLANE_NUM_DATA * XPLANE_DATA_SIZE) 

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

        self.xplane_receiver_thread = threading.Thread(target=self.receive_data_from_xplane_loop, args=())
        self.xplane_data_parser_thread = threading.Thread(target=self.parse_data_from_xplane_loop, args=())

        self._is_quit = False


    def connect(self) -> RETURN_STATUS:
        
        print(f"{self._my_name} :: Establishing connection to XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port}")

        status = XPlaneCommunicator.RETURN_STATUS.OK_CONNECTED

        self.listener_from_xplane.bind((self.xplane_listener_ip, self.xplane_listener_port))

        print(f"{self._my_name} :: Trying to receive data from XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port}")

        data, addr = self.listener_from_xplane.recvfrom(XPLANE_MAX_PACKET_SIZE)

        print(f"Received data from XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port}, from address: {addr}, data: {data}, data length: {len(data)}")

        print(f"{self._my_name} :: Connection to XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port} established.")

        return status
    
    def receive_data_from_xplane_loop(self) -> None:

        print(f"{self._my_name} :: receiving data from XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port}")

        current_udp_rate, avg_udp_rate = 0.0, 0.0

        data_counter = 0

        while not self._is_quit:

            self.fps_calculator_receiver.start()

            data, addr = self.listener_from_xplane.recvfrom(XPLANE_MAX_PACKET_SIZE)

            self.xplane_received_data_queue.append((data, data_counter))

            self.fps_calculator_receiver.update()

            current_udp_rate = self.fps_calculator_receiver.get_fps()
            avg_udp_rate =  self.fps_calculator_receiver.get_avg_fps()

            print(f"Current UDP rate: {current_udp_rate} | Avg UDP rate: {avg_udp_rate}, XPlane address: {addr}, XPlane data length: {len(data)}, data count: {data_counter}")

            data_counter += 1


        print(f"{self._my_name} :: stopped receiving data from XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port}")

        return
    
    def parse_data_from_xplane_loop(self) -> None:

        print(f"{self._my_name} :: parsing data from XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port}")

        while not self._is_quit:

            if len(self.xplane_received_data_queue) == 0:
                continue

            data, data_counter = self.xplane_received_data_queue.popleft()

            print(f"{self._my_name} :: Parsing data number : {data_counter} from XPlane.")

            self.parse(data)
            

        print(f"{self._my_name} :: stopped parsing data from XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port}")

        return
    
    def parse(self, data: bytes) -> Union[None, Dict]:

        '''
        Now, the protocol : 

        The first 4 byte are the header. if xplane send data (stuff you selected in the data output) they read, in ASCII : "DATA".
        followed by 1 byte you can ignore
        followed by 4 byte, but only the first of the four is important : it's the index (the stuff in the 1st column)
        followed by 8*4 byte : they are the data. For more inforation also check "show in cockpit" in the preference so you'll now more about what the data are.
        then you have another pack of 4 + 8*4 until the end of the datagram.
        rince, repeat.

        '''

        print(f"{self._my_name} :: Parsing data from XPlane, data length: {len(data)}")

        if len(data) < XPLANE_HEADER_SIZE+XPLANE_DATA_SIZE:
            print(f"{self._my_name} :: Data is too small to be parsed.")
            return None
        
        parsed_data = {}

        data_without_header = data[XPLANE_HEADER_SIZE:]

        all_data_size = len(data_without_header)

        print(f"{self._my_name} :: Number of data fields: {all_data_size // XPLANE_DATA_SIZE}")

        for data_start_idx in range(0, all_data_size, XPLANE_DATA_SIZE):

            data_end = data_start_idx + XPLANE_DATA_SIZE

            data_field = data_without_header[data_start_idx:data_end]

            field_index = data_field[0]

            rest_of_data = data_field[4:]

            print(f"{self._my_name} :: Parsing data field number: {field_index}")

            for i in range(0, len(rest_of_data), 4):

                data_value = struct.unpack('f', rest_of_data[i:i+4])[0]

                print(f"field index: {field_index}, data index: {i//4}, data value: {data_value}")

        return parsed_data
    


    def start_receiving_loop(self) -> RETURN_STATUS:

        print(f"{self._my_name} :: Starting to receive data loop from XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port}")

        status = XPlaneCommunicator.RETURN_STATUS.OK_LOOP_STARTED

        self.xplane_receiver_thread.start()

        print(f"{self._my_name} :: Started to receive data loop from XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port}")

        return status
    
    def start_parsing_loop(self) -> RETURN_STATUS:

        print(f"{self._my_name} :: Starting to parse data loop from XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port}")

        status = XPlaneCommunicator.RETURN_STATUS.OK_LOOP_STARTED

        self.xplane_data_parser_thread.start()

        print(f"{self._my_name} :: Started to parse data loop from XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port}")

        return status

    def stop_receiving_loop(self) -> RETURN_STATUS:

        print(f"{self._my_name} :: Stopping to receive data loop from XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port}")

        status = XPlaneCommunicator.RETURN_STATUS.OK_LOOP_STOPPED

        self._is_quit = True

        self.xplane_receiver_thread.join()

        print(f"{self._my_name} :: Stopped to receive data loop from XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port}")

        return status
    
    def stop_parsing_loop(self) -> RETURN_STATUS:

        print(f"{self._my_name} :: Stopping to parse data loop from XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port}")

        status = XPlaneCommunicator.RETURN_STATUS.OK_LOOP_STOPPED

        self._is_quit = True

        self.xplane_data_parser_thread.join()

        print(f"{self._my_name} :: Stopped to parse data loop from XPlane at {self.xplane_listener_ip}:{self.xplane_listener_port}")

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
