import {useState } from "react";
import { FaArrowRight } from "react-icons/fa"; 
import Modal from "../../../modals/modal";
import Archived_Graphs_List from "./archived_graphs_list";
import "../../../styles/modals.css";
import { IoMdClose } from "react-icons/io";

interface ChartInputProps {
  onSubmit: (query: string | number[]) => void;
  loading: boolean;
}

export default function ChartInput({ onSubmit, loading,}: ChartInputProps) {
  const [query, setQuery] = useState("");
  const [isModalOpen, setModalOpen] = useState(false)
  const [isGraphOpen, setIsGraphOpen] = useState(false);

  const openModal = () => setModalOpen(true);
  const closeModal = () => setModalOpen(false);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!query.trim()) return;
    onSubmit(query);
    setQuery("");
  };

  return (
    <div className="chart-container">
      <div className="input-title">
        <h2 className="chart-title">What can I help you with?</h2>
        <img 
              src={loading ? "illi_loading.png" : "illi.png"} 
              alt="Status Image" 
              className={loading ? "flash" : ""} 
            />    
         </div>

      <form onSubmit={handleSubmit} className="chart-input-wrapper">
        <input
          type="text"
          placeholder="Enter chart suggestion..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="chart-input"
        />
        <button type="submit" className="chart-send-button">
            {loading ? (
              <div className="spinner"></div>
            ) : (
              <FaArrowRight className="chart-send-icon" />
            )}
       </button>
      </form>
      <div className="input-btns">
        <button >Prompt history</button>
        <button onClick={openModal}>Archived charts</button>
      </div>

      <div>

      <Modal isOpen={isModalOpen} onClose={closeModal}>
        <div className="modal-header">
        <h2>Archived Charts</h2>
        {!isGraphOpen && ( 
        <button className="close-btn" onClick={closeModal}>
        <IoMdClose />
        </button>
    )}
      </div>
        <Archived_Graphs_List isOpen={isModalOpen} onClose={closeModal} setIsGraphOpen={setIsGraphOpen} />
      </Modal>
    </div>
    </div>
  );
}
