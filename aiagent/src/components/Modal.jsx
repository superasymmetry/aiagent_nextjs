// import React from 'react';
// import {X} from 'lucide-react';

// function Modal(){
//     return(
//         <div className='fixed inset-0 bg-gray-800 bg-opacity-30 backdrop-blur-sm flex justify-center'>
//             <div className='mt-10 flex flex-col gap5 text-white'>
//                 <button className='place-self-end'><X size={30}/></button>
//                 <div><title>Choose a template</title></div>
//                 <select>
//                     <option value ="template1">Hierarchical Agent</option>
//                     <option value ="template2">Peer-to-peer Agent</option>
//                     <option value ="template3">Master Agent</option>
//                 </select>
//                 <p>Browse user-made templates</p>
//             </div>

//         </div>
//     )
// }

// export default Modal;

import React, { useState, useRef } from 'react';
import { X } from 'lucide-react';

function Modal({ onClose, onTemplateSelect }) {
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const modalRef = useRef();

  const closeModal = (e) => {
    if (modalRef.current === e.target) {
      onClose();
    }
  }

  const handleSelectChange = (e) => {
    setSelectedTemplate(e.target.value);
    console.log('Selected template:', e.target.value);
    setSelectedTemplate(e.target.value);
    console.log(selectedTemplate);
  };
  

  return (
    <div ref={modalRef} onClick={closeModal} className='fixed inset-0 bg-gray-800 bg-opacity-30 backdrop-blur-sm flex justify-center items-center z-50'>
      <div className='bg-white rounded-lg p-6 shadow-lg w-[320px] text-black relative'>
        <button
          className='absolute top-3 right-3 text-gray-500 hover:text-gray-800'
          onClick={onClose}
        >
          <X size={24} />
        </button>

        <h2 className='text-lg font-semibold mb-4'>Choose a template</h2>

        <select
          value={selectedTemplate}
          onChange={handleSelectChange}
          className='w-full px-3 py-2 border border-gray-300 rounded-md mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500'
        >
          <option value="">Select a template</option>
          <option value="template1">Hierarchical Agent</option>
          <option value="template2">Peer-to-peer Agent</option>
          <option value="template3">Master Agent</option>
        </select>

        <p className='text-sm text-gray-600'>
          Browse user-made templates.
        </p>
      </div>
    </div>
  );
}

export default Modal;
