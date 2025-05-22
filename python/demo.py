import sys
import os 

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
if base_path not in sys.path:
    sys.path.insert(0, base_path)


from modules.xplane_communicator import XPlaneCommunicator

def main():

    xplane_communicator = XPlaneCommunicator()
    
    if xplane_communicator.connect() != XPlaneCommunicator.RETURN_STATUS.OK_CONNECTED:
        return 1
    
    xplane_communicator.start_receiving_loop()

    input_char = ""

    while input_char != "q":
        input_char = input("Press 'q' to quit: ")
    
    xplane_communicator.stop_receiving_loop()
    
    xplane_communicator.disconnect()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())