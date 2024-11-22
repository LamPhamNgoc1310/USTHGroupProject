from pygrabber.dshow_graph import FilterGraph


# Function to list all the available camera sources
def list_cameras():
    graph = FilterGraph()
    devices = graph.get_input_devices()
    return devices