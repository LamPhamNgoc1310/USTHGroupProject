import React, { useState } from 'react';
import { Button, Modal, Input, Select } from 'antd';
import { BulbOutlined, BulbFilled } from '@ant-design/icons';
import './ToolBar.css';

const { Option } = Select;

function Toolbar({ isDarkMode, toggleTheme, isToolbarModalOpen, openToolbarModal, closeToolbarModal }) {
  const [fields, setFields] = useState(Array(5).fill({ text: '', option: '' }));

  // Handle text input change for each row
  const handleInputChange = (index, value) => {
    const updatedFields = [...fields];
    updatedFields[index] = {
      ...updatedFields[index], // Copy the existing row
      text: value, // Update only the text of the specific row
    };
    setFields(updatedFields); // Update state
  };

  // Handle select dropdown change for each row
  const handleSelectChange = (index, value) => {
    const updatedFields = [...fields];
    updatedFields[index] = {
      ...updatedFields[index], // Copy the existing row
      option: value, // Update only the option of the specific row
    };
    setFields(updatedFields); // Update state
  };

  return (
    <div className='toolbar'>
      {/* Toggle Theme Button */}
      <Button
        className='toolbar-btn'
        type='link'
        onClick={toggleTheme}
        aria-label='Toggle Light/Dark Mode'
        icon={isDarkMode ? <BulbFilled /> : <BulbOutlined />}
      >
        {isDarkMode ? 'Dark Mode' : 'Light Mode'}
      </Button>

      {/* Open Setting Button */}
      <Button
        className='toolbar-btn'
        type='link'
        onClick={openToolbarModal} // Open modal when button clicked
        aria-label='Open Modal'
      >
        Open Keybind Setting
      </Button>

      {/* Assign Hand Gestures Modal */}
      <Modal
        title="Assign Hand Gestures"
        open={isToolbarModalOpen} // Modal open state
        onOk={closeToolbarModal} // Close modal on Ok
        onCancel={closeToolbarModal} // Close modal on Cancel
      >
        {fields.map((field, index) => (
          <div
            key={index}
            style={{
              display: 'flex',
              alignItems: 'center',
              marginBottom: '10px',
            }}
          >
            {/* Input box to edit labels */}
            <Input
              style={{ flex: 1, marginRight: '10px' }}
              value={field.text}
              onChange={(e) => handleInputChange(index, e.target.value)} // Update specific row text
              placeholder={`Input ${index + 1}`}
            />

            {/* Select dropdown to assign key */}
            <Select
              style={{ flex: 1 }}
              value={field.option} // Select the option for the current row
              onChange={(value) => handleSelectChange(index, value)} // Update the selected option for the specific row
              placeholder='Select a key'
            >
              <Option value='option1'>Key 1</Option>
              <Option value='option2'>Key 2</Option>
              <Option value='option3'>Key 3</Option>
              <Option value='option4'>Key 4</Option>
              <Option value='option5'>Key 5</Option>
            </Select>
          </div>
        ))}
      </Modal>
    </div>
  );
}

export default Toolbar;
