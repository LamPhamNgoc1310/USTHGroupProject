// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts

const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electron", {
  saveVideo: (buffer) => ipcRenderer.send("save-video", buffer),
  onSaveVideoReply: (callback) =>
    ipcRenderer.on("save-video-reply", (event, response) => callback(response)),
});

