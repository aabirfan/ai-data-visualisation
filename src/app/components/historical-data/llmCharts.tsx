import { useState } from "react";
import { GoogleGenerativeAI } from "@google/generative-ai";
import ChartInput from "./chartInput";
import "../styles/llmCharts.css";

export default function LLMCharts() {
  const [response, setResponse] = useState(""); 
  const [loading, setLoading] = useState(false);

  const handleChartRequest = async (query: string) => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/prompt", {
        method: "POST",
        headers: {
          "Content-Type": "application/json", 
        },
        body: JSON.stringify({ prompt: query }),
      });
  
      const data = await res.json();
      if (res.ok) {
        setResponse(data.message);
      } else {
        setResponse("Error: " + data.detail);
      }
    } catch (error) {
      console.error("Error sending prompt:", error);
      setResponse("An error occurred.");
    }
    setLoading(false);
  };


  return (
    <div className="llm-container">
      {}
      <ChartInput onSubmit={handleChartRequest} />

      {}
      {loading && <p className="loading">Generating response...</p>}
      {response && (
        <div className="response-box">
          <p>{response}</p> {}
        </div>
      )}
    </div>
  );
}
