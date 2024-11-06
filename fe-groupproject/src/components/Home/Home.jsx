import React, { useState } from 'react'
import Camera from '../Camera/Camera.jsx'
import {Button, Modal} from 'antd'
import './Home.css'

function Home() {
  const [recording, setRecording] = useState(false)
  const [isModalOpen, setIsModalOpen] = useState(false);
  const showModal = () => {
    setIsModalOpen(true);
  };
  const handleOk = () => {
    setIsModalOpen(false);
  };
  const handleCancel = () => {
    setIsModalOpen(false);
  };

  const handleRecordClick = () => {
    setRecording(!recording)
  }
  return (
    <div className='home-container'>
      <div className="home-toolbar">
        
      </div>
      <div className='home-camera'>
        <Camera />
      </div>

      <div className="button-container">
        <Button className='record-button' type="primary" onClick={handleRecordClick}>{recording ? 'STOP RECORDING' : 'RECORD'}</Button>
        <Button className='manual-button' type="link" onClick={showModal}>
        User Manual
      </Button>
      <Modal title="User Manual" open={isModalOpen} onOk={handleOk} onCancel={handleCancel}>
        <p>Lorem, ipsum dolor sit amet consectetur adipisicing elit. Vel laboriosam tempore dolore adipisci ducimus, officiis doloremque facilis atque, illum ex recusandae optio eos dicta quisquam repudiandae, iste quod a maxime?</p>
      </Modal>
      </div>
    </div>

  )
}

export default Home
