import React, { useState, useEffect } from "react";
import Modal from "../../../modals/modal";
import { IoMdClose } from "react-icons/io";

interface PromptHistoryProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (query: string) => void;
}

export default function PromptHistory({ isOpen, onClose, onSubmit }: PromptHistoryProps) {
  const [promptHistory, setPromptHistory] = useState<{ query: string; timestamp: string }[]>([]);
  const [loading, setLoading] = useState(false); 

  const fetchPromptHistory = () => {
    setLoading(true); 
    fetch("http://localhost:8000/api/get-prompt-history/")
      .then((res) => res.json())
      .then((data) => {
        setPromptHistory(data.data || []);
      })
      .catch((error) => console.error(error))
      .finally(() => setLoading(false)); 
  };

  const handleClearHistory = () => {
    fetch("http://localhost:8000/api/clear-prompt-history/", { method: "DELETE" })
      .then((res) => res.json())
      .then(() => {
        setPromptHistory([]);
      })
      .catch((error) => console.error(error));
  };

  useEffect(() => {
    if (isOpen) {
      fetchPromptHistory();
    }
  }, [isOpen]);

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <div className="modal-title">
        <h2>Prompt History</h2>
      </div>

      <div className="prompt-list-container">
        {loading ? ( 
          <p className="loading-message">Loading...</p>
        ) : promptHistory.length > 0 ? (
          <ul className="prompt-list">
            {[...promptHistory].reverse().map((entry, index) => (
              <li key={index} className="prompt-item">
                <div className="prompt-text">
                  <strong>{entry.query}</strong> <br />
                  <small>
                    {new Date(entry.timestamp).toLocaleDateString()},{" "}
                    {new Date(entry.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </small>
                </div>
                <button
                  className="execute-btn"
                  onClick={() => {
                    onSubmit(entry.query);
                    onClose();
                  }}
                >
                  Ask again
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <p className="no-history-message">No prompt history yet.</p>
        )}
      </div>

      <div className="modal-header">
        <button className="close-btn" onClick={onClose}>
          <IoMdClose />
        </button>
      </div>
      <button className="clear-history-btn" onClick={handleClearHistory}>
        Clear History
      </button>
    </Modal>
  );
}
