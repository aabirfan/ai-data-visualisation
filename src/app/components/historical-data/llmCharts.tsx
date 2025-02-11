import { useState, useRef, useEffect } from "react";
import Highcharts from "highcharts";
import ChartInput from "./chartInput";
import HighchartsReact from 'highcharts-react-official';


import "../styles/llmCharts.css";
import "../styles/charts.css";

interface ApiResponse {
  message?: any; 
  error?: string;
}

interface HighchartsCodeRendererProps {
  code: string; 
}


const HighchartsCodeRenderer: React.FC<HighchartsCodeRendererProps> = ({ code }) => {
  const [options, setOptions] = useState<Highcharts.Options | null>(null);

  useEffect(() => {
    if (code) {
      try {
        const parsedOptions: Highcharts.Options = JSON.parse(code);
        setOptions(parsedOptions);
      } catch (error) {
        console.error("Error parsing the chart options:", error);
      }
    }
  }, [code]);

  if (!options) {
    return <p>Loading chart...</p>;
  }

  return (
    <div>
      <HighchartsReact highcharts={Highcharts} options={options} />
    </div>
  );
};

export default function LLMCharts() {
  const [response, setResponse] = useState<any | null>(null);
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
        if (typeof data.message === "string") {
          data.message = data.message.replace(/```typescript|```|json/g, "");
        }

        setResponse(data.message || "No Data Available.");
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
      <div className="llm-content">
        {loading && <p className="loading">Fetching data...</p>}
        <div className="graph-container">
          {response && <HighchartsCodeRenderer code={response} />}
        </div>
        {response && (
          <div className="response-box">
            <p>{response}</p>
          </div>
        )}
      </div>
    </div>
  );
}
