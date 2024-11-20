// TODO:
// run in background
// accessing local config files using FileReader(), note: must add a function to read auto

import React, { useState, useEffect, useRef } from "react";
import { Button, Modal} from "antd";
import "./Camera.css";

const { ipcRenderer } = window.require('electron')

function Camera() {
  const [recording, setRecording] = useState(false);
  const [isUserManualOpen, setIsUserManualOpen] = useState(false); // User Manual modal state
  const [time, setTime] = useState(0);

  const videoRef = useRef(null);
  const mediaRecorder = useRef(null);
  const recordedChunks = useRef([]);

   // Start video stream from the user's camera
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoRef.current.srcObject = stream;
      videoRef.current.play();
      mediaRecorder.current = new MediaRecorder(stream, { mimeType: "video/webm" });

      mediaRecorder.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          recordedChunks.current.push(event.data);
        }
      };

      mediaRecorder.current.onstop = async () => {
        // Combine chunks into a single Blob
        const blob = new Blob(recordedChunks.current, { type: "video/webm" });
        recordedChunks.current = [];

        // Convert blob to buffer and send to main process for saving
        const buffer = Buffer.from(await blob.arrayBuffer());
        ipcRenderer.send("save-video", buffer); // Send the video buffer to the main process

        // Handle the save response
        ipcRenderer.once("save-video-reply", (event, response) => {
          if (response.success) {
            console.log("Video saved successfully.");
          } else {
            console.error("Failed to save video:", response.error);
          }
        });
      };
    } catch (error) {
      console.error("Error accessing camera:", error);
      alert("Failed to access the camera. Please check your camera permissions.");
    }
  };

  useEffect(() => {
    let timer;
    if (recording) {
      timer = setInterval(() => {
        setTime((prev) => prev + 1);
      }, 1000);
    } else {
      clearInterval(timer); // Stop the timer when recording stops
    }

    return () => clearInterval(timer); // Cleanup the interval when the component unmounts
  }, [recording]);

  
  const formatTime = (time) => {
    const hours = Math.floor(time / 3600);
    const minutes = Math.floor((time % 3600)/60);
    const seconds = time % 60;
    return `${hours.toString().padStart(2,"0")}:${minutes.toString().padStart(2,"0")}:${seconds.toString().padStart(2,"0")}`
  }

  // Start recording
  const handleStartRecording = () => {
    if (mediaRecorder.current) {
      setRecording(true);
      mediaRecorder.current.start();
    }
  };

  // Stop recording
  const handleStopRecording = () => {
    if (mediaRecorder.current) {
      setRecording(false);
      mediaRecorder.current.stop();
    }
  };

  // Start the camera when the component mounts
  React.useEffect(() => {
    startCamera();
    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        const stream = videoRef.current.srcObject;
        const tracks = stream.getTracks();
        tracks.forEach((track) => track.stop());
      }
    };
  }, []);

  // Handle modal open/close for User Manual
  const handleUserManualModal = (open) => setIsUserManualOpen(open);

  return (
    <div className="camera-container">

      <div className="camera-select"></div>

      <div className="video-container">
        <video ref={videoRef} autoPlay muted className="video"></video>
      </div>

      <div className="button-container">
        {/* Recording Button */}
        {recording ? (
          <Button
            className="stop-button"
            type="primary"
            onClick={handleStopRecording}
          >
            <span className="btn-text">Stop Recording</span>
          </Button>
        ) : (
          <Button
            className="record-button"
            type="primary"
            onClick={handleStartRecording}
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
