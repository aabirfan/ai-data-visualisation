import { useState } from "react";
import { FaArrowRight } from "react-icons/fa"; 
import Modal from "../../../modals/modal";
import Archived_Graphs_List from "./archived_graphs_list";
import PromptHistory from "./promptHistory"; 
import "../../../styles/modals.css";
import { IoMdClose } from "react-icons/io";

interface ChartInputProps {
  onSubmit: (query: string) => void; 
  loading: boolean;
  selectedAsset: string;
}

export default function ChartInput({ onSubmit, loading, selectedAsset }: ChartInputProps) {
  const [query, setQuery] = useState("");
  const [isModalOpen, setModalOpen] = useState(false);
  const [isGraphOpen, setIsGraphOpen] = useState(false);
  const [isPromptHistoryOpen, setPromptHistoryOpen] = useState(false);

  const openModal = () => setModalOpen(true);
  const closeModal = () => setModalOpen(false);
  const openPromptHistory = () => setPromptHistoryOpen(true);
  const closePromptHistory = () => setPromptHistoryOpen(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>, asset_id: string) => {
    e.preventDefault();

    if (!query.trim() || !asset_id) {
      console.error("Missing query or asset_id");
      return;
    }
  
    const data = {
      query,
      asset_id
    };

    console.log("Sending data:", data);
    
    try {
      const response = await fetch("http://localhost:8000/api/save-prompt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
  
      const result = await response.json();
      console.log("Upload Success:", result);
      onSubmit(data.query);
      setQuery("");
    } catch (error) {
      console.error("Upload Error:", error);
    }
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

     <form
        onSubmit={(e) => handleSubmit(e, selectedAsset)} 
        className="chart-input-wrapper"
      >
  
        <input
          type="text"
          placeholder="Enter chart suggestion..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="chart-input"
        />
        <button type="submit" className="chart-send-button">
          {loading ? <div className="spinner"></div> : <FaArrowRight className="chart-send-icon" />}
        </button>
      </form>

      <div className="input-btns">
        <button onClick={openPromptHistory}>Prompt history</button>
        <button onClick={openModal}>Archived charts</button>
      </div>

      <PromptHistory isOpen={isPromptHistoryOpen} onClose={closePromptHistory} onSubmit={onSubmit} selectedAsset={selectedAsset} />

      <Modal isOpen={isModalOpen} onClose={closeModal}>
        <div className="modal-header">
          <h2>Archived Charts</h2>
          {!isGraphOpen && ( 
            <button className="close-btn" onClick={closeModal}>
              <IoMdClose />
            </button>
          )}
        </div>
        <Archived_Graphs_List isOpen={isModalOpen} onClose={closeModal} setIsGraphOpen={setIsGraphOpen} selectedAsset={selectedAsset} />
      </Modal>
    </div>
  );
}
