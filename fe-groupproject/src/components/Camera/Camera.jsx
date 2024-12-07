import React, { useState, useEffect, useRef } from "react";
import { Button, Modal } from "antd";
import "./Camera.css";

const { ipcRenderer } = window.require("electron");

function Camera() {
  const [isUserManualOpen, setIsUserManualOpen] = useState(false);
  const [flaskRunning, setFlaskRunning] = useState(false); // Flask server status
  const [cameraDuration, setCameraDuration] = useState(0); // Camera open duration

  const videoRef = useRef(null);
  const timerRef = useRef(null); // Reference for the timer interval

  // Start the Flask server and track duration
  const handleStartCamera = () => {
    if (flaskRunning) {
      console.log("Flask server is already running.");
      return;
    }

    ipcRenderer.send("start-flask"); // Send a signal to the main process to start Flask

    ipcRenderer.once("flask-started", (event, status) => {
      if (status.success) {
        console.log("Flask server started successfully.");
        setFlaskRunning(true);

        // Start tracking the duration
        timerRef.current = setInterval(() => {
          setCameraDuration((prev) => prev + 1);
        }, 1000);
      } else {
        console.error("Failed to start Flask server:", status.error);
      }
    });
  };

  // Stop the Flask server and reset duration
  const handleStopCamera = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current); // Clear the timer
    }

    setFlaskRunning(false);
    setCameraDuration(0); // Reset duration
    ipcRenderer.send("stop-flask"); // Signal to stop Flask server
  };

  // Format time for the display
  const formatTime = (time) => {
    const hours = Math.floor(time / 3600);
    const minutes = Math.floor((time % 3600) / 60);
    const seconds = time % 60;
    return `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
  };

  // Cleanup when the component unmounts
  useEffect(() => {
    return () => {
      if (flaskRunning) {
        ipcRenderer.send("stop-flask"); // Ensure Flask is stopped
        if (timerRef.current) {
          clearInterval(timerRef.current);
        }
      }
    };
  }, [flaskRunning]);

  // Handle user manual modal visibility
  const handleUserManualModal = (open) => {
    setIsUserManualOpen(open);
  };

  return (
    <div className="camera-container">
      <div className="camera-select"></div>
      <div className="video-container">
        {/* Use iframe to display Flask's video feed */}
        {flaskRunning ? (
          <iframe
            src="http://localhost:5000/video_feed"
            title="Video Feed"
            width="640"
            height="480"
            frameBorder="0"
            allowFullScreen
            ref={videoRef}
            onError={() => {
              alert("Failed to load video feed.");
            }}
          ></iframe>
        ) : (
          <p>Start the camera to view the feed.</p>
        )}
      </div>

      <div className="button-container">
        {/* Start/Stop Camera Button */}
        {flaskRunning ? (
          <Button
            className="stop-camera-button"
            type="primary"
            onClick={handleStopCamera}
          >
            Stop Camera
          </Button>
        ) : (
          <Button
            className="start-camera-button"
            type="primary"
            onClick={handleStartCamera}
          >
            Start Camera
          </Button>
        )}

        {/* Duration Display */}
        <div className="duration-display">
          <span>Duration: {formatTime(cameraDuration)}</span>
        </div>

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
            <h2>1. Start Camera</h2>
            <li>Press the "Start Camera" button to launch the camera feed.</li>
            <li>The app will display the live video feed.</li>
            <li>The duration for which the camera has been open will be shown.</li>
          </ul>
          <ul>
            <h2>2. Keybinding</h2>
            <li>Press "Open Keybind Setting" to configure your shortcuts.</li>
            <li>You can assign gestures to keybinds in the settings.</li>
          </ul>
        </Modal>
      </div>
    </div>
  );
}

export default Camera;
