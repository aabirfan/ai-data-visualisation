import React, { useEffect, useState, useRef } from "react";
import "../../styles/promptSuggestions.css";

interface Props {
  selectedAsset: string;
  isNew?: boolean;
  onSubmit: (query: string) => void;
}

export default function PromptSuggestions({ selectedAsset, isNew, onSubmit }: Props) {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const hasFetched = useRef(false);
  
  useEffect(() => {
    async function fetchSuggestions() {
      if (!selectedAsset || hasFetched.current) return;
      hasFetched.current = true;

      try {
        setLoading(true);
        const res = await fetch(`http://localhost:8000/api/prompt-suggestions/?asset_id=${selectedAsset}`);
        const data = await res.json();
        setSuggestions(data.suggestions);
      } catch (err) {
      } finally {
        setLoading(false);
      }
    }

    fetchSuggestions();
  }, [selectedAsset]);

  async function handleSuggestionClick(suggestion: string) {
    try {
      await fetch("http://localhost:8000/api/save-prompt/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: suggestion, asset_id: selectedAsset })
      });
    } catch (err) {
    }

    onSubmit(suggestion); 
  }

  return (
    <div className={`suggestion-container ${isNew ? "centered" : ""}`}>
      {loading ? (
        <p className="loading">Loading suggestions...</p>
      ) : (
        suggestions.map((suggestion, index) => (
          <button
            key={index}
            className="suggestion-pill"
            onClick={() => handleSuggestionClick(suggestion)}
          >
            {suggestion}
          </button>
        ))
      )}
    </div>
  );
}
