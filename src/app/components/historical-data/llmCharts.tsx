import { useState } from "react";
import ChartInput from "./chartInput";
import "../styles/llmCharts.css";

interface ApiResponse {
  message?: string;
  error?: string;
}

export default function LLMCharts() {
  const [response, setResponse] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleChartRequest = async (query: string) => {
    setLoading(true);
    setResponse(null);

    try {
      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      const data: ApiResponse = await res.json();

      if (!res.ok) {
        setResponse("Unexpected error occurred.");
      } else {
        setResponse(data.message || "No data available.");
      }
    } catch (error) {
      console.error("Error sending request:", error);
      setResponse("An error occurred while processing your request.");
    }

    setLoading(false);
  };

  return (
    <div className="llm-container">
      <ChartInput onSubmit={handleChartRequest} />

      {loading && <p className="loading">Fetching data...</p>}

      {response && (
        <div className="response-box">
          <p>{response}</p>
        </div>
      )}
    </div>
  );
}
