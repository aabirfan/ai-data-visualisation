import { useState } from "react";
import { GoogleGenerativeAI } from "@google/generative-ai";
import ChartInput from "./chartInput";
import "./LLMCharts.css";

export default function LLMCharts() {
  const [response, setResponse] = useState(""); 
  const [loading, setLoading] = useState(false);

  const apiKey: string = process.env.NEXT_PUBLIC_GEMINI_API_KEY ?? "";
  if (!apiKey) throw new Error("Missing API Key. ");

  const genAI = new GoogleGenerativeAI(apiKey);
  const model = genAI.getGenerativeModel({ model: "gemini-pro" });

  const handleChartRequest = async (query: string) => {
    setLoading(true);
    setResponse(""); 

    try {
      console.log("Sending request to Gemini API with query:", query);

      const result = await model.generateContent({
        contents: [{ role: "user", parts: [{ text: query }] }],
      });

      console.log("Raw API Response:", result);

      const aiResponse = result.response.text ? await result.response.text() : "No response";

      console.log("Extracted AI Response:", aiResponse);
      setResponse(aiResponse);
    } catch (error) {
      console.error("Error fetching response:", error);
      setResponse("Error communicating with AI.");
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
          <h2>AI Response:</h2>
          <p>{response}</p> {}
        </div>
      )}
    </div>
  );
}
