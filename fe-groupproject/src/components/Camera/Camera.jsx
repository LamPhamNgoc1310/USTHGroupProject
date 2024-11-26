import React, { useState, useEffect, useRef } from "react";
import { Button, Modal } from "antd";
import "./Camera.css";

const { ipcRenderer } = window.require('electron');

function Camera() {
  const [recording, setRecording] = useState(false);
  const [isUserManualOpen, setIsUserManualOpen] = useState(false);
  const [time, setTime] = useState(0);
  const [isSaveModalOpen, setIsSaveModalOpen] = useState(false); // Save Modal state

  const videoRef = useRef(null); 
  const mediaRecorder = useRef(null);
  const recordedChunks = useRef([]);

  const socketRef = useRef(null); // WebSocket reference
  const [frame, setFrame] = useState(null); // To store the latest frame

  // Start receiving frames from the WebSocket stream
  useEffect(() => {
    // Establish WebSocket connection
    socketRef.current = new WebSocket("ws://localhost:8765");

    // Handle incoming frames
    socketRef.current.onmessage = (event) => {
      console.log("Received frame:", event.data);  // Log the data to debug
      try {
        setFrame('data:image/jpeg;base64,' + event.data); // Update the frame
      } catch {
        console.error("Error processing frame:", error);
      }
    };
    
    socketRef.current.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    socketRef.current.onclose = () => {
      console.log("WebSocket connection closed");
    };

    // Cleanup when component unmounts
    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, []);

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

  // Format time for the display
  const formatTime = (time) => {
    const hours = Math.floor(time / 3600);
    const minutes = Math.floor((time % 3600) / 60);
    const seconds = time % 60;
    return `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
  };

  // Start recording
  const handleStartRecording = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject;
      const options = { mimeType: 'video/webm' };
      mediaRecorder.current = new MediaRecorder(stream, options);
  
      mediaRecorder.current.ondataavailable = (event) => {
        recordedChunks.current.push(event.data);
      };
  
      mediaRecorder.current.onstop = () => {
        console.log("Recording stopped.");
        setIsSaveModalOpen(true);
      };
  
      setRecording(true);
      mediaRecorder.current.start();
    } else {
      console.error("Camera not initialized.");
    }
  };

  // Stop recording
  const handleStopRecording = () => {
    if (mediaRecorder.current) {
      setRecording(false);
      mediaRecorder.current.stop();
    } else {
      console.error("MediaRecorder not initialized");
    }
  };

  // Handle user manual modal visibility
  const handleUserManualModal = (open) => {
    setIsUserManualOpen(open);
  };

  // Handle save modal visibility
  const handleSaveModal = async (confirm) => {
    if (!confirm) {
      setIsSaveModalOpen(false);
      return; // User canceled
    }
  
    setIsSaveModalOpen(false); // Close modal
    
    try {
      const blob = new Blob(recordedChunks.current, { type: "video/webm" });
      recordedChunks.current = [];  // Clear recorded chunks
  
      const arrayBuffer = await blob.arrayBuffer();
      const buffer = Buffer.from(arrayBuffer);
      ipcRenderer.send("save-video", buffer);
  
      ipcRenderer.once("save-video-reply", (event, response) => {
        if (response.success) {
          console.log("Video saved successfully.");
        } else {
          console.error("Failed to save video:", response.error);
        }
      });
    } catch (error) {
      console.error("Error while saving the video:", error);
    }
  };
  
  

  return (
    <div className="camera-container">
      <div className="camera-select"></div>
      <div className="video-container">
        {/* If a frame is received, show it as an image */}
        {frame && <img id="videoStream" src={frame} alt="Live Stream" className="video" />}
      </div>

      <div className="button-container">
        {/* Recording Button */}
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

        {/* User Manual Button */}
        <Button className="manual-button" type="link" onClick={() => handleUserManualModal(true)}>
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
            <li>Labels can be assigned to a shortcut/key</li>
          </ul>
        </Modal>

        {/* Save Confirmation Modal */}
        <Modal
          title="Save Video"
          open={isSaveModalOpen}
          onOk={() => handleSaveModal(true)} // Confirm save
          onCancel={() => handleSaveModal(false)} // Cancel save
        >
          <p>Do you want to save the recorded video?</p>
        </Modal>
      </div>
    </div>
  );
}

export default Camera;
