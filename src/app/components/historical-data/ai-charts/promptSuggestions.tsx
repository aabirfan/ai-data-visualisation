import React, { useEffect, useState, useRef } from "react";
import "../../../styles/promptSuggestions.css";

interface Props {
  selectedAsset: string;
  onSubmit: (query: string) => void;
}

export default function PromptSuggestions({ selectedAsset, onSubmit }: Props) {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const hasFetched = useRef(false);
  
  useEffect(() => {
    async function fetchSuggestions() {
      if (!selectedAsset || hasFetched.current) return;
      hasFetched.current = true;

      try {
        const res = await fetch(`http://localhost:8000/api/prompt-suggestions/?asset_id=${selectedAsset}`);
        const data = await res.json();
        setSuggestions(data.suggestions);
      } catch (err) {
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
    <div className="suggestion-container">
      {suggestions.map((suggestion, index) => (
        <button
          key={index}
          className="suggestion-pill"
          onClick={() => handleSuggestionClick(suggestion)}
        >
          {suggestion}
        </button>
      ))}
    </div>
  );
}
