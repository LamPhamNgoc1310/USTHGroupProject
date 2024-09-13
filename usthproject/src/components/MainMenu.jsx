import React, { useState } from "react";
import "./MainMenu.css";

function MainMenu() {
  const [recording, setRecording] = useState(false);

  const handleRecordingClick = () => {
    setRecording(!recording);
  };

  return (
    <div className="mainmenu-container">
      <div className="mainmenu-header">
        <div className="logo">
          This is header: 10% horizontal
          <img src="" alt="" />
          <h6>Name</h6>
        </div>
      </div>

      <div className="camera-box">
        <h1>this is the camera box: 60% vertical
        </h1>
      </div>

      <div className="manuals-area">
        <div className="buttons-area">
          Button area
          <button onClick={handleRecordingClick}>
            {recording ? <h5>Standing by</h5> : <h5>Recording</h5>}
          </button>
        </div>
        <h1>
          This is the manuals page: 40% vertical
          Lorem ipsum, dolor sit amet consectetur adipisicing elit. Accusantium
          quos, debitis nam soluta voluptatem dicta nihil placeat! Odio magni
          vitae, obcaecati quasi suscipit voluptatem id dolorum dignissimos
          velit, iste neque!
        </h1>
      </div>
    </div>
  );
}

export default MainMenu;
