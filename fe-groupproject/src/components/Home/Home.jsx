import React, { useState } from 'react';
import Camera from '../Camera/Camera.jsx';
import Toolbar from '../Toolbar/Toolbar.jsx';
import { Button, Modal } from 'antd';
import './Home.css';

function Home() {
  const [recording, setRecording] = useState(false);
  const [isUserManualOpen, setIsUserManualOpen] = useState(false); // User Manual modal state
  const [isToolbarModalOpen, setIsToolbarModalOpen] = useState(false); // Toolbar modal state
  const [isDarkMode, setIsDarkMode] = useState(false);

  // Toggle theme between dark and light
  const toggleTheme = () => setIsDarkMode((prev) => !prev);
  
  // Toggle recording state
  const toggleRecording = () => setRecording((prev) => !prev);

  // Handle modal open/close for User Manual
  const handleUserManualModal = (open) => setIsUserManualOpen(open);
  
  // Handle modal open/close for Toolbar
  const openToolbarModal = () => setIsToolbarModalOpen(true);
  const closeToolbarModal = () => setIsToolbarModalOpen(false);

  return (
    <div className={`home-container ${isDarkMode ? 'dark-mode' : 'light-mode'}`}>

      <div className="home-toolbar">
        <Toolbar
          isDarkMode={isDarkMode}
          toggleTheme={toggleTheme}
          isToolbarModalOpen={isToolbarModalOpen}
          openToolbarModal={openToolbarModal}
          closeToolbarModal={closeToolbarModal}
        />
      </div>

      <div className='home-camera'>
        <Camera />
      </div>

      <div className="button-container">
        {/* Recording Button */}
        <Button 
          className='record-button' 
          type="primary" 
          onClick={toggleRecording}>
            {recording ? 'STOP RECORDING' : 'RECORD'}
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
            <p>Lorem, ipsum dolor sit amet consectetur adipisicing elit. Vel laboriosam tempore dolore adipisci ducimus, 
            officiis doloremque facilis atque, illum ex recusandae optio eos dicta quisquam repudiandae, iste quod a maxime?</p>
        </Modal>

      </div>

    </div>
  );
}

export default Home;
