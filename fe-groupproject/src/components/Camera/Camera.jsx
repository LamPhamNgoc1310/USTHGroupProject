// TODO:
// run in background
// accessing local config files using FileReader(), note: must add a function to read auto

import React, { useState, useRef, useEffect } from "react";
import { Button, Modal} from "antd";
import "./Camera.css";

function Camera() {
  const [recording, setRecording] = useState(false);
  const [isUserManualOpen, setIsUserManualOpen] = useState(false); // User Manual modal state
  const [time, setTime] = useState(0);

  useEffect(()=> {
    let timer;
    if(recording) {
        timer = setInterval(()=> {
            setTime((prev) => prev+1)
        }, 1000);
    };

    return () => clearInterval(timer);
  }, [recording])
  
  const formatTime = (time) => {
    const hours = Math.floor(time / 3600);
    const minutes = Math.floor((time % 3600)/60);
    const seconds = Math.floor((time % 3600) % 60);
    return `${hours.toString().padStart(2,"0")}:${minutes.toString().padStart(2,"0")}:${seconds.toString().padStart(2,"0")}`
  }

  const handleStartRecording = () => {
    setRecording((prev)=>!prev);
  };

  const handleStopRecording = () => {
    setRecording((prev)=>!prev);
  };

  // Handle modal open/close for User Manual
  const handleUserManualModal = (open) => setIsUserManualOpen(open);

  return (
    <div className="camera-container">
      <div className="camera-select"></div>
      <div className="video-container">
        {/* <video className="video" ref={videoRef}></video> */}
      </div>
      <div className="button-container">
        {/* Recording Button */}
        {recording ? (
          <Button
            className="stop-button"
            type="primary"
            onClick={handleStartRecording}
          >
            <span className="btn-text">Stop</span>
          </Button>
        ) : (
          <Button
            className="record-button"
            type="primary"
            onClick={handleStopRecording}
          >
            <span className="btn-text">Record</span>
          </Button>
        )}
        <Button onClick={() => setTime(0)}>Reset time</Button>
        <span>{formatTime(time)}</span>

        {/* User Manual Button */}
        <Button
          className="manual-button"
          type="link"
          onClick={() => handleUserManualModal(true)}
        >
          <div>User Manual</div>
        </Button>

        {/* User Manual Modal */}
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
            <li>
              What hand gestures the camera saw will be the input to the app
            </li>
          </ul>
          <ul>
            <h2>2. Setting</h2>
            <li>Press "Open Keybind Setting" to open the setting</li>
            <li>The window is where you setup your keybinding</li>
            <li>Labels can be asigned to a shortcut/key</li>
          </ul>
        </Modal>
      </div>
    </div>
  );
}

export default Camera;
