import websockets
import json
import sys
import os 

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
if base_path not in sys.path:
    sys.path.insert(0, base_path)


from websockets.sync.client import connect

from libs.FPS_Calculator.python.modules.fps import FPS

def main():

    fps = FPS()

    url = "ws://192.168.80.77:8088/api/v2"

    socker = connect(url)

    message = {
            "req_id": 9998, 
            "type": "dataref_subscribe_values",
            "params": {
                "datarefs": [ 
                    { "id": 1710600641712  }

                ]
            }
    }

    json_message = json.dumps(message)

    socker.send(json_message)

    while True:

        fps.start()

        message = socker.recv()

        fps.update()

        current_fps = fps.get_fps()
        avg_fps = fps.get_avg_fps()

        print(f"message received: {message} | Current FPS: {round(current_fps, 2)} | Avg FPS: {round(avg_fps, 2)}")
              
    socker.close()

    return 0

if __name__ == "__main__":
    sys.exit(main())