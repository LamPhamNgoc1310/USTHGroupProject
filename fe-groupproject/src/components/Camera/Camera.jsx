import React, { useState, useEffect, useRef } from 'react';
import { Button, Modal } from 'antd';
import './Camera.css';

function Camera() {
  const [recording, setRecording] = useState(false);
  const [isUserManualOpen, setIsUserManualOpen] = useState(false);
  const [time, setTime] = useState(0);
  const [frame, setFrame] = useState(null);

  const videoRef = useRef(null);
  const mediaRecorder = useRef(null);
  const recordedChunks = useRef([]);

  useEffect(() => {
    // Receive frames from the main process via IPC
    window.electron.onFrameReceived((frameBase64) => {
      setFrame(`data:image/jpeg;base64,${frameBase64}`);
    });
  
    return () => {
      // Clean up listener on unmount
      window.electron.removeFrameListener();
    };
  }, []);

  useEffect(() => {
    let timer;
    if (recording) {
      timer = setInterval(() => {
        setTime((prev) => prev + 1);
      }, 1000);
    } else {
      clearInterval(timer);
    }

    return () => clearInterval(timer);
  }, [recording]);

  const formatTime = (time) => {
    const hours = Math.floor(time / 3600);
    const minutes = Math.floor((time % 3600) / 60);
    const seconds = time % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes
      .toString()
      .padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  const handleStartRecording = () => {
    setRecording(true);
    // Send a message to the main process to start recording
    window.electron.ipcRenderer.send('start-recording');
  };

  const handleStopRecording = () => {
    setRecording(false);
    // Send a message to the main process to stop recording
    window.electron.ipcRenderer.send('stop-recording');
  };

  const handleUserManualModal = (open) => setIsUserManualOpen(open);

  return (
    <div className="camera-container">
      <div className="camera-select"></div>

      <div className="video-container">
        {frame && (
          <img
            ref={videoRef}
            src={frame}
            alt="Camera Feed"
            className="video"
            style={{ width: '640px', height: '480px' }}
          />
        )}
      </div>

      <div className="button-container">
        {recording ? (
          <Button className="stop-button" type="primary" onClick={handleStopRecording}>
            <span className="btn-text">Stop Recording</span>
          </Button>
        ) : (
          <Button className="record-button" type="primary" onClick={handleStartRecording}>
            <span className="btn-text">Record</span>
          </Button>
        )}
        <Button onClick={() => setTime(0)}>Reset time</Button>
        <span>{formatTime(time)}</span>

        <Button className="manual-button" type="link" onClick={() => handleUserManualModal(true)}>
          <div>User Manual</div>
        </Button>

        <Modal
          title="User Manual"
          open={isUserManualOpen}
          onOk={() => handleUserManualModal(false)}
          onCancel={() => handleUserManualModal(false)}
        >
          <h1>User Manual</h1>
          <ul>
            <h2>1. Recording</h2>
            <li>Press the "RECORD" button to start the camera</li>
            <li>What hand gestures the camera saw will be the input to the app</li>
          </ul>
          <ul>
            <h2>2. Setting</h2>
            <li>Press "Open Keybind Setting" to open the setting</li>
            <li>The window is where you setup your keybinding</li>
            <li>Labels can be assigned to a shortcut/key</li>
          </ul>
        </Modal>
      </div>
    </div>
  );
}

export default Camera;
