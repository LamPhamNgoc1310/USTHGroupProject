// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  // Method to receive frame data
  onFrameReceived: (callback) => {
    ipcRenderer.on('frame-data', (event, message) => callback(message));
  },

  // Optional: Method to remove the frame data listener if needed
  removeFrameListener: () => {
    ipcRenderer.removeAllListeners('frame-data');
  },

  // Optional: Add any other IPC functionality as needed
  sendMessage: (channel, data) => {
    ipcRenderer.send(channel, data);
  }
});

