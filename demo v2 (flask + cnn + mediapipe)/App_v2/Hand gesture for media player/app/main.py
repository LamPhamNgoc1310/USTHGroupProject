from PyQt5.QtWidgets import QApplication
import sys
from WebcamViewer2 import WebcamViewer

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    viewer = WebcamViewer()
    viewer.show()
    sys.exit(app.exec_())
    # print("done")