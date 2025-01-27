import { useState } from "react";
import { FaArrowRight } from "react-icons/fa"; 


export default function ChartInput({ onSubmit }: { onSubmit: (query: string) => void }) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!query.trim()) return;
    onSubmit(query);
    setQuery("");
  };

  return (
    <div className="chart-container">
      <h2 className="chart-title">How would you like your chart? ✨</h2>
      <form onSubmit={handleSubmit} className="chart-input-wrapper">
        <input
          type="text"
          placeholder="Enter chart suggestion..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="chart-input"
        />
        <button type="submit" className="chart-send-button">
          <FaArrowRight className="chart-send-icon" />
        </button>
      </form>
    </div>
  );
}
