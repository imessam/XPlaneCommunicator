from enum import Enum

class XPlaneCommunicator:

    class RETURN_STATUS(Enum):
        OK = 0
        OK_CONNECTED = 1
        OK_DISCONNECTED = 2
        
        ERROR = 3
        ERROR_CANNOT_CONNECT = 4
        ERROR_CANNOT_DISCONNECT = 5

    def __init__(self, xplane_host_ip: str, xplane_host_port: str) -> None:
        
        self.xplane_host_ip : str = xplane_host_ip
        self.xplane_host_port : str = xplane_host_port

    def connect(self) -> RETURN_STATUS:
        
        status = XPlaneCommunicator.RETURN_STATUS.OK_CONNECTED

        return status


    def disconnect(self) -> RETURN_STATUS:
        
        status = XPlaneCommunicator.RETURN_STATUS.OK_DISCONNECTED

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
