import React from 'react';
import { IoMdClose } from "react-icons/io";
import "../styles/modals.css";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode; 
}

const Modal: React.FC<ModalProps> = ({ isOpen, onClose, children }) => {
  if (!isOpen) return null;  

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <button className="close-btn" onClick={onClose}><IoMdClose/></button>
        {children} 
      </div>
    </div>
  );
};

export default Modal;
