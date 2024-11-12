import React, { useState,  useRef, useEffect } from 'react'
import { Button, Modal } from 'antd';
import './Camera.css'

function Camera() {
  const [recording, setRecording] = useState(false);
  const [isUserManualOpen, setIsUserManualOpen] = useState(false); // User Manual modal state

   // Toggle recording state
   const toggleRecording = () => setRecording((prev) => !prev);

   // Handle modal open/close for User Manual
   const handleUserManualModal = (open) => setIsUserManualOpen(open);

   // Video capture
  return (
    <div className='camera-container'>
      <div className="video-container">
      
      </div>
      <div className="button-container">
        {/* Recording Button */}
        <Button 
          className='record-button' 
          type="primary" 
          onClick={toggleRecording}>
            <span className='btn-text'>
            {recording ? 'STOP' : 'RECORD'}
            </span>
        </Button>

        {/* User Manual Button */}
        <Button 
          className='manual-button' 
          type="link" 
          onClick={() => handleUserManualModal(true)}>
            User Manual
        </Button>

        {/* User Manual Modal */}
        <Modal 
          title="User Manual" 
          open={isUserManualOpen} 
          onOk={() => handleUserManualModal(false)} 
          onCancel={() => handleUserManualModal(false)}>
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
              <li>Labels can be asigned to a shortcut/key</li>
            </ul>

        </Modal>

      </div>
    </div>
  )
}

export default Camera
