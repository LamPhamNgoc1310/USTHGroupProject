import React, { useState } from 'react';
import Camera from '../Camera/Camera.jsx';
import Toolbar from '../Toolbar/Toolbar.jsx';

import './Home.css';

function Home() {
  const [isToolbarModalOpen, setIsToolbarModalOpen] = useState(false); // Toolbar modal state
  const [isDarkMode, setIsDarkMode] = useState(false);

  // Toggle theme between dark and light
  const toggleTheme = () => setIsDarkMode((prev) => !prev);
  
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
    </div>
  );
}

export default Home;
