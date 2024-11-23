// TODO:  
// run in background
// accessing local config files using FileReader(), note: must add a function to read auto

import React, { useState, useRef, useEffect } from "react";
import { Button, Modal, Select } from "antd";
import "./Camera.css";

function Camera() {
  const [recording, setRecording] = useState(false);
  const [isUserManualOpen, setIsUserManualOpen] = useState(false); // User Manual modal state

  // Toggle recording state
  const toggleRecording = () => setRecording((prev) => !prev);

  // Handle modal open/close for User Manual
  const handleUserManualModal = (open) => setIsUserManualOpen(open);

  // Get camera
  const [cameras, setCameras] = useState([]);
  const [selectedCameraId, setSelectedCameraId] = useState(null);
  const getCameras = async () => {
    try {
      const cameras = await navigator.mediaDevices.enumerateDevices();
      setCameras(cameras.filter((camera) => camera.kind === "videoinput"));
      if(cameras.length >0) {
        setSelectedCameraId(cameras[0].deviceId);
      }
    } catch (e) {
      console.log("getCamera error:", e);
    }
  };
  useEffect(() => {
    getCameras();
  }, []);

  // Video capture
  const videoRef = useRef(null);

  const getVideo = (cameraId) => {
    console.log("Selected Camera Id:", selectedCameraId);
    navigator.mediaDevices
      .getUserMedia({
        video: { 
          deviceId: cameraId ? { exact: cameraId } : undefined,
          width: 1920, height: 1080 },
      })
      .then((stream) => {
        let video = videoRef.current;
        video.srcObject = stream;
        video.play();
      })
      .catch((e) => {
        console.error("getVideo error:", e);
      });
  };

  useEffect(() => {
    if (selectedCameraId) {
      getVideo(selectedCameraId);
    }

  }, [selectedCameraId]);

  
  return (
    <div className="camera-container">
      <div className="camera-select">
        <Select
          placeholder="Select a Camera"
          style={{ width: 200 }}
          onChange={(value) => setSelectedCameraId(value)}
          value={selectedCameraId}
        >
          {cameras.map((camera) => (
            <Select.Option key={camera.deviceId} value={camera.deviceId}>
              {camera.label}
            </Select.Option>
          ))}
        </Select>
      </div>
      <div className="video-container">
        <video className="video" ref={videoRef}></video>
      </div>
      <div className="button-container">
        {/* Recording Button */}
        <Button
          className="record-button"
          type="primary"
          onClick={toggleRecording}
        >
          <span className="btn-text">{recording ? "STOP" : "RECORD"}</span>
        </Button>
        <span>{recordingTime}hello</span>

        {/* User Manual Button */}
        <Button
          className="manual-button"
          type="link"
          onClick={() => handleUserManualModal(true)}
        >
          User Manual
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
