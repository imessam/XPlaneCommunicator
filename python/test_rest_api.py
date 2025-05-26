import requests
import json
import sys
import os 

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
if base_path not in sys.path:
    sys.path.insert(0, base_path)

from libs.FPS_Calculator.python.modules.fps import FPS

def main():

    fps = FPS()

    url = "http://192.168.80.77:8088/api/v2/datarefs/1710600641712/value"

    # # defining a params dict for the parameters to be sent to the API
    # params = {'address':location}

    while True:

        fps.start()

        response = requests.get(url = url)

        fps.update()

        current_fps = fps.get_fps()
        avg_fps = fps.get_avg_fps()

        print(f"response received: {response.json()} | Current FPS: {round(current_fps, 2)} | Avg FPS: {round(avg_fps, 2)}")
              
    return 0

if __name__ == "__main__":
    sys.exit(main())