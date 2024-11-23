import pythoncom
from pygrabber.dshow_graph import FilterGraph
from flask import Flask, jsonify

app = Flask(__name__)

# Function to list all the available camera sources
def list_cameras():
    pythoncom.CoInitialize()
    try:
        graph = FilterGraph()
        devices = graph.get_input_devices()
        return devices
    finally:
        pythoncom.CoUninitialize()

@app.route('/camera_sources', methods=['GET'])
def getCameraSourceAPI():
    cameras = list_cameras()
    camera_list = [{'id': i, 'name': camera} for i, camera in enumerate(cameras)]
    return jsonify(camera_list)



if __name__ == '__main__':
    app.run(debug=True)